"""Decorator helpers to monitor arbitrary functions using an existing MonitoredModel."""

from typing import Callable, Optional
import time
from .monitored_model import MonitoredModel
from .utils import logger

def monitor_function(monitored_model: MonitoredModel, name: Optional[str] = None) -> Callable:
    """
    Create a decorator that records latency of arbitrary functions and enqueues telemetry.

    Usage:
        @monitor_function(mm, "handler")
        def handler(...): ...
    """
    def decorator(fn: Callable) -> Callable:
        fname = name or getattr(fn, "__name__", "function")
        def wrapped(*args, **kwargs):
            start = time.time()
            try:
                return fn(*args, **kwargs)
            finally:
                latency = time.time() - start
                try:
                    payload = {
                        "timestamp": time.time(),
                        "model_name": f"{monitored_model.model_name}.{fname}",
                        "latency": float(latency),
                        "input_shape": None,
                        "output_shape": None,
                        "agent_version": None,
                    }
                    monitored_model.queue.enqueue(payload)
                except Exception:
                    logger.exception("monitor_function: failed to enqueue telemetry (ignored)")
        return wrapped
    return decorator
