from src.checkout_api import authorize_checkout


class StubSessions:
    def __init__(self, outcome: bool | Exception) -> None:
        self.outcome = outcome

    def validate(self, token: str) -> bool:
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


# ---------------------------------------------------------------------------
# Happy-path tests
# ---------------------------------------------------------------------------

def test_active_session_authorizes_checkout() -> None:
    assert authorize_checkout(
        "token",
        sessions=StubSessions(True),
        correlation_id="req-100",
    ) == {
        "status": 200,
        "body": {"authorized": True},
    }


# ---------------------------------------------------------------------------
# Timeout / 503 tests
# ---------------------------------------------------------------------------

def test_timeout_is_exposed_as_service_unavailable() -> None:
    result = authorize_checkout(
        "token",
        sessions=StubSessions(TimeoutError()),
        correlation_id="req-200",
    )
    assert result["status"] == 503
    assert result["body"]["error"] == "authentication_unavailable"  # type: ignore[index]


def test_timeout_response_includes_retryable_true() -> None:
    """503 body must signal that the client may safely retry."""
    result = authorize_checkout(
        "token",
        sessions=StubSessions(TimeoutError()),
        correlation_id="req-201",
    )
    assert result["body"]["retryable"] is True  # type: ignore[index]


def test_timeout_response_includes_correlation_id() -> None:
    """503 body must echo the correlation_id supplied by the caller."""
    result = authorize_checkout(
        "token",
        sessions=StubSessions(TimeoutError()),
        correlation_id="req-202",
    )
    assert result["body"]["correlation_id"] == "req-202"  # type: ignore[index]


def test_timeout_correlation_id_is_caller_supplied() -> None:
    """Different callers receive their own correlation_id in the response."""
    result_a = authorize_checkout(
        "token",
        sessions=StubSessions(TimeoutError()),
        correlation_id="req-a",
    )
    result_b = authorize_checkout(
        "token",
        sessions=StubSessions(TimeoutError()),
        correlation_id="req-b",
    )
    assert result_a["body"]["correlation_id"] == "req-a"  # type: ignore[index]
    assert result_b["body"]["correlation_id"] == "req-b"  # type: ignore[index]

