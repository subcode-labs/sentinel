# Sentinel Python SDK

The official Python client for the Sentinel Secret Management system.

## Installation

```bash
pip install sentinel-client
```

## Usage

```python
from sentinel_client import SentinelClient, AccessIntent

# 1. Initialize the client
client = SentinelClient(
    base_url="http://localhost:3000",
    api_token="sentinel_dev_key",
    agent_id="my-agent-001"
)

# 2. Define your intent
intent = AccessIntent(
    summary="Accessing production database",
    description="Running nightly data migration",
    task_id="task-889"
)

# 3. Request a secret
# This handles automatic polling if approval is required.
try:
    secret = client.request_secret(
        resource_id="prod/db/read-write",
        intent=intent,
        ttl_seconds=3600
    )
    print(f"Secret acquired: {secret.value}")
    
except Exception as e:
    print(f"Access denied or failed: {e}")
```

## Features

- **Type-safe:** Uses Pydantic models for strict validation.
- **Async Polling:** Automatically handles `PENDING_APPROVAL` status by polling the server.
- **Error Handling:** Custom exceptions for specific failure modes (Auth, Network, Denial, Timeout).

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## CLI Usage

The SDK includes a command-line interface (CLI) for quick access to secrets.

```bash
# Set environment variables (optional but recommended)
export SENTINEL_URL="http://localhost:3000"
export SENTINEL_TOKEN="your_token"
export AGENT_ID="your_agent_id"

# Request a secret
sentinel get my-secret

# Output as .env format
sentinel get my-secret --format env >> .env

# Request with specific intent
sentinel get prod/db --intent "Fixing prod incident"
```
