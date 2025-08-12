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
from typing import Optional

import torch
import triton

from cuequivariance_ops.triton.pair_bias import (
    pair_bias_linear_mask_forward_kernel,
    pair_bias_mask_forward_kernel,
    pair_bias_norm_linear_mask_forward_kernel,
)
from cuequivariance_ops_torch.fused_layer_norm_torch import (
    Layout,
    fused_layer_norm_backward_kernel_wrapper,
    fused_layer_norm_forward_kernel_wrapper,
)
from cuequivariance_ops_torch.utils import nvtx_range_pop, nvtx_range_push

CUEQ_ATTENTION_PAIR_BIAS_FALLBACK_THRESHOLD: int = int(
    os.getenv("CUEQ_ATTENTION_PAIR_BIAS_FALLBACK_THRESHOLD", "100")
)


def _attention_pair_bias_mask_torch(
    z: torch.Tensor,
    mask: torch.Tensor,
    w_proj_z: torch.Tensor,
    b_proj_z: Optional[torch.Tensor],
    w_ln: Optional[torch.Tensor],
    b_ln: Optional[torch.Tensor],
    num_heads: int,
    multiplicity: int,
    eps: float,
    inf: float,
    compute_pair_bias: bool,
) -> torch.Tensor:
    """Original PyTorch implementation of attention pair bias mask."""
    z_dtype = z.dtype
    B_mask = mask.shape[0]
    B_z = z.shape[0]
    mask_with_multiplicity = B_mask == B_z * multiplicity and multiplicity > 1

    z = z.to(torch.float32)
    mask = mask.to(torch.float32)

    if compute_pair_bias:
        w_proj_z = w_proj_z.to(torch.float32)
        if b_proj_z is not None:
            b_proj_z = b_proj_z.to(torch.float32)
        w_ln = w_ln.to(torch.float32)
        b_ln = b_ln.to(torch.float32)

        B, U, V, DIM_Z = z.shape
        z_norm = torch.nn.functional.layer_norm(
            z,
            (DIM_Z,),
            weight=w_ln,
            bias=b_ln,
            eps=eps,
        )

        z_proj = torch.nn.functional.linear(z_norm, w_proj_z, bias=b_proj_z)
        z_proj = torch.einsum("bijh->bhij", z_proj).contiguous()

    else:
        assert z.shape[-1] == num_heads
        z_norm = z
        z_proj = z_norm
        z_proj = torch.einsum("bijh->bhij", z_proj).contiguous()

    if mask_with_multiplicity:
        z_proj = z_proj.repeat_interleave(multiplicity, dim=0).contiguous()

    out = z_proj + (1.0 - mask[:, None, None].float()) * (-inf)
    out = out.to(z_dtype)

    if not mask_with_multiplicity:
        out = out.repeat_interleave(multiplicity, dim=0).contiguous()

    return out


def _attention_pair_bias_torch(
    s: torch.Tensor,
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    z: torch.Tensor,
    mask: torch.Tensor,
    num_heads: int,
    w_proj_z: torch.Tensor,
    w_proj_g: torch.Tensor,
    w_proj_o: torch.Tensor,
    w_ln_z: Optional[torch.Tensor],
    b_ln_z: Optional[torch.Tensor],
    b_proj_z: Optional[torch.Tensor] = None,
    b_proj_g: Optional[torch.Tensor] = None,
    b_proj_o: Optional[torch.Tensor] = None,
    inf: float = 1e6,
    eps: float = 1e-5,
    attn_scale: Optional[float] = None,
    compute_pair_bias: bool = True,
    multiplicity: int = 1,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Original PyTorch implementation of attention pair bias."""
    B, H, U, D_Q = q.shape

    z_dtype = z.dtype
    s = s.to(torch.float32)
    q = q.to(torch.float32)
    k = k.to(torch.float32)
    v = v.to(torch.float32)
    z = z.to(torch.float32)
    w_proj_g = w_proj_g.to(torch.float32)
    w_proj_o = w_proj_o.to(torch.float32)
    if b_proj_g is not None:
        b_proj_g = b_proj_g.to(torch.float32)
    if b_proj_o is not None:
        b_proj_o = b_proj_o.to(torch.float32)

    bias = _attention_pair_bias_mask_torch(
        z,
        mask,
        w_proj_z,
        b_proj_z,
        w_ln_z,
        b_ln_z,
        num_heads,
        multiplicity,
        eps,
        inf,
        compute_pair_bias,
    )

    attn = torch.einsum("bhid,bhjd->bhij", q, k)
    if attn_scale is None:
        attn = attn / (D_Q**0.5)
    else:
        attn = attn * attn_scale
    attn = attn + bias
    attn = attn.softmax(dim=-1)
    out = torch.einsum("bhij,bhjd->bihd", attn, v).reshape(B, -1, H * D_Q)

    g = torch.nn.functional.linear(s, w_proj_g, bias=b_proj_g)
    g = torch.sigmoid(g)
    o = torch.nn.functional.linear(g * out, w_proj_o, bias=b_proj_o)
    o = o.to(z_dtype)
    return o, bias


class AttentionPairBiasMask(torch.autograd.Function):
    @staticmethod
    def forward(
        ctx,
        z: torch.Tensor,
        mask: torch.Tensor,
        w_proj_z: torch.Tensor,
        b_proj_z: torch.Tensor,
        w_ln: Optional[torch.Tensor],
        b_ln: Optional[torch.Tensor],
        num_heads: int,
        multiplicity: int,
        eps: float,
        inf: float,
        grad_enabled: bool,
        compute_pair_bias: bool,
    ):
        nvtx_range_push("AttentionPairBiasMask.forward")

        B, U, V, DIM_Z = z.shape

        has_bias = b_proj_z is not None
        elementwise_affine = w_ln is not None or b_ln is not None

        if multiplicity > 1 and B * multiplicity == mask.shape[0]:
            mask_with_multiplicity = True
        else:
            mask_with_multiplicity = False

        out_mask = torch.empty(
            (B * multiplicity, num_heads, U, V), dtype=z.dtype, device=z.device
        )

        if not compute_pair_bias:
            # TODO better perf-tuning
            TILE_V = 128
            NUM_HEADS_PER_BLK = 4
            num_warps = 8
            num_stages = 2

            grid = (
                triton.cdiv(V, TILE_V),
                U,
                triton.cdiv(num_heads, NUM_HEADS_PER_BLK) * B,
            )

            pair_bias_mask_forward_kernel[grid](
                z,
                mask,
                U,
                V,
                multiplicity,
                out_mask,
                TILE_V=TILE_V,
                NUM_HEADS=num_heads,
                NUM_HEADS_PER_BLK=NUM_HEADS_PER_BLK,
                INF=inf,
                MASK_WITH_MULTIPLICITY=mask_with_multiplicity,
                num_warps=num_warps,
                num_stages=num_stages,
            )

            z_norm, mean, rstd = None, None, None

        else:
            if DIM_Z in (16, 32, 64, 128):
                # TODO better perf-tuning
                TILE_V = 64
                NUM_HEADS_PER_BLK = 16
                HEAD_BLKS = triton.cdiv(num_heads, NUM_HEADS_PER_BLK)
                TILE_K = 32 if DIM_Z > 16 else 16
                num_warps = 4
                num_stages = 3

                grid = (triton.cdiv(V, TILE_V), U, HEAD_BLKS * B)

                if grad_enabled:
                    z_norm = torch.empty(
                        (B, U, V, DIM_Z), dtype=z.dtype, device=z.device
                    )
                    mean = torch.empty((B, U, V), dtype=torch.float32, device=z.device)
                    rstd = torch.empty((B, U, V), dtype=torch.float32, device=z.device)
                else:
                    z_norm, mean, rstd = None, None, None

                pair_bias_norm_linear_mask_forward_kernel[grid](
                    z,
                    mask,
                    w_proj_z,
                    b_proj_z,
                    w_ln,
                    b_ln,
                    U,
                    V,
                    multiplicity,
                    out_mask,
                    z_norm,
                    mean,
                    rstd,
                    TILE_V=TILE_V,
                    TILE_K=TILE_K,
                    NUM_HEADS=num_heads,
                    NUM_HEADS_PER_BLK=NUM_HEADS_PER_BLK,
                    DIM_Z=DIM_Z,
                    INF=inf,
                    EPS=eps,
                    ELEMENTWISE_AFFINE=elementwise_affine,
                    IS_TRAINING=grad_enabled,
                    HAS_BIAS=has_bias,
                    MASK_WITH_MULTIPLICITY=mask_with_multiplicity,
                    num_warps=num_warps,
                    num_stages=num_stages,
                )

            else:
                z_norm, mean, rstd = fused_layer_norm_forward_kernel_wrapper(
                    z.view(B, -1, DIM_Z),
                    w_ln,
                    b_ln,
                    eps=eps,
                    layout=Layout.BND_BND,
                    elementwise_affine=elementwise_affine,
                )

                z_norm = z_norm.view(B, U, V, DIM_Z)

                # TODO better perf-tuning
                TILE_V = 64
                NUM_HEADS_PER_BLK = 16
                HEAD_BLKS = triton.cdiv(num_heads, NUM_HEADS_PER_BLK)
                TILE_K = 32 if DIM_Z > 16 else 16
                num_warps = 4
                num_stages = 3

                grid = (triton.cdiv(V, TILE_V), U, HEAD_BLKS * B)
                assert DIM_Z % TILE_K == 0, (
                    f"DIM_Z {DIM_Z} must be divisible by TILE_K {TILE_K}"
                )
                pair_bias_linear_mask_forward_kernel[grid](
                    z_norm,
                    mask,
                    w_proj_z,
                    b_proj_z,
                    U,
                    V,
                    multiplicity,
                    out_mask,
                    TILE_V=TILE_V,
                    TILE_K=TILE_K,
                    NUM_HEADS=num_heads,
                    NUM_HEADS_PER_BLK=NUM_HEADS_PER_BLK,
                    DIM_Z=DIM_Z,
                    INF=inf,
                    HAS_BIAS=has_bias,
                    MASK_WITH_MULTIPLICITY=mask_with_multiplicity,
                    num_warps=num_warps,
                    num_stages=num_stages,
                )

                if not grad_enabled:
                    z_norm, mean, rstd = None, None, None

        ctx.save_for_backward(z, w_proj_z, b_proj_z, w_ln, b_ln, z_norm, mean, rstd)
        ctx.multiplicity = multiplicity
        ctx.compute_pair_bias = compute_pair_bias
        ctx.num_heads = num_heads
        nvtx_range_pop()
        return out_mask

    @staticmethod
    def backward(ctx, grad_out_mask: torch.Tensor):
        nvtx_range_push("AttentionPairBiasMask.backward")
        # gradient through "mask" is straightforward
        # hence, gradient on z_norm and w/b of proj are simply BMMs
        z, w_proj_z, b_proj_z, w_ln, b_ln, z_norm, mean, rstd = ctx.saved_tensors
        B, U, V, DIM_Z = z.shape

        if ctx.multiplicity > 1:
            # if multiplicity > 1, we need to sum over the multiplicity dimension
            grad_out_mask = grad_out_mask.view(
                -1, ctx.multiplicity, *grad_out_mask.shape[1:]
            )
            grad_out_mask = grad_out_mask.sum(dim=1)

        grad_out_mask = grad_out_mask.view(B, ctx.num_heads, -1)

        if not ctx.compute_pair_bias:
            # TODO more efficient transpose
            grad_z = (
                grad_out_mask.transpose(1, 2).contiguous().view(B, U, V, ctx.num_heads)
            )

            grad_w_proj_z = None
            grad_b_proj_z = None
            grad_w_ln = None
            grad_b_ln = None

        else:
            grad_w_proj_z = grad_out_mask @ z_norm.view(B, -1, DIM_Z)
            grad_w_proj_z = grad_w_proj_z.sum(dim=0)
            if b_proj_z is not None:
                grad_b_proj_z = grad_out_mask.sum(dim=-1).sum(dim=0)
            else:
                grad_b_proj_z = None

            # gradient through layernorm in unfused fashion
            grad_z_norm = grad_out_mask.transpose(1, 2) @ w_proj_z
            elementwise_affine = w_ln is not None or b_ln is not None

            mean = mean.view(B, -1)
            rstd = rstd.view(B, -1)

            grad_z, grad_w_ln, grad_b_ln = fused_layer_norm_backward_kernel_wrapper(
                grad_z_norm,
                z.view(B, -1, DIM_Z),
                w_ln,
                mean,
                rstd,
                elementwise_affine,
                Layout.BND_BND,
            )
            grad_z = grad_z.view(B, U, V, DIM_Z)

        nvtx_range_pop()

        return (
            grad_z,
            None,
            grad_w_proj_z,
            grad_b_proj_z,
            grad_w_ln,
            grad_b_ln,
            None,
            None,
            None,
            None,
            None,
            None,
        )


def attention_pair_bias_mask(
    z: torch.Tensor,
    mask: torch.Tensor,
    w_proj_z: torch.Tensor,
    b_proj_z: Optional[torch.Tensor],
    w_ln: Optional[torch.Tensor],
    b_ln: Optional[torch.Tensor],
    num_heads: int,
    multiplicity: int,
    eps: float = 1e-5,
    inf: float = 1e6,
    compute_pair_bias: bool = True,
):
    # Use original PyTorch implementation for short sequences in eager mode only
    if not torch._jit_internal.is_scripting() and not torch.compiler.is_compiling():
        seq_seq_len = z.shape[-2] * z.shape[-3]
        if seq_seq_len <= CUEQ_ATTENTION_PAIR_BIAS_FALLBACK_THRESHOLD**2:
            return _attention_pair_bias_mask_torch(
                z,
                mask,
                w_proj_z,
                b_proj_z,
                w_ln,
                b_ln,
                num_heads,
                multiplicity,
                eps,
                inf,
                compute_pair_bias,
            )

    grad_enabled = torch.is_grad_enabled()
    return AttentionPairBiasMask.apply(
        z,
        mask,
        w_proj_z,
        b_proj_z,
        w_ln,
        b_ln,
        num_heads,
        multiplicity,
        eps,
        inf,
        grad_enabled,
        compute_pair_bias,
    )


def attention_pair_bias(
    s: torch.Tensor,
    q: torch.Tensor,
    k: torch.Tensor,
    v: torch.Tensor,
    z: torch.Tensor,
    mask: torch.Tensor,
    num_heads: int,
    w_proj_z: torch.Tensor,
    w_proj_g: torch.Tensor,
    w_proj_o: torch.Tensor,
    w_ln_z: torch.Tensor,  # TODO: make this optional
    b_ln_z: torch.Tensor,  # TODO: make this optional
    b_proj_z: Optional[torch.Tensor] = None,
    b_proj_g: Optional[torch.Tensor] = None,
    b_proj_o: Optional[torch.Tensor] = None,
    inf: float = 1e6,
    eps: float = 1e-5,
    attn_scale: Optional[float] = None,
    compute_pair_bias: bool = True,
    multiplicity: Optional[int] = 1,
):
    # q: query sequence (B x M) x H x U x DH
    # k/v: key/value sequence (B x M) x H x V x DH
    # z: pairwise tensor B x U x V x DIM_Z
    # mask: B x V or (B x M) x V

    BM, H, S, DH = q.shape
    B = z.shape[0]
    assert BM % B == 0

    # Use original PyTorch implementation for short sequences in eager mode only
    if not torch._jit_internal.is_scripting() and not torch.compiler.is_compiling():
        seq_len = z.shape[-2]
        if seq_len <= CUEQ_ATTENTION_PAIR_BIAS_FALLBACK_THRESHOLD:
            return _attention_pair_bias_torch(
                s,
                q,
                k,
                v,
                z,
                mask,
                num_heads,
                w_proj_z,
                w_proj_g,
                w_proj_o,
                w_ln_z,
                b_ln_z,
                b_proj_z,
                b_proj_g,
                b_proj_o,
                inf,
                eps,
                attn_scale,
                compute_pair_bias,
                multiplicity,
            )

    bias = attention_pair_bias_mask(
        z,
        mask,
        w_proj_z,
        b_proj_z,
        w_ln_z,
        b_ln_z,
        num_heads=H,
        multiplicity=multiplicity,
        eps=eps,
        inf=inf,
        compute_pair_bias=compute_pair_bias,
    )
    if not torch.compiler.is_compiling():
        with torch.nn.attention.sdpa_kernel(
            backends=[
                torch.nn.attention.SDPBackend.CUDNN_ATTENTION,
                torch.nn.attention.SDPBackend.FLASH_ATTENTION,
                torch.nn.attention.SDPBackend.EFFICIENT_ATTENTION,
            ],
            set_priority=True,
        ):
            o = torch.nn.functional.scaled_dot_product_attention(
                q,
                k,
                v,
                attn_mask=bias,
                is_causal=False,
                scale=attn_scale,
            )

    else:
        with torch.nn.attention.sdpa_kernel(
            backends=[
                torch.nn.attention.SDPBackend.CUDNN_ATTENTION,
                torch.nn.attention.SDPBackend.FLASH_ATTENTION,
                torch.nn.attention.SDPBackend.EFFICIENT_ATTENTION,
            ],
        ):
            o = torch.nn.functional.scaled_dot_product_attention(
                q,
                k,
                v,
                attn_mask=bias,
                is_causal=False,
                scale=attn_scale,
            )

    # TODO more efficient transpose
    o = torch.einsum("bhid->bihd", o).contiguous().view(B * multiplicity, -1, H * DH)

    g = torch.nn.functional.linear(s, w_proj_g, bias=b_proj_g)
    g = torch.sigmoid(g)
    o = torch.nn.functional.linear(g * o, w_proj_o, bias=b_proj_o)

    return o, bias
