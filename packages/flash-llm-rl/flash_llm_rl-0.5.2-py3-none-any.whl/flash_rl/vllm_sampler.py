# SPDX-License-Identifier: Apache-2.0

from typing import Optional

import torch
import torch.nn as nn

from vllm import envs
from vllm.logger import init_logger
from vllm.platforms import current_platform

logger = init_logger(__name__)

try:
    import flashinfer.sampling
    is_flashinfer_available = True
except ImportError:
    is_flashinfer_available = False


class HackedTopKTopPSampler(nn.Module):

    def __init__(self):
        super().__init__()
        if current_platform.is_cuda():
            if is_flashinfer_available:
                flashinfer_version = flashinfer.__version__
                if flashinfer_version >= "0.2.3":
                    # FIXME(DefTruth): Currently, we have errors when using
                    # FlashInfer>=v0.2.3 for top-p & top-k sampling. As a
                    # workaround, we disable FlashInfer for top-p & top-k
                    # sampling by default while FlashInfer>=v0.2.3.
                    # The sampling API removes the success return value
                    # of all sampling API, which is not compatible with
                    # earlier design.
                    # https://github.com/flashinfer-ai/flashinfer/releases/
                    # tag/v0.2.3
                    logger.info(
                        "Currently, FlashInfer top-p & top-k sampling sampler "
                        "is disabled because FlashInfer>=v0.2.3 is not "
                        "backward compatible. Falling back to the PyTorch-"
                        "native implementation of top-p & top-k sampling.")
                    self.forward = self.forward_native
                elif envs.VLLM_USE_FLASHINFER_SAMPLER is not False:
                    # NOTE(woosuk): The V0 sampler doesn't use FlashInfer for
                    # sampling unless VLLM_USE_FLASHINFER_SAMPLER=1 (i.e., by
                    # default it is unused). For backward compatibility, we set
                    # `VLLM_USE_FLASHINFER_SAMPLER` as None by default and
                    # interpret it differently in V0 and V1 samplers: In V0,
                    # None means False, while in V1, None means True. This is
                    # why we use the condition
                    # `envs.VLLM_USE_FLASHINFER_SAMPLER is not False` here.
                    logger.info("Using FlashInfer for top-p & top-k sampling.")
                    self.forward = self.forward_cuda
                else:
                    logger.warning(
                        "FlashInfer is available, but it is not enabled. "
                        "Falling back to the PyTorch-native implementation of "
                        "top-p & top-k sampling. For the best performance, "
                        "please set VLLM_USE_FLASHINFER_SAMPLER=1.")
                    self.forward = self.forward_native
            else:
                logger.warning(
                    "FlashInfer is not available. Falling back to the PyTorch-"
                    "native implementation of top-p & top-k sampling. For the "
                    "best performance, please install FlashInfer.")
                self.forward = self.forward_native
        elif current_platform.is_tpu():
            if envs.VLLM_TPU_DISABLE_TOPK_TOPP_OPTIMIZATION:
                logger.warning(
                    "TPU-specific optimization for top-k & top-p sampling are "
                    "disabled, falling back to PyTorch-native implementation "
                    "which could be very slow.")
                self.forward = self.forward_native
            else:
                self.forward = self.forward_tpu
        else:
            self.forward = self.forward_native

    def forward_native(
        self,
        logits: torch.Tensor,
        generators: dict[int, torch.Generator],
        k: Optional[torch.Tensor],
        p: Optional[torch.Tensor],
    ) -> torch.Tensor:
        """PyTorch-native implementation of top-k and top-p sampling."""    
        logits = apply_top_k_top_p(logits, k, p)
        return random_sample(logits, generators), logits

    def forward_cuda(
        self,
        logits: torch.Tensor,
        generators: dict[int, torch.Generator],
        k: Optional[torch.Tensor],
        p: Optional[torch.Tensor],
    ) -> torch.Tensor:
        """More optimized implementation for top-k and top-p sampling."""
        if k is None and p is None:
            # We prefer `random_sample` over `flashinfer_sample` when sorting is
            # not needed. This is because `random_sample` does not require
            # CPU-GPU synchronization while `flashinfer_sample` does.
            return random_sample(logits, generators), logits
        else:
            return self.forward_native(logits, generators, k, p)
        # return flashinfer_sample(probs, k, p, generators)

    def forward_tpu(
        self,
        logits: torch.Tensor,
        generators: dict[int, torch.Generator],
        k: Optional[torch.Tensor],
        p: Optional[torch.Tensor],
    ) -> torch.Tensor:
        # If only top-k is specified, use pytorch's builtin topk op. This leads
        # to significant speed up on TPU compared to using apply_top_k_top_p.
        if k is not None and p is None:
            topk_values, topk_indices = torch.topk(logits, k, dim=-1)

            mask = torch.ones_like(logits, dtype=torch.bool)
            mask.scatter_(-1, topk_indices, False)
            logits.masked_fill_(mask, float('-inf'))
        else:
            # TODO Placeholder for TPU optimized topp kernel
            # logits = apply_top_k_top_p(logits, k, p)
            pass

        return random_sample(logits, generators), logits

def apply_top_k_top_p(
    logits: torch.Tensor,
    k: Optional[torch.Tensor],
    p: Optional[torch.Tensor],
) -> torch.Tensor:
    """Apply top-k and top-p masks to the logits.

    This function sorts the logits tensor, which can be slow for large batches.
    """
    if k is None and p is None:
        return logits
    logits_sort, logits_idx = logits.sort(dim=-1, descending=False)

    if k is not None:
        # Apply top-k.
        top_k_mask = logits_sort.size(1) - k.to(torch.long)  # shape: B
        # Get all the top_k values.
        top_k_mask = logits_sort.gather(1, top_k_mask.unsqueeze(dim=1))
        top_k_mask = logits_sort < top_k_mask
        logits_sort.masked_fill_(top_k_mask, -float("inf"))

    if p is not None:
        # Apply top-p.
        probs_sort = logits_sort.softmax(dim=-1)
        probs_sum = probs_sort.cumsum(dim=-1)
        top_p_mask = probs_sum <= 1 - p.unsqueeze(dim=1)
        # at least one
        top_p_mask[:, -1] = False
        logits_sort.masked_fill_(top_p_mask, -float("inf"))

    # Re-sort the probabilities.
    logits = logits_sort.scatter(dim=-1, index=logits_idx, src=logits_sort)
    return logits

def random_sample(
    logits: torch.Tensor,
    generators: dict[int, torch.Generator],
) -> torch.Tensor:
    """Randomly sample from the probabilities.

    We use this function instead of torch.multinomial because torch.multinomial
    causes CPU-GPU synchronization.
    """
    gumbel = torch.empty_like(logits)
    # NOTE(woosuk): To batch-process the requests without their own seeds,
    # which is the common case, we first assume that every request does
    # not have its own seed. Then, we overwrite the values for the requests
    # that have their own seeds.
    if len(generators) != logits.shape[0]:
        gumbel.exponential_()
    if generators:
        # TODO(woosuk): This can be slow because we handle each request
        # one by one. Optimize this.
        for i, generator in generators.items():
            gumbel[i].exponential_(generator=generator)
    return logits.add_(gumbel, alpha=-1).argmax(dim=-1).view(-1)
