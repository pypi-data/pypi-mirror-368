# File: tests/test_qpool.py

from __future__ import annotations

import asyncio
import logging
import ssl
import threading
import time
from multiprocessing import Manager, cpu_count
from typing import Dict, List

import aiohttp
import certifi
import pytest
import pytest_check as check
from aiohttp import ClientError, ClientSession

from wombat.multiprocessing.models import Prop, RequiresProps
from wombat.multiprocessing.orchestrator import Orchestrator
from wombat.multiprocessing.tasks import RetryableTask, Task, TaskState
from wombat.multiprocessing.worker import Worker


def init_aiohttp_session() -> ClientSession:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))


async def async_fetch_url(worker: Worker, url: str, props: Dict[str, Prop]):
    session_prop: Prop = worker.props["aiohttp_session"]
    session: ClientSession = session_prop.instance
    try:
        if not session:
            raise RuntimeError("aiohttp session prop is not initialized")
        async with session.get(url) as resp:
            resp.raise_for_status()
            return resp.status
    except ClientError as e:
        worker.log(f"Connection error: {e}. Re-initializing session.", logging.WARNING)
        if session_prop and session_prop.exit_stack:
            await session_prop.exit_stack.aclose()
        await worker.initialize_prop(
            props=worker.props, prop_name="aiohttp_session", reinitialize=True
        )
        raise


def fail(worker: Worker):
    raise Exception("This function always fails.")


def hang_forever(worker: Worker):
    """An action that deliberately hangs."""
    while True:
        time.sleep(1)


def sleep_then_finish(worker: Worker, duration: float):
    """An action that sleeps for a given duration."""
    time.sleep(duration)


def failing_initializer():
    """An initializer that is guaranteed to fail."""
    raise ValueError("Prop initialization failed")


def use_prop(worker: Worker, props: Dict[str, Prop]):
    """An action that attempts to use a prop."""
    if not props["failing_prop"].instance:
        raise ValueError("Prop was not initialized")


async def mock_async_fetch_url_success(worker: Worker, url: str, props: Dict[str, Prop]):
    """A mock action that simulates a successful async URL fetch."""
    await asyncio.sleep(0.01)
    return 200


def noop(worker: Worker):
    """An action that does nothing, quickly."""
    pass


class CleanupTracker:
    def __init__(self, flag):
        self.flag = flag

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.flag.value = 1


def use_cleanup_prop(worker: Worker, props: Dict[str, Prop]):
    """An action that does nothing but use a prop."""
    assert props["cleanup_prop"].instance is not None


@pytest.fixture(scope="module")
def manager():
    """Module-scoped multiprocessing manager to ensure lifecycle."""
    with Manager() as m:
        yield m


_cleanup_flag_proxy = None


def cleanup_prop_initializer():
    return CleanupTracker(_cleanup_flag_proxy)


def fail_conditionally(
    worker: Worker, task_id: str, succeed_on_try: int, props: Dict[str, Prop]
):
    """
    Action that fails until a certain attempt number is reached.
    Uses a shared dictionary (from a multiprocessing.Manager) to track attempts.
    """
    tracker = props["attempt_tracker"].instance
    lock = props["lock"].instance

    with lock:
        current_attempt = tracker.get(task_id, 0)
        tracker[task_id] = current_attempt + 1

    if current_attempt < succeed_on_try - 1:
        raise ValueError(f"Failing on attempt {current_attempt + 1}")
    return "Success"


orchestrator_configs = {
    "async": {
        "actions": {"async_fetch_url": async_fetch_url},
        "props": {
            "aiohttp_session": Prop(initializer=init_aiohttp_session),
        },
    },
    "fail": {
        "actions": {"fail": fail},
        "props": {},
    },
    "hang": {"actions": {"hang": hang_forever}, "props": {}},
    "sleep": {"actions": {"sleep": sleep_then_finish}, "props": {}},
    "failing_prop": {
        "actions": {"use_prop": use_prop},
        "props": {"failing_prop": Prop(initializer=failing_initializer)},
    },
    "noop": {"actions": {"noop": noop}, "props": {}},
    "conditional_fail": {
        "actions": {"fail_conditionally": fail_conditionally},
        "props": {},  # props will be added dynamically in test
    },
    "cleanup": {
        "actions": {"use_cleanup_prop": use_cleanup_prop},
        "props": {},  # props will be added dynamically in test
    },
}


class Fail(Task):
    action: str = "fail"


class AsyncFetchUrlTask(Task, RequiresProps):
    action: str = "async_fetch_url"
    requires_props: List[str] = ["aiohttp_session"]


class RetryableAsyncFetchUrlTask(RetryableTask, RequiresProps):
    action: str = "async_fetch_url"
    requires_props: List[str] = ["aiohttp_session"]
    max_tries: int = 3
    initial_delay: float = 0.1


class HangTask(Task):
    action: str = "hang"


class SleepTask(Task):
    action: str = "sleep"


class UsePropTask(Task, RequiresProps):
    action: str = "use_prop"
    requires_props: List[str] = ["failing_prop"]


class NoopTask(Task):
    action: str = "noop"


class ConditionalFailTask(RetryableTask, RequiresProps):
    action: str = "fail_conditionally"
    requires_props: List[str] = ["attempt_tracker", "lock"]


class UseCleanupPropTask(Task, RequiresProps):
    action: str = "use_cleanup_prop"
    requires_props: List[str] = ["cleanup_prop"]


@pytest.mark.asyncio
async def test_orchestrator_async():
    sizes = [100, 200, 300, 400, 500]
    test_urls = [f"https://picsum.photos/{size}" for size in sizes]
    tasks = [AsyncFetchUrlTask(args=[url]) for url in test_urls]

    config = orchestrator_configs["async"].copy()
    config["actions"] = {"async_fetch_url": mock_async_fetch_url_success}

    orchestrator = Orchestrator(
        num_workers=cpu_count(),
        show_progress=False,
        task_models=[AsyncFetchUrlTask],
        **config,
    )

    await orchestrator.add_tasks(tasks)
    job_results = orchestrator.stop_workers()

    check.equal(len(job_results), len(sizes), "Expected correct number of results")
    errors = sum(1 for r in job_results if not isinstance(r.result, int))
    check.equal(errors, 0, "Expected no errors in async approach")
    check.is_true(all(r.result == 200 for r in job_results), "Expected all 200s")


@pytest.mark.asyncio
async def test_repeatedly_finish_tasks():
    tasks = [Fail() for _ in range(10)]
    orchestrator = Orchestrator(
        num_workers=cpu_count(),
        show_progress=False,
        task_models=[Fail],
        **orchestrator_configs["fail"],
    )

    await orchestrator.add_tasks(tasks)
    orchestrator.finish_tasks()
    job_results_1 = list(orchestrator.get_results())
    check.equal(len(job_results_1), 10)
    check.is_true(all(r.task.status == TaskState.fail for r in job_results_1))

    await orchestrator.add_tasks(tasks)
    orchestrator.finish_tasks()
    job_results_2 = list(orchestrator.get_results())
    orchestrator.stop_workers()


@pytest.mark.asyncio
async def test_prop_context_manager_cleanup(manager):
    """Verify that a prop's async context manager is properly exited on worker shutdown."""
    global _cleanup_flag_proxy
    _cleanup_flag_proxy = manager.Value("i", 0)

    config = orchestrator_configs["cleanup"].copy()
    config["props"] = {"cleanup_prop": Prop(initializer=cleanup_prop_initializer)}

    orchestrator = Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[UseCleanupPropTask],
        **config,
    )

    await orchestrator.add_task(UseCleanupPropTask())
    orchestrator.stop_workers()

    check.equal(
        _cleanup_flag_proxy.value, 1, "Prop's __aexit__ should have been called."
    )
    check.equal(len(job_results_2), 10)
    check.is_true(all(r.task.status == TaskState.fail for r in job_results_2))


@pytest.mark.asyncio
async def test_stop_workers_with_no_added_tasks():
    orchestrator = Orchestrator(
        num_workers=cpu_count(),
        show_progress=False,
        **orchestrator_configs["fail"],
    )
    await orchestrator.start_workers()
    results = orchestrator.stop_workers()
    check.equal(len(results), 0)


@pytest.mark.timeout(20)
@pytest.mark.asyncio
async def test_stop_workers_with_hanging_task():
    """Verify that `stop_workers` terminates a hanging worker and exits."""
    orchestrator = Orchestrator(
        num_workers=2,
        show_progress=False,
        task_models=[HangTask],
        **orchestrator_configs["hang"],
    )
    await orchestrator.add_task(HangTask())
    results = orchestrator.stop_workers()
    # The main assertion is that `stop_workers` returns without hanging.
    # The orchestrator should terminate the misbehaving worker.
    # We expect 0 results because the task never finishes.
    check.equal(len(results), 0)


@pytest.mark.asyncio
async def test_finish_tasks_concurrency():
    """Verify `finish_tasks` only waits for tasks submitted before it was called."""
    orchestrator = Orchestrator(
        num_workers=2,
        show_progress=False,
        task_models=[SleepTask],
        **orchestrator_configs["sleep"],
    )
    # Batch 1: Fast tasks
    tasks1 = [SleepTask(args=[0.1]) for _ in range(4)]
    await orchestrator.add_tasks(tasks1)

    # Use a thread to call finish_tasks, because it blocks
    finish_thread = threading.Thread(target=orchestrator.finish_tasks)
    finish_thread.start()

    # Give finish_tasks a moment to start and record the total_tasks count
    time.sleep(0.1)

    # Batch 2: Slow tasks, added after finish_tasks is running
    tasks2 = [SleepTask(args=[5]) for _ in range(2)]
    await orchestrator.add_tasks(tasks2)

    # The finish_thread should join long before the slow tasks complete.
    # A generous timeout to allow the fast tasks to complete.
    finish_thread.join(timeout=5)

    check.is_false(
        finish_thread.is_alive(),
        "finish_tasks should not wait for tasks added after it was called",
    )

    # Clean up
    orchestrator.stop_workers()


@pytest.mark.asyncio
async def test_prop_initialization_failure():
    """Verify the orchestrator remains stable when a prop fails to initialize."""
    orchestrator = Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[UsePropTask],
        **orchestrator_configs["failing_prop"],
    )
    await orchestrator.add_task(UsePropTask())
    results = orchestrator.stop_workers()
    # The orchestrator should not hang. The task should fail.
    check.equal(len(results), 1)
    check.equal(results[0].task.status, TaskState.fail)


@pytest.mark.asyncio
async def test_graceful_shutdown_with_many_tasks():
    """Test that the orchestrator shuts down cleanly with a large number of tasks."""
    orchestrator = Orchestrator(
        num_workers=cpu_count(),
        show_progress=False,
        task_models=[Fail],
        **orchestrator_configs["fail"],
    )
    # Add a large number of tasks to the queue
    num_tasks = 1000
    tasks = [Fail() for _ in range(num_tasks)]
    await orchestrator.add_tasks(tasks)

    # Immediately stop the workers. This should not hang.
    results = orchestrator.stop_workers()

    check.equal(
        len(results), num_tasks, "All tasks should be processed or accounted for."
    )


@pytest.mark.asyncio
async def test_rate_limiting():
    """Verify that the tasks_per_minute_limit is respected."""
    num_tasks = 10
    tasks_per_minute = 120  # 2 tasks per second
    # Expected duration for 10 tasks at 2/sec is 5 seconds.
    expected_duration_sec = num_tasks / (tasks_per_minute / 60.0)

    orchestrator = Orchestrator(
        num_workers=2,  # Use more than 1 worker to test coordination
        show_progress=False,
        task_models=[NoopTask],
        tasks_per_minute_limit=tasks_per_minute,
        **orchestrator_configs["noop"],
    )

    start_time = time.monotonic()
    await orchestrator.add_tasks([NoopTask() for _ in range(num_tasks)])
    results = orchestrator.stop_workers()
    end_time = time.monotonic()

    duration = end_time - start_time
    check.equal(len(results), num_tasks)

    # Allow for some timing variance and overhead, but check it's not too fast.
    # The rate limiter sleeps, so the time should be at least the expected duration.
    check.greater_equal(
        duration,
        expected_duration_sec * 0.9,
        f"Execution was too fast ({duration:.2f}s) for rate limit.",
    )


@pytest.mark.asyncio
async def test_retry_logic(manager):
    """Verify that a task is retried on failure and eventually succeeds."""
    attempt_tracker = manager.dict()
    lock = manager.Lock()

    config = orchestrator_configs["conditional_fail"].copy()
    config["props"] = {
        "attempt_tracker": Prop(initializer=attempt_tracker, use_context_manager=False),
        "lock": Prop(initializer=lock, use_context_manager=False),
    }

    orchestrator = Orchestrator(
        num_workers=2,
        show_progress=False,
        task_models=[ConditionalFailTask],
        **config,
    )

    task = ConditionalFailTask(
        args=[
            None,  # placeholder for task id
            2,  # succeed on 2nd attempt
        ],
        max_tries=2,
    )
    task.args[0] = str(task.id)  # Pass task's own ID to action for tracking

    await orchestrator.add_task(task)
    results = orchestrator.stop_workers()

    check.equal(len(results), 1)
    result = results[0]

    check.equal(result.task.status, TaskState.success)
    check.equal(result.result, "Success")
    check.equal(
        result.task.tries, 1, "Task should have been retried once before succeeding."
    )
    check.equal(
        attempt_tracker.get(str(task.id)),
        2,
        "Action should have been executed twice.",
    )


def test_retryable_backoff_calculation():
    """Verify the exponential backoff calculation is correct."""
    task = RetryableTask(action="test", initial_delay=1, max_delay=10, max_tries=5)
    task.tries = 1
    check.equal(task.backoff(), 2.0)  # 1 * (2**1)
    task.tries = 2
    check.equal(task.backoff(), 4.0)  # 1 * (2**2)
    task.tries = 3
    check.equal(task.backoff(), 8.0)  # 1 * (2**3)
    task.tries = 4
    check.equal(task.backoff(), 10.0)  # Capped at max_delay (16.0 > 10.0)


@pytest.mark.asyncio
async def test_add_task_and_add_tasks_counting():
    """Verify that total_tasks is counted correctly across add_task and add_tasks."""
    orchestrator = Orchestrator(
        num_workers=1,
        show_progress=False,
        task_models=[NoopTask],
        **orchestrator_configs["noop"],
    )

    await orchestrator.add_task(NoopTask())
    check.equal(orchestrator.total_tasks, 1)

    await orchestrator.add_tasks([NoopTask(), NoopTask()])
    check.equal(orchestrator.total_tasks, 3)

    await orchestrator.add_task(NoopTask())
    check.equal(orchestrator.total_tasks, 4)

    orchestrator.stop_workers()
