"""HTTP helper utilities for LLM providers.

Provides a shared request-with-retries helper for providers using httpx.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Optional

import httpx


async def request_with_retries(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    retries: int = 3,
    backoff_base: float = 1.0,
    retry_on: tuple[type[Exception], ...] = (
        httpx.ConnectError,
        httpx.ReadTimeout,
        httpx.RemoteProtocolError,
        httpx.HTTPStatusError,
    ),
    request_builder: Optional[Callable[[], dict[str, Any]]] = None,
    **kwargs: Any,
) -> httpx.Response:
    """Perform an HTTP request with simple exponential backoff and retries.

    If request_builder is provided, it will be called for each attempt to build
    fresh kwargs (e.g., streams or non-reusable bodies).
    """
    last_exc: Optional[Exception] = None
    for attempt in range(retries):
        try:
            call_kwargs = {**kwargs}
            if request_builder is not None:
                call_kwargs.update(request_builder() or {})
            resp = await client.request(method.upper(), url, **call_kwargs)
            resp.raise_for_status()
            return resp
        except retry_on as exc:
            last_exc = exc
            if attempt < retries - 1:
                await asyncio.sleep(backoff_base * (2**attempt))
                continue
            raise
    # If we exit the loop without returning or raising, re-raise last
    assert last_exc is not None
    raise last_exc

