"""Customer-facing checkout authorization boundary."""

from __future__ import annotations

from typing import Protocol


class SessionGateway(Protocol):
    def validate(self, token: str) -> bool: ...


def authorize_checkout(token: str, *, sessions: SessionGateway) -> dict[str, object]:
    """Translate session validation into the public checkout response."""

    try:
        active = sessions.validate(token)
    except TimeoutError:
        return {
            "status": 503,
            "body": {"error": "authentication_unavailable"},
        }

    if not active:
        return {"status": 401, "body": {"error": "invalid_session"}}
    return {"status": 200, "body": {"authorized": True}}

