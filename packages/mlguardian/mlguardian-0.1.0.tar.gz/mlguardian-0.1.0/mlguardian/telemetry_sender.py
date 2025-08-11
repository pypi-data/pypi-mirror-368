"""HTTP sender for telemetry batches with retry/backoff."""

from typing import Any, Dict, List, Optional
import requests
from requests.exceptions import RequestException
from .utils import logger, exponential_backoff
from .config import API_KEY, TIMEOUT, MAX_RETRIES, BACKOFF_BASE, BACKOFF_JITTER

DEFAULT_PATH = "/monitor"

class TelemetrySender:
    def __init__(self, api_url: str, api_key: Optional[str] = None, timeout: Optional[float] = None):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key or API_KEY or None
        self.timeout = float(timeout) if timeout is not None else TIMEOUT

    def _headers(self) -> Dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.api_key:
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def send_batch(self, items: List[Dict[str, Any]]) -> bool:
        """
        Send a list of telemetry items to the server.
        Retries on transient errors with exponential backoff.
        Returns True if send succeeded.
        """
        if not items:
            return True
        url = f"{self.api_url}{DEFAULT_PATH}"
        # allow single object or list (server may accept both)
        body = items[0] if len(items) == 1 else items

        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = requests.post(url, json=body, headers=self._headers(), timeout=self.timeout)
                if 200 <= resp.status_code < 300:
                    logger.debug("Telemetry batch sent (size=%d)", len(items))
                    return True
                logger.warning("Telemetry sender: HTTP %s - %s", resp.status_code, resp.text)
            except RequestException as exc:
                logger.debug("Telemetry sender attempt %d failed: %s", attempt, exc)

            if attempt < MAX_RETRIES:
                wait = exponential_backoff(attempt, base=BACKOFF_BASE, jitter=BACKOFF_JITTER)
                logger.debug("Telemetry sender backing off %.2fs", wait)
                import time
                time.sleep(wait)

        logger.error("Telemetry sender: failed to deliver batch after retries (size=%d)", len(items))
        return False
