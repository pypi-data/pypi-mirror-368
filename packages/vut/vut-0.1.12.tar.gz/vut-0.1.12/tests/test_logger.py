import logging
import os
import tempfile

from pytest_mock import MockerFixture

from vut.logger import get_logger


def test_get_logger__stdout_only(caplog):
    logger = get_logger("stdout_only")
    logger.info("This is an info message")

    assert (
        "stdout_only",
        logging.INFO,
        "This is an info message",
    ) in caplog.record_tuples


def test_get_logger__file_only(caplog):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        log_file = temp_file.name
    logger = get_logger("file_only", log_file=log_file)
    logger.info("This is an info message")
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "This is an info message" in log_content
    assert (
        "file_only",
        logging.INFO,
        "This is an info message",
    ) not in caplog.record_tuples
    temp_file.close()


def test_get_logger__with_hydra(mocker: MockerFixture, caplog):
    config = mocker.Mock()
    with tempfile.TemporaryDirectory() as temp_dir:
        config.runtime.output_dir = temp_dir
        config.job.name = "test_job"
        mocker.patch("hydra.core.hydra_config.HydraConfig.get", return_value=config)
        logger = get_logger("with_hydra")
        logger.propagate = True
        logger.info("This is an info message")

        log_file_path = os.path.join(temp_dir, "test_job.log")
        with open(log_file_path, "r") as f:
            log_content = f.read()
        assert "This is an info message" in log_content
        assert (
            "with_hydra",
            logging.INFO,
            "This is an info message",
        ) in caplog.record_tuples


def test_get_logger__stdout_and_file(caplog):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        log_file = temp_file.name
    logger = get_logger("stdout_and_file", log_file=log_file)
    logger.propagate = True
    logger.info("This is an info message")
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "This is an info message" in log_content
    assert (
        "stdout_and_file",
        logging.INFO,
        "This is an info message",
    ) in caplog.record_tuples
    os.remove(log_file)


def test_get_logger__level_warning(caplog):
    logger = get_logger("level_warning", level=logging.WARNING)
    logger.info("This is an info message")
    assert (
        "level_warning",
        logging.INFO,
        "This is an info message",
    ) not in caplog.record_tuples
    logger.warning("This is a warning message")
    assert (
        "level_warning",
        logging.WARNING,
        "This is a warning message",
    ) in caplog.record_tuples
