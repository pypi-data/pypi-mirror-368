# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from typing import Optional

import torch
from torch.onnx import symbolic_helper


@symbolic_helper.parse_args("v", "v", "b")
def symbolic_segmented_transpose(g, tensor, segment_info, contiguous):
    out_shape = symbolic_helper._get_tensor_sizes(tensor)
    output_type = tensor.type().with_sizes(out_shape)
    out = g.op(
        "cuequivariance_ops::segmented_transpose",
        tensor,
        segment_info,
        contiguous_i=contiguous,
    )
    out.setType(output_type)
    return out


torch.onnx.register_custom_op_symbolic(
    "cuequivariance_ops::segmented_transpose",
    symbolic_segmented_transpose,
    1,
)


def is_none_value(value):
    if value is None:
        return True
    return (
        isinstance(value, torch._C.Value)
        and value.node().kind() == "prim::Constant"
        and isinstance(value.type(), torch._C.NoneType)
    )


def symbolic_fused_tensor_product_fwd(
    g,
    in0: torch.Tensor,
    in1: torch.Tensor,
    in2: Optional[torch.Tensor],
    tp_path_csr_offsets_fwd: torch.Tensor,
    tp_path_csr_offsets_dgrad_in0: torch.Tensor,
    tp_path_csr_offsets_dgrad_in1: torch.Tensor,
    tp_path_csr_offsets_dgrad_in2: torch.Tensor,
    tp_path_offsets_fwd: torch.Tensor,
    tp_path_offsets_dgrad_in0: torch.Tensor,
    tp_path_offsets_dgrad_in1: torch.Tensor,
    tp_path_offsets_dgrad_in2: torch.Tensor,
    tp_path_cg_values_fwd: torch.Tensor,
    tp_path_cg_values_dgrad_in0: torch.Tensor,
    tp_path_cg_values_dgrad_in1: torch.Tensor,
    tp_path_cg_values_dgrad_in2: torch.Tensor,
    connection_mode: int,
    output_stride: int,
):
    # print(f"connection_mode={connection_mode}, in2.type()={in2.type()}")
    out_shape = symbolic_helper._get_tensor_sizes(in0)
    sz = symbolic_helper._parse_arg(output_stride, "i")
    mode = symbolic_helper._parse_arg(connection_mode, "i")
    output_type = in0.type().with_sizes(out_shape[:1] + [sz])

    output = g.op(
        "cuequivariance_ops::fused_tensor_product",
        in0,
        in1,
        in0 if is_none_value(in2) else in2,
        tp_path_csr_offsets_fwd,
        tp_path_csr_offsets_dgrad_in0,
        tp_path_csr_offsets_dgrad_in1,
        tp_path_csr_offsets_dgrad_in2,
        tp_path_offsets_fwd,
        tp_path_offsets_dgrad_in0,
        tp_path_offsets_dgrad_in1,
        tp_path_offsets_dgrad_in2,
        tp_path_cg_values_fwd,
        tp_path_cg_values_dgrad_in0,
        tp_path_cg_values_dgrad_in1,
        tp_path_cg_values_dgrad_in2,
        connection_mode_i=mode,
        output_stride_i=sz,
    )
    output.setType(output_type)
    return output


torch.onnx.register_custom_op_symbolic(
    "cuequivariance_ops::fused_tensor_product_fwd",
    symbolic_fused_tensor_product_fwd,
    1,
)


def symbolic_tensor_product_uniform_1d_jit(
    g, in0, in1, in2, noos, nop, data, math_data
):
    in0_shape = symbolic_helper._get_tensor_sizes(in0)
    in1_shape = symbolic_helper._get_tensor_sizes(in1)
    in2_shape = symbolic_helper._get_tensor_sizes(in2)
    number_of_output_segments = symbolic_helper._parse_arg(noos, "i")
    number_of_paths = symbolic_helper._parse_arg(nop, "i")
    math_code = symbolic_helper._parse_arg(math_data, "i")

    out_shape = (
        max(in0_shape[0], in1_shape[0], in2_shape[0]),
        number_of_output_segments,
        max(
            in0_shape[2],
            in1_shape[2],
            in2_shape[2] if len(in2_shape) >= 3 else in1_shape[2],
        ),
    )

    output_type = in0.type().with_sizes(out_shape)

    output = g.op(
        "cuequivariance_ops::tensor_product_uniform_1d",
        in0,
        in1,
        in2,
        data,
        number_of_output_segments_i=number_of_output_segments,
        number_of_paths_i=number_of_paths,
        math_code_i=math_code,
    )
    output.setType(output_type)
    return output


torch.onnx.register_custom_op_symbolic(
    "cuequivariance_ops::tensor_product_uniform_1d_jit",
    symbolic_tensor_product_uniform_1d_jit,
    1,
)


try:
    import onnxscript

    # from onnxscript import BOOL, FLOAT
    from onnxscript import opset18 as op

    _onnx_opset = onnxscript.values.Opset("cuequivariance_ops", version=1)
    """
    @onnxscript.script(_onnx_opset)
    def onnxscript_triangular_attention(q:FLOAT, k:FLOAT, v:FLOAT, b:FLOAT, mask:BOOL) -> Tuple[FLOAT, FLOAT, FLOAT]:
        o, sm_lse, sm_max = _onnx_opset.triangular_attention(
            q, k, v, b, mask, # plugin_namespace="cuequivariance_ops"
        )
        return o, sm_lse, sm_max
    """

    @onnxscript.script(_onnx_opset, default_opset=op)
    def onnxscript_segmented_transpose(
        tensor,
        segment_info,
        input_contiguous_as_info: bool,
    ):
        return _onnx_opset.segmented_transpose(
            tensor,
            segment_info,
            contiguous=input_contiguous_as_info,
        )

    @onnxscript.script(_onnx_opset, default_opset=op)
    def onnxscript_fused_tensor_product_fwd(
        in0,
        in1,
        in2,
        tp_path_csr_offsets_fwd,
        tp_path_csr_offsets_dgrad_in0,
        tp_path_csr_offsets_dgrad_in1,
        tp_path_csr_offsets_dgrad_in2,
        tp_path_offsets_fwd,
        tp_path_offsets_dgrad_in0,
        tp_path_offsets_dgrad_in1,
        tp_path_offsets_dgrad_in2,
        tp_path_cg_values_fwd,
        tp_path_cg_values_dgrad_in0,
        tp_path_cg_values_dgrad_in1,
        tp_path_cg_values_dgrad_in2,
        connection_mode: int,
        output_stride: int,
    ):
        return _onnx_opset.fused_tensor_product(
            in0,
            in1,
            in2,
            tp_path_csr_offsets_fwd,
            tp_path_csr_offsets_dgrad_in0,
            tp_path_csr_offsets_dgrad_in1,
            tp_path_csr_offsets_dgrad_in2,
            tp_path_offsets_fwd,
            tp_path_offsets_dgrad_in0,
            tp_path_offsets_dgrad_in1,
            tp_path_offsets_dgrad_in2,
            tp_path_cg_values_fwd,
            tp_path_cg_values_dgrad_in0,
            tp_path_cg_values_dgrad_in1,
            tp_path_cg_values_dgrad_in2,
            connection_mode=connection_mode,
            output_stride=output_stride,
        )

    @onnxscript.script(_onnx_opset, default_opset=op)
    def onnxscript_tensor_product_uniform_1d_jit(
        in0,
        in1,
        in2,
        number_of_output_segments: int,
        number_of_paths: int,
        data,
        math_code: int,
    ):
        return _onnx_opset.tensor_product_uniform_4x1d(
            in0,
            in1,
            in2,
            data,
            number_of_output_segments=number_of_output_segments,
            number_of_paths=number_of_paths,
            math_code=math_code,
        )

    op_table = {
        # torch.ops.cuequivariance_ops.trianglular_attention.default: onnxscript_triangular_attention,
        torch.ops.cuequivariance_ops.segmented_transpose: onnxscript_segmented_transpose,
        torch.ops.cuequivariance_ops.fused_tensor_product_fwd: onnxscript_fused_tensor_product_fwd,
        torch.ops.cuequivariance_ops.tensor_product_uniform_1d_jit: onnxscript_tensor_product_uniform_1d_jit,
    }

    cuequivariance_ops_torch_onnx_registry = torch.onnx.OnnxRegistry()

    cuequivariance_ops_torch_onnx_registry.register_op(
        namespace="cuequivariance_ops",
        op_name="segmented_transpose",
        overload="default",
        function=onnxscript_segmented_transpose,
    )

    cuequivariance_ops_torch_onnx_registry.register_op(
        namespace="cuequivariance_ops",
        op_name="fused_tensor_product_fwd",
        overload="default",
        function=onnxscript_fused_tensor_product_fwd,
    )

    cuequivariance_ops_torch_onnx_registry.register_op(
        namespace="cuequivariance_ops",
        op_name="tensor_product_uniform_1d_jit",
        overload="default",
        function=onnxscript_tensor_product_uniform_1d_jit,
    )


except ImportError:
    cuequivariance_ops_torch_onnx_registry = None

"""
# This section defines run-time plugins, used when running exported ONNX graph with ONNXruntime
"""

try:
    from onnxruntime import SessionOptions
    from onnxruntime_extensions import PyCustomOpDef, get_library_path, onnx_op

    def ort_fused_tensor_product(*args, **kwargs):
        connection_mode = kwargs["connection_mode"]
        output_stride = kwargs["output_stride"]
        cargs = [torch.from_numpy(i).cuda() for i in args]
        return torch.ops.cuequivariance_ops.fused_tensor_product_fwd(
            *cargs, connection_mode, output_stride
        )

    @onnx_op(
        op_type="cuequivariance_ops::fused_tensor_product",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
        ],
        attrs={
            "connection_mode": PyCustomOpDef.dt_int64,
            "output_stride": PyCustomOpDef.dt_int64,
        },
    )
    def ort_fused_tensor_product_fp32(*args, **kwargs):
        return ort_fused_tensor_product(*args, **kwargs)

    @onnx_op(
        op_type="cuequivariance_ops::fused_tensor_product",
        inputs=[
            PyCustomOpDef.dt_float16,
            PyCustomOpDef.dt_float16,
            PyCustomOpDef.dt_float16,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
            PyCustomOpDef.dt_int32,
        ],
        attrs={
            "connection_mode": PyCustomOpDef.dt_int64,
            "output_stride": PyCustomOpDef.dt_int64,
        },
    )
    def ort_fused_tensor_product_fp16(*args, **kwargs):
        return ort_fused_tensor_product(*args, **kwargs)

    def ort_segmented_transpose(in1, in2, **kwargs):
        contiguous = kwargs["contiguous"]
        return torch.ops.cuequivariance_ops.segmented_transpose(
            torch.from_numpy(in1).cuda(), torch.from_numpy(in2).cuda(), contiguous
        )

    @onnx_op(
        op_type="cuequivariance_ops::segmented_transpose",
        inputs=[PyCustomOpDef.dt_float, PyCustomOpDef.dt_int32],
        attrs={
            "contiguous": PyCustomOpDef.dt_int64,
        },
    )
    def ort_segmented_transpose_fp32(in1, in2, **kwargs):
        return ort_segmented_transpose(in1, in2, **kwargs)

    @onnx_op(
        op_type="cuequivariance_ops::segmented_transpose",
        inputs=[PyCustomOpDef.dt_float16, PyCustomOpDef.dt_int32],
        outputs=[PyCustomOpDef.dt_float16],
        attrs={
            "contiguous": PyCustomOpDef.dt_int64,
        },
    )
    def ort_segmented_transpose_fp16(in1, in2, **kwargs):
        return ort_segmented_transpose(in1, in2, **kwargs)

    @onnx_op(
        op_type="cuequivariance_ops::tensor_product_uniform_1d_jit",
        inputs=[
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_float,
            PyCustomOpDef.dt_int32,
        ],
        attrs={
            "number_of_output_segments": PyCustomOpDef.dt_int64,
            "number_of_paths": PyCustomOpDef.dt_int64,
            "math_code": PyCustomOpDef.dt_int64,
        },
    )
    def ort_tensor_product_uniform_1d(*args, **kwargs):
        number_of_output_segments = kwargs["number_of_output_segments"]
        number_of_paths = kwargs["number_of_paths"]
        math_code = kwargs["math_code"]
        cargs = [torch.from_numpy(i).cuda() for i in args]
        return torch.ops.cuequivariance_ops.tensor_product_uniform_1d_jit(
            cargs[0],
            cargs[1],
            cargs[2],
            number_of_output_segments,
            number_of_paths,
            cargs[3],
            math_code,
        )

    # This function register ORT implementations on runtime side
    def register_custom_ops_library():
        ops = SessionOptions()
        ops.register_custom_ops_library(get_library_path())
        return ops

except ImportError:
    pass

__all__ = ["cuequivariance_ops_torch_onnx_registry"]
