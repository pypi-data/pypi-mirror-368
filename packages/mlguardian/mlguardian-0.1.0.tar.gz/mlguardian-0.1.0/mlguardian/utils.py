"""Small utilities used by the agent."""
import time
import logging
import random
from typing import Optional, Tuple, Any

logger = logging.getLogger("mlguardian")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(asctime)s [mlguardian] %(levelname)s: %(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)

def now_ts() -> float:
    """Return current time as epoch float (UTC)."""
    return time.time()

def exponential_backoff(attempt: int, base: float = 0.5, jitter: float = 0.1) -> float:
    """
    Exponential backoff with jitter.
    attempt: 0-based attempt index.
    """
    backoff = base * (2 ** attempt)
    return backoff + random.uniform(-jitter, jitter)

def shape_of(obj: Any) -> Optional[Tuple]:
    """Try to produce a short representation of the shape of obj."""
    try:
        s = getattr(obj, "shape", None)
        if s is not None:
            # normalize numpy shapes and tuples
            if isinstance(s, tuple):
                return s
            return (s,)
        if hasattr(obj, "__len__"):
            return (len(obj),)
    except Exception:
        return None
    return None
