import time
from datetime import datetime

from vut.time import format_time, get_elapsed_time, get_time


def test_get_time():
    result = get_time()
    assert isinstance(result, float), "get_time should return a float"


def test_get_elapsed_time():
    start = time.perf_counter()
    time.sleep(0.1)
    result = get_elapsed_time(start)
    assert isinstance(result, float), "get_elapsed_time should return a float"


def test_format_time():
    seconds = time.time()
    result = format_time(seconds)
    assert isinstance(result, str), "format_time should return a string"


def test_format_time__custom_format():
    seconds = time.time()
    custom_format = "%Y-%m-%d"
    result = format_time(seconds, custom_format)
    expected = datetime.fromtimestamp(seconds).strftime(custom_format)
    assert result == expected, (
        f"format_time should return {expected} with format {custom_format}"
    )
