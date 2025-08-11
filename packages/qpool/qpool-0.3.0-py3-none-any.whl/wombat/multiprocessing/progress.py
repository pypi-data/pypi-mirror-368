from __future__ import annotations
from typing import Optional, Union, Tuple
from wombat.utils.errors.decorators import enforce_type_hints_contracts
from rich.table import Column
from rich.text import Text
from rich import get_console
from rich.progress import (
    Progress,
    TaskID,
    ProgressColumn,
    Task as RichTask,
    SpinnerColumn,
    BarColumn,
    TimeElapsedColumn,
)
from wombat.multiprocessing.models import ProgressUpdate
from wombat.multiprocessing.queues import ModelQueue
from wombat.utils.dictionary import deep_merge
from multiprocessing import Value
import time
from queue import Empty


def tasks_per_second_from_task(task: RichTask, precision: int):
    # Extract ProgressUpdate from task.fields
    if not task or (not task.elapsed) or (task.elapsed == 0):
        return None

    return round(
        0 if task.completed == 0 else (task.completed / task.elapsed),
        precision,
    )


class TimeRemainingColumn(ProgressColumn):
    """Renders estimated time remaining."""

    max_refresh = 0.5

    @enforce_type_hints_contracts
    def __init__(self, compact: bool = False, table_column: Optional[Column] = None):
        self.compact = compact
        super().__init__(table_column=table_column)

    @enforce_type_hints_contracts
    def render(self, task: RichTask) -> Text:
        """Show time remaining."""
        style = "progress.remaining"

        if (
            not task
            or not task.total
            or task.total == 0
            or not task.completed
            or task.completed == 0
            or not task.elapsed
            or task.elapsed == 0
        ):
            return Text("--:--" if self.compact else "-:--:--", style=style)

        tasks_per_second: float | None = tasks_per_second_from_task(task, 2)

        if not tasks_per_second:
            return Text("--:--" if self.compact else "-:--:--", style=style)

        remaining_tasks: int = int(task.total - task.completed)

        estimated_time_remaining = remaining_tasks / tasks_per_second
        minutes, seconds = divmod(round(estimated_time_remaining), 60)
        hours, minutes = divmod(minutes, 60)

        if self.compact and not hours:
            formatted = f"{minutes:02d}:{seconds:02d}"
        else:
            formatted = f"{hours:d}:{minutes:02d}:{seconds:02d}"

        return Text(formatted, style=style)


class ItemsPerMinuteColumn(ProgressColumn):
    """Renders tasks per minute."""

    max_refresh = 0.5

    def __init__(self, precision: int = 2, table_column: Optional[Column] = None):
        super().__init__(table_column=table_column)
        self.precision = precision

    def render(self, task: RichTask) -> Text:
        """Show tasks per minute."""
        style = "progress.remaining"

        if not task or (not task.elapsed) or (task.elapsed == 0):
            return Text("?/m", style=style)

        tasks_per_second = tasks_per_second_from_task(task, self.precision)
        if tasks_per_second is None:
            return Text("?/m", style=style)

        tasks_per_minute = tasks_per_second * 60
        return Text(f"{tasks_per_minute:.2f}/m", style=style)


def create_progress_bars(num_bars) -> Tuple[Progress, TaskID]:
    console = get_console()
    progress_bar = Progress(
        SpinnerColumn(),
        "{task.fields[status]}...",
        BarColumn(),
        "{task.completed} of {task.total}",
        "[red]❌: {task.fields[failures]}",
        "[yellow]🔃: {task.fields[retries]}",
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        ItemsPerMinuteColumn(),
        console=console,
        auto_refresh=True,
    )
    tasks = []
    for bar in range(num_bars):
        tasks.append(
            progress_bar.add_task(
                description=f"Worker-{bar}",
                start=True,
                total=0,
                completed=0,
                visible=True,
                status="Starting...",
                failures=0,
                retries=0,
            )
        )
    return progress_bar, tasks


@enforce_type_hints_contracts
def add(a: Union[int, float], b: Union[int, float, None]) -> Union[int, float]:
    if b is None:
        return a
    return a + b


def merge_progress(progress: ProgressUpdate, update: ProgressUpdate) -> ProgressUpdate:
    strategies = {
        k: add if isinstance(v, (int, float)) and k != "task_id" else "override"
        for k, v in progress
    }
    return ProgressUpdate.model_validate(
        obj=deep_merge(
            progress.model_dump(),
            update.model_dump(exclude_none=True),
            strategies=strategies,
        )
    )


def run_progress(
    queue: ModelQueue,
    num_bars: int,
    total_progress_tasks: Value,
    remaining_progress_tasks: Value,
):
    progress_bar, task_ids = create_progress_bars(num_bars=num_bars)
    processed_tasks: int = 0
    total_task_id = progress_bar.add_task(
        description="Total",
        start=True,
        total=0,
        completed=0,
        visible=True,
        status="Starting...",
        failures=0,
        retries=0,
    )
    progress_data = {
        **{task_id: ProgressUpdate(task_id=task_id) for task_id in task_ids},
        total_task_id: ProgressUpdate(task_id=-1, status="Starting..."),
    }

    try:
        progress_bar.start()
        while True:
            try:
                update_task = queue.get(block=True, timeout=0.1)
                queue.task_done()

                progress_update: Optional[ProgressUpdate] = update_task.kwargs.get(
                    "update"
                )
                if not progress_update:
                    continue

                processed_tasks += 1
                with (
                    remaining_progress_tasks.get_lock(),
                    total_progress_tasks.get_lock(),
                ):
                    remaining_progress_tasks.value = (
                        total_progress_tasks.value - processed_tasks
                    )
                    # Sentinel check to close the progress bar
                    if (
                        progress_update.total == -1
                        and remaining_progress_tasks.value <= 0
                    ):
                        break

                # Determine which progress bar(s) to update
                task_id_to_update = (
                    progress_update.task_id
                    if progress_update.task_id != -1
                    else total_task_id
                )

                # Update the specific worker bar (or the total bar if task_id is -1)
                if task_id_to_update in progress_data:
                    current_progress = progress_data[task_id_to_update]
                    progress_data[task_id_to_update] = merge_progress(
                        current_progress, progress_update
                    )

                    # Update Rich progress bar for the specific task
                    p = progress_data[task_id_to_update]
                    progress_bar.update(
                        task_id_to_update,
                        total=p.total,
                        completed=p.completed,
                        status=p.status,
                        failures=p.failures,
                        retries=p.retries,
                    )

                # **FIX**: Always aggregate worker updates into the total progress bar using cleaner logic.
                if progress_update.task_id != -1:
                    total_p = progress_data[total_task_id]
                    update_dump = progress_update.model_dump(exclude_defaults=True)

                    total_p.completed += update_dump.get("completed", 0)
                    total_p.failures += update_dump.get("failures", 0)
                    total_p.retries += update_dump.get("retries", 0)
                    total_p.total += update_dump.get("total", 0)

                    # Update Rich progress bar for the total
                    progress_bar.update(
                        total_task_id,
                        total=total_p.total,
                        completed=total_p.completed,
                        failures=total_p.failures,
                        retries=total_p.retries,
                    )

            except Empty:
                continue  # Wait for more updates
            except (OSError, ValueError):
                # These can happen during shutdown, it's safe to exit.
                break
    finally:
        progress_bar.refresh()
        progress_bar.stop()
