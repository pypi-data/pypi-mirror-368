from __future__ import annotations

from typing import Mapping, TypedDict, Union


# Scalar unions mirroring the JS SDK types
Scalar = Union[str, int, float, bool]
NullableScalar = Union[str, int, float, bool, None]


# Record-like mappings for request payloads
ContactProperties = Mapping[str, NullableScalar]
EventProperties = Mapping[str, Scalar]
TransactionalVariables = Mapping[str, Union[str, int, float]]
MailingLists = Mapping[str, bool]


class TransactionalAttachment(TypedDict, total=False):
    filename: str
    contentType: str
    data: str


__all__ = [
    "Scalar",
    "NullableScalar",
    "ContactProperties",
    "EventProperties",
    "TransactionalVariables",
    "MailingLists",
    "TransactionalAttachment",
]
