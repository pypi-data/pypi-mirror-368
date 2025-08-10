from pathlib import Path

import numpy as np
import torch
from numpy.typing import NDArray
from torch import Tensor

from vut.io import load_lines


def to_class_name(
    x: list | NDArray | Tensor, index_to_text: dict[int, str]
) -> list[str]:
    """Convert class indices to class names.

    Args:
        x (list | NDArray | Tensor): The input data containing class indices.
        index_to_text (dict[int, str]): A mapping from class indices to class names.

    Raises:
        TypeError: If the input type is unsupported.

    Returns:
        list[str]: A list of class names corresponding to the input indices.
    """
    if len(x) == 0:
        return []
    if isinstance(x, list):
        assert not isinstance(x[0], list), "List must be 1D"
        return [index_to_text.get(i, "") for i in x]
    if isinstance(x, np.ndarray):
        assert x.ndim == 1, "Array must be 1D"
        x = x.tolist()
        return [index_to_text.get(i, "") for i in x]
    if isinstance(x, torch.Tensor):
        assert x.ndim == 1, "Tensor must be 1D"
        x = x.detach().cpu().tolist()
        return [index_to_text.get(i, "") for i in x]


def to_class_index(x: list[str], text_to_index: dict[str, int]) -> list[int]:
    """Convert class names to class indices.

    Args:
        x (list[str]): The input data containing class names.
        text_to_index (dict[str, int]): A mapping from class names to class indices.

    Raises:
        TypeError: If the input type is unsupported.

    Returns:
        list[int]: A list of class indices corresponding to the input class names.
    """
    if len(x) == 0:
        return []
    assert not isinstance(x[0], list), "List must be 1D"
    return [text_to_index.get(i, -1) for i in x]


def to_class_mapping(x: list[tuple[int, str]]) -> tuple[dict[str, int], dict[int, str]]:
    """Convert a list of class indices and names to a mapping.

    Args:
        x (list[tuple[int, str]]): A list of tuples, where each tuple contains a class index and its name.

    Returns:
        tuple[dict[str, int], dict[int, str]]: A tuple containing two dictionaries:
            - text_to_index: Mapping from class names to class indices.
            - index_to_text: Mapping from class indices to class names.
    """
    text_to_index = {}
    index_to_text = {}
    for i, text in x:
        text_to_index[text] = i
        index_to_text[i] = text
    return text_to_index, index_to_text


def load_class_mapping(
    path: str | Path, has_header: bool = False, separator: str = ","
) -> tuple[dict[str, int], dict[int, str]]:
    """Load class mapping from a csv-like file.
    Format should be:
    ```
    <index><separator><class_name>
    <index><separator><class_name>
    ...
    ```
    where <index> is an integer and <class_name> is a string.

    Args:
        path (str | Path): Path to the class mapping file.
        has_header (bool): Whether the file has a header line. Defaults to False.
        separator (str): Separator for the index and class name. Defaults to ",".

    Returns:
        tuple[dict[int, str], dict[str, int]]: A tuple containing two dictionaries:
            - text_to_index: Mapping from class names to class indices.
            - index_to_text: Mapping from class indices to class names.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    lines = load_lines(path)
    if has_header:
        lines = lines[1:]
    lines = [line.split(separator) for line in lines]
    assert len(lines[0]) == 2, (
        f"Invalid format in file: {path}. Expected format: <index>{separator}<class_name>"
    )
    try:
        lines = [(int(line[0]), line[1]) for line in lines]
    except ValueError:
        raise ValueError(
            f"Invalid index format in file: {path}. index must be an integer."
        )
    return to_class_mapping(lines)


def load_action_mapping(
    path: str | Path,
    has_header: bool = False,
    action_separator: str = ",",
    step_separator: str = " ",
) -> dict[str, list[str]]:
    """Load action mapping from a csv-like file.
    Format should be:
    ```
    <action_name><action_separator><step_name><step_separator><step_name>...
    <action_name><action_separator><step_name><step_separator><step_name>...
    ...
    ```
    where <action_name> is a string and <step_name> is a string.

    Args:
        path (str | Path): Path to the action mapping file.
        has_header (bool): Whether the file has a header line. Defaults to False.
        action_separator (str): Separator for the action name. Defaults to ",".
        step_separator (str): Separator for the step name. Defaults to " ".

    Returns:
        dict[str, list[str]]: A dictionary mapping action names to lists of step names.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    lines = load_lines(path)
    if has_header:
        lines = lines[1:]
    lines = [line.split(action_separator) for line in lines]
    assert len(lines[0]) == 2, (
        f"Invalid format in file: {path}. Expected format: <index>{action_separator}<action_name>"
    )
    mapping = {}
    for line in lines:
        index, action = line
        steps = action.split(step_separator)
        mapping[index] = steps
    return mapping


def load_video_action_mapping(
    path: str | Path,
    has_header: bool = False,
    separator: str = ",",
) -> dict[str, str]:
    """Load video action mapping from a csv-like file.
    Format should be:
    ```
    <video_name><separator><action_name>
    <video_name><separator><action_name>
    ...
    ```
    where <video_name> and <action_name> are strings.

    Args:
        path (str | Path): Path to the video action mapping file.
        has_header (bool): Whether the file has a header line. Defaults to False.
        separator (str): Separator for the video name and action name. Defaults to ",".

    Returns:
        dict[str, str]: A dictionary mapping video names to action names.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    lines = load_lines(path)
    if has_header:
        lines = lines[1:]
    lines = [line.split(separator) for line in lines]
    return dict(lines)


def load_video_boundaries_from_file(
    file_path: str | Path,
    has_header: bool = False,
    separator: str = ",",
) -> list[tuple[int, int]]:
    """Load boundaries of untrimmed video from a csv-like file.
    Format should be:
    ```
    <start_frame><separator><end_frame>
    <start_frame><separator><end_frame>
    ...
    ```
    where <start_frame> and <end_frame> are integers.

    Args:
        file_path (str | Path): Path to the video boundaries file.
        has_header (bool, optional): Whether the file has a header line. Defaults to False.
        separator (str, optional): Separator for the video name and boundaries. Defaults to ",".

    Returns:
        list[tuple[int, int]]: A list of tuples containing the start and end frames from video.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    lines = load_lines(file_path)
    if has_header:
        lines = lines[1:]
    lines = [line.split(separator) for line in lines]
    assert len(lines[0]) == 2, (
        f"Invalid format in file: {file_path}. Expected format: <start_frame>{separator}<end_frame>"
    )
    try:
        lines = [(int(line[0]), int(line[1])) for line in lines]
    except ValueError:
        raise ValueError(
            f"Invalid format in file: {file_path}. start_frame and end_frame must be integers."
        )
    return lines


def load_video_boundaries(
    dir_path: str | Path,
    has_header: bool = False,
    separator: str = ",",
) -> dict[str, list[tuple[int, int]]]:
    """Load boundaries of untrimmed videos from multiple files in a directory.
    Format should be:
    ```
    <start_frame><separator><end_frame>
    <start_frame><separator><end_frame>
    ...
    ```
    where <start_frame> and <end_frame> are integers.

    Args:
        dir_path (str | Path): Path to the directory containing video boundary files.
        has_header (bool, optional): Whether the files have a header line. Defaults to False.
        separator (str, optional): Separator for start and end frames. Defaults to ",".

    Returns:
        dict[str, list[tuple[int, int]]]: A dictionary mapping video names to their start and end frames.
    """
    dir_path = Path(dir_path)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {dir_path}")
    files = [f for f in dir_path.iterdir() if f.is_file()]
    mapping = {}
    for file in files:
        boundaries = load_video_boundaries_from_file(
            file, has_header=has_header, separator=separator
        )
        mapping[file.stem] = boundaries
    return mapping
