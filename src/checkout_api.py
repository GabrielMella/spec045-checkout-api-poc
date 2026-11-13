"""Customer-facing checkout authorization boundary."""

from __future__ import annotations

from typing import Protocol


class SessionGateway(Protocol):
    def validate(self, token: str, *, correlation_id: str | None = None) -> bool: ...


def authorize_checkout(
    token: str,
    *,
    sessions: SessionGateway,
    correlation_id: str | None = None,
) -> dict[str, object]:
    """Translate session validation into the public checkout response."""

    try:
        active = sessions.validate(token, correlation_id=correlation_id)
    except TimeoutError:
        return {
            "status": 503,
            "body": {
                "error": "authentication_unavailable",
                "correlation_id": correlation_id,
            },
        }

    if not active:
        return {"status": 401, "body": {"error": "invalid_session"}}
    return {"status": 200, "body": {"authorized": True}}

