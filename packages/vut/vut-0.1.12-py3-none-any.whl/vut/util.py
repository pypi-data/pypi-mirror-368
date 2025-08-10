import os
import random
from pathlib import Path

import numpy as np
import torch
from dotenv import load_dotenv
from numpy.typing import NDArray
from torch import Tensor

type Segment = tuple[int, tuple[int, int]]


def init_seed(seed: int = 42) -> None:
    """Initialize the random seed for reproducibility.

    Args:
        seed (int, optional): Seed value for random number generation. Defaults to 42.
    """
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
        torch.cuda.manual_seed(seed)


def unique(lst: list | NDArray | Tensor) -> list | NDArray | Tensor:
    """Return unique elements from the input list, NDArray, or Tensor while preserving order.

    Args:
        lst (list | NDArray | Tensor): Input list, NDArray, or Tensor to find unique elements from. Dimension size must be 1.

    Returns:
        list | NDArray | Tensor: Unique elements.
    """
    if isinstance(lst, list):
        return list(dict.fromkeys(lst))

    if isinstance(lst, np.ndarray):
        assert lst.ndim == 1, "Only 1D arrays are supported"
        _, indices = np.unique(lst, return_index=True)
        return lst[np.sort(indices)]

    if isinstance(lst, torch.Tensor):
        assert lst.ndim == 1, "Only 1D tensors are supported"
        # TODO: implement a more efficient way to get unique elements using torch
        return torch.tensor(
            list(dict.fromkeys(lst.cpu().tolist())),
            dtype=lst.dtype,
            device=lst.device,
        )

    raise TypeError(
        f"Unsupported type: {type(lst)}. Supported types are list, NDArray, and Tensor."
    )


def to_list(x: list | NDArray | Tensor) -> list:
    """Convert input to list.

    Args:
        x (list | NDArray | Tensor): Input to convert.

    Returns:
        list: Converted list.
    """
    if isinstance(x, list):
        return x

    if isinstance(x, np.ndarray):
        return x.tolist()

    if isinstance(x, torch.Tensor):
        return x.cpu().tolist()

    raise TypeError(
        f"Unsupported type: {type(x)}. Supported types are list, NDArray, and Tensor."
    )


def to_np(x: list | NDArray | Tensor) -> NDArray:
    """Convert input to numpy array.

    Args:
        x (list | NDArray | Tensor): Input to convert.

    Returns:
        NDArray: Converted numpy array.
    """
    if isinstance(x, list):
        return np.array(x)

    if isinstance(x, np.ndarray):
        return x

    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy()

    raise TypeError(
        f"Unsupported type: {type(x)}. Supported types are list, NDArray, and Tensor."
    )


def to_tensor(x: list | NDArray | Tensor) -> Tensor:
    """Convert input to PyTorch tensor.

    Args:
        x (list | NDArray | Tensor): Input to convert.

    Returns:
        Tensor: Converted PyTorch tensor.
    """
    if isinstance(x, list):
        return torch.tensor(x)

    if isinstance(x, np.ndarray):
        return torch.from_numpy(x)

    if isinstance(x, torch.Tensor):
        return x

    raise TypeError(
        f"Unsupported type: {type(x)}. Supported types are list, NDArray, and Tensor."
    )


def to_segments(
    x: list[int] | NDArray | Tensor, backgrounds: list[int] | NDArray | Tensor
) -> list[Segment]:
    """Convert input to segments.

    Args:
        x (list[int] | NDArray | Tensor): Input to convert.
        backgrounds (list[int] | NDArray | Tensor): Background segments.

    Returns:
        list[Segment]: Converted segments. Each segment is a tuple of (value, (start_index, end_index)). Range is [start_index, end_index).
    """
    _x = to_np(x)
    if len(_x) == 0:
        return []
    diff = np.flatnonzero(np.diff(_x, prepend=_x[0] - 1))
    indices = np.append(diff, len(_x))
    _backgrounds = set(to_list(backgrounds))

    segments = []
    for start, end in zip(indices[:-1], indices[1:]):
        value = int(_x[start])
        if value not in _backgrounds:
            segments.append((value, (int(start), int(end))))

    return segments


def to_frames(x: list[Segment]) -> list[int]:
    """Convert segments to frame indices.

    Args:
        x (list[Segment]): List of segments, where each segment is a tuple of (value, (start_index, end_index)).

    Returns:
        list[int]: List of frame indices corresponding to the segments.
    """
    frames = []
    for value, (start, end) in x:
        frames.extend([value] * (end - start))
    return frames


class Env:
    def __init__(self, dotenv_path: str | Path | None = None) -> None:
        """Initialize the Env class and load environment variables from .env file.

        Args:
            dotenv_path (str | Path | None, optional): Path to the .env file.
                If None, will look for .env in the current directory. Defaults to None.
        """
        load_dotenv(dotenv_path)

    def __call__(self, name: str) -> str:
        """Get the value of an environment variable.

        Args:
            name (str): Name of the environment variable.

        Returns:
            str: Value of the environment variable or an empty string if not set.
        """
        return os.getenv(name, "")

    def bool(self, name: str) -> bool:
        """Get the boolean value of an environment variable.

        Args:
            name (str): Name of the environment variable.

        Returns:
            bool: True if the environment variable is set to '1', 'true', or 'yes', False otherwise.
        """
        return self(name).lower() in ("1", "true", "yes")

    def int(self, name: str) -> int:
        """Get the integer value of an environment variable.

        Args:
            name (str): Name of the environment variable.

        Returns:
            int: Integer value of the environment variable or 0 if not set.
        """
        try:
            return int(self(name))
        except ValueError:
            return 0

    def float(self, name: str) -> float:
        """Get the float value of an environment variable.

        Args:
            name (str): Name of the environment variable.

        Returns:
            float: Float value of the environment variable or 0.0 if not set.
        """
        try:
            return float(self(name))
        except ValueError:
            return 0.0
