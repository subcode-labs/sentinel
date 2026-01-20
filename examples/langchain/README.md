# Sentinel + LangChain Example

This example demonstrates how to integrate Sentinel into a LangChain-based agent using custom Tools.

## How it works

1. We define a helper function `get_secure_key` that uses `SentinelClient` to request a secret.
2. We wrap this function inside a LangChain `Tool`.
3. When the agent decides it needs to search GitHub, it invokes the tool.
4. The tool triggers a Sentinel request with an "intent" description.
5. If the secret requires approval, Sentinel pauses the request and the tool polls until a human approves/denies it.

## Prerequisites

- Python 3.8+
- `requests` library
- `langchain` and `langchain-openai` (optional, for full agent demo)

## Running the example

```bash
# Install dependencies
pip install requests langchain langchain-openai

# Set your OpenAI key (optional)
export OPENAI_API_KEY="sk-..."

# Run the demo
python langchain_sentinel.py
```

If `OPENAI_API_KEY` is not set, the script will run a mock execution of the secure tool to show the Sentinel handshake.
