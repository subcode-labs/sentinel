# Sentinel x PydanticAI Integration

This example demonstrates how to use Sentinel with [PydanticAI](https://ai.pydantic.dev/) to securely manage secrets.

It showcases two key patterns:
1.  **Bootstrapping:** Using Sentinel to fetch the LLM's API Key (e.g., `OPENAI_API_KEY`) before the agent starts.
2.  **Just-in-Time Access:** Using dependency injection to pass the Sentinel Client into tools, allowing them to request secrets dynamically only when needed.

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Sentinel Server** (or use Sentinel Cloud).

3.  **Run the example:**

    ```bash
    # Ensure SENTINEL_URL and SENTINEL_TOKEN are set if not using defaults
    export SENTINEL_URL="http://localhost:3000/api"
    export SENTINEL_TOKEN="your_sentinel_token"
    
    python pydantic_ai_sentinel.py
    ```

## How it Works

The example defines a `SentinelDeps` dataclass that holds the authenticated Sentinel client. This is passed to the agent via `deps_type`.

When the agent calls the `get_weather` tool, it receives the `SentinelClient` via the context (`ctx.deps.sentinel`). It then performs a JIT request for the API key needed for that specific tool call.
