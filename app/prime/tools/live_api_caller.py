from __future__ import annotations

import os
import threading
import time
from typing import Any, Optional

import httpx

_ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
_DEFAULT_TIMEOUT = 30.0

_token_lock = threading.Lock()
_token_cache: dict[str, Any] = {"access_token": "", "expires_at": 0.0}


def _base_url() -> str:
    return (os.getenv("PRIME_API_BASE_URL") or "http://127.0.0.1:8001").rstrip("/")


def _credentials() -> tuple[str, str]:
    return (
        os.getenv("PRIME_API_USERNAME") or "raymond",
        os.getenv("PRIME_API_PASSWORD") or "",
    )


def _static_token() -> str:
    return (os.getenv("PRIME_TOOL_BEARER_TOKEN") or "").strip()


def _fetch_fresh_token() -> str:
    username, password = _credentials()
    if not password:
        return ""
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                f"{_base_url()}/auth/login",
                data={"username": username, "password": password},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if resp.is_success:
                return resp.json().get("access_token", "")
    except Exception:
        pass
    return ""


def _get_token() -> str:
    static = _static_token()
    if static:
        return static

    with _token_lock:
        now = time.monotonic()
        if _token_cache["access_token"] and _token_cache["expires_at"] > now:
            return _token_cache["access_token"]

        token = _fetch_fresh_token()
        if token:
            _token_cache["access_token"] = token
            _token_cache["expires_at"] = now + (25 * 60)  # cache 25 min
        return token


def _invalidate_token() -> None:
    with _token_lock:
        _token_cache["access_token"] = ""
        _token_cache["expires_at"] = 0.0


def call_prime_api(
    *,
    method: str,
    path: str,
    params: Optional[dict[str, Any]] = None,
    json_body: Optional[dict[str, Any]] = None,
    timeout: float = _DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    method = (method or "GET").upper().strip()
    if method not in _ALLOWED_METHODS:
        return {"ok": False, "error": f"Method not allowed: {method}"}

    if not path.startswith("/"):
        path = "/" + path

    url = f"{_base_url()}{path}"

    for attempt in range(2):
        token = _get_token()
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            with httpx.Client(timeout=timeout, headers=headers) as client:
                resp = client.request(method, url, params=params, json=json_body)

                if resp.status_code == 401 and attempt == 0:
                    _invalidate_token()
                    continue

                ct = (resp.headers.get("content-type") or "").lower()
                data = resp.json() if "application/json" in ct else resp.text[:20_000]
                return {
                    "ok": resp.is_success,
                    "status_code": resp.status_code,
                    "url": str(resp.url),
                    "data": data,
                }
        except Exception as exc:
            return {"ok": False, "error": repr(exc), "url": url}

    return {"ok": False, "error": "Auth failed after token refresh retry", "url": url}
