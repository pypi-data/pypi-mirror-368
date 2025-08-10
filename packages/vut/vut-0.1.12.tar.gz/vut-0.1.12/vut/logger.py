from logging import INFO, FileHandler, Logger, getLogger

from hydra.core.hydra_config import HydraConfig
from rich.logging import RichHandler


def get_logger(name: str = __name__, level: int = INFO, log_file: str = None) -> Logger:
    """Get a logger with a rich handler.

    Args:
        name (str, optional): Name of the logger. Defaults to __name__.
        level (int, optional): Logging level. Defaults to INFO.
        log_file (str, optional): Path to the log file. Defaults to None.

    Returns:
        Logger: Logger instance configured with handlers.
    """
    try:
        hydra_config = HydraConfig.get()
        hydra_path = hydra_config.runtime.output_dir
        job_name = hydra_config.job.name
        log_path = f"{hydra_path}/{job_name}.log"
    except ValueError:
        log_path = log_file

    logger = getLogger(name)
    logger.setLevel(level)

    if log_path:
        file_handler = FileHandler(log_path)
        logger.addHandler(file_handler)
        logger.propagate = False

    rich_handler = RichHandler()
    logger.addHandler(rich_handler)

    return logger
