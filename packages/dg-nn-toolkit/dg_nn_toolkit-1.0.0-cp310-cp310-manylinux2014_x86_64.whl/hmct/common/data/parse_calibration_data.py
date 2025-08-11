import contextlib
import hashlib
import logging
from typing import Any, Dict, Iterator, Optional, Sequence, Union

import numpy as np


def md5sum(data, name):
    with contextlib.suppress(Exception):
        logging.info(f"{name} md5sum: {hashlib.md5(data).hexdigest()}")


def parse_calibration_data(
    cali_dict: Optional[Dict[str, Any]] = None,
) -> Union[Dict[str, Union[Sequence[np.ndarray], Iterator]], None]:
    cali_dict = {} if cali_dict is None else cali_dict
    if "calibration_data" in cali_dict:
        md5sum(cali_dict["calibration_data"], "Calibration data")
    elif "calibration_loader" in cali_dict:
        cali_dict["calibration_data"] = cali_dict.get("calibration_loader")
    return cali_dict.get("calibration_data")
