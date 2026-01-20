# Sentinel x LangGraph Integration

This example demonstrates how to integrate **Sentinel** into a **LangGraph** agent.

LangGraph allows for building stateful, multi-actor applications with LLMs. In this example, we build a simple ReAct-style agent where one of the tools requires a secret API key. Instead of providing the key to the agent at startup, the tool requests it **just-in-time** from Sentinel.

## Features

- **Just-in-Time Access:** The agent does not hold secrets in its state.
- **Granular Control:** Access is requested only when the specific tool is invoked.
- **Audit Trail:** Sentinel logs the intent and task ID associated with the access request.

## Prerequisites

- Python 3.9+
- A running instance of Sentinel (or Sentinel Cloud)
- `OPENAI_API_KEY` (optional, for full agent execution)

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

```bash
# Sentinel Configuration
export SENTINEL_URL="http://localhost:3000"
export SENTINEL_TOKEN="your_sentinel_token"

# OpenAI (Optional)
export OPENAI_API_KEY="sk-..."
```

## Running the Example

```bash
python main.py
```

## How it works

1. **State Graph:** We define a standard LangGraph `StateGraph` with a `chatbot` node and a `tools` node.
2. **Secure Tool:** We define `secure_search` as a standard LangChain tool.
3. **Secret Retrieval:** Inside the tool, we use `SentinelClient` to fetch `secure_db_key`.
   - If the key requires approval, the tool execution effectively pauses (or polls) until approval is granted.
   - The key is used immediately and then discarded from scope (returned in the result string, but not stored in the agent's persistent state).

```python
@tool
def secure_search(query: str):
    # Fetch key just-in-time
    api_key = get_secure_key("secure_db_key")
    return do_search(query, api_key)
```
