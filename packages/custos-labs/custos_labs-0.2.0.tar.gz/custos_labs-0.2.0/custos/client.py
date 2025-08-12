# custos/client.py

import json
import threading
import time
from typing import Optional
import requests

from .config import CustosConfig
from .guardian import CustosGuardian

_HEARTBEAT_INTERVAL_SEC = 2.0

class AutoLoggingGuardian:
    """
    Pure-Custos:
      - Starts automatic heartbeats every 2s so the simulator shows HRV.
      - Optionally, you (or our server) can still call evaluate(prompt, response)
        to post "response" beats (these can cause flatlines if misaligned).
    """
    def __init__(self, cfg: CustosConfig):
        if not cfg.api_key:
            raise RuntimeError("custos: api_key not set; call custos.set_api_key(...) first")
        self.cfg = cfg
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"ApiKey {self.cfg.api_key}",
            "Content-Type": "application/json"
        })
        # local engine (optional safeguard)
        self._engine = CustosGuardian(api_key=(cfg.api_key[:8] + "..."))

        # start background heartbeats
        self._hb_stop = threading.Event()
        self._hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._hb_thread.start()

    def _post_async(self, payload: dict):
        def _send():
            try:
                self._session.post(
                    f"{self.cfg.backend_url.rstrip('/')}/simulator/logs/",
                    data=json.dumps(payload),
                    timeout=self.cfg.timeout_sec,
                )
            except Exception:
                # never break user apps on telemetry failures
                pass
        threading.Thread(target=_send, daemon=True).start()

    def _heartbeat_loop(self):
        # tiny jitter so the graph visibly wiggles
        tick = 0
        while not self._hb_stop.is_set():
            tick += 1
            conf = 0.97 if (tick % 2) else 0.99
            self._post_async({"kind": "heartbeat", "confidence": conf})
            self._hb_stop.wait(_HEARTBEAT_INTERVAL_SEC)

    def stop(self):
        self._hb_stop.set()

    def evaluate(self, prompt: str, response: str, confidence: float = 1.0):
        # Optional: when available, this ties beats to actual responses.
        try:
            self._engine.evaluate(prompt, response)
        except Exception:
            # backend will still mark misalignment on the log
            pass
        self._post_async({
            "kind": "response",
            "prompt": prompt or "",
            "response": response or "",
            "confidence": confidence
        })
        return {"alignment_status": "sent"}
