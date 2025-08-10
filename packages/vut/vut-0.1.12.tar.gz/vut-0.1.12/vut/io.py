import os
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
from numpy.typing import NDArray
from torch import Tensor


def get_dirs(path: str | Path, recursive: bool = False) -> list[Path]:
    """Get directories from the specified path.

    Args:
        path (str | Path): The path to search for directories.
        recursive (bool, optional): Whether to search directories recursively. Defaults to False.

    Returns:
        list[Path]: A list of directories found.
    """
    path = str(path)
    dirs = set()

    if not os.path.exists(path) or not os.path.isdir(path):
        return []

    if not recursive:
        dirs = [
            os.path.join(path, d)
            for d in os.listdir(path)
            if os.path.exists(os.path.join(path, d))
            and os.path.isdir(os.path.join(path, d))
        ]
        return [Path(d) for d in dirs]

    for path, _, files in os.walk(path):
        if len(files) > 0:
            dirs.add(path)

    return sorted([Path(d) for d in dirs])


def get_images(
    img_dir: str | Path, ext: list[str] = ["jpg", "jpeg", "png", "gif", "webp"]
) -> list[Path]:
    """Get image paths from a directory.

    Args:
        img_dir (str | Path): The directory to search for images.
        ext (list[str], optional): List of image file extensions to include. Defaults to ["jpg", "jpeg", "png", "gif", "webp"].

    Raises:
        FileNotFoundError: If the directory does not exist.
        NotADirectoryError: If the path is not a directory.

    Returns:
        list[Path]: A list of image paths found in the directory.
    """
    img_dir = Path(img_dir)
    if not img_dir.exists():
        raise FileNotFoundError(f"Image directory '{img_dir}' does not exist.")
    if not img_dir.is_dir():
        raise NotADirectoryError(f"'{img_dir}' is not a directory.")

    ext = set([e.lower() for e in ext])
    paths = [p for p in img_dir.rglob("*") if p.suffix[1:].lower() in ext]
    return sorted(paths)


def save_list(lst: list, path: str | Path, callback=None) -> None:
    """Save a list to a file.

    Args:
        lst (list): List to save.
        path (str | Path): Path to save the list.
        callback (callable, optional): A function to apply to each item before saving. Defaults to None.
    """
    with open(path, "w") as f:
        f.writelines(
            f"{callback(item) if callback is not None else item}\n" for item in lst
        )


def save_np(arr: NDArray, path: str | Path) -> None:
    """Save a numpy array to a file.

    Args:
        arr (NDArray): Numpy array to save.
        path (str | Path): Path to save the numpy array.
    """
    np.save(path, arr)


def save_tensor(tensor: Tensor, path: str | Path) -> None:
    """Save a PyTorch tensor to a file.

    Args:
        tensor (Tensor): PyTorch tensor to save.
        path (str | Path): Path to save the tensor.
    """
    torch.save(tensor, path)


def save(x: list | NDArray | Tensor, path: str | Path) -> None:
    """Save a list, numpy array, or PyTorch tensor to a file.

    Args:
        x (list | NDArray | Tensor): Input to save.
        path (str | Path): Path to save the input.
    """
    if isinstance(x, list):
        save_list(x, path)
    elif isinstance(x, np.ndarray):
        save_np(x, path)
    elif isinstance(x, torch.Tensor):
        save_tensor(x, path)


def save_image(image: NDArray, path: str | Path) -> None:
    """Save an image to a file.

    Args:
        image (NDArray): Image to save.
        path (str | Path): Path to save the image.
    """
    cv2.imwrite(str(path), image)


def load_lines(path: str | Path, callback=None) -> list[str] | list[Any]:
    """Load lines from a text file.

    Args:
        path (str | Path): Path to load the file from.
        callback (callable, optional): A function to apply to each line after loading. Defaults to None.

    Returns:
        list: A list of strings loaded from the file. If callback is provided, the list will contain the results of applying the callback to each line.
    """
    with open(path, "r") as f:
        if callback is not None:
            loaded_list = [callback(line) for line in f.readlines()]
        else:
            loaded_list = [line.strip() for line in f.readlines() if line.strip()]
    return loaded_list


def load_np(path: str | Path) -> NDArray:
    """Load a numpy array from a file.

    Args:
        path (str | Path): Path to load the numpy array from.

    Returns:
        NDArray: Loaded numpy array.
    """
    return np.load(path)


def load_tensor(path: str | Path) -> Tensor:
    """Load a PyTorch tensor from a file.

    Args:
        path (str | Path): Path to load the tensor from.

    Returns:
        Tensor: Loaded PyTorch tensor.
    """
    return torch.load(path)


def load_file(path: str | Path) -> list[str]:
    """Load a text file and return its contents as a list of lines.

    Args:
        path (str | Path): Path to the text file.

    Returns:
        list[str]: List of lines in the text file.
    """
    return load_lines(path)


def load_files(path: str | Path, callback=None) -> dict[str, list[str]]:
    """Load multiple text files and return their contents as a dictionary with filename as key.

    Args:
        path (str | Path): Path to the directory containing text files.
        callback (callable, optional): A function to apply to each line after loading. Defaults to None.

    Returns:
        dict[str, list[str]]: Dictionary with filename as key and list of lines as value.
    """
    files = [f for f in Path(path).glob("*") if f.is_file()]
    return {file.name: load_lines(file, callback) for file in files}


def load_image(path: str | Path) -> NDArray:
    """Load an image from a file.

    Args:
        path (str | Path): Path to the image file.

    Returns:
        NDArray: Loaded image as a numpy array.
    """
    return cv2.imread(str(path), cv2.IMREAD_UNCHANGED)


def load_images(paths: list[str | Path]) -> list[NDArray]:
    """Load multiple images from files.

    Args:
        paths (list[str | Path]): List of paths to the image files.

    Returns:
        list[NDArray]: List of loaded images as numpy arrays.
    """
    return [load_image(path) for path in paths]
