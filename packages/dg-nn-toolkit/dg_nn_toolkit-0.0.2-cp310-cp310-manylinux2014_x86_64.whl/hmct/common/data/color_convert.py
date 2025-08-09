from enum import Enum


class ColorConvert(Enum):
    NULL = 0
    # same input type, input range changes from 0~255 to -128~127.
    RGB_TO_RGB_128 = 1
    BGR_TO_BGR_128 = 2
    YUV444_TO_YUV444_128 = 3
    GRAY_TO_GRAY_128 = 4
    # different input type, same input range.
    RGB_TO_BGR = 5
    BGR_TO_RGB = 6
    RGB_TO_YUV444 = 7
    BGR_TO_YUV444 = 8
    # different input type, input range changes from 0~255 to -128~127.
    RGB_TO_BGR_128 = 9
    BGR_TO_RGB_128 = 10
    RGB_TO_YUV444_128 = 11
    BGR_TO_YUV444_128 = 12
    RGB_TO_YUV_BT601_FULL_RANGE = 13
    RGB_TO_YUV_BT601_VIDEO_RANGE = 14
    BGR_TO_YUV_BT601_FULL_RANGE = 15
    BGR_TO_YUV_BT601_VIDEO_RANGE = 16

    @staticmethod
    def get_convert_type(original_type: str, expected_type: str) -> "ColorConvert":
        """Obtain the color convert type.

        Args:
            original_type: The original input color type of the model.
            expected_type: The expected input color type after building the model.
        """
        original_type = original_type.upper()
        expected_type = expected_type.upper()
        if original_type == expected_type:
            return ColorConvert.NULL

        convert_type = "_TO_".join([original_type, expected_type])
        if not hasattr(ColorConvert, convert_type):
            raise ValueError(
                f"The conversion of the original type {original_type} to "
                f"the expected type {expected_type} is not supported.",
            )

        return getattr(ColorConvert, convert_type)

    @staticmethod
    def split_color_convert(color_convert):
        """Split ColorConvert into float input type and fixed input type.

        Args:
            color_convert: ColorConvert object to split.

        Returns:
            A tuple which includes float input type and fixed input type.
        """
        if color_convert not in ColorConvert.__members__.values():
            raise ValueError(f"Unsupported color convert type: {color_convert}")
        if color_convert != ColorConvert.NULL:
            return color_convert.name.split("_TO_")

        return ["RGB", "RGB"]
