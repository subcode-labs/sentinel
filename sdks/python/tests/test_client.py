import pytest
import respx
from httpx import Response

from sentinel_client import SentinelClient, AccessIntent, AccessStatus
from sentinel_client.exceptions import SentinelDeniedError, SentinelTimeoutError


@pytest.fixture
def client():
    return SentinelClient(
        base_url="http://test-server", api_token="test-token", agent_id="test-agent"
    )


@pytest.fixture
def intent():
    return AccessIntent(
        summary="Test Access", description="Testing the SDK", task_id="task-123"
    )


@respx.mock
def test_request_secret_approved_immediately(client, intent):
    respx.post("http://test-server/v1/access/request").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req_123",
                "status": "APPROVED",
                "secret": {
                    "type": "managed_secret",
                    "value": "super_secret_value",
                    "expires_at": "2024-01-01T00:00:00Z",
                },
            },
        )
    )

    secret = client.request_secret("resource-1", intent)
    assert secret.value == "super_secret_value"
    assert secret.type == "managed_secret"


@respx.mock
def test_request_secret_denied_immediately(client, intent):
    respx.post("http://test-server/v1/access/request").mock(
        return_value=Response(
            403,
            json={
                "request_id": "req_123",
                "status": "DENIED",
                "reason": "Forbidden resource",
            },
        )
    )

    with pytest.raises(SentinelDeniedError, match="Forbidden resource"):
        client.request_secret("resource-forbidden", intent)


@respx.mock
def test_request_secret_polling_approval(client, intent):
    # Initial request -> Pending
    route_post = respx.post("http://test-server/v1/access/request").mock(
        return_value=Response(
            202,
            json={
                "request_id": "req_pending",
                "status": "PENDING_APPROVAL",
                "polling_url": "/v1/access/requests/req_pending",
            },
        )
    )

    # Poll 1 -> Pending
    route_get_1 = respx.get("http://test-server/v1/access/requests/req_pending").mock(
        side_effect=[
            Response(
                200, json={"request_id": "req_pending", "status": "PENDING_APPROVAL"}
            ),
            Response(
                200,
                json={
                    "request_id": "req_pending",
                    "status": "APPROVED",
                    "secret": {
                        "type": "managed_secret",
                        "value": "delayed_secret",
                        "expires_at": "2024-01-01T00:00:00Z",
                    },
                },
            ),
        ]
    )

    secret = client.request_secret(
        "resource-sensitive",
        intent,
        polling_interval=0.1,  # Fast polling for test
        polling_timeout=2.0,
    )

    assert secret.value == "delayed_secret"
    assert route_post.called
    assert route_get_1.call_count == 2


@respx.mock
def test_request_secret_polling_timeout(client, intent):
    respx.post("http://test-server/v1/access/request").mock(
        return_value=Response(
            202, json={"request_id": "req_timeout", "status": "PENDING_APPROVAL"}
        )
    )

    respx.get("http://test-server/v1/access/requests/req_timeout").mock(
        return_value=Response(
            200, json={"request_id": "req_timeout", "status": "PENDING_APPROVAL"}
        )
    )

    with pytest.raises(SentinelTimeoutError):
        client.request_secret(
            "resource-sensitive", intent, polling_interval=0.1, polling_timeout=0.5
        )
