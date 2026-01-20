# Sentinel + LlamaIndex Example

This example demonstrates how to integrate Sentinel into a LlamaIndex application to securely manage API keys.

## How it works

1. The script initializes the `SentinelClient`.
2. Before setting up LlamaIndex, it requests the `openai_api_key` from Sentinel.
3. Sentinel logs the intent and enforces policy (e.g., approval workflows).
4. Once the key is retrieved, it is injected into the environment for LlamaIndex to use.
5. The application proceeds to create a VectorStoreIndex and answer a query.

## Prerequisites

- Python 3.8+
- Sentinel Server running locally (or Cloud URL)
- Sentinel Python SDK (`sentinel-client`)

## Running the example

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo
# Assumes Sentinel is running at http://localhost:3000
# and has a secret named 'openai_api_key' (or will auto-generate one in dev mode)
python llamaindex_sentinel.py
```

## Note on API Keys

In development mode (`SENTINEL_ENV=dev` or default), Sentinel will auto-generate a mock secret (e.g., `secret_v1_...`) if one doesn't exist. This will cause the LlamaIndex OpenAI call to fail with a 401 error, which is expected behavior for this demo unless you manually update the secret value in the Sentinel database to a real OpenAI key.

## Setup in Sentinel

Ensure you have:
1. A Project created.
2. A Secret named `openai_api_key`.
3. An Agent (or use the default token).
