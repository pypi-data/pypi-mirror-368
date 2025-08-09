from typing import Dict, List, Union

import numpy as np


class Loss:
    def run(
        self,
        data1: Union[Dict[str, List[np.ndarray]], np.ndarray],
        data2: Union[Dict[str, List[np.ndarray]], np.ndarray],
    ) -> float:
        if isinstance(data1, dict) and isinstance(data2, dict):
            return self._run_dict(data1, data2)
        if isinstance(data1, np.ndarray) and isinstance(data2, np.ndarray):
            return self._run_array(data1, data2)

        raise TypeError(
            f"type(data1) and type(data2) should be Dict"
            f"[str, List[np.ndarray]] or np.ndarray, "
            f"but got {type(data1)} and {type(data2)}",
        )

    def _run_dict(
        self,
        data1: Dict[str, List[np.ndarray]],
        data2: Dict[str, List[np.ndarray]],
    ) -> float:
        loss_values = []
        for name in set(data1.keys()) & set(data2.keys()):
            sample_loss_values = []
            # 处理标量输出
            if np.ndim(data1[name]) == 0 and np.ndim(data2[name]) == 0:
                return self._run_array(data1[name], data2[name])
            if np.ndim(data1[name]) == 0 or np.ndim(data2[name]) == 0:
                return 0.0
            for out1, out2 in zip(data1[name], data2[name]):
                if out1.shape == out2.shape:
                    sample_loss_values.append(self._run_array(out1, out2))
                else:
                    sample_loss_values.append(0.0)
            loss_values.append(np.array(sample_loss_values).mean())
        return np.mean(loss_values) if loss_values else 0.0

    def _run_array(self, data1: np.ndarray, data2: np.ndarray) -> float:
        data1 = data1.flatten()
        data2 = data2.flatten()
        return self.loss(data1, data2)

    def optimal(self, similarities: List[float]) -> int:
        return self.optimal_function()(similarities)

    @staticmethod
    def create(name):
        if name == "mse":
            return MSE()
        if name == "mre":
            return MRE()
        if name == "cosine-similarity":
            return CosineSimilarity()
        if name == "sqnr":
            return SQNR()
        if name == "chebyshev":
            return Chebyshev()

        raise ValueError(f"Unsupported loss type{name}.")


class MSE(Loss):
    def __init__(self):
        self.name = "mse"

    def loss(self, data1: np.ndarray, data2: np.ndarray) -> float:
        return np.mean(np.square(data1 - data2))

    def optimal_function(self):
        return np.argmin


class MRE(Loss):
    def __init__(self):
        self.name = "mre"

    def loss(self, data1: np.ndarray, data2: np.ndarray) -> float:
        return np.mean(np.abs(data1 - data2))

    def optimal_function(self):
        return np.argmin


class CosineSimilarity(Loss):
    def __init__(self):
        self.name = "cosine-similarity"

    def loss(self, data1: np.ndarray, data2: np.ndarray) -> float:
        data1_norm = max(np.linalg.norm(data1), 1e-8)
        data2_norm = max(np.linalg.norm(data2), 1e-8)
        return np.dot(data1, data2) / (data1_norm * data2_norm)

    def optimal_function(self):
        return np.argmax


class SQNR(Loss):
    def __init__(self):
        self.name = "sqnr"

    def loss(self, data1: np.ndarray, data2: np.ndarray) -> float:
        signal = np.linalg.norm(data1)
        noise = np.linalg.norm(data1 - data2)
        sqnr = np.sqrt(signal) / np.sqrt(noise)
        return 20.0 * np.log10(sqnr)

    def optimal_function(self):
        return np.argmax


class Chebyshev(Loss):
    def __init__(self):
        self.name = "chebyshev"

    def loss(self, data1: np.ndarray, data2: np.ndarray) -> float:
        return np.max(np.abs(data1 - data2))

    def optimal_function(self):
        return np.argmin
