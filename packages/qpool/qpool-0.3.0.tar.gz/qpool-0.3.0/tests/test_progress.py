from __future__ import annotations

import pytest
import pytest_check as check
from rich.progress import Task as RichTask
from rich.text import Text

from wombat.multiprocessing.models import ProgressUpdate
from wombat.multiprocessing.progress import (
    TimeRemainingColumn,
    ItemsPerMinuteColumn,
    merge_progress,
    tasks_per_second_from_task,
)


# Helper to create mock rich.progress.Task objects
def create_mock_rich_task(
    completed: int = 0, total: int = 100, elapsed: float | None = 0.0
) -> RichTask:
    return RichTask(
        id=1,
        description="test",
        total=total,
        completed=completed,
        visible=True,
        fields={},
        _get_time=lambda: 0.0,
        start_time=0.0,
        finished_time=None,
        elapsed=elapsed,
    )


def test_tasks_per_second_from_task():
    task = create_mock_rich_task(completed=50, elapsed=10.0)
    check.equal(tasks_per_second_from_task(task, 2), 5.0)

    task_no_elapsed = create_mock_rich_task(completed=50, elapsed=0.0)
    check.is_none(tasks_per_second_from_task(task_no_elapsed, 2))

    task_no_completed = create_mock_rich_task(completed=0, elapsed=10.0)
    check.is_none(tasks_per_second_from_task(task_no_completed, 2))


def test_time_remaining_column():
    column = TimeRemainingColumn()
    task = create_mock_rich_task(completed=50, total=100, elapsed=10.0)  # 5 tasks/sec
    # 50 remaining tasks at 5 tasks/sec = 10 seconds
    check.equal(column.render(task), Text("0:00:10", style="progress.remaining"))

    # Test compact view
    column_compact = TimeRemainingColumn(compact=True)
    check.equal(column_compact.render(task), Text("00:10", style="progress.remaining"))

    # Test edge case with no progress
    task_no_progress = create_mock_rich_task(completed=0, elapsed=10.0)
    check.equal(
        column.render(task_no_progress), Text("-:--:--", style="progress.remaining")
    )


def test_items_per_minute_column():
    column = ItemsPerMinuteColumn()
    task = create_mock_rich_task(completed=50, elapsed=10.0)  # 5 tasks/sec
    # 5 tasks/sec * 60 = 300 tasks/min
    check.equal(column.render(task), Text("300.00/m", style="progress.remaining"))

    # Test edge case with no progress
    task_no_progress = create_mock_rich_task(completed=0, elapsed=10.0)
    check.equal(column.render(task_no_progress), Text("?/m", style="progress.remaining"))


def test_merge_progress():
    p1 = ProgressUpdate(task_id=1, total=10, completed=5, failures=1, retries=2)
    p2 = ProgressUpdate(
        task_id=1, total=5, completed=3, failures=1, retries=1, status="new"
    )

    merged = merge_progress(p1, p2)
    check.equal(merged.task_id, 1)  # overridden
    check.equal(merged.status, "new")  # overridden
    check.equal(merged.total, 15)  # added
    check.equal(merged.completed, 8)  # added
    check.equal(merged.failures, 2)  # added
    check.equal(merged.retries, 3)  # added
