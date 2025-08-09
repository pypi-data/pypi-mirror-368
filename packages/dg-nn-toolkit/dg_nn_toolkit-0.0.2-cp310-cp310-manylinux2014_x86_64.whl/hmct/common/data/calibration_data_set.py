import logging
import os
from typing import (
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
    overload,
)

import numpy as np

from horizon_nn.ir import DataType, onnx_dtype_to_numpy_dtype


class Dataset:
    """Dataset is used to parse and store data.

    Dataset can receive data in different format, details in descriptions
    of set_data_dict func.

    Dataset will store data in self._data_dict, and can be
    represented as {"input_name1": [data1_0, data1_1, data1_2...],
                    "input_name2": [data2_0, data2_1, data2_2...]}

    Data can be get via get_data func.
    """

    @overload
    def __init__(
        self,
        input_data: Mapping[str, Union[Iterable[np.ndarray], str]],
    ): ...

    @overload
    def __init__(
        self,
        *,
        input_shapes: Mapping[str, Sequence[int]],
        input_dtypes: Mapping[str, DataType],
    ): ...

    def __init__(
        self,
        input_data: Optional[Mapping[str, Union[Iterable[np.ndarray], str]]] = None,
        input_shapes: Optional[Mapping[str, Sequence[int]]] = None,
        input_dtypes: Optional[Mapping[str, DataType]] = None,
    ):
        """Create dataset from input args.

        Either input_data or input_shapes/input_dtypes should be given.
        If input_data is None, random data will be generated and used instead.

        Args:
            input_data (optional): the key is input name, and the value
                is iterable object or numpy data path.
            input_shapes (optional): model input shapes.
            input_dtypes (optional): model input dtypes.
        """
        self._data_dict = {}
        self._number_of_samples = 0

        if input_data is None:
            assert (
                input_shapes is not None and input_dtypes is not None
            ), "input_shapes/input_dtypes should be given when input_data is None."
            input_data = self._generate_random_data(
                input_shapes,
                input_dtypes,
            )

        self._set_data_dict(input_data)

    @property
    def number_of_samples(self) -> int:
        """返回当前Dataset的样本数量."""
        return self._number_of_samples

    def _set_data_dict(
        self, data_dict: Mapping[str, Union[Iterable[np.ndarray], str]]
    ) -> None:
        """Set data_dict from data_dict.

        Args:
            data_dict: A dict, the key is input_name, the value should be
            iterable object of ndarray or directory containing ndarray.
        """
        # Parse the data_dict.
        if isinstance(data_dict, Mapping):
            for name, data in data_dict.items():
                if isinstance(data, str):
                    self._load_data_from_path(name, data)
                elif isinstance(data, Iterable):
                    self._load_data_from_iterable(name, data)
                else:
                    raise TypeError(
                        f"Type of data should be str or iterable object,"
                        f"but got {type(data)}"
                    )
        else:
            raise TypeError(
                f"type(data_dict) should be Mapping, but got {type(data_dict)}"
            )

        # calculate and check number of sample from the input_data received.
        for name, data in self._data_dict.items():
            number_of_samples = len(data)
            logging.debug(
                f"input name: {name},  number_of_samples: {number_of_samples}"
            )
            if not self._number_of_samples:
                self._number_of_samples = number_of_samples
            else:
                if self._number_of_samples != number_of_samples:
                    raise ValueError(
                        f"Input {name} received wrong num of data\n"
                        f"Previous num of sample: {self._number_of_samples}, "
                        f"Input {name}'s num of sample: {number_of_samples}"
                    )
        logging.info(f"There are {self._number_of_samples} samples in the data set.")

    def _load_data_from_iterable(self, name: str, data: Iterable[np.ndarray]) -> None:
        """Load data from iterable object.

        Args:
            name: The input name
            data: Iterable object to load data
        """
        data = list(data)
        if type(data[0]) is not np.ndarray:
            raise TypeError(
                f"Wrong type of data received in "
                f"iterable format. Type of data in "
                f"the iterator: {type(data[0])}"
            )
        self._data_dict[name] = data

    def _load_data_from_path(self, name: str, path: str) -> None:
        """Load data from directory.

        Args:
            name: The input name
            path: The directory containing ndarray files
        """
        if os.path.isdir(path):
            self._data_dict[name] = [
                np.load(os.path.join(path, f)) for f in sorted(os.listdir(path))
            ]
        else:
            raise ValueError(f"{path} is not a directory.")

    def get_data(
        self,
        input_names: Optional[Sequence[str]] = None,
        start: int = 0,
        end: int = 1,
    ) -> Dict[str, np.ndarray]:
        """This function will return a dict of data.

        If input_nodes is given, only return data for these nodes.

        start and end will slice self._data_dict and return the
        required piece of data from self._data_dict.
        """
        end = min(end, self._number_of_samples)
        start = min(start, end)

        inputs = {}
        if input_names is None:
            for name in self._data_dict:
                inputs[name] = np.concatenate(self._data_dict[name][start:end], axis=0)
        else:
            for name in input_names:
                if name in self._data_dict:
                    inputs[name] = np.concatenate(
                        self._data_dict[name][start:end], axis=0
                    )
                else:
                    raise ValueError(f"There exists no input {name} in the dataset.")
        return inputs

    def _generate_random_data(
        self,
        input_shapes: Mapping[str, Sequence[int]],
        input_dtypes: Mapping[str, DataType],
    ) -> Dict[str, List[np.ndarray]]:
        """Generate random data with specified shape and dtype."""
        data_dict = {}
        assert len(input_shapes) == len(input_dtypes)

        for input_name, input_shape in input_shapes.items():
            array_type = onnx_dtype_to_numpy_dtype(input_dtypes[input_name])
            data_dict[input_name] = [np.random.random(input_shape).astype(array_type)]
        return data_dict

    def save(self, path: str) -> None:
        """Save the dataset to the given path."""
        for input_name, data_list in self._data_dict.items():
            save_path = f"{path}/{input_name}"
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            for idx, data in enumerate(data_list):
                np.save(f"{save_path}/{idx}.npy", data)

    def copy(self, number_of_samples: int) -> "Dataset":
        """Return a subset of the current dataset with specified number_of_samples."""
        number_of_samples = min(self._number_of_samples, number_of_samples)
        return Dataset(
            input_data={
                name: data[-number_of_samples:]
                for name, data in self._data_dict.items()
            }
        )
