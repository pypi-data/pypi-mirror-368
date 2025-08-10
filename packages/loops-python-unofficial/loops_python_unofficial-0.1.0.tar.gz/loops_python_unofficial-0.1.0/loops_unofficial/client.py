from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional

import httpx
from .types import (
    ContactProperties,
    EventProperties,
    MailingLists,
    TransactionalAttachment,
    TransactionalVariables,
)


class RateLimitExceededError(Exception):
    def __init__(self, limit: int, remaining: int) -> None:
        super().__init__(f"Rate limit of {limit} requests per second exceeded.")
        self.limit = int(limit)
        self.remaining = int(remaining)


class APIError(Exception):
    def __init__(self, status_code: int, json: Mapping[str, Any]) -> None:  # noqa: A002
        message: Optional[str] = None
        if isinstance(json.get("error"), dict) and isinstance(json["error"].get("message"), str):
            message = json["error"]["message"]
        elif isinstance(json.get("error"), str):
            message = json["error"]
        elif isinstance(json.get("message"), str):
            message = json["message"]

        super().__init__(f"{status_code}{f' - {message}' if message else ''}")
        self.status_code = status_code
        self.json = json


class ValidationError(Exception):
    pass


@dataclass
class _QueryOptions:
    path: str
    method: str = "GET"
    payload: Optional[Mapping[str, Any]] = None
    params: Optional[Mapping[str, str]] = None
    headers: Optional[Mapping[str, str]] = None


class LoopsClient:
    api_root: str = "https://app.loops.so/api/"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self._client = httpx.Client(timeout=30.0)

    def close(self) -> None:
        self._client.close()

    def _make_query(self, options: _QueryOptions) -> Dict[str, Any]:
        headers: MutableMapping[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if options.headers:
            for key, value in options.headers.items():
                if value:
                    headers[key] = value

        # Build URL with simple string concatenation to avoid URL join quirks
        url = f"{self.api_root}{options.path}"

        if options.method == "GET":
            params = options.params or None
            response = self._client.get(url, headers=headers, params=params)
        else:
            response = self._client.request(
                options.method,
                url,
                headers=headers,
                params=None,
                json=options.payload or None,
            )

        if response.status_code == 429:
            limit = int(response.headers.get("x-ratelimit-limit", "10"))
            remaining = int(response.headers.get("x-ratelimit-remaining", "10"))
            raise RateLimitExceededError(limit, remaining)

        if not response.is_success:
            data = self._safe_json(response)
            raise APIError(response.status_code, data)

        return self._safe_json(response)

    @staticmethod
    def _safe_json(response: httpx.Response) -> Dict[str, Any]:
        try:
            data = response.json()
            if isinstance(data, dict):
                return data
            return {"data": data}
        except Exception:  # pragma: no cover - extremely unlikely for Loops API
            return {"success": False, "message": "Invalid JSON response"}

    # Public API methods
    def test_api_key(self) -> Dict[str, Any]:
        return self._make_query(_QueryOptions(path="v1/api-key"))

    def create_contact(
        self,
        email: str,
        properties: ContactProperties | None = None,
        mailing_lists: MailingLists | None = None,
    ) -> Dict[str, Any]:
        if not isinstance(email, str) or "@" not in email:
            raise TypeError("Invalid email format")
        payload: Dict[str, Any] = {"email": email}
        if properties:
            payload.update(properties)
        if mailing_lists is not None:
            payload["mailingLists"] = dict(mailing_lists)
        return self._make_query(
            _QueryOptions(path="v1/contacts/create", method="POST", payload=payload)
        )

    def update_contact(
        self,
        email: str,
        properties: ContactProperties,
        mailing_lists: MailingLists | None = None,
    ) -> Dict[str, Any]:
        if not isinstance(email, str) or "@" not in email:
            raise TypeError("Invalid email format")
        payload: Dict[str, Any] = {"email": email}
        payload.update(properties)
        if mailing_lists is not None:
            payload["mailingLists"] = dict(mailing_lists)
        return self._make_query(
            _QueryOptions(path="v1/contacts/update", method="PUT", payload=payload)
        )

    def find_contact(
        self, *, email: str | None = None, user_id: str | None = None
    ) -> Dict[str, Any]:
        if email and user_id:
            raise ValidationError("Only one parameter is permitted.")
        if not email and not user_id:
            raise ValidationError("You must provide an `email` or `userId` value.")
        params: Dict[str, str] = {}
        if email:
            params["email"] = email
        if user_id:
            params["userId"] = user_id
        return self._make_query(_QueryOptions(path="v1/contacts/find", params=params))

    def delete_contact(
        self, *, email: str | None = None, user_id: str | None = None
    ) -> Dict[str, Any]:
        if email and user_id:
            raise ValidationError("Only one parameter is permitted.")
        if not email and not user_id:
            raise ValidationError("You must provide an `email` or `userId` value.")
        payload: Dict[str, str] = {}
        if email:
            payload["email"] = email
        if user_id:
            payload["userId"] = user_id
        return self._make_query(
            _QueryOptions(path="v1/contacts/delete", method="POST", payload=payload)
        )

    def create_contact_property(self, name: str, type_: str) -> Dict[str, Any]:
        if not name:
            raise TypeError("Property name is required")
        if type_ not in {"string", "number", "boolean", "date"}:
            raise TypeError("Invalid property type")
        return self._make_query(
            _QueryOptions(
                path="v1/contacts/properties",
                method="POST",
                payload={"name": name, "type": type_},
            )
        )

    def get_contact_properties(self, list_: str | None = None) -> Dict[str, Any]:
        return self._make_query(
            _QueryOptions(
                path="v1/contacts/properties",
                params={"list": list_ or "all"},
            )
        )

    def get_mailing_lists(self) -> Dict[str, Any]:
        return self._make_query(_QueryOptions(path="v1/lists"))

    def send_event(
        self,
        *,
        email: str | None = None,
        user_id: str | None = None,
        event_name: str,
        contact_properties: ContactProperties | None = None,
        event_properties: EventProperties | None = None,
        mailing_lists: MailingLists | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Dict[str, Any]:
        if not user_id and not email:
            raise ValidationError("You must provide an `email` or `userId` value.")
        payload: Dict[str, Any] = {"eventName": event_name}
        if contact_properties:
            payload.update(contact_properties)
        if event_properties is not None:
            payload["eventProperties"] = dict(event_properties)
        if mailing_lists is not None:
            payload["mailingLists"] = dict(mailing_lists)
        if email:
            payload["email"] = email
        if user_id:
            payload["userId"] = user_id
        return self._make_query(
            _QueryOptions(
                path="v1/events/send",
                method="POST",
                payload=payload,
                headers=headers,
            )
        )

    def send_transactional_email(
        self,
        *,
        transactional_id: str,
        email: str,
        add_to_audience: bool | None = None,
        data_variables: TransactionalVariables | None = None,
        attachments: list[TransactionalAttachment] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> Dict[str, Any]:
        if not transactional_id or not email:
            raise TypeError("transactional_id and email are required")
        payload: Dict[str, Any] = {
            "transactionalId": transactional_id,
            "email": email,
        }
        if add_to_audience is not None:
            payload["addToAudience"] = add_to_audience
        if data_variables is not None:
            payload["dataVariables"] = dict(data_variables)
        if attachments is not None:
            payload["attachments"] = list(attachments)
        return self._make_query(
            _QueryOptions(
                path="v1/transactional",
                method="POST",
                payload=payload,
                headers=headers,
            )
        )

    def get_transactional_emails(
        self, *, per_page: Optional[int] = None, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        params: Dict[str, str] = {"perPage": str(per_page or 20)}
        if cursor:
            params["cursor"] = cursor
        return self._make_query(_QueryOptions(path="v1/transactional", params=params))
