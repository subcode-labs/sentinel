# Sentinel x Smolagents Integration

This example demonstrates how to give a **HuggingFace Smolagents** `CodeAgent` access to secrets managed by Sentinel.

By exposing Sentinel as a tool, your agent can autonomously retrieve API keys and credentials "just-in-time" when it writes code that requires them, rather than having all secrets injected into the process environment at startup.

## Prerequisites

1.  **Sentinel Cloud** or **Self-Hosted Sentinel** instance running.
2.  Python 3.8+

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Set your environment variables:
    ```bash
    # Sentinel Config
    export SENTINEL_URL="http://localhost:3000" # or your cloud URL
    export SENTINEL_TOKEN="your_sentinel_token"

    # HuggingFace Token (for the model)
    export HUGGING_FACE_HUB_TOKEN="hf_..."
    ```

3.  Run the example:
    ```bash
    python main.py
    ```

## How it Works

The integration is a simple `@tool` definition that wraps the Sentinel SDK:

```python
@tool
def get_secret(key: str) -> str:
    """
    Securely retrieves a secret from the Sentinel vault.
    Use this tool when you need an API key...
    """
    response = sentinel.get_secret(key)
    return response.value
```

The `CodeAgent` can then generate Python code that calls this function:

```python
# Agent generated code
key = get_secret("OPENAI_API_KEY")
headers = {"Authorization": f"Bearer {key}"}
# ... perform request ...
```
