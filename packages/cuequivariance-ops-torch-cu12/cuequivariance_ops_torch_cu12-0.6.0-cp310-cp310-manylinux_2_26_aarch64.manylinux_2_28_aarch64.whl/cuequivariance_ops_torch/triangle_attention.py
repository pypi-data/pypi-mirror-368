# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import os
from typing import List, Optional, Tuple

import torch

import cuequivariance_ops_torch._ext as ops

CUEQ_TRIATTN_FALLBACK_THRESHOLD: int = int(
    os.getenv("CUEQ_TRIATTN_FALLBACK_THRESHOLD", "100")
)


def _should_use_tf32():
    tf32_override = os.getenv("NVIDIA_TF32_OVERRIDE")
    return (
        tf32_override != "0" and torch.backends.cuda.matmul.allow_tf32
    ) or tf32_override == "1"


def _permute_final_dims(tensor: torch.Tensor, inds: List[int]):
    zero_index = -1 * len(inds)
    first_inds = list(range(len(tensor.shape[:zero_index])))
    return tensor.permute(first_inds + [zero_index + i for i in inds])


def _triangle_attention_torch(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    bias: torch.Tensor,
    mask: Optional[torch.Tensor],
    scale: Optional[float],
):
    """PyTorch reference implementation matching CUDA kernel API and precision. Fallback option for short sequences."""
    if scale is None:
        scale = 1.0 / (query.shape[-1] ** 0.5)

    # Permute key for matrix multiplication
    key = _permute_final_dims(key, (1, 0))

    # Compute attention scores
    a = torch.matmul(query * scale, key)

    # Add biases
    if mask is not None:
        mask = -1e9 * (~mask).float()
        biases = [mask, bias]
    else:
        biases = [bias]

    for b in biases:
        a += b

    a = torch.nn.functional.softmax(a, -1)
    a = torch.matmul(a, value)
    return a


# TODO: support needs_input_grad
@torch.library.custom_op(
    "cuequivariance_ops::triangle_attention_bwd",
    mutates_args=(),
    device_types="cuda",
)
def _(
    d_o: torch.Tensor,
    o: torch.Tensor,
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    bias: torch.Tensor,
    mask: Optional[torch.Tensor],
    lse: torch.Tensor,
    scale: Optional[float],
) -> List[torch.Tensor]:
    """
    Custom Torch operation for backward pass of triangle attention
    """

    q = q.detach().contiguous()
    k = k.detach().contiguous()
    v = v.detach().contiguous()
    bias = bias.detach().contiguous()
    d_q = torch.zeros_like(q)
    d_k = torch.empty_like(k)
    d_v = torch.empty_like(v)
    d_tb = torch.zeros_like(bias)
    d_o_dot = q.new_empty(q.shape[:-1], dtype=torch.float32)
    dq_fp32_buf = (
        d_q if q.dtype == torch.float32 else q.new_zeros(q.shape, dtype=torch.float32)
    )
    stream = torch.cuda.current_stream().cuda_stream
    use_tf32 = _should_use_tf32()

    if mask is not None:
        mask = mask.to(dtype=torch.bool).detach().contiguous()

    ops.triangle_attention_bwd(
        d_q,
        d_k,
        d_v,
        d_tb,
        d_o_dot,
        dq_fp32_buf,
        d_o.detach().contiguous(),
        o.detach().contiguous(),
        lse.detach().contiguous(),
        q,
        k,
        v,
        mask,
        bias,
        scale,
        use_tf32,
        stream,
    )

    return d_q, d_k, d_v, d_tb


@torch.library.register_fake(
    "cuequivariance_ops::triangle_attention_bwd",
)
def _(
    d_o: torch.Tensor,
    o: torch.Tensor,
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    bias: torch.Tensor,
    mask: Optional[torch.Tensor],
    lse: torch.Tensor,
    scale: Optional[float],
) -> List[torch.Tensor]:
    """
    Fake Torch operation for backward pass of triangle attention
    """
    return (
        torch.empty_like(q),
        torch.empty_like(k),
        torch.empty_like(v),
        torch.empty_like(bias),
    )


def ensure_dims(ten: torch.Tensor, n: int) -> torch.Tensor:
    while len(ten.shape) < n:
        ten = ten.unsqueeze(0)
    return ten


@torch.library.custom_op(
    "cuequivariance_ops::triangle_attention",
    mutates_args=(),
    device_types="cuda",
)
def _(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    bias: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
    scale: Optional[float] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Custom Torch operation for forward pass of triangle attention
    """
    stream = torch.cuda.current_stream().cuda_stream

    q = q.detach().contiguous()
    o = torch.empty_like(q)
    softmax_lse = q.new_empty(q.shape[:-1], dtype=torch.float32)
    softmax_max = q.new_empty(q.shape[:-1], dtype=torch.float32)
    use_tf32 = _should_use_tf32()

    if mask is not None:
        mask = mask.to(dtype=torch.bool).detach().contiguous()

    # Call kernel
    ops.triangle_attention(
        o,
        softmax_lse,
        softmax_max,
        q,
        k.detach().contiguous(),
        v.detach().contiguous(),
        mask,
        bias.detach().contiguous(),
        scale,
        use_tf32,
        stream,
    )
    return o, softmax_lse, softmax_max


@torch.library.register_fake(
    "cuequivariance_ops::triangle_attention",
)
def _(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    bias: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
    scale: Optional[float] = None,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Fake Torch operation for forward pass of triangle attention
    """
    return (torch.empty_like(q), q.new_empty(q.shape[:-1]), q.new_empty(q.shape[:-1]))


def _backward(ctx, d_output, *args):
    """
    Autograd fixture for backward pass of triangle attention
    """
    q, k, v, bias, o, lse = ctx.saved_tensors
    d_q, d_k, d_v, dbias = torch.ops.cuequivariance_ops.triangle_attention_bwd(
        d_output,
        o,
        q,
        k,
        v,
        bias,
        ctx.mask,
        lse,
        ctx.scale,
    )
    return d_q, d_k, d_v, dbias, None, None


def _setup_context(ctx, inputs, output):
    """
    Autograd fixture for backward pass of triangle attention
    """
    q, k, v, bias, mask, scale = inputs
    o, lse, _ = output
    ctx.save_for_backward(q, k, v, bias, o, lse)
    ctx.mask = mask.detach() if mask is not None else None
    ctx.scale = scale


torch.library.register_autograd(
    "cuequivariance_ops::triangle_attention",
    _backward,
    setup_context=_setup_context,
)


def triangle_attention(
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    bias: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
    scale: Optional[float] = None,
    return_aux: bool = False,
) -> torch.Tensor | Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # Ensure all tensors have 5 dimensions
    q = ensure_dims(q, 5)
    k = ensure_dims(k, 5)
    v = ensure_dims(v, 5)

    # Convert bias to float32 and ensure dimensions
    bias = ensure_dims(bias.to(dtype=torch.float32), 5)

    # Handle mask if provided
    if mask is not None:
        mask = ensure_dims(mask.to(dtype=torch.bool), 5)

    """
    Normally, this would have been in @register_autocast - but we have to keep bias in float32
    Another problem is that torch.get_autocast_dtype breaks jit.script() here
    and we don't want this conversion inside the custom op
    (because then we have no way of saving casted q,k,v for backward except returning them)
    Since scripting under autocast is not super reliable anyway, we just do autocast here.
    Chances that q, k and v are not cast by this time are slim, too - so the worst that can
    happen is we lose some efficiency in that exotic case of autocast + jit.script().
    """
    seq_len = q.shape[-2]
    if not torch._jit_internal.is_scripting():
        if torch.is_autocast_enabled():
            dtype = torch.get_autocast_dtype("cuda")
            q = q.to(dtype=dtype)
            k = k.to(dtype=dtype)
            v = v.to(dtype=dtype)

        if seq_len <= CUEQ_TRIATTN_FALLBACK_THRESHOLD and not return_aux:
            # Use original PyTorch implementation for short sequences
            return _triangle_attention_torch(q, k, v, bias, mask, scale)
    else:
        if seq_len <= 100 and not return_aux:
            # Hardcoded in order to not break scripted mode with getenv or global variables
            return _triangle_attention_torch(q, k, v, bias, mask, scale)

    output, sm_lse, sm_max = torch.ops.cuequivariance_ops.triangle_attention(
        q, k, v, bias, mask, scale
    )

    if return_aux:
        return output, sm_lse, sm_max
    else:
        return output
