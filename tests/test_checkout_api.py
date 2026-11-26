from src.checkout_api import authorize_checkout


class StubSessions:
    def __init__(self, outcome: bool | Exception) -> None:
        self.outcome = outcome

    def validate(self, token: str) -> bool:
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class TrackingSessions:
    """Stub that records whether validate was called."""

    def __init__(self) -> None:
        self.called = False

    def validate(self, token: str) -> bool:
        self.called = True
        return True


def test_active_session_authorizes_checkout() -> None:
    assert authorize_checkout("token", sessions=StubSessions(True)) == {
        "status": 200,
        "body": {"authorized": True},
    }


def test_timeout_is_exposed_as_service_unavailable() -> None:
    assert authorize_checkout("token", sessions=StubSessions(TimeoutError())) == {
        "status": 503,
        "body": {"error": "authentication_unavailable"},
    }


def test_empty_token_returns_400_without_gateway_call() -> None:
    stub = TrackingSessions()
    result = authorize_checkout("", sessions=stub)
    assert result == {"status": 400, "body": {"error": "missing_session_token"}}
    assert not stub.called


def test_whitespace_only_token_returns_400_without_gateway_call() -> None:
    stub = TrackingSessions()
    result = authorize_checkout("   ", sessions=stub)
    assert result == {"status": 400, "body": {"error": "missing_session_token"}}
    assert not stub.called
