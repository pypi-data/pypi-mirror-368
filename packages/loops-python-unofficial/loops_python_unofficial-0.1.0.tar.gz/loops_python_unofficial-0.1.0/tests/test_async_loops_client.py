from __future__ import annotations

import asyncio
from typing import Any, Dict
import json

import httpx
import pytest

from loops_unofficial import APIError
from loops_unofficial import AsyncLoopsClient as AClient
from loops_unofficial import RateLimitExceededError, ValidationError


class MockAsyncTransport(httpx.AsyncBaseTransport):
    def __init__(self, handler):
        self._handler = handler

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        return await self._handler(request)


def json_response(
    status_code: int, json: Dict[str, Any], headers: Dict[str, str] | None = None
) -> httpx.Response:
    return httpx.Response(
        status_code,
        headers={"Content-Type": "application/json", **(headers or {})},
        json=json,
    )


@pytest.mark.asyncio
async def test_async_test_api_key_success() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/v1/api-key")
        return json_response(200, {"success": True, "teamName": "Async Team"})

    client = AClient("test-api-key")
    client._client = httpx.AsyncClient(transport=MockAsyncTransport(handler))  # type: ignore[attr-defined]
    assert await client.test_api_key() == {"success": True, "teamName": "Async Team"}
    await client.aclose()


@pytest.mark.asyncio
async def test_async_rate_limit() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429, headers={"x-ratelimit-limit": "10", "x-ratelimit-remaining": "0"}
        )

    client = AClient("k")
    client._client = httpx.AsyncClient(transport=MockAsyncTransport(handler))  # type: ignore[attr-defined]
    with pytest.raises(RateLimitExceededError):
        await client.test_api_key()
    await client.aclose()


@pytest.mark.asyncio
async def test_async_send_event_validation() -> None:
    client = AClient("k")
    with pytest.raises(ValidationError):
        await client.send_event(event_name="x")
    await client.aclose()


@pytest.mark.asyncio
async def test_async_send_transactional_email_error() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return json_response(404, {"success": False, "message": "Not found"})

    client = AClient("k")
    client._client = httpx.AsyncClient(transport=MockAsyncTransport(handler))  # type: ignore[attr-defined]
    with pytest.raises(APIError):
        await client.send_transactional_email(transactional_id="x", email="a@b.com")
    await client.aclose()
