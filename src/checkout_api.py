"""Customer-facing checkout authorization boundary."""

from __future__ import annotations

from typing import Protocol


class SessionGateway(Protocol):
    def validate(self, token: str) -> bool: ...


def authorize_checkout(
    token: str,
    *,
    sessions: SessionGateway,
    correlation_id: str,
) -> dict[str, object]:
    """Translate session validation into the public checkout response.

    Args:
        token: Session token to validate.
        sessions: Gateway to the session-validation service.
        correlation_id: Opaque request identifier included in timeout error
            responses so support tooling and clients can correlate incidents.

    Returns:
        A dict with ``status`` and ``body`` keys.  On timeout the body
        contains ``error``, ``retryable`` and ``correlation_id``.
    """

    try:
        active = sessions.validate(token)
    except TimeoutError:
        return {
            "status": 503,
            "body": {
                "error": "authentication_unavailable",
                "retryable": True,
                "correlation_id": correlation_id,
            },
        }

    if not active:
        return {"status": 401, "body": {"error": "invalid_session"}}
    return {"status": 200, "body": {"authorized": True}}

