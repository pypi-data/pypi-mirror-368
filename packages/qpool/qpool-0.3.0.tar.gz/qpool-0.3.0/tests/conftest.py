# File: tests/conftest.py
"""
Pytest wiring for better qpool diagnostics:
- Force DEBUG-level logs to a temp file via env vars.
- On any test failure, print the last N lines of the qpool log so retry traces are visible.

Environment variables honored by src/wombat/multiprocessing/log.py:
  QPOOL_LOG_FILE, QPOOL_LOG_LEVEL, QPOOL_LOG_STDOUT, QPOOL_LOG_MAX, QPOOL_LOG_BACKUPS
"""

import io
import os
import tempfile
import pytest


@pytest.fixture(autouse=True, scope="session")
def _qpool_debug_logging_session():
    """
    Session-scoped fixture that ensures qpool logs go to a temporary file
    at DEBUG level. The file is preserved after the session for postmortem.
    """
    tmpdir = tempfile.mkdtemp(prefix="qpool_logs_")
    log_path = os.path.join(tmpdir, "qpool.log")
    os.environ.setdefault("QPOOL_LOG_FILE", log_path)
    os.environ.setdefault("QPOOL_LOG_LEVEL", "DEBUG")
    # To also mirror logs to stdout, uncomment the next line:
    # os.environ.setdefault("QPOOL_LOG_STDOUT", "1")
    yield
    # Keep the temp log directory for inspection; do not delete here.


def _tail(path: str, lines: int = 300) -> str:
    """
    Return the last `lines` lines of a file located at `path`.
    Robust for large files via backward reads; falls back to full read on errors.
    """
    try:
        with open(path, "rb") as f:
            try:
                f.seek(0, io.SEEK_END)
                file_size = f.tell()
                if file_size == 0:
                    return "<empty log file>"
                block = 4096
                data = bytearray()
                # Read from the end in blocks until we have enough lines
                while len(data.splitlines()) <= lines and f.tell() > 0:
                    read_size = min(block, f.tell())
                    f.seek(f.tell() - read_size)
                    chunk = f.read(read_size)
                    f.seek(f.tell() - read_size)
                    data[:0] = chunk
                    if f.tell() == 0:
                        break
                text = data.decode(errors="replace")
                return "\n".join(text.splitlines()[-lines:])
            except Exception:
                f.seek(0)
                return f.read().decode(errors="replace")
    except FileNotFoundError:
        return "<qpool log file not found>"


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hookwrapper implementation:
    - Let pytest run the phase.
    - If the call phase failed, print the tail of the qpool log.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        path = os.getenv("QPOOL_LOG_FILE", "logfile.log")
        tail = _tail(path, lines=300)
        # Use a clear delimiter so it's easy to grep in CI logs.
        print("\n================= QPOOL LOG TAIL (last 300 lines) =================")
        print(tail)
        print("================= END QPOOL LOG TAIL =================\n")
