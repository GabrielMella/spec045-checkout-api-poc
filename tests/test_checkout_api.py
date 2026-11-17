from src.checkout_api import authorize_checkout


class StubSessions:
    def __init__(self, outcome: bool | Exception) -> None:
        self.outcome = outcome

    def validate(self, token: str) -> bool:
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def test_active_session_authorizes_checkout() -> None:
    assert authorize_checkout("token", sessions=StubSessions(True)) == {
        "status": 200,
        "body": {"authorized": True},
    }


def test_timeout_is_exposed_as_service_unavailable() -> None:
    assert authorize_checkout("token", sessions=StubSessions(TimeoutError())) == {
        "status": 503,
        "body": {"error": "authentication_unavailable"},
        "headers": {"Retry-After": 30},
    }


def test_timeout_response_includes_retry_after() -> None:
    response = authorize_checkout("token", sessions=StubSessions(TimeoutError()))
    assert "Retry-After" in response["headers"]  # type: ignore[index]
    assert response["headers"]["Retry-After"] > 0  # type: ignore[index]
