import torch
from torch.onnx import register_custom_op_symbolic
import torch.onnx.symbolic_helper as sym_help
from torch.onnx.symbolic_helper import parse_args
import torch.onnx.symbolic_opset9 as sym_opset9


@parse_args("v", "v")
def maximum(g, self, other):
    # torch.maximum(input, other)
    return g.op("Max", self, other)


@parse_args("v", "v")
def minimum(g, self, other):
    # torch.minimum(input, other)
    return g.op("Min", self, other)


# scale_quanti
@parse_args("v", "v", "v", "i", "i", "i", "b", "b", "b", "s", "s")
def symbolic_quantize(
    g,
    data,
    scale,
    zero_point,
    vector_dim,
    quant_min,
    quant_max,
    saturate,
    in_place,
    compat_mask=True,
    approximate_mode="bpu_round",
    march="bayes",
):
    num_bits = 8 if quant_max == 127 else 16
    # set zero_point to 0 and make onnx graph concise.
    # "constant" will be folded and its onnx graph is more concise than "cast"
    if vector_dim == -1:
        zero_point = g.op(
            "Constant",
            value_t=torch.zeros(1, dtype=torch.int8),
        )
    else:
        zero_point = g.op(
            "Constant",
            value_t=torch.zeros(zero_point.type().sizes(), dtype=torch.int8),
        )

    return g.op(
        "horizon::HzDequantize",
        g.op("horizon::HzQuantize", data, scale, zero_point, bits_i=num_bits),
        scale,
        zero_point,
    )


@parse_args("v", "v", "v", "i", "i", "i")
def fake_quantize_per_channel_affine(
    g,
    inputs,
    scale,
    zero_point,
    axis,
    quant_min=-128,
    quant_max=127,
):
    if (quant_min, quant_max) != (-128, 127) and (quant_min, quant_max) != (
        -32768,
        32767,
    ):
        raise RuntimeError(
            f"Horizon defines [-128, 127] for qint8 and [-32768, 32767] "
            f"for qint16, but got [{quant_min}, {quant_max}]",
        )

    # Horizon defines zero_point to be int8 or int16
    if quant_min == -128:
        num_bits = 8
        zero_point = g.op(
            "Cast",
            zero_point,
            to_i=sym_help.cast_pytorch_to_onnx["Char"],
        )
    else:
        num_bits = 16
        zero_point = g.op(
            "Cast",
            zero_point,
            to_i=sym_help.cast_pytorch_to_onnx["Short"],
        )

    return g.op(
        "horizon::HzDequantize",
        g.op(
            "horizon::HzQuantize",
            inputs,
            scale,
            zero_point,
            bits_i=num_bits,
            axis_i=axis,
        ),
        scale,
        zero_point,
        axis_i=axis,
    )


@parse_args("v", "t", "i", "i", "i")
def fake_quantize_per_tensor_affine(
    g,
    inputs,
    scale,
    zero_point,
    quant_min=-128,
    quant_max=127,
):
    if (quant_min, quant_max) != (-128, 127) and (quant_min, quant_max) != (
        -32768,
        32767,
    ):
        raise RuntimeError(
            f"Horizon defines [-128, 127] for qint8 and [-32768, 32767] "
            f"for qint16, but got [{quant_min}, {quant_max}]",
        )
    scale = scale.float().data  # Avoid exporter generating double type
    zero_point_dtype = torch.int8 if quant_min == -128 else torch.int16
    num_bits = 8 if quant_min == -128 else 16
    zero_point = torch.tensor(
        zero_point,
        dtype=zero_point_dtype,
    )  # ONNX requires zero_point to be tensor
    return g.op(
        "horizon::HzDequantize",
        g.op("horizon::HzQuantize", inputs, scale, zero_point, bits_i=num_bits),
        scale,
        zero_point,
    )


@parse_args("v", "v", "i", "i", "i")
def grid_sampler(g, input, grid, interpolation_mode, padding_mode, align_corners=False):
    interpolation_mode_list = ["bilinear", "nearest", "bicubic"]
    padding_mode_list = ["zeros", "border", "reflection"]
    return g.op(
        "horizon::GridSample",
        input,
        grid,
        mode_s=interpolation_mode_list[interpolation_mode],
        padding_mode_s=padding_mode_list[padding_mode],
        align_corners_i=align_corners,
    )


@parse_args("v", "v")
def bitwise_and(g, self, other):
    return g.op("horizon::BitwiseAnd", self, other)


@parse_args("v", "v")
def bitwise_or(g, self, other):
    return g.op("horizon::BitwiseOr", self, other)


@parse_args("v", "v")
def bitwise_xor(g, self, other):
    return g.op("horizon::BitwiseXor", self, other)


@parse_args("v", "v")
def tile(g, self, repeats):
    if not sym_help._is_value(repeats):  # noqa: SLF001
        repeats = g.op("Constant", value_t=torch.LongTensor(repeats))
    if sym_help._is_packed_list(repeats):  # noqa: SLF001
        repeat_size_len = len(sym_help._unpack_list(repeats))  # noqa: SLF001
    else:
        const_repeats = sym_help._maybe_get_const(repeats, "is")  # noqa: SLF001
        repeat_size_len = len(const_repeats)
    if self.isCompleteTensor():
        sizes = self.type().sizes()
        diff_dims = repeat_size_len - len(sizes)
        if diff_dims > 0:
            self = sym_opset9.view(
                g,
                self,
                g.op("Constant", value_t=torch.tensor([1] * diff_dims + sizes)),
            )
        if diff_dims < 0:
            const_repeats = sym_help._maybe_get_const(repeats, "is")  # noqa: SLF001
            repeats = g.op(
                "Constant",
                value_t=torch.tensor(
                    [1] * (-diff_dims) + const_repeats,
                    dtype=sym_help.scalar_type_to_pytorch_type[4],
                ),
            )
    return g.op("Tile", self, repeats)


@parse_args("v")
def relu6_10(g, self):
    return g.op("Clip", self, min_f=0, max_f=6)


@parse_args("v")
def acosh(g, self):
    return g.op("Acosh", self)


@parse_args("v")
def asinh(g, self):
    return g.op("Asinh", self)


@parse_args("v")
def atanh(g, self):
    return g.op("Atanh", self)


@parse_args("v")
def cosh(g, self):
    return g.op("Cosh", self)


@parse_args("v")
def sinh(g, self):
    return g.op("Sinh", self)


@parse_args("v")
def relu6(g, self):
    dtype = self.type().scalarType()
    if dtype is None:
        dtype = 6  # float
    else:
        dtype = sym_help.scalar_type_to_onnx.index(sym_help.cast_pytorch_to_onnx[dtype])
    dtype = sym_help.scalar_type_to_pytorch_type[dtype]
    return g.op(
        "Clip",
        self,
        torch.tensor(0, dtype=dtype),
        torch.tensor(6, dtype=dtype),
    )


@parse_args("v", "i")
def channelshuffle(g, self, other):
    return g.op("horizon::HzChannelShuffle", self, group_i=other, data_format_s="NCHW")


@parse_args("v", "i")
def pixelunshuffle(g, self, other):
    in_channel = sym_help._get_tensor_dim_size(self, 1)  # noqa: SLF001
    self = g.op("SpaceToDepth", self, blocksize_i=other)
    indices = []
    for i in range(in_channel):
        for j in range(other * other):
            indices.append(i + j * in_channel)
    return g.op(
        "Gather",
        self,
        g.op("Constant", value_t=torch.LongTensor(indices)),
        axis_i=1,
    )


# Export pytorch operator to onnx opset9 operator.
register_custom_op_symbolic("::tile", tile, 9)
# Export pytorch operator to onnx opset10 operator.
register_custom_op_symbolic("::maximum", maximum, 10)
register_custom_op_symbolic("::minimum", minimum, 10)
register_custom_op_symbolic("horizon::scale_quanti", symbolic_quantize, 10)
register_custom_op_symbolic("::grid_sampler", grid_sampler, 10)
register_custom_op_symbolic(
    "::fake_quantize_per_channel_affine",
    fake_quantize_per_channel_affine,
    10,
)
register_custom_op_symbolic(
    "::fake_quantize_per_tensor_affine",
    fake_quantize_per_tensor_affine,
    10,
)
register_custom_op_symbolic("::bitwise_and", bitwise_and, 10)
register_custom_op_symbolic("::bitwise_or", bitwise_or, 10)
register_custom_op_symbolic("::bitwise_xor", bitwise_xor, 10)
register_custom_op_symbolic("::relu6", relu6_10, 10)
register_custom_op_symbolic("::channel_shuffle", channelshuffle, 10)
register_custom_op_symbolic("::pixel_unshuffle", pixelunshuffle, 10)
register_custom_op_symbolic("::acosh", acosh, 10)
register_custom_op_symbolic("::asinh", asinh, 10)
register_custom_op_symbolic("::atanh", atanh, 10)
register_custom_op_symbolic("::cosh", cosh, 10)
register_custom_op_symbolic("::sinh", sinh, 10)
# Export pytorch operator to onnx opset11 operator.
register_custom_op_symbolic("::relu6", relu6, 11)
# Export pytorch operator to onnx opset13 operator.
register_custom_op_symbolic("::tile", tile, 13)
