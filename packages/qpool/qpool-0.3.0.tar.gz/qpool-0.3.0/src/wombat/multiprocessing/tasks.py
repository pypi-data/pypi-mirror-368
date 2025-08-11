from __future__ import annotations
from typing import List, Dict, Literal
from wombat.multiprocessing.models import (
    Identifiable,
    MixedActionable,
    RequiresProps,
    ProgressUpdate,
    Progresses,
    Retryable,
    Lifecycle,
    TaskState,
    Loggable,
    Sentinel,
)


class Task(Identifiable, Progresses, Loggable, Lifecycle, MixedActionable):
    pass


class RetryableTask(Task, Retryable):
    pass


class ControlTask(Task):
    pass


class ExitTask(ControlTask):
    action: str = "exit"


class LogTask(Identifiable, MixedActionable, RequiresProps):
    action: str = "log"
    requires_props: List[str] = ["logger"]


class ProgressTask(Identifiable, MixedActionable, RequiresProps):
    action: str = "progress"
    requires_props: List[str] = ["process", "progress_bar", "progress"]
    kwargs: Dict[Literal["update"], ProgressUpdate] = {
        "update": ProgressUpdate(
            task_id=-1,
            total=0,
            completed=0,
            elapsed=0.0,
            remaining=0.0,
            failures=0,
            retries=0,
            status="created",
        )
    }


class EOQ(Sentinel):
    sentinel: str = "EOQ"


def set_task_status(task: Lifecycle, status: TaskState):
    task_has_lifecycle = isinstance(task, Lifecycle)
    if task_has_lifecycle:
        task.status = status
