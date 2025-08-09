class QuantizationType:
    def __init__(self):
        # max, kl, percentile, minmax
        self.calibration_method = ""

        self.asymmetric = False

        self.perchannel = False

        self.int16 = False

        self.bias_correction = False

        self.default = False

        self.weight = False

    def type_str(self):
        type = f"{self.calibration_method}"

        if self.asymmetric:
            type = "{}_{}".format(type, "asy")

        if self.perchannel:
            type = "{}_{}".format(type, "perchannel")

        if self.int16:
            type = "{}_{}".format(type, "int16")

        if self.bias_correction:
            type = "{}_{}".format(type, "bias")

        if self.weight:
            type = "{}_{}".format(type, "weight")

        return type

    def set_method(self, calibration_method):
        if "percentile" in calibration_method:
            self.calibration_method = "percentile"
        elif "kl" in calibration_method:
            self.calibration_method = "kl"
        elif "max" in calibration_method:
            self.calibration_method = "max"
        elif "min-max" in calibration_method:
            self.calibration_method = "minmax"
        else:
            self.calibration_method = calibration_method
        if "per_channel" in calibration_method:
            self.perchannel = True
        else:
            self.perchannel = False
        if "asymmetric" in calibration_method:
            self.asymmetric = True
        else:
            self.asymmetric = False

    def update(self, other: "QuantizationType") -> None:
        if other.calibration_method:
            self.calibration_method = other.calibration_method
        if other.asymmetric:
            self.asymmetric = other.asymmetric
        if other.perchannel:
            self.perchannel = other.perchannel
        if other.int16:
            self.int16 = other.int16
        if other.bias_correction:
            self.bias_correction = other.bias_correction
        if other.weight:
            self.weight = other.weight
        if other.default:
            self.default = other.default

    @property
    def method(self):
        if self.default:
            return "default"
        return self.calibration_method
