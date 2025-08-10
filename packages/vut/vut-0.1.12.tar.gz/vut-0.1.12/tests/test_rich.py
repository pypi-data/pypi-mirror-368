import time

import pytest
from pytest_mock import MockerFixture
from rich.console import Console
from rich.progress import Task, TextColumn

from vut.rich import IterationSpeedColumn, Progress, track


def test_iteration_speed_column(mocker: MockerFixture):
    column = IterationSpeedColumn()
    task = mocker.Mock(spec=Task)
    task.finished_speed = None
    task.speed = 1500.0

    result = column.render(task)

    assert "1.5×10³ it/s" in str(result)


def test_iteration_speed_column__no_speed(mocker: MockerFixture):
    column = IterationSpeedColumn()
    task = mocker.Mock(spec=Task)
    task.finished_speed = None
    task.speed = None

    result = column.render(task)

    assert "? it/s" in str(result)


def test_progress__single_entry():
    with Progress() as progress:
        assert progress is not None
        assert hasattr(progress, "add_task")


def test_progress__nested_entry():
    progress = Progress()

    with progress as p1:
        assert p1 is not None
        with progress as p2:
            assert p1 is p2
            assert progress.context_count == 2
        assert progress.context_count == 1
    assert progress.context_count == 0


@pytest.mark.filterwarnings("ignore:Progress is a singleton.")
def test_progress__warning():
    Progress(TextColumn("[progress.description]{task.description}"))
    with pytest.warns(UserWarning, match="Progress is a singleton."):
        Progress(TextColumn("[progress.description]{task.description}"))


def test_track(mocker: MockerFixture):
    sequence = [1, 2, 3]
    result = []

    mock_console = mocker.Mock(spec=Console)

    for item in track(sequence, description="Test", console=mock_console):
        result.append(item)

    assert result == sequence


def test_track__generator_sequence():
    def generator():
        for i in range(3):
            yield i

    result = []
    for item in track(generator(), description="Test", disable=True):
        result.append(item)

    assert result == [0, 1, 2]


def test_track__update_period():
    sequence = [1, 2, 3, 4, 5]
    result = []

    for item in track(sequence, description="Test", update_period=0.1, disable=True):
        result.append(item)
        time.sleep(0.05)

    assert result == sequence
