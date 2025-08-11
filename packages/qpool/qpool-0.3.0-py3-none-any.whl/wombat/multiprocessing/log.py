# File: src/wombat/multiprocessing/log.py
import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, cast

from wombat.utils.errors.decorators import enforce_type_hints_contracts


def _env_level(default: int) -> int:
    val = os.getenv("QPOOL_LOG_LEVEL", "")
    if not val:
        return default
    try:
        return getattr(logging, val.upper(), default)
    except Exception:
        return default


@enforce_type_hints_contracts
def setup_logging(
    name: str = "QPoolLogger",
    level: int = logging.ERROR,
    log_file: str = "logfile.log",
    to_console: bool | None = None,
) -> Logger:
    """
    Create or reuse a logger that writes structured lines.

    Environment overrides
    ---------------------
    QPOOL_LOG_FILE   : path to log file (default: logfile.log)
    QPOOL_LOG_LEVEL  : DEBUG|INFO|WARNING|ERROR|CRITICAL (default: from `level`)
    QPOOL_LOG_STDOUT : "1" to also emit to console (default: off)
    QPOOL_LOG_MAX    : max bytes before rotation (default: 2MB)
    QPOOL_LOG_BACKUPS: number of rotated files to keep (default: 2)
    """
    log_file = os.getenv("QPOOL_LOG_FILE", log_file)
    resolved_level = _env_level(level)
    to_console = (
        to_console if to_console is not None else os.getenv("QPOOL_LOG_STDOUT") == "1"
    )
    max_bytes = int(os.getenv("QPOOL_LOG_MAX", str(2 * 1024 * 1024)))
    backups = int(os.getenv("QPOOL_LOG_BACKUPS", "2"))

    logger = logging.getLogger(name)
    logger.setLevel(resolved_level)
    logger.propagate = False  # avoid duplicate lines if root configured elsewhere

    # Basic structured line: timestamp level name pid msg
    fmt = "%(asctime)s | %(levelname)s | %(name)s | pid=%(process)d | %(message)s"
    formatter = logging.Formatter(fmt)

    # Idempotent handler setup
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        file_handler = RotatingFileHandler(
            log_file, mode="a", maxBytes=max_bytes, backupCount=backups
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(resolved_level)
        logger.addHandler(file_handler)

    if to_console and not any(
        isinstance(h, logging.StreamHandler) for h in logger.handlers
    ):
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.setLevel(resolved_level)
        logger.addHandler(sh)

    logger.debug(
        f"Logger initialized: file={log_file}, level={logging.getLevelName(resolved_level)}, console={to_console}"
    )
    return logger


def log(worker, message: str, level: int, props: Dict[str, Any]):
    logger: Logger = cast(Logger, props["logger"].instance)
    logger.log(level=level, msg=message)
