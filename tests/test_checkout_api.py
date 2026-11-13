from src.checkout_api import authorize_checkout


class StubSessions:
    def __init__(self, outcome: bool | Exception) -> None:
        self.outcome = outcome
        self.received_correlation_id: str | None = None

    def validate(self, token: str, *, correlation_id: str | None = None) -> bool:
        self.received_correlation_id = correlation_id
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def test_active_session_authorizes_checkout() -> None:
    assert authorize_checkout("token", sessions=StubSessions(True)) == {
        "status": 200,
        "body": {"authorized": True},
    }


def test_timeout_is_exposed_as_service_unavailable() -> None:
    assert authorize_checkout(
        "token",
        sessions=StubSessions(TimeoutError()),
        correlation_id="req-abc",
    ) == {
        "status": 503,
        "body": {"error": "authentication_unavailable", "correlation_id": "req-abc"},
    }


def test_correlation_id_forwarded_to_gateway() -> None:
    stub = StubSessions(True)
    authorize_checkout("token", sessions=stub, correlation_id="req-xyz")
    assert stub.received_correlation_id == "req-xyz"


def test_timeout_without_correlation_id_includes_none() -> None:
    assert authorize_checkout("token", sessions=StubSessions(TimeoutError())) == {
        "status": 503,
        "body": {"error": "authentication_unavailable", "correlation_id": None},
    }
