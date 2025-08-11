"""
Configuration defaults for mlguardian agent.
Read overrides from environment variables.
"""
import os
from typing import Final

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except Exception:
        return default

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default

API_URL: Final[str] = os.getenv("MLGUARDIAN_API_URL", "http://localhost:8001")
API_KEY: Final[str] = os.getenv("MLGUARDIAN_API_KEY", "")
DEFAULT_MODEL_NAME: Final[str] = os.getenv("MLGUARDIAN_MODEL_NAME", "default_model")
TIMEOUT: Final[float] = _env_float("MLGUARDIAN_TIMEOUT", 2.0)

# sender queue
QUEUE_MAXSIZE: Final[int] = _env_int("MLGUARDIAN_QUEUE_MAXSIZE", 2000)
BATCH_SIZE: Final[int] = _env_int("MLGUARDIAN_BATCH_SIZE", 20)
BATCH_INTERVAL_SECONDS: Final[float] = _env_float("MLGUARDIAN_BATCH_INTERVAL", 1.0)

# retries/backoff
MAX_RETRIES: Final[int] = _env_int("MLGUARDIAN_MAX_RETRIES", 4)
BACKOFF_BASE: Final[float] = _env_float("MLGUARDIAN_BACKOFF_BASE", 0.5)
BACKOFF_JITTER: Final[float] = _env_float("MLGUARDIAN_BACKOFF_JITTER", 0.1)

# sampling (0.0 = none, 1.0 = all)
SAMPLE_RATE: Final[float] = _env_float("MLGUARDIAN_SAMPLE_RATE", 1.0)

# whether to swallow all transport exceptions (recommended True)
IGNORE_TRANSPORT_ERRORS: Final[bool] = os.getenv(
    "MLGUARDIAN_IGNORE_TRANSPORT_ERRORS", "true"
).lower() in ("1", "true", "yes")
