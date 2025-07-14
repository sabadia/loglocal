# log_service.py
import sys
import os
import time
import asyncio
from functools import wraps

from loglocal.models.log_local import LogLocal


def _config_logger():
    from loguru import logger as loguru_logger
    _local = LogLocal()

    loguru_logger.remove()
    loguru_logger.add(
        sys.stderr,
        level=_local.log_config.level,
        format=_local.log_format,
        colorize=True,
        backtrace=True,
        diagnose=_local.log_config.diagnose
    )
    loguru_logger.add(
        os.path.join(_local.log_path, "app.log"),
        level=_local.log_config.level,
        format=_local.log_format,
        rotation=_local.log_config.file_rotation,
        retention=_local.log_config.file_retention,
        compression="zip",
        serialize=_local.log_config.serialize,
        enqueue=_local.log_config.enqueue,
        backtrace=True,
        diagnose=_local.log_config.diagnose
    )

    return loguru_logger


_loguru_logger = _config_logger()


def log_calls(func=None):
    """
    Decorator to wrap sync or async functions:
    - logs start with truncated args/kwargs
    - logs elapsed time
    - logs return
    - catches exceptions and logs full traceback
    """
    def decorator(fn):
        @wraps(fn)
        async def async_wrapper(*args, **kwargs):
            extra = {"args": repr(args)[:200], "kwargs": repr(kwargs)[:200]}
            _loguru_logger.bind(**extra).info(f"→ {fn.__name__} started")
            start = time.monotonic()
            try:
                result = await fn(*args, **kwargs)
                elapsed = time.monotonic() - start
                _loguru_logger.bind(duration=f"{elapsed:.3f}s").info(f"← {fn.__name__} finished result={repr(result)[:200]}")
                return result
            except Exception:
                _loguru_logger.exception(f"❌ Error in {fn.__name__}")
                raise

        @wraps(fn)
        def sync_wrapper(*args, **kwargs):
            extra = {"args": repr(args)[:200], "kwargs": repr(kwargs)[:200]}
            _loguru_logger.bind(**extra).info(f"→ {fn.__name__} started")
            start = time.monotonic()
            try:
                result = fn(*args, **kwargs)
                elapsed = time.monotonic() - start
                _loguru_logger.bind(duration=f"{elapsed:.3f}s").info(f"← {fn.__name__} finished result={repr(result)[:200]}")
                return result
            except Exception:
                _loguru_logger.exception(f"❌ Error in {fn.__name__}")
                raise

        return async_wrapper if asyncio.iscoroutinefunction(fn) else sync_wrapper

    return decorator(func) if func else decorator

# optional helper for binding context globally
def get_logger(**context):
    return _loguru_logger.bind(**context)

loglocal = get_logger()
