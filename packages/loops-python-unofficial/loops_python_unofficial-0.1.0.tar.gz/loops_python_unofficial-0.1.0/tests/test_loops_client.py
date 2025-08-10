from __future__ import annotations

from typing import Any, Dict
import json

import httpx
import pytest

from loops_unofficial import APIError, LoopsClient, RateLimitExceededError, ValidationError


class MockTransport(httpx.BaseTransport):
    def __init__(self, handler):
        self._handler = handler

    def handle_request(self, request: httpx.Request) -> httpx.Response:  # type: ignore[override]
        return self._handler(request)


def make_client(handler) -> LoopsClient:
    client = LoopsClient("test-api-key")
    client._client = httpx.Client(transport=MockTransport(handler))  # type: ignore[attr-defined]
    return client


def json_response(
    status_code: int, json: Dict[str, Any], headers: Dict[str, str] | None = None
) -> httpx.Response:
    return httpx.Response(
        status_code,
        headers={"Content-Type": "application/json", **(headers or {})},
        json=json,
    )


def test_constructor_requires_api_key() -> None:
    with pytest.raises(ValueError):
        LoopsClient("")


def test_test_api_key_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/v1/api-key")
        return json_response(200, {"success": True, "teamName": "Test Team"})

    client = make_client(handler)
    assert client.test_api_key() == {"success": True, "teamName": "Test Team"}


def test_test_api_key_invalid() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return json_response(401, {"error": "Invalid API key"})

    client = make_client(handler)
    with pytest.raises(APIError):
        client.test_api_key()


def test_rate_limit_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429, headers={"x-ratelimit-limit": "10", "x-ratelimit-remaining": "0"}
        )

    client = make_client(handler)
    with pytest.raises(RateLimitExceededError):
        client.test_api_key()


def test_create_contact_success_minimal() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path.endswith("/v1/contacts/create")
        assert json.loads(request.content.decode()) == {"email": "test@example.com"}
        return json_response(200, {"success": True, "id": "123"})

    client = make_client(handler)
    resp = client.create_contact("test@example.com")
    assert resp == {"success": True, "id": "123"}


def test_create_contact_invalid_email() -> None:
    client = LoopsClient("k")
    with pytest.raises(TypeError):
        client.create_contact("not-an-email")


def test_update_contact_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path.endswith("/v1/contacts/update")
        assert json.loads(request.content.decode()) == {
            "email": "test@example.com",
            "firstName": "John",
            "lastName": "Doe",
            "mailingLists": {"newsletter_id": True},
        }
        return json_response(200, {"success": True, "id": "123"})

    client = make_client(handler)
    resp = client.update_contact(
        "test@example.com", {"firstName": "John", "lastName": "Doe"}, {"newsletter_id": True}
    )
    assert resp == {"success": True, "id": "123"}


def test_find_contact_validation() -> None:
    client = LoopsClient("k")
    with pytest.raises(ValidationError):
        client.find_contact()
    with pytest.raises(ValidationError):
        client.find_contact(email="a@b.com", user_id="x")


def test_find_contact_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("email") == "hello@gmail.com"
        return json_response(200, {"data": []})

    client = make_client(handler)
    client.find_contact(email="hello@gmail.com")


def test_delete_contact_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert json.loads(request.content.decode()) == {"email": "hello@gmail.com"}
        return json_response(200, {"success": True, "message": "Contact deleted."})

    client = make_client(handler)
    resp = client.delete_contact(email="hello@gmail.com")
    assert resp["success"] is True


def test_create_contact_property_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert json.loads(request.content.decode()) == {"name": "customField", "type": "string"}
        return json_response(200, {"success": True})

    client = make_client(handler)
    resp = client.create_contact_property("customField", "string")
    assert resp["success"] is True


def test_get_contact_properties() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("list") == "all"
        return json_response(200, [])

    client = make_client(handler)
    client.get_contact_properties()


def test_get_mailing_lists() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return json_response(200, [])

    client = make_client(handler)
    client.get_mailing_lists()


def test_send_event_success_with_headers() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("Idempotency-Key") == "unique_key_123"
        assert json.loads(request.content.decode()) == {
            "eventName": "test_event",
            "email": "test@example.com",
        }
        return json_response(200, {"success": True})

    client = make_client(handler)
    resp = client.send_event(
        email="test@example.com",
        event_name="test_event",
        headers={"Idempotency-Key": "unique_key_123"},
    )
    assert resp["success"] is True


def test_send_event_validation() -> None:
    client = LoopsClient("k")
    with pytest.raises(ValidationError):
        client.send_event(event_name="x")


def test_send_transactional_email_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path.endswith("/v1/transactional")
        assert json.loads(request.content.decode()) == {
            "transactionalId": "email_123",
            "email": "test@example.com",
            "dataVariables": {"name": "John"},
        }
        return json_response(200, {"success": True})

    client = make_client(handler)
    resp = client.send_transactional_email(
        transactional_id="email_123", email="test@example.com", data_variables={"name": "John"}
    )
    assert resp["success"] is True


def test_get_transactional_emails_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.get("perPage") == "20"
        return json_response(200, {"pagination": {"totalResults": 0}, "data": []})

    client = make_client(handler)
    resp = client.get_transactional_emails()
    assert isinstance(resp.get("data"), list)
