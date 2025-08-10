import tempfile
from pathlib import Path

import numpy as np
import pytest
import torch

from vut.mapping import (
    load_action_mapping,
    load_class_mapping,
    load_video_action_mapping,
    load_video_boundaries,
    load_video_boundaries_from_file,
    to_class_index,
    to_class_mapping,
    to_class_name,
)


def test_to_class_name():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = [0, 1, 2]
    expected = ["cat", "dog", "bird"]
    result = to_class_name(indices, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_name__empty():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = []
    expected = []
    result = to_class_name(indices, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_name__unknown_index():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = [0, 1, 3]
    expected = ["cat", "dog", ""]
    result = to_class_name(indices, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_name__invalid_shape():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = [[0, 1], [2]]
    with pytest.raises(AssertionError):
        to_class_name(indices, mapping)


def test_to_class_name__ndarray():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = np.array([0, 1, 2])
    expected = ["cat", "dog", "bird"]
    result = to_class_name(indices, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_name__invalid_ndarray():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = np.array([[0, 1], [2, 3]])
    with pytest.raises(AssertionError):
        to_class_name(indices, mapping)


def test_to_class_name__tensor():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = torch.tensor([0, 1, 2])
    expected = ["cat", "dog", "bird"]
    result = to_class_name(indices, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_name__invalid_tensor():
    mapping = {
        0: "cat",
        1: "dog",
        2: "bird",
    }
    indices = torch.tensor([[0, 1], [2, 3]])
    with pytest.raises(AssertionError):
        to_class_name(indices, mapping)


def test_to_class_index():
    mapping = {
        "cat": 0,
        "dog": 1,
        "bird": 2,
    }
    names = ["cat", "dog", "bird"]
    expected = [0, 1, 2]
    result = to_class_index(names, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_index__empty():
    mapping = {
        "cat": 0,
        "dog": 1,
        "bird": 2,
    }
    names = []
    expected = []
    result = to_class_index(names, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_index__unknown_name():
    mapping = {
        "cat": 0,
        "dog": 1,
        "bird": 2,
    }
    names = ["cat", "dog", "fish"]
    expected = [0, 1, -1]
    result = to_class_index(names, mapping)
    assert result == expected, f"Expected {expected}, but got {result}"


def test_to_class_index__invalid_shape():
    mapping = {
        "cat": 0,
        "dog": 1,
        "bird": 2,
    }
    names = [["cat", "dog"], ["bird"]]
    with pytest.raises(AssertionError):
        to_class_index(names, mapping)


def test_to_class_mapping():
    data = [(0, "cat"), (1, "dog"), (2, "bird")]
    expected_text_to_index = {"cat": 0, "dog": 1, "bird": 2}
    expected_index_to_text = {0: "cat", 1: "dog", 2: "bird"}
    text_to_index, index_to_text = to_class_mapping(data)
    assert text_to_index == expected_text_to_index
    assert index_to_text == expected_index_to_text


def test_to_class_mapping__empty():
    data = []
    expected_text_to_index = {}
    expected_index_to_text = {}
    text_to_index, index_to_text = to_class_mapping(data)
    assert text_to_index == expected_text_to_index
    assert index_to_text == expected_index_to_text


@pytest.fixture
def class_mapping_file():
    content = "0,cat\n1,dog\n2,bird"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)
        filepath = f.name
    yield filepath
    Path(filepath).unlink()


@pytest.fixture
def class_mapping_file_with_header():
    content = "index,name\n0,cat\n1,dog\n2,bird"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)
        filepath = f.name
    yield filepath
    Path(filepath).unlink()


def test_load_class_mapping(class_mapping_file):
    expected_text_to_index = {"cat": 0, "dog": 1, "bird": 2}
    expected_index_to_text = {0: "cat", 1: "dog", 2: "bird"}
    text_to_index, index_to_text = load_class_mapping(class_mapping_file)
    assert text_to_index == expected_text_to_index
    assert index_to_text == expected_index_to_text


def test_load_class_mapping__with_header(class_mapping_file_with_header):
    expected_text_to_index = {"cat": 0, "dog": 1, "bird": 2}
    expected_index_to_text = {0: "cat", 1: "dog", 2: "bird"}
    text_to_index, index_to_text = load_class_mapping(
        class_mapping_file_with_header, has_header=True
    )
    assert text_to_index == expected_text_to_index
    assert index_to_text == expected_index_to_text


def test_load_class_mapping__file_not_found():
    with pytest.raises(FileNotFoundError):
        load_class_mapping("non_existent_file.csv")


@pytest.fixture
def action_mapping_file():
    content = "0,action_a step_a1 step_a2\n1,action_b step_b1"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)
        filepath = f.name
    yield filepath
    Path(filepath).unlink()


def test_load_action_mapping(action_mapping_file):
    expected_mapping = {
        "0": ["action_a", "step_a1", "step_a2"],
        "1": ["action_b", "step_b1"],
    }
    mapping = load_action_mapping(action_mapping_file, step_separator=" ")
    assert mapping == expected_mapping


def test_load_action_mapping__file_not_found():
    with pytest.raises(FileNotFoundError):
        load_action_mapping("non_existent_file.csv")


@pytest.fixture
def video_action_mapping_file():
    content = "video1,action_a\nvideo2,action_b"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)
        filepath = f.name
    yield filepath
    Path(filepath).unlink()


def test_load_video_action_mapping(video_action_mapping_file):
    expected_mapping = {
        "video1": "action_a",
        "video2": "action_b",
    }
    mapping = load_video_action_mapping(video_action_mapping_file)
    assert mapping == expected_mapping


def test_load_video_action_mapping__file_not_found():
    with pytest.raises(FileNotFoundError):
        load_video_action_mapping("non_existent_file.csv")


@pytest.fixture
def video_boundaries_file():
    content = "0,100\n101,200"
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)
        filepath = f.name
    yield filepath
    Path(filepath).unlink()


def test_load_video_boundaries_from_file(video_boundaries_file):
    expected_boundaries = [(0, 100), (101, 200)]
    boundaries = load_video_boundaries_from_file(video_boundaries_file)
    assert boundaries == expected_boundaries


def test_load_video_boundaries_from_file__file_not_found():
    with pytest.raises(FileNotFoundError):
        load_video_boundaries_from_file("non_existent_file.csv")


@pytest.fixture
def video_boundaries_dir(tmp_path):
    dir_path = tmp_path / "boundaries"
    dir_path.mkdir()
    (dir_path / "video1.csv").write_text("0,10\n11,20")
    (dir_path / "video2.txt").write_text("100,110\n111,120")
    return dir_path


def test_load_video_boundaries(video_boundaries_dir):
    expected_mapping = {
        "video1": [(0, 10), (11, 20)],
        "video2": [(100, 110), (111, 120)],
    }
    mapping = load_video_boundaries(video_boundaries_dir)
    assert mapping == expected_mapping


def test_load_video_boundaries__dir_not_found():
    with pytest.raises(FileNotFoundError):
        load_video_boundaries("non_existent_dir")


def test_load_video_boundaries__not_a_dir():
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        filepath = f.name
    with pytest.raises(NotADirectoryError):
        load_video_boundaries(filepath)
    Path(filepath).unlink()
