from typing import Any

from ..config import Config
from ..misc import debug

try:
    import numpy as np
except ImportError:
    np = None
    debug("Numpy not found, Numpy Default Classes will not work")

if np:
    import json

    from numpy import matrix, ndarray

    def nd_array_to_data(nd_array: ndarray[Any, Any]) -> list[Any]:
        return nd_array.tolist()

    def nd_array_from_data(data: list[Any]) -> ndarray[Any, Any]:
        return np.array(data)

    def matrix_to_data(matrix_: matrix[Any, Any]) -> list:
        return json.loads((str(matrix_).replace(" ", ",")))

    def load() -> None:
        Config.add_class(
            name="NDArray",
            class_=ndarray,
            to_data=nd_array_to_data,
            from_data=nd_array_from_data,
        )
        Config.add_class(name="Matrix", class_=matrix, to_data=matrix_to_data)
