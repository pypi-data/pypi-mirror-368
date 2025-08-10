import tempfile
from pathlib import Path

import pytest
import torch
from pytest_mock import MockerFixture

from vut.cuda import get_device, load_model, save_model
from vut.models import I3D


def test_get_device__cpu():
    device = get_device("cpu")
    assert device.type == "cpu", "Device should be CPU"


def test_get_device__cuda():
    if torch.cuda.is_available():
        device = get_device(0)
        assert device.type == "cuda", "Device should be CUDA"
    else:
        pytest.skip("CUDA is not available, skipping test.")


def test_get_device__non_existent_cuda():
    device = get_device(torch.cuda.device_count() + 1)
    assert device.type == "cpu", (
        "Device should fall back to CPU when CUDA is not available"
    )


def test_get_device__invalid_id():
    with pytest.raises(ValueError):
        get_device(-1)


def test_load_model__valid_path(mocker: MockerFixture):
    model = I3D()
    logger = mocker.Mock()
    logger.info = mocker.Mock()
    logger.warning = mocker.Mock()

    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = Path(temp_dir) / "model.pth"
        torch.save(model.state_dict(), model_path)
        assert model_path.exists(), "Model path should exist"
        assert model_path.is_file(), "Model path should be a file"

        model = load_model(model, model_path, logger=logger)

        assert logger.info.call_count == 1, "Logger should log info message"
        assert logger.warning.call_count == 0, "Logger should not log warning message"


def test_load_model__no_logger(mocker: MockerFixture):
    model = I3D()

    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = Path(temp_dir) / "model.pth"
        torch.save(model.state_dict(), model_path)
        assert model_path.exists(), "Model path should exist"
        assert model_path.is_file(), "Model path should be a file"

        mock_logger = mocker.patch("vut.cuda.get_logger")
        model = load_model(model, model_path)
        assert mock_logger.call_count == 1, "Logger should be called once"


def test_load_model__with_device(mocker: MockerFixture):
    model = I3D()
    device = get_device()
    model = model.to(device)
    logger = mocker.Mock()
    logger.info = mocker.Mock()
    logger.warning = mocker.Mock()

    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = Path(temp_dir) / "model.pth"
        torch.save(model.state_dict(), model_path)
        assert model_path.exists(), "Model path should exist"
        assert model_path.is_file(), "Model path should be a file"

        model = load_model(model, model_path, device=device, logger=logger)

        assert logger.info.call_count == 1, "Logger should log info message"
        assert logger.warning.call_count == 0, "Logger should not log warning message"


def test_load_model__invalid_path(mocker: MockerFixture):
    model = I3D()
    logger = mocker.Mock()
    logger.info = mocker.Mock()
    logger.warning = mocker.Mock()

    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = Path(temp_dir) / "invalid_model.pth"
        assert not model_path.exists(), "Model path should not exist"

        model = load_model(model, model_path, logger=logger)

        assert logger.info.call_count == 0, "Logger should not log info message"
        assert logger.warning.call_count == 1, "Logger should log warning message"


def test_save_model():
    model = I3D()
    with tempfile.TemporaryDirectory() as temp_dir:
        model_path = Path(temp_dir) / "model.pth"
        save_model(model, model_path)
        assert model_path.exists(), "Model path should exist"
        assert model_path.is_file(), "Model path should be a file"
