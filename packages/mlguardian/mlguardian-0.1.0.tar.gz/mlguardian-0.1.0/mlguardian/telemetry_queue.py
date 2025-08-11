"""Background in-memory queue + worker that batches telemetry and sends them."""

from typing import Dict, List, Optional
import threading
import queue
import time
from .utils import logger
from .telemetry_sender import TelemetrySender
from .config import QUEUE_MAXSIZE, BATCH_SIZE, BATCH_INTERVAL_SECONDS

class TelemetryQueue:
    """Thread-based queue and worker for batching and sending telemetry."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        queue_maxsize: int = QUEUE_MAXSIZE,
        batch_size: int = BATCH_SIZE,
        batch_interval_seconds: float = BATCH_INTERVAL_SECONDS,
        timeout: Optional[float] = None,
    ):
        self.sender = TelemetrySender(api_url=api_url, api_key=api_key, timeout=timeout)
        self.batch_size = batch_size
        self.batch_interval_seconds = batch_interval_seconds
        self._queue: "queue.Queue[Dict]" = queue.Queue(maxsize=queue_maxsize)
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._worker, name="mlguardian-queue", daemon=True)
        self._thread.start()
        logger.debug("TelemetryQueue: worker started")

    def enqueue(self, payload: Dict, block: bool = False, timeout: float = 0.0) -> bool:
        """Enqueue a telemetry payload. Returns False if queue is full."""
        try:
            self._queue.put(payload, block=block, timeout=timeout)
            return True
        except queue.Full:
            logger.warning("TelemetryQueue: queue full - dropping telemetry")
            return False

    def _worker(self) -> None:
        buffer: List[Dict] = []
        last_send = time.time()
        while not self._stop_event.is_set():
            remaining = max(0.0, self.batch_interval_seconds - (time.time() - last_send))
            try:
                item = self._queue.get(timeout=remaining)
                buffer.append(item)
            except queue.Empty:
                pass

            if buffer and (len(buffer) >= self.batch_size or (time.time() - last_send) >= self.batch_interval_seconds):
                batch = buffer[: self.batch_size]
                try:
                    self.sender.send_batch(batch)
                except Exception:
                    logger.exception("TelemetryQueue: unexpected error sending batch")
                buffer = buffer[len(batch) :]
                last_send = time.time()

        # flush remaining on stop
        if buffer:
            logger.debug("TelemetryQueue: flushing %d items before stop", len(buffer))
            try:
                self.sender.send_batch(buffer)
            except Exception:
                logger.exception("TelemetryQueue: error flushing remaining items")

    def flush(self, timeout: Optional[float] = None) -> bool:
        """Block until queue empty or timeout reached. Returns True if empty."""
        start = time.time()
        while not self._queue.empty():
            if timeout is not None and (time.time() - start) > timeout:
                logger.warning("TelemetryQueue: flush timeout reached; queue not empty")
                return False
            time.sleep(0.05)
        return True

    def stop(self) -> None:
        """Stop background worker (best-effort)."""
        self._stop_event.set()
        try:
            self._thread.join(timeout=2.0)
        except Exception:
            logger.debug("TelemetryQueue: worker did not stop within timeout")
