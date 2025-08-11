# File: src/wombat/multiprocessing/worker.py
from __future__ import annotations

"""
Worker process for qpool.

Adds structured retry tracing at DEBUG level so we can see:
- when a task fails,
- before/after calling attempt(),
- scheduling into retry heap (with backoff),
- popping from retry heap to execute a retry,
- status and tries after each transition.

No functional behavior changes; only diagnostics are added.
"""

import asyncio
from uuid import uuid4
from collections import deque
from typing import Any, Optional, Dict, Callable
import heapq
from pydantic import UUID4
from multiprocessing import Value

from contextlib import AsyncExitStack
from queue import Empty
from enum import Enum
import inspect
from wombat.utils.dictionary import deep_merge
import logging
import time
from traceback import format_exc

from wombat.multiprocessing.models import (
    Identifiable,
    KeywordActionable,
    PositionalActionable,
    MixedActionable,
    RequiresProps,
    ProgressUpdate,
    Progresses,
    Retryable,
    Lifecycle,
    Actionable,
    TaskState,
    Evaluatable,
    ResultTaskPair,
    Prop,
)
from wombat.multiprocessing.tasks import (
    LogTask,
    ProgressTask,
    ControlTask,
    ExitTask,
    EOQ,
    set_task_status,
)
from wombat.multiprocessing.queues import ModelQueue, log_task
from wombat.multiprocessing.progress import add
from wombat.multiprocessing.utilities import (
    is_async_context_manager,
    is_sync_context_manager,
)


class WorkerStatus(Enum):
    CREATED = 0
    RUNNING = 1
    SLEEPING = 2
    STOPPED = 3
    PAUSED = 4


class Worker:
    def __init__(
        self,
        context: Any,
        actions: Dict[str, Callable],
        control_queues: Dict[str, ModelQueue],
        task_queue: ModelQueue,
        status: Value,
        total_progress_tasks: Optional[Value] = None,
        log_queue: Optional[ModelQueue] = None,
        result_queue: Optional[ModelQueue] = None,
        progress_queue: Optional[ModelQueue] = None,
        props: Optional[Prop] = None,
        name: Optional[str] = None,
        task_id: Optional[int] = -1,
        id: Optional[UUID4] = None,
        get_time: Callable[[], float] = time.monotonic,
        tasks_per_minute_limit: Optional[int] = None,
    ) -> None:
        self.context = context
        self.total_progress_tasks = total_progress_tasks
        self.finished_tasks = self.context.Value("i", 0)
        self.total_tasks = self.context.Value("i", 0)
        self.last_update = None
        self.get_time = get_time
        self.task_timestamps = deque()
        self.tasks_per_minute_limit = tasks_per_minute_limit
        self.start_time = get_time()
        self.id = id if id else uuid4()
        self.name = name if name else f"Worker-{self.id}"
        self.task_id = task_id
        self.control_queues = control_queues
        self.task_queue = task_queue
        self.log_queue = log_queue
        self.result_queue = result_queue
        self.retries = []  # heap of (ready_at, task)
        self.progress = ProgressUpdate(task_id=self.task_id)
        self.progress_delta = ProgressUpdate(task_id=self.task_id)
        self.progress_queue = progress_queue
        self.is_retrying = False
        self.actions = actions

        self.props = props
        self.status = status

        try:
            self._process = self.context.Process(
                target=self.start_event_loop,
                kwargs={"actions": self.actions, "props": self.props},
                name=self.name,
            )
            if not self._process.is_alive():
                self.log(f"Worker {self.name} prepared for start", logging.DEBUG)
        except Exception:
            self.log(
                f"Worker {self.name} failed to initialize: \n{format_exc()}",
                logging.ERROR,
            )

    # ---------------------------
    # Debug / tracing utilities
    # ---------------------------

    def _trace_retry(self, task: Any, phase: str, extra: Dict[str, Any] | None = None):
        """Emit a structured DEBUG line for retry diagnostics."""
        try:
            tid = getattr(task, "id", "<no-id>")
            tries = getattr(task, "tries", "<na>")
            status = getattr(task, "status", "<na>")
            payload = {
                "phase": phase,
                "task_id": str(tid),
                "tries": tries,
                "status": str(status),
            }
            if extra:
                payload.update(extra)
            self.log(f"RETRY_TRACE {payload}", logging.DEBUG)
        except Exception:
            # Never let tracing break execution.
            pass

    # ---------------------------
    # Progress & Logging helpers
    # ---------------------------

    def update_progress(self, force_update: bool = False):
        update = self.progress_delta.model_dump(exclude_unset=True)
        if self.progress_queue and (
            force_update
            or self.last_update is None
            or self.get_time() - self.last_update > 1
        ):
            self.last_update = self.get_time()
            merged = deep_merge(
                self.progress.model_dump(),
                update,
                strategies={
                    k: add if isinstance(v, (int, float)) else "override"
                    for k, v in self.progress
                },
            )
            self.progress = ProgressUpdate.parse_obj(merged)
            if self.total_progress_tasks:
                with self.total_progress_tasks.get_lock():
                    self.total_progress_tasks.value += 1
            self.progress_queue.put(
                ProgressTask(
                    kwargs={"update": self.progress_delta},
                )
            )
            self.progress_delta = ProgressUpdate(task_id=self.task_id)

    def log(self, message: str, level: int):
        if self.log_queue:
            self.log_queue.put(
                LogTask(action="log", kwargs={"message": message, "level": level})
            )

    # ---------------
    # Process control
    # ---------------

    def start(self):
        if not self._process.is_alive():
            self.log(f"Starting process for {self.name}", logging.DEBUG)
            self._process.start()
            with self.status.get_lock():
                self.status.value = WorkerStatus.RUNNING.value

    # -------------
    # Task execution
    # -------------

    async def execute_task(
        self, task: Actionable, func, props: Dict[str, Prop], is_async: bool
    ):
        task_is_identifiable = isinstance(task, Identifiable)
        task_has_lifecycle = isinstance(task, Lifecycle)
        task_provides_progress = isinstance(task, Progresses)

        # Capability-based detection for retries
        has_attempt = hasattr(task, "attempt")
        has_retry_fields = all(hasattr(task, attr) for attr in ("tries", "max_tries"))
        task_can_be_retried = (
            has_attempt or has_retry_fields or isinstance(task, Retryable)
        )

        task_requires_props = isinstance(task, RequiresProps)
        task_accepts_positional_args = isinstance(task, PositionalActionable)
        task_accepts_keyword_args = isinstance(task, KeywordActionable)
        task_accepts_mixed_args = isinstance(task, MixedActionable)
        task_can_be_evaluated_for_success = isinstance(task, Evaluatable)

        last_exception = None
        result_data = None
        try:
            if task_is_identifiable:
                log_task(
                    queue=self.log_queue,
                    task=task,
                    message=f"Executing task: {task.id}",
                    level=logging.INFO,
                )

            args = task.args if isinstance(task, PositionalActionable) else []
            kwargs = task.kwargs if isinstance(task, KeywordActionable) else {}

            if task_requires_props:
                if task_accepts_keyword_args or task_accepts_mixed_args:
                    kwargs["props"] = task.filter_props(props=props)
                elif task_accepts_positional_args:
                    args.append(task.filter_props(props=props))

            if is_async:
                coroutine = func(self, *args, **kwargs)
                result_data = await coroutine
            else:
                result_data = func(self, *args, **kwargs)

            success = (
                task.evaluate(result_data)
                if task_can_be_evaluated_for_success
                else True
            )

            if not success:
                set_task_status(task, TaskState.fail)
            else:
                set_task_status(task, TaskState.success)

        except Exception:
            last_exception = format_exc()
            set_task_status(task, TaskState.fail)
            log_task(
                queue=self.log_queue,
                task=task,
                message=f"Error while executing task {task} with function {func}: {last_exception}",
                level=logging.ERROR,
            )
        finally:
            if task_has_lifecycle:
                if task.status == TaskState.success:
                    self.progress_delta.completed += 1
                    if self.result_queue:
                        self.result_queue.put(
                            ResultTaskPair(task=task, result=result_data)
                        )
                    with self.finished_tasks.get_lock():
                        self.finished_tasks.value += 1

                elif task.status == TaskState.fail:
                    if task_can_be_retried:
                        self._trace_retry(task, "fail_before_attempt")

                        if has_attempt:
                            try:
                                self._trace_retry(task, "attempt_call_before")
                                task.attempt()  # type: ignore[attr-defined]
                                self._trace_retry(task, "attempt_call_after")
                            except Exception as e:
                                self._trace_retry(
                                    task, "attempt_call_error", {"error": repr(e)}
                                )
                                # If `attempt()` fails, it is a permanent failure.
                                set_task_status(task, TaskState.fail)
                        else:
                            # If a task is retryable but has no `attempt` method,
                            # it's a permanent failure.
                            set_task_status(task, TaskState.fail)

                        if getattr(task, "status", None) == TaskState.retry:
                            # Compute backoff (best-effort)
                            backoff_delay = 0.0
                            if hasattr(task, "backoff"):
                                try:
                                    backoff_delay = float(task.backoff())  # type: ignore[attr-defined]
                                except Exception:
                                    backoff_delay = 0.0

                            ready_at = self.get_time() + backoff_delay
                            self._trace_retry(
                                task,
                                "schedule_retry",
                                {"backoff": backoff_delay, "ready_at": ready_at},
                            )
                            self.progress_delta.retries += 1
                            heapq.heappush(self.retries, (ready_at, task))
                        else:
                            self._trace_retry(task, "permanent_fail")
                            self.progress_delta.failures += 1
                            if self.result_queue:
                                self.result_queue.put(
                                    ResultTaskPair(
                                        task=task, result=[last_exception, result_data]
                                    )
                                )
                            with self.finished_tasks.get_lock():
                                self.finished_tasks.value += 1
                    else:
                        self.progress_delta.failures += 1
                        if self.result_queue:
                            self.result_queue.put(
                                ResultTaskPair(
                                    task=task, result=[last_exception, result_data]
                                )
                            )
                        with self.finished_tasks.get_lock():
                            self.finished_tasks.value += 1

                if task_provides_progress:
                    self.update_progress()

    # ----------------------
    # Event loop & run logic
    # ----------------------

    def start_event_loop(self, actions: Dict[str, Callable], props: Dict[str, Any]):
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.log(
                f"Starting event loop for {self.name}:{self._process.pid}",
                logging.CRITICAL,
            )
            self.loop.run_until_complete(self.run(actions, props=props))
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    async def enforce_rate_limit(self):
        if self.tasks_per_minute_limit is None:
            return

        with self.tasks_per_minute_limit.get_lock():
            limit = self.tasks_per_minute_limit.value
        if limit <= 0:
            return

        interval = 60.0 / limit
        now = self.get_time()

        if self.task_timestamps:
            time_since_last = now - self.task_timestamps[-1]
            if time_since_last < interval:
                wait_time = interval - time_since_last
                self.log(
                    f"Worker {self.name} is rate-limited, sleeping for {wait_time:.2f} seconds",
                    logging.DEBUG,
                )
                await asyncio.sleep(wait_time)

        # Prune old timestamps to prevent the deque from growing indefinitely.
        one_minute_ago = now - 60
        while self.task_timestamps and self.task_timestamps[0] < one_minute_ago:
            self.task_timestamps.popleft()

    async def initialize_prop(
        self, props: Dict[str, Prop], prop_name: str, reinitialize: bool = False
    ):
        try:
            prop = props[prop_name]
            initializer = prop.initializer
            resolved_value = prop.instance if not reinitialize else None
            exit_stack = prop.exit_stack if not reinitialize else AsyncExitStack()
            if exit_stack is None and prop.use_context_manager:
                exit_stack = AsyncExitStack()
            if resolved_value is None:
                if asyncio.iscoroutinefunction(initializer):
                    resolved_value = await initializer()
                elif callable(initializer):
                    resolved_value = initializer()
                else:
                    resolved_value = initializer
            if prop.use_context_manager and resolved_value:
                prop_is_async_cm = is_async_context_manager(resolved_value)
                prop_is_sync_cm = (
                    is_sync_context_manager(resolved_value)
                    if not prop_is_async_cm
                    else False
                )
                if prop_is_async_cm:
                    await exit_stack.enter_async_context(resolved_value)
                elif prop_is_sync_cm:
                    exit_stack.enter_context(resolved_value)
            props[prop_name] = Prop(
                initializer=initializer,
                instance=resolved_value,
                use_context_manager=prop.use_context_manager,
                exit_stack=exit_stack,
            )
        except Exception as e:
            self.log(
                f"Worker {self.name} failed to initialize prop {prop_name}: {e}\n{format_exc()}",
                logging.ERROR,
            )
            return e

    async def run(self, actions: Dict[str, Callable], props: Dict[str, Prop]):
        self.props = props if props is not None else {}
        to_gather = [
            self.initialize_prop(self.props, prop_name) for prop_name in props.keys()
        ]
        await asyncio.gather(*to_gather)
        try:
            self.log(f"Worker {self.name} is running", logging.INFO)
            with self.status.get_lock():
                self.status.value = WorkerStatus.RUNNING.value
            self.progress_delta.status = f"Starting {self.name}"
            while True:
                self.is_retrying = False
                task = None
                if self.retries and self.retries[0][0] <= self.get_time():
                    self.is_retrying = True
                    ready_at, task = heapq.heappop(self.retries)
                    self._trace_retry(task, "pop_retry_heap", {"ready_at": ready_at})

                if task is None:
                    for queue in self.control_queues.values():
                        try:
                            control_task: Optional[ControlTask] = queue.get_nowait()
                            queue.task_done()
                            if isinstance(control_task, ExitTask):
                                self.log(
                                    f"Received exit task in worker {self.name}",
                                    logging.INFO,
                                )
                                return
                            else:
                                queue.put(control_task)
                        except Empty:
                            pass
                if task is None:
                    try:
                        task = self.task_queue.get(block=False)
                        if task:
                            with self.total_tasks.get_lock():
                                self.total_tasks.value += 1
                            self.task_queue.task_done()
                    except Empty:
                        pass
                if task:
                    with self.status.get_lock():
                        self.status.value = WorkerStatus.RUNNING.value
                    await self.enforce_rate_limit()
                    if isinstance(task, Actionable):
                        set_task_status(task, TaskState.attempt)
                        func = self.actions.get(task.action)
                        if func:
                            await self.execute_task(
                                task=task,
                                func=func,
                                props=self.props,
                                is_async=inspect.iscoroutinefunction(func),
                            )
                        else:
                            self.log(
                                f"No action '{task.action}' found for task {task.id}",
                                logging.ERROR,
                            )
                        self.task_timestamps.append(self.get_time())
                else:
                    with self.status.get_lock():
                        self.status.value = WorkerStatus.SLEEPING.value
                    await asyncio.sleep(0.1)
        except Exception as e:
            self.log(
                f"Worker {self.name} encountered a fatal exception: {e}\n{format_exc()}",
                logging.ERROR,
            )
        finally:
            with self.status.get_lock():
                self.status.value = WorkerStatus.STOPPED.value
            if self.progress_queue:
                self.progress_delta.status = f"Stopping worker {self.name}"
                self.update_progress(force_update=True)
            for prop in self.props.values():
                if prop.use_context_manager and prop.exit_stack:
                    await prop.exit_stack.aclose()
            if self.result_queue:
                # Signal that this worker is done sending results. This is more reliable
                # than the orchestrator doing it, as it avoids race conditions.
                self.result_queue.put(ResultTaskPair(task=EOQ(), result=None))
