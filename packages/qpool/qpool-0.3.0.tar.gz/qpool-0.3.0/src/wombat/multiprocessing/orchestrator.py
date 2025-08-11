# region Imports [ rgba(0,0,0,0.5) ]
from __future__ import annotations
from uuid import uuid4
from annotated_types import Ge
from typing import (
    List,
    Any,
    Optional,
    Dict,
    Type,
    Callable,
    Annotated,
)
from multiprocessing import get_context

from threading import Thread
from wombat.multiprocessing.log import setup_logging, log
from wombat.utils.errors.decorators import enforce_type_hints_contracts
import logging
import time

from wombat.multiprocessing.models import (
    ProgressUpdate,
    Actionable,
    TaskState,
    ResultTaskPair,
    UninitializedProp,
)
from wombat.multiprocessing.tasks import (
    LogTask,
    ProgressTask,
    Task,
    ExitTask,
    EOQ,
    set_task_status,
)
from wombat.multiprocessing.queues import (
    drain_queue,
    drain_queue_non_blocking,
    TaskQueue,
    LogQueue,
    ResultQueue,
    ControlQueue,
    ProgressQueue,
)
from wombat.multiprocessing.progress import run_progress
from wombat.multiprocessing.worker import Worker, WorkerStatus
from typing import Generator
# endregion


class Orchestrator:
    @enforce_type_hints_contracts
    def __init__(
        self,
        num_workers: Annotated[int, Ge(0)],
        actions: Dict[str, Callable],
        props: Optional[Dict[str, Any]] = None,
        show_progress: bool = False,
        task_models: List[Type[Task]] | None = None,
        tasks_per_minute_limit: Optional[int] = None,
    ):
        task_models = (
            task_models if task_models is not None and len(task_models) > 0 else [Task]
        )
        self.context = get_context("spawn")
        self.tasks_per_minute_limit = (
            self.context.Value("i", tasks_per_minute_limit // num_workers)
            if tasks_per_minute_limit
            else None
        )

        self._results_buffer: List[ResultTaskPair] = []
        self.total_progress_tasks = self.context.Value("i", 0)
        self.total_tasks = 0
        self.props = props if props is not None else {}
        self.started = False
        self.task_queue = TaskQueue(
            context=self.context, name="tasks", models=task_models, joinable=True
        )
        self.log_queue = LogQueue(context=self.context, name="log", joinable=True)
        self.result_queues = {}
        logger_id = uuid4()
        control_queue_name = f"control-{logger_id}"
        self.logger_control_queues = {
            f"{control_queue_name}": ControlQueue(
                context=self.context,
                name=f"{control_queue_name}",
                joinable=True,
            )
        }
        self.worker_control_queues = {}
        self.workers = []
        self.show_progress = show_progress
        self.progress_thread = None
        self.progress_queue = None
        if show_progress:
            self.progress_queue = ProgressQueue(
                context=self.context, name="progress", joinable=True
            )
            self.total_progress_tasks = self.context.Value("i", 0)
            self.remaining_progress_tasks = self.context.Value("i", 0)

        self.worker_states = {
            f"logger-{logger_id}": self.context.Value("i", WorkerStatus.CREATED.value)
        }
        self.logger = Worker(
            context=self.context,
            name=f"logger-{logger_id}",
            id=uuid4(),
            status=self.worker_states[f"logger-{logger_id}"],
            total_progress_tasks=None,
            control_queues={"primary": self.logger_control_queues[control_queue_name]},
            task_queue=self.log_queue,
            actions={"log": log},
            props={
                "logger": UninitializedProp(
                    initializer=setup_logging, use_context_manager=False
                )
            },
        )
        for i in range(num_workers):
            worker_id = uuid4()
            worker_name = f"worker-{i}"
            control_queue_name = f"control-{worker_id}"
            self.worker_states[worker_name] = self.context.Value(
                "i", WorkerStatus.CREATED.value
            )
            self.worker_control_queues[control_queue_name] = ControlQueue(
                context=self.context, name=control_queue_name, joinable=True
            )
            self.result_queues[f"worker-{i}"] = ResultQueue(
                context=self.context, name=f"worker-{i}-results", joinable=False
            )
            self.workers.append(
                Worker(
                    context=self.context,
                    name=worker_name,
                    id=worker_id,
                    task_id=i,
                    control_queues={
                        "primary": self.worker_control_queues[control_queue_name]
                    },
                    status=self.worker_states[worker_name],
                    log_queue=self.log_queue,
                    task_queue=self.task_queue,
                    result_queue=self.result_queues[f"worker-{i}"],
                    progress_queue=self.progress_queue,
                    total_progress_tasks=self.total_progress_tasks,
                    actions=actions,
                    props=self.props,
                    tasks_per_minute_limit=self.tasks_per_minute_limit,
                )
            )

    @enforce_type_hints_contracts
    def update_progress(self, update: ProgressUpdate):
        with self.total_progress_tasks.get_lock():
            self.total_progress_tasks.value += 1
        if self.show_progress and self.progress_queue:
            self.progress_queue.put(
                ProgressTask(
                    kwargs={
                        "update": update,
                    }
                )
            )

    @enforce_type_hints_contracts
    def log(self, message: str, level: int):
        self.log_queue.put(
            LogTask(
                kwargs={
                    "message": message,
                    "level": level,
                }
            )
        )

    async def start_workers(self):
        """Starts workers and optionally monitors progress."""
        if self.started:
            return
        self.started = True
        self.logger.start()
        # Start workers
        self.log(
            message=f"Started logger with id {self.logger.id} and name {self.logger.name}",
            level=logging.DEBUG,
        )

        for worker in self.workers:
            worker.start()

        if self.show_progress:
            self.progress_thread = Thread(
                target=run_progress,
                args=(
                    self.progress_queue,
                    len(self.workers),
                    self.total_progress_tasks,
                    self.remaining_progress_tasks,
                ),
                daemon=True,
            )
            self.progress_thread.start()

    def _sum_worker_finished_tasks(self, workers: List[Worker]) -> int:
        total = 0
        for worker in workers:
            with worker.finished_tasks.get_lock():
                total += worker.finished_tasks.value
        return total

    def finish_tasks(self, timeout: Optional[float] = None):
        """
        Waits for all tasks submitted *at the time of calling* to complete.

        This method blocks until the number of finished tasks (succeeded or failed)
        matches the total task count recorded when the method was invoked. It does not
        prevent new tasks from being added concurrently, but it will not wait for them.
        This is useful for creating synchronization points in your workflow.

        Args:
            timeout (Optional[float]): If specified, the maximum time in seconds to
                wait. If the timeout is reached, the method will stop waiting and return.
        """
        tasks_to_finish = self.total_tasks
        total_finished_tasks = self._sum_worker_finished_tasks(self.workers)
        start_time = time.monotonic()

        # If all known tasks are already finished, we can return early.
        if tasks_to_finish <= total_finished_tasks:
            self.log(message="No pending tasks to finish.", level=logging.INFO)
        else:
            self.log(
                message=f"Finishing work for {tasks_to_finish} tasks.",
                level=logging.INFO,
            )
            self.update_progress(ProgressUpdate(task_id=-1, status="Finishing work"))

            # Loop until the number of finished tasks catches up to our snapshot.
            while tasks_to_finish > total_finished_tasks:
                if timeout and (time.monotonic() - start_time) > timeout:
                    self.log(
                        f"finish_tasks timed out after {timeout} seconds.",
                        level=logging.WARNING,
                    )
                    break
                # Drain results non-blockingly to prevent workers from deadlocking on full pipes.
                # These are stored in a buffer and collected later in stop_workers.
                for worker in self.workers:
                    self._results_buffer.extend(
                        drain_queue_non_blocking(worker.result_queue)
                    )

                self.log(
                    message=f"Waiting for results to be processed {total_finished_tasks}/{tasks_to_finish}",
                    level=logging.DEBUG,
                )
                time.sleep(0.1)
                total_finished_tasks = self._sum_worker_finished_tasks(self.workers)

        # One final drain to catch any stragglers that finished between the last
        # check and the loop exit.
        for worker in self.workers:
            self._results_buffer.extend(drain_queue_non_blocking(worker.result_queue))

        # The EOQ sentinel is now sent by each worker upon exit, which prevents a
        # race condition where results could be missed. This block is no longer needed.

    def _get_buffered_results(self) -> List[ResultTaskPair]:
        """Returns and clears the internal results buffer."""
        results = self._results_buffer
        self._results_buffer = []
        return results

    def get_results(
        self, block: bool = False
    ) -> Generator[ResultTaskPair, None, None]:
        """Drains and yields all results from the workers' result queues."""
        self.log(message="Getting results", level=logging.INFO)
        self.update_progress(ProgressUpdate(task_id=-1, status="Getting results"))

        # First, yield any results that were buffered during finish_tasks.
        yield from self._get_buffered_results()

        drain_function = drain_queue if block else drain_queue_non_blocking
        for worker in self.workers:
            self.log(
                message=f"Draining results from worker {worker.name}",
                level=logging.DEBUG,
            )
            yield from drain_function(worker.result_queue)

    def stop_workers(self) -> List[ResultTaskPair]:
        """Gracefully stops all workers, waits for tasks to finish, and collects results."""
        # **FIX**: Add a guard to prevent hanging if workers were never started.
        if not self.started:
            self.log(
                message="Orchestrator not started. No workers to stop.",
                level=logging.INFO,
            )
            return []

        self.log(
            message="Stopping workers and finishing all tasks.", level=logging.INFO
        )
        # Wait for tasks to finish, but with a timeout to prevent hanging indefinitely.
        # 10s is less than the test timeout of 15s, giving time for termination logic.
        self.finish_tasks(timeout=10.0)
        self.task_queue.close()
        self.task_queue.join()

        self.update_progress(ProgressUpdate(task_id=-1, status="Closing queues"))
        self.log(message="Closing worker control queues", level=logging.DEBUG)
        for control_queue in self.worker_control_queues.values():
            control_queue.put(ExitTask())
            control_queue.close()
            # Do not join the control queue, as a hanging worker will never call
            # task_done(), causing a deadlock. The process join timeout handles this.

        self.update_progress(ProgressUpdate(task_id=-1, status="Joining processes"))
        # Ensure all worker processes are properly terminated
        self.log(message="Joining worker processes", level=logging.INFO)
        results: List[ResultTaskPair] = self._get_buffered_results()
        for worker in self.workers:
            worker._process.join(timeout=5.0)  # Add a timeout for resilience
            if worker._process.is_alive():
                self.log(
                    f"Worker {worker.name} did not exit gracefully. Terminating.",
                    level=logging.WARNING,
                )
                worker._process.terminate()
                worker._process.join(timeout=1.0)  # Wait for termination
                # For a terminated worker, its queue won't get an EOQ. Drain non-blockingly.
                results.extend(drain_queue_non_blocking(worker.result_queue))
            else:
                # For a gracefully exited worker, drain until the EOQ is found.
                results.extend(drain_queue(worker.result_queue))
            self.log(message=f"Worker-{worker.id} has exited.", level=logging.DEBUG)

        self.log(message="All workers have exited", level=logging.INFO)

        self.update_progress(
            ProgressUpdate(task_id=-1, status="Closing final resources")
        )
        # Stop progress monitoring
        if self.show_progress and self.progress_queue and self.progress_thread:
            self.update_progress(ProgressUpdate(task_id=-1, total=-1))
            self.progress_queue.join()
            self.progress_thread.join()

        # Stop the logger
        self.log_queue.close()
        self.log_queue.join()
        for queue in self.logger_control_queues.values():
            queue.put(ExitTask())
            queue.close()
            queue.join()
        self.logger._process.join(timeout=5.0)
        return results

    @enforce_type_hints_contracts
    async def add_task(self, task: Task):
        """Adds a single task to the queue. Convenience wrapper around add_tasks."""
        # **FIX**: Removed self.total_tasks += 1 to prevent double-counting.
        # The add_tasks method is now the single source of truth for counting.
        await self.add_tasks([task])

    @enforce_type_hints_contracts
    async def add_tasks(self, tasks: List[Actionable]) -> List[Task]:
        """Adds a batch of tasks to the queue and starts workers if not already running."""
        if not self.started:
            await self.start_workers()

        # **FIX**: Increment count only for tasks that are successfully enqueued.
        successfully_added = 0
        enqueue_failures = []
        for task in tasks:
            set_task_status(task, TaskState.queue)
            if self.task_queue.put(task):
                successfully_added += 1
            else:
                enqueue_failures.append(task)

        self.total_tasks += successfully_added

        # Update progress if progress monitoring is enabled
        if self.show_progress and self.progress_queue and successfully_added > 0:
            self.update_progress(
                ProgressUpdate(
                    task_id=-1,
                    total=successfully_added,
                )
            )
        self.log(
            message=f"Added {successfully_added} tasks to the task queue. Failures: {len(enqueue_failures)}",
            level=logging.DEBUG,
        )
        return enqueue_failures
