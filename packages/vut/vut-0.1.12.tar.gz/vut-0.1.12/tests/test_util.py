import os

import numpy as np
import pytest
import torch
from pytest_mock import MockerFixture

from vut.util import (
    Env,
    init_seed,
    to_frames,
    to_list,
    to_np,
    to_segments,
    to_tensor,
    unique,
)


def test_init_seed__same_values():
    init_seed(42)
    data = np.random.rand(1000)
    init_seed(42)
    expected = np.random.rand(1000)
    assert np.array_equal(data, expected), (
        "Random data should be the same after re-initializing the seed"
    )


def test_init_seed__different_values():
    init_seed(42)
    data1 = np.random.rand(1000)
    init_seed(43)
    data2 = np.random.rand(1000)
    assert not np.array_equal(data1, data2), (
        "Random data should be different after changing the seed"
    )


test_case_unique = [
    # empty
    ([], []),
    # single element
    ([1], [1]),
    # multiple elements
    ([1, 2, 3], [1, 2, 3]),
    # duplicates
    ([1, 2, 2, 3], [1, 2, 3]),
    ([1, 1, 1], [1]),
    # mixed types
    ([1, 2.0, 3], [1, 2.0, 3]),
    # order preservation
    ([3, 1, 2, 1], [3, 1, 2]),
    ([1, 3, 1, 2, 4, 3, 2], [1, 3, 2, 4]),
]


@pytest.mark.parametrize(
    "data, expected",
    test_case_unique,
)
def test_unique__list(data, expected):
    assert unique(data) == expected


@pytest.mark.parametrize(
    "data, expected",
    test_case_unique,
)
def test_unique__ndarray(data, expected):
    data = np.array(data)
    expected = np.array(expected)
    assert np.array_equal(unique(data), expected)


@pytest.mark.parametrize(
    "data, expected",
    test_case_unique,
)
def test_unique__tensor(data, expected):
    data = torch.tensor(data)
    expected = torch.tensor(expected)
    assert torch.equal(unique(data), expected)


def test_unique__unsupported_type():
    with pytest.raises(TypeError):
        unique("unsupported type")


def test_to_list__list():
    data = [1, 2, 3]
    result = to_list(data)
    assert result == data, "Should return the same list"


def test_to_list__ndarray():
    data = np.array([1, 2, 3])
    result = to_list(data)
    assert result == data.tolist(), "Should return the same list"


def test_to_list__tensor():
    data = torch.tensor([1, 2, 3])
    result = to_list(data)
    assert result == data.tolist(), "Should return the same list"


def test_to_list__unsupported_type():
    with pytest.raises(TypeError):
        to_list("unsupported type")


def test_to_np__list():
    data = [1, 2, 3]
    result = to_np(data)
    assert np.array_equal(result, np.array(data)), "Should return the same numpy array"


def test_to_np__ndarray():
    data = np.array([1, 2, 3])
    result = to_np(data)
    assert np.array_equal(result, data), "Should return the same numpy array"


def test_to_np__tensor():
    data = torch.tensor([1, 2, 3])
    result = to_np(data)
    assert np.array_equal(result, data.numpy()), "Should return the same numpy array"


def test_to_np__unsupported_type():
    with pytest.raises(TypeError):
        to_np("unsupported type")


def test_to_tensor__list():
    data = [1, 2, 3]
    result = to_tensor(data)
    assert torch.equal(result, torch.tensor(data)), "Should return the same tensor"


def test_to_tensor__ndarray():
    data = np.array([1, 2, 3])
    result = to_tensor(data)
    assert torch.equal(result, torch.tensor(data)), "Should return the same tensor"


def test_to_tensor__tensor():
    data = torch.tensor([1, 2, 3])
    result = to_tensor(data)
    assert torch.equal(result, data), "Should return the same tensor"


def test_to_tensor__unsupported_type():
    with pytest.raises(TypeError):
        to_tensor("unsupported type")


def test_env(mocker: MockerFixture):
    mocker.patch.dict(os.environ, {"VUT_ENV": "test_env"})
    env = Env()
    assert env("VUT_ENV") == "test_env", "Should return the value of VUT_ENV"


def test_env__dotenv_loading(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "TEST_VAR=dotenv_value\nTEST_BOOL=true\nTEST_INT=100\nTEST_FLOAT=3.14\n"
    )

    env = Env(str(env_file))

    assert env("TEST_VAR") == "dotenv_value", "Should load variable from .env file"
    assert env.bool("TEST_BOOL") is True, "Should load boolean from .env file"
    assert env.int("TEST_INT") == 100, "Should load integer from .env file"
    assert env.float("TEST_FLOAT") == 3.14, "Should load float from .env file"


def test_env_bool(mocker: MockerFixture):
    mocker.patch.dict(os.environ, {"VUT_ENV": "True"})
    env = Env()
    assert env.bool("VUT_ENV") is True, "Should return True for 'True' string"


def test_env_int(mocker: MockerFixture):
    mocker.patch.dict(os.environ, {"VUT_ENV": "42"})
    env = Env()
    assert env.int("VUT_ENV") == 42, "Should return the integer value of VUT_ENV"


def test_env_float(mocker: MockerFixture):
    mocker.patch.dict(os.environ, {"VUT_ENV": "3.14"})
    env = Env()
    assert env.float("VUT_ENV") == 3.14, "Should return the float value of VUT_ENV"


test_case_to_segments = [
    # simple case: continuous values with one background
    ([1, 1, 2, 2, 2, 3, 3, 1, 1], [1], [(2, (2, 5)), (3, (5, 7))]),
    # no background segments
    ([1, 2, 3], [], [(1, (0, 1)), (2, (1, 2)), (3, (2, 3))]),
    # all background segments
    ([1, 1, 1], [1], []),
    # empty input
    ([], [], []),
    # single element not in background
    ([1], [2], [(1, (0, 1))]),
    # single element in background
    ([1], [1], []),
    # multiple backgrounds
    ([1, 2, 3, 1, 2], [1, 2], [(3, (2, 3))]),
    # complex case with background changes
    ([0, 1, 1, 2, 2, 0, 0, 3, 3, 3], [0], [(1, (1, 3)), (2, (3, 5)), (3, (7, 10))]),
]


@pytest.mark.parametrize(
    "data, backgrounds, expected",
    test_case_to_segments,
)
def test_to_segments(data, backgrounds, expected):
    result = to_segments(data, backgrounds)
    assert result == expected


# Test cases for to_frames
test_case_to_frames = [
    # simple case
    ([(1, (0, 3)), (2, (3, 5))], [1, 1, 1, 2, 2]),
    # single segment
    ([(5, (0, 4))], [5, 5, 5, 5]),
    # empty input
    ([], []),
    # segments with different lengths
    ([(1, (0, 2)), (3, (2, 3)), (7, (3, 6))], [1, 1, 3, 7, 7, 7]),
    # single frame segments
    ([(1, (0, 1)), (2, (1, 2)), (3, (2, 3))], [1, 2, 3]),
]


@pytest.mark.parametrize(
    "segments, expected",
    test_case_to_frames,
)
def test_to_frames(segments, expected):
    result = to_frames(segments)
    assert result == expected
