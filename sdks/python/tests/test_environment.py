import pytest
import respx
from httpx import Response
import json

from sentinel_client import SentinelClient, AccessIntent


@pytest.fixture
def intent():
    return AccessIntent(
        summary="Test Access", description="Testing the SDK", task_id="task-123"
    )


@respx.mock
def test_request_secret_with_default_environment(intent):
    client = SentinelClient(
        base_url="http://test-server", api_token="test-token", agent_id="test-agent"
    )

    # Defaults to production
    route = respx.post("http://test-server/v1/access/request").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req_123",
                "status": "APPROVED",
                "secret": {"type": "v", "value": "s", "expires_at": "t"},
            },
        )
    )

    client.request_secret("resource-1", intent)

    assert route.called
    request_body = json.loads(route.calls.last.request.read().decode("utf-8"))
    assert request_body["environment"] == "production"


@respx.mock
def test_request_secret_with_init_environment(intent):
    client = SentinelClient(
        base_url="http://test-server",
        api_token="test-token",
        agent_id="test-agent",
        environment="staging",
    )

    route = respx.post("http://test-server/v1/access/request").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req_123",
                "status": "APPROVED",
                "secret": {"type": "v", "value": "s", "expires_at": "t"},
            },
        )
    )

    client.request_secret("resource-1", intent)

    assert route.called
    request_body = json.loads(route.calls.last.request.read().decode("utf-8"))
    assert request_body["environment"] == "staging"


@respx.mock
def test_request_secret_with_override_environment(intent):
    client = SentinelClient(
        base_url="http://test-server",
        api_token="test-token",
        agent_id="test-agent",
        environment="staging",
    )

    route = respx.post("http://test-server/v1/access/request").mock(
        return_value=Response(
            200,
            json={
                "request_id": "req_123",
                "status": "APPROVED",
                "secret": {"type": "v", "value": "s", "expires_at": "t"},
            },
        )
    )

    # Override with 'dev'
    client.request_secret("resource-1", intent, environment="dev")

    assert route.called
    request_body = json.loads(route.calls.last.request.read().decode("utf-8"))
    assert request_body["environment"] == "dev"


@respx.mock
def test_fetch_secrets_with_environment():
    client = SentinelClient(
        base_url="http://test-server",
        api_token="test-token",
        agent_id="test-agent",
        environment="staging",
    )

    route = respx.get("http://test-server/v1/secrets").mock(
        return_value=Response(200, json={})
    )

    client.fetch_secrets()

    assert route.called
    # httpx stores params in the query string, accessible via url.params in newer httpx or url.query
    # Using simple check
    assert "environment=staging" in str(route.calls.last.request.url)


@respx.mock
def test_list_resources_with_environment():
    client = SentinelClient(
        base_url="http://test-server",
        api_token="test-token",
        agent_id="test-agent",
        environment="staging",
    )

    route = respx.get("http://test-server/v1/resources").mock(
        return_value=Response(200, json=[])
    )

    client.list_resources()

    assert route.called
    assert "environment=staging" in str(route.calls.last.request.url)
