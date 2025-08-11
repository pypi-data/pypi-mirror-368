from __future__ import annotations
from typing import List, Union, Optional, TypeVar, Generic, Type, Callable
from pydantic import BaseModel
from queue import Empty
from multiprocessing import Queue, JoinableQueue
from wombat.utils.errors.decorators import enforce_type_hints_contracts
from wombat.multiprocessing.models import ResultTaskPair
from multiprocessing.context import BaseContext
from wombat.multiprocessing.tasks import (
    EOQ,
    LogTask,
    ProgressTask,
    Task,
    ControlTask,
    Loggable,
)
import time

T = TypeVar("T", bound=BaseModel)


def explicitly_is(item: BaseModel, models: List[Type[BaseModel]]) -> bool:
    return any([item.__class__ == model for model in models])


def implicitly_is(item: BaseModel, models: List[Type[BaseModel]]) -> bool:
    return any([isinstance(item, model) for model in models])


class ModelQueue:
    name: str
    joinable: bool = False
    queue: Union[JoinableQueue, Queue]
    models: List[Type[BaseModel]]
    validator: Callable[[BaseModel, List[Type[BaseModel]]], bool]
    context: BaseContext

    def __init__(
        self,
        context: BaseContext,
        name: str,
        models: List[Type[BaseModel]],
        joinable: bool = False,
        validator: Optional[
            Callable[[BaseModel, List[Type[BaseModel]]], bool]
        ] = explicitly_is,
    ):
        self.context = context
        self.name = name
        self.joinable = joinable
        self.validator = validator
        self.models = models
        self.queue = self.context.JoinableQueue() if joinable else self.context.Queue()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.join()

    def put(self, item: T, block: bool = True, timeout: Optional[float] = None) -> bool:
        if not self.validator(item, self.models):
            return False
        try:
            self.queue.put(item, block=block, timeout=timeout)
            return True
        except Exception:
            return False

    def get(self, block: bool = True, timeout: Optional[float] = None) -> Optional[T]:
        return self.queue.get(block, timeout)

    def task_done(self):
        if not self.joinable:
            return
        self.queue.task_done()

    def join(self):
        if self.joinable:
            self.queue.join()
        else:
            self.queue.join_thread()

    def empty(self):
        return self.queue.empty()

    def full(self):
        return self.queue.full()

    def get_nowait(self):
        return self.queue.get_nowait()

    def put_nowait(self, obj):
        return self.queue.put_nowait(obj)

    def close(self):
        return self.queue.close()


def log_task(
    task: Loggable,
    message: str,
    queue: Optional[ModelQueue] = None,
    level: Optional[int] = None,
):
    """Log a message to the provided queue.

    Args:
        queue (ModelQueue): The queue to log to
        message (str): The message to log
        level (int, optional): The level suggested at the point of logging. If not set the tasks log_level will be used. Defaults to None.
    """
    if not queue:
        return
    task_is_loggable = isinstance(task, Loggable)
    if not task_is_loggable:
        return
    log_level = level if level else task.log_level
    log_task = LogTask(
        kwargs={
            "message": message,
            "level": log_level,
        },
    )
    queue.put(log_task)


@enforce_type_hints_contracts
def TaskQueue(
    context: BaseContext,
    name: str,
    joinable: bool = True,
    models: List[Type[Task]] = None,
) -> ModelQueue:
    models = models or [Task]
    return ModelQueue(context=context, name=name, models=models, joinable=joinable)


@enforce_type_hints_contracts
def ProgressQueue(
    context: BaseContext, name: str, joinable: bool = True, validator=explicitly_is
) -> ModelQueue:
    return ModelQueue(
        context=context,
        name=name,
        models=[ProgressTask],
        joinable=joinable,
        validator=validator,
    )


@enforce_type_hints_contracts
def ControlQueue(
    context: BaseContext, name: str, joinable: bool = True, validator=implicitly_is
) -> ModelQueue:
    return ModelQueue(
        context=context,
        name=name,
        models=[ControlTask],
        joinable=joinable,
        validator=validator,
    )


@enforce_type_hints_contracts
def ResultQueue(context: BaseContext, name: str, joinable: bool = False) -> ModelQueue:
    return ModelQueue(
        context=context, name=name, models=[ResultTaskPair], joinable=joinable
    )


@enforce_type_hints_contracts
def LogQueue(context: BaseContext, name: str, joinable: bool = True) -> ModelQueue:
    return ModelQueue(context=context, name=name, models=[LogTask], joinable=joinable)


@enforce_type_hints_contracts
def drain_queue_non_blocking(model_queue: ModelQueue) -> List[BaseModel]:
    """Drains a queue of all currently available items, without blocking."""
    results = []
    while True:
        try:
            result: ResultTaskPair = model_queue.get(block=False)
            model_queue.task_done()
            results.append(result)
        except Empty:
            break  # The queue is empty, so we're done.
    return results


@enforce_type_hints_contracts
def drain_queue(model_queue: ModelQueue) -> List[BaseModel]:
    """Drains a queue until an EOQ sentinel is found."""
    results = []
    while True:
        # Block until an item is available. This is more efficient than polling.
        # An EOQ sentinel is guaranteed to be put on the queue, so this will not hang.
        result: ResultTaskPair = model_queue.get(block=True)
        model_queue.task_done()
        if isinstance(result.task, EOQ):
            break
        results.append(result)
    return results
