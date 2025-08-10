import time
from datetime import datetime


def get_time() -> float:
    """Get the current time in seconds since the performance counter started.

    Returns:
        float: The current time in seconds.
    """
    return time.perf_counter()


def get_elapsed_time(start: float) -> float:
    """Calculate the elapsed time since the given start time.

    Args:
        start (float): The start time in seconds.

    Returns:
        float: The elapsed time in seconds.
    """
    return time.perf_counter() - start


def format_time(seconds: float, format="%Y-%m-%d %H:%M:%S") -> str:
    """Format the given time in seconds into a human-readable string.

    Args:
        seconds (float): The time in seconds.
        format (str, optional): The format string. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: The formatted time string.
    """
    return datetime.fromtimestamp(seconds).strftime(format)
