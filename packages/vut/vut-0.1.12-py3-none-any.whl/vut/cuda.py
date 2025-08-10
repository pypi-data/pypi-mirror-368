from pathlib import Path
from typing import Literal

import torch
from torch.nn import Module

from .logger import get_logger


def get_device(id: int | Literal["cpu", "cuda"] = 0) -> torch.device:
    """Get the device to be used for tensor operations.

    Args:
        id (int | Literal["cpu", "cuda"], optional): Device index or 'cpu'. Defaults to 0.

    Returns:
        torch.device: The device to be used for tensor operations.
    """
    if isinstance(id, int) or id == "cuda":
        if id == "cuda":
            return torch.device("cuda")
        if id < 0:
            raise ValueError(
                f"Invalid device id: {id}. Must be a non-negative integer."
            )
        if id >= torch.cuda.device_count():
            return torch.device("cpu")
        return torch.device(f"cuda:{id}")
    if id == "cpu":
        return torch.device("cpu")


def load_model(
    model: Module,
    model_path: str | Path,
    device: torch.device | Literal["cpu", "cuda"] = "cpu",
    logger=None,
    strict: bool = True,
) -> Module:
    """Load a model from a given path.

    Args:
        model (Module): The model to be loaded.
        model_path (str | Path): The path to the model file.
        device (torch.device | Literal["cpu", "cuda"], optional): The device to load the model onto. Defaults to "cpu".
        logger (Logger, optional): Logger for logging messages. Defaults to None.
        strict (bool, optional): Whether to enforce strict loading of the model. Defaults to True.

    Returns:
        Module: The loaded model.
    """
    if not logger:
        logger = get_logger()
    model = model.to(device)
    _model_path = Path(model_path)
    if _model_path.exists() and _model_path.is_file():
        model.load_state_dict(
            torch.load(model_path, map_location=device, weights_only=strict),
            strict=strict,
        )
        logger.info(f"Model was loaded from {model_path}")
    else:
        logger.warning(f"Model was not found in {model_path}")
    return model


def save_model(model: Module, model_path: str | Path) -> None:
    """Save the model to the specified path.

    Args:
        model (Module): The model to be saved.
        model_path (str | Path): The path where the model will be saved.
    """
    model = model.cpu()
    torch.save(model.state_dict(), str(model_path))
