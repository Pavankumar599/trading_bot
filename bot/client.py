import hashlib
import hmac
import logging
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

log = logging.getLogger(__name__)

class BinanceAPIError(RuntimeError):
    def __init__(self, status_code: int, payload: Any):
        super().__init__(f"Binance API error {status_code}: {payload}")
        self.status_code = status_code
        self.payload = payload

class BinanceFuturesClient:
    """Minimal REST client for Binance USDT-M Futures (testnet-ready)."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://testnet.binancefuture.com",
        timeout: int = 15,
        recv_window: int = 5000,
        session: Optional[requests.Session] = None,
    ):
        self.api_key = api_key
        self.api_secret = api_secret.encode("utf-8")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.recv_window = recv_window
        self.session = session or requests.Session()

    def _sign(self, query_string: str) -> str:
        return hmac.new(self.api_secret, query_string.encode("utf-8"), hashlib.sha256).hexdigest()

    def _headers(self) -> Dict[str, str]:
        return {"X-MBX-APIKEY": self.api_key}

    def _request(self, method: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"

        # Add required signed params
        params = dict(params)
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = self.recv_window

        # Build query string and sign it
        qs = urlencode(params, doseq=True)
        signature = self._sign(qs)
        signed_qs = f"{qs}&signature={signature}"

        # Logging (do not log signature; do not log secret)
        safe_params = dict(params)
        log.info("REQUEST %s %s params=%s", method.upper(), path, safe_params)

        try:
            if method.upper() == "GET":
                resp = self.session.get(url, headers=self._headers(), params=signed_qs, timeout=self.timeout)
            else:
                # Futures signed endpoints accept params in query string even for POST
                resp = self.session.request(method.upper(), url, headers=self._headers(), params=signed_qs, timeout=self.timeout)
        except requests.RequestException as e:
            log.exception("NETWORK ERROR calling %s %s: %s", method.upper(), path, e)
            raise

        content_type = resp.headers.get("Content-Type", "")
        data: Any
        try:
            if "application/json" in content_type:
                data = resp.json()
            else:
                data = resp.text
        except Exception:
            data = resp.text

        log.info("RESPONSE %s %s status=%s body=%s", method.upper(), path, resp.status_code, data)

        if not (200 <= resp.status_code < 300):
            raise BinanceAPIError(resp.status_code, data)

        if isinstance(data, dict):
            return data
        return {"raw": data}

    # Public endpoints
    def ping(self) -> Dict[str, Any]:
        url = f"{self.base_url}/fapi/v1/ping"
        log.info("REQUEST GET /fapi/v1/ping")
        resp = self.session.get(url, timeout=self.timeout)
        try:
            data = resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else resp.text
        except Exception:
            data = resp.text
        log.info("RESPONSE GET /fapi/v1/ping status=%s body=%s", resp.status_code, data)
        resp.raise_for_status()
        return data if isinstance(data, dict) else {"raw": data}

    # Signed endpoints
    def create_order(self, **order_params: Any) -> Dict[str, Any]:
        """POST /fapi/v1/order"""
        return self._request("POST", "/fapi/v1/order", order_params)
