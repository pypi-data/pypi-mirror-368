from __future__ import annotations

import os
import json
import time
from typing import Any, Dict, Generator, List, Optional

import httpx

from ..config import get_openrouter_key, rc_cache_path
from ..utils.errors import AuthError, RateLimitError, NetworkError

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def redact(s: str, keep: int = 6) -> str:
    if not s:
        return ""
    return s[:keep] + "..." if len(s) > keep else "***"


def _raise_http_error(e: httpx.HTTPStatusError) -> None:
    code = e.response.status_code
    text = e.response.text[:500]
    if code in (401, 403):
        raise AuthError("OpenRouter auth failed (401/403). Check OPENROUTER_API_KEY.") from e
    if code == 429:
        raise RateLimitError("OpenRouter rate limit (429). Slow down or upgrade plan.") from e
    raise NetworkError(f"OpenRouter HTTP {code}: {text}") from e


class OpenRouterClient:
    """
    Minimal OpenRouter client:
      - chat() for non-streaming responses
      - stream_chat() yields token deltas
      - list_models_cached() helper lives at module level
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = OPENROUTER_BASE_URL,
        timeout: float = 60.0,
        referer: Optional[str] = None,
        title: Optional[str] = None,
    ) -> None:
        self.api_key = api_key or get_openrouter_key()
        self.base_url = base_url
        self.timeout = timeout
        self.referer = referer or os.getenv("OPENROUTER_REFERER")
        self.title = title or os.getenv("OPENROUTER_TITLE") or "Agentik"
        self._client = httpx.Client(timeout=self.timeout)

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            raise AuthError(
                "OPENROUTER_API_KEY is not set. Use `agentik keys set openrouter sk-or-...` or set env."
            )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.title:
            headers["X-Title"] = self.title
        return headers

    def chat(
        self, messages: List[Dict[str, str]], model: str, **params: Any
    ) -> Dict[str, Any]:
        """Return dict with keys: raw (full response), content (assistant text or "")."""
        payload = {"model": model, "messages": messages} | params
        try:
            r = self._client.post(
                f"{self.base_url}/chat/completions", headers=self._headers(), json=payload
            )
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            _raise_http_error(e)
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.TransportError) as e:
            raise NetworkError("Network error talking to OpenRouter.") from e

        data = r.json()
        choice = data.get("choices", [{}])[0]
        content = ""
        if "message" in choice and isinstance(choice["message"], dict):
            content = choice["message"].get("content") or ""
        return {"raw": data, "content": content}

    def stream_chat(
        self, messages: List[Dict[str, str]], model: str, **params: Any
    ) -> Generator[str, None, None]:
        """Yield content deltas as they arrive."""
        payload = {"model": model, "stream": True, "messages": messages} | params
        try:
            with self._client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            ) as r:
                r.raise_for_status()
                for line in r.iter_lines():
                    if not line:
                        continue
                    if line.startswith(b"data: "):
                        chunk = line[len(b"data: ") :].decode("utf-8", errors="ignore").strip()
                        if chunk == "[DONE]":
                            break
                        try:
                            obj = json.loads(chunk)
                            delta = obj.get("choices", [{}])[0].get("delta", {}).get("content")
                            if delta:
                                yield delta
                        except Exception:
                            continue
        except httpx.HTTPStatusError as e:
            _raise_http_error(e)
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.TransportError) as e:
            raise NetworkError("Network error (stream) talking to OpenRouter.") from e


def ensure_openrouter_key(required: bool = True) -> Optional[str]:
    """Check env or .agentikrc for OPENROUTER key; raise if required and missing."""
    key = get_openrouter_key()
    if not key and required:
        raise AuthError(
            "OPENROUTER_API_KEY is not set. Use:\n"
            "  PowerShell: setx OPENROUTER_API_KEY \"sk-or-...\"\n"
            "  or: agentik keys set openrouter sk-or-... --global"
        )
    return key


def list_models_cached(ttl: int = 24 * 3600) -> List[Dict[str, Any]]:
    """Cached model list (24h default) at ~/.agentik/cache/models.json"""
    cache_file = rc_cache_path("models.json")
    if cache_file.exists():
        try:
            meta = json.loads(cache_file.read_text(encoding="utf-8"))
            if time.time() - meta.get("_ts", 0) < ttl and "data" in meta:
                return meta["data"]
        except Exception:
            pass

    api_key = get_openrouter_key()
    if not api_key:
        return []

    try:
        with httpx.Client(timeout=30.0) as c:
            r = c.get(
                f"{OPENROUTER_BASE_URL}/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            r.raise_for_status()
            data = r.json().get("data", [])
    except httpx.HTTPStatusError as e:
        _raise_http_error(e)
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.TransportError) as e:
        raise NetworkError("Network error listing models.") from e

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps({"_ts": time.time(), "data": data}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return data
