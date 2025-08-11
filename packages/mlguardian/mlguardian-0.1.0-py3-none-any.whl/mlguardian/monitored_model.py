"""Public MonitoredModel wrapper for machine learning models."""

from typing import Any, Optional, Dict
import time
import random
from .telemetry_queue import TelemetryQueue
from .utils import now_ts, shape_of, logger
from .config import API_URL, SAMPLE_RATE, DEFAULT_MODEL_NAME
from ._version import __version__ as AGENT_VERSION

class MonitoredModel:
    """
    Wraps a model object exposing a `.predict(X, **kwargs)` method and
    emits telemetry asynchronously to a configured endpoint.

    Example:
        mm = MonitoredModel(model, api_url="http://localhost:8001", model_name="mymodel")
        preds = mm.predict(X)
    """

    def __init__(
        self,
        model: Any,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        sample_rate: float = SAMPLE_RATE,
        timeout: Optional[float] = None,
    ):
        self.model = model
        self.api_url = (api_url or API_URL).rstrip("/")
        self.model_name = model_name or DEFAULT_MODEL_NAME
        self.sample_rate = float(sample_rate)
        self._agent_version = AGENT_VERSION
        # create and start telemetry queue worker
        self.queue = TelemetryQueue(api_url=self.api_url, api_key=api_key, timeout=timeout)

    def _should_send(self) -> bool:
        if self.sample_rate >= 1.0:
            return True
        if self.sample_rate <= 0.0:
            return False
        return random.random() < self.sample_rate

    def _make_payload(self, latency: float, X: Any, y_pred: Any, extra: Optional[Dict] = None) -> Dict:
        payload = {
            "timestamp": now_ts(),
            "model_name": self.model_name,
            "latency": float(latency),
            "input_shape": str(shape_of(X)),
            "output_shape": str(shape_of(y_pred)),
            "agent_version": self._agent_version,
        }
        if extra:
            payload["extra"] = extra
        return payload

    def predict(self, X: Any, **kwargs) -> Any:
        """Wrap and call the underlying model.predict and enqueue telemetry non-blocking."""
        start = time.time()
        result = self.model.predict(X, **kwargs)
        latency = time.time() - start

        try:
            if self._should_send():
                payload = self._make_payload(latency, X, result)
                ok = self.queue.enqueue(payload, block=False)
                if not ok:
                    logger.debug("MonitoredModel: enqueue returned False (queue full)")
        except Exception:
            # never let telemetry break the user's model
            logger.exception("MonitoredModel: telemetry enqueue failed (ignored)")

        return result

    def predict_sync(self, X: Any, **kwargs) -> Any:
        """Synchronous prediction that blocks until telemetry send attempt finishes."""
        start = time.time()
        result = self.model.predict(X, **kwargs)
        latency = time.time() - start
        payload = self._make_payload(latency, X, result)
        # direct send using a temporary sender
        from .telemetry_sender import TelemetrySender
        sender = TelemetrySender(api_url=self.api_url)
        try:
            sender.send_batch([payload])
        except Exception:
            logger.exception("MonitoredModel: synchronous send failed (ignored)")
        return result

    def flush(self, timeout: float = 5.0) -> bool:
        """Flush queued telemetry. Returns True if successful within timeout."""
        try:
            return self.queue.flush(timeout=timeout)
        except Exception:
            logger.exception("MonitoredModel: flush error")
            return False

    def stop(self) -> None:
        """Stop background worker and flush remaining telemetry."""
        try:
            self.queue.stop()
        except Exception:
            logger.exception("MonitoredModel: stop error")
