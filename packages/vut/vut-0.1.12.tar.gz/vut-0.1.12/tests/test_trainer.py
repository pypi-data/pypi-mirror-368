import tempfile

import pytest
from pytest_mock import MockerFixture

from vut.config import Config
from vut.trainer import Trainer


class MockTrainer(Trainer):
    def train(self):
        return "train_called"

    def validate(self):
        return "validate_called"

    def test(self):
        return "test_called"

    def predict(self):
        return "predict_called"


@pytest.fixture
def mock_hydra_config(mocker: MockerFixture):
    with tempfile.TemporaryDirectory() as temp_dir:
        config = mocker.Mock()
        config.runtime.output_dir = temp_dir
        config.job.name = "test_job"
        mocker.patch("hydra.core.hydra_config.HydraConfig.get", return_value=config)
        yield config


@pytest.fixture
def sample_config():
    return Config(
        seed=42,
        device="cpu",
        result_dir="test_results",
    )


def test_trainer(mock_hydra_config, sample_config):
    trainer = MockTrainer(sample_config)

    assert trainer.cfg == sample_config
    assert trainer.output_dir == mock_hydra_config.runtime.output_dir
    assert trainer.device is not None
    assert trainer.logger is not None
