import threading
import time
import warnings
from typing import Callable, Iterable, List, Optional, Sequence, TypeVar, Union

import rich.filesize as filesize
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    ProgressColumn,
    Task,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.progress import Progress as RichProgress
from rich.style import StyleType
from rich.text import Text

ProgressType = TypeVar("ProgressType")


class IterationSpeedColumn(ProgressColumn):
    """Displays iteration speed in it/s (iterations per second)."""

    def render(self, task: "Task") -> Text:
        speed = task.finished_speed or task.speed
        if speed is None:
            return Text("? it/s", style="progress.percentage")
        unit, suffix = filesize.pick_unit_and_suffix(
            int(speed),
            ["", "×10³", "×10⁶", "×10⁹", "×10¹²"],
            1000,
        )
        data_speed = speed / unit
        return Text(f"{data_speed:.1f}{suffix} it/s", style="progress.percentage")


class Progress:
    """Renders an auto-updating progress bar(s) with optional nested tasks.

    Args:
        *columns (ProgressColumn): Columns to display in the progress bar.
        console (Console, optional): Optional Console instance. Defaults to an internal Console instance writing to stdout.
        auto_refresh (bool, optional): Enable auto refresh. If disabled, you will need to call `refresh()`.
        refresh_per_second (Optional[float], optional): Number of times per second to refresh the progress information or None to use default (10). Defaults to None.
        speed_estimate_period: (float, optional): Period (in seconds) used to calculate the speed estimate. Defaults to 30.
        transient: (bool, optional): Clear the progress on exit. Defaults to False.
        redirect_stdout: (bool, optional): Enable redirection of stdout, so ``print`` may be used. Defaults to True.
        redirect_stderr: (bool, optional): Enable redirection of stderr. Defaults to True.
        get_time: (Callable, optional): A callable that gets the current time, or None to use Console.get_time. Defaults to None.
        disable (bool, optional): Disable progress display. Defaults to False
        expand (bool, optional): Expand tasks table to fit width. Defaults to False.
    """

    _instance: Optional["Progress"] = None
    _lock = threading.Lock()
    _initialized = False
    _initial_columns: Optional[Sequence[ProgressColumn]] = None
    _initial_kwargs: Optional[dict] = None
    _suppress_warnings = False

    def __new__(cls, *columns, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initial_columns = columns
                cls._instance._initial_kwargs = kwargs
            elif not cls._suppress_warnings and columns:
                if columns != cls._instance._initial_columns:
                    warnings.warn(
                        "Progress is a singleton. New initialization parameters ignored.",
                        UserWarning,
                    )
        return cls._instance

    def __init__(self, *columns, **kwargs):
        with self._lock:
            if not Progress._initialized:
                self.progress: Optional[RichProgress] = None
                self.active_tasks: List[int] = []
                self.context_count = 0
                self._context_lock = threading.RLock()
                Progress._initialized = True

    def __enter__(self):
        self._context_lock.__enter__()

        if self.progress is None:
            if self._initial_columns is None:
                raise ValueError(
                    "Configuration must be set when creating Progress instance"
                )

            self.progress = RichProgress(*self._initial_columns, **self._initial_kwargs)
            self.context_count = 1

            self.progress.__enter__()
            return self.progress
        else:
            self.context_count += 1
            return self.progress

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.context_count -= 1

            if self.context_count == 0:
                if self.progress:
                    if hasattr(self.progress, "refresh"):
                        self.progress.refresh()
                    self.progress.__exit__(exc_type, exc_val, exc_tb)
                    self.progress = None
                    self.active_tasks.clear()
        finally:
            self._context_lock.__exit__(exc_type, exc_val, exc_tb)


def track(
    sequence: Union[Sequence[ProgressType], Iterable[ProgressType]],
    description: str = "Working...",
    total: Optional[int] = None,
    completed: int = 0,
    auto_refresh: bool = True,
    console: Optional[Console] = None,
    transient: bool = False,
    get_time: Optional[Callable[[], float]] = None,
    refresh_per_second: float = 10,
    style: StyleType = "bar.back",
    complete_style: StyleType = "bar.complete",
    finished_style: StyleType = "bar.finished",
    pulse_style: StyleType = "bar.pulse",
    update_period: float = 0.0,
    disable: bool = False,
    show_bar: bool = True,
    show_progress: bool = False,
    show_speed: bool = True,
    show_remaining: bool = False,
    show_elapsed: bool = True,
    show_count: bool = True,
    leave: bool = True,
) -> Iterable[ProgressType]:
    """Track progress by iterating over a sequence with a nested progress bar.

    Args:
        sequence (Iterable[ProgressType]): A sequence (must support "len") you wish to iterate over.
        description (str, optional): Description of task show next to progress bar. Defaults to "Working".
        total: (int, optional): Total number of steps. Default is len(sequence).
        completed (int, optional): Number of steps completed so far. Defaults to 0.
        auto_refresh (bool, optional): Automatic refresh, disable to force a refresh after each iteration. Default is True.
        transient: (bool, optional): Clear the progress on exit. Defaults to False.
        console (Console, optional): Console to write to. Default creates internal Console instance.
        refresh_per_second (float): Number of times per second to refresh the progress information. Defaults to 10.
        style (StyleType, optional): Style for the bar background. Defaults to "bar.back".
        complete_style (StyleType, optional): Style for the completed bar. Defaults to "bar.complete".
        finished_style (StyleType, optional): Style for a finished bar. Defaults to "bar.finished".
        pulse_style (StyleType, optional): Style for pulsing bars. Defaults to "bar.pulse".
        update_period (float, optional): Minimum time (in seconds) between calls to update(). Defaults to 0.0.
        disable (bool, optional): Disable display of progress.
        show_bar (bool, optional): Show the bar if total is known. Defaults to True.
        show_progress (bool, optional): Show progress bar if total is known. Defaults to False.
        show_speed (bool, optional): Show speed if total isn't known. Defaults to True.
        show_remaining (bool, optional): Show remaining time if total isn't known. Defaults to False.
        show_elapsed (bool, optional): Show elapsed time if total isn't known. Defaults to True.
        show_count (bool, optional): Show count of completed/total items. Defaults to True.
        leave (bool, optional): Leave finished tasks for cleaner display. Defaults to True.
    Returns:
        Iterable[ProgressType]: An iterable of the values in the sequence.

    """
    if disable:
        yield from sequence
        return

    columns = [
        *(
            [TextColumn("[progress.description]{task.description}")]
            if description
            else []
        ),
        *(
            [
                BarColumn(
                    style=style,
                    complete_style=complete_style,
                    finished_style=finished_style,
                    pulse_style=pulse_style,
                )
            ]
            if show_bar
            else []
        ),
        *(["•", TaskProgressColumn(show_speed=show_speed)] if show_progress else []),
        *(["•", TimeRemainingColumn()] if show_remaining else []),
        *(["•", TimeElapsedColumn()] if show_elapsed else []),
        *(["•", MofNCompleteColumn()] if show_count else []),
        *(["•", IterationSpeedColumn()] if show_speed else []),
    ]

    Progress._suppress_warnings = True
    try:
        with Progress(
            *columns,
            auto_refresh=auto_refresh,
            console=console,
            transient=transient,
            get_time=get_time,
            refresh_per_second=refresh_per_second or 10,
            disable=disable,
        ) as progress:
            task_id = progress.add_task(description, total=total, completed=completed)
            try:
                if total is None:
                    try:
                        if hasattr(sequence, "__len__"):
                            total = len(sequence)
                            progress.update(task_id, total=total)
                    except (TypeError, AttributeError):
                        pass

                advance_count = 0
                total_processed = 0
                last_update_time = time.time() if update_period > 0 else 0

                for item in sequence:
                    yield item
                    total_processed += 1

                    if update_period > 0:
                        advance_count += 1
                        current_time = time.time()
                        if current_time - last_update_time >= update_period:
                            progress.advance(task_id, advance_count)
                            advance_count = 0
                            last_update_time = current_time
                    else:
                        progress.advance(task_id, 1)

                if advance_count > 0:
                    progress.advance(task_id, advance_count)

                if total is not None:
                    progress.update(task_id, completed=total)
                elif total_processed > 0:
                    progress.update(
                        task_id, total=total_processed, completed=total_processed
                    )

                if hasattr(progress, "refresh"):
                    progress.refresh()

            finally:
                if not leave and task_id in progress.task_ids:
                    progress.remove_task(task_id)
    finally:
        Progress._suppress_warnings = False
