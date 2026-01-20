# Sentinel Integration Examples

This directory contains examples showing how to integrate Sentinel's intent-based secret management into popular AI agent frameworks.

## Why use Sentinel with AI Agents?

Autonomous agents often need access to sensitive credentials (API keys, DB passwords, cloud tokens). Hardcoding these in environment variables or configuration files is risky, especially when agents have non-deterministic behavior.

Sentinel provides:
1. **Isolation**: Agents only get secrets when they explicitly request them.
2. **Intent Context**: Every request includes a description of *why* the secret is needed.
3. **Human-in-the-loop**: Sensitive requests can be held for human approval.
4. **Auditability**: Complete logs of all secret access with full context.

## Available Examples

| Framework | Directory | Description |
|-----------|-----------|-------------|
| **LangChain** | [`/langchain`](./langchain) | Using Sentinel with LangChain Tools and ReAct agents. |
| **CrewAI** | [`/crewai`](./crewai) | Integrating Sentinel into CrewAI tasks and agent workflows. |

## Quick Start (Mock Environment)

To try these examples without a full agent framework setup:

1. **Start Sentinel Server**:
   ```bash
   cd ..
   bun install
   bun run src/server.ts
   ```

2. **Run an Example**:
   ```bash
   # In another terminal
   cd examples/langchain
   python langchain_sentinel.py
   ```

## Creating Your Own Integration

All examples in this directory use `sentinel_utils.py`, a lightweight Python wrapper for the Sentinel REST API. You can copy this file into your project to get started quickly before the official Python SDK is released.

### Basic Pattern

```python
from sentinel_utils import SentinelClient

client = SentinelClient(base_url="http://localhost:3000", api_token="...", agent_id="...")

result = client.request_with_polling(
    resource_id="github_token",
    intent={
        "task_id": "DEPLOY-123",
        "summary": "Pushing release tags",
        "description": "Agent needs to tag the new release on GitHub"
    }
)

if result['status'] == 'APPROVED':
    secret = result['secret']['value']
    # Use the secret...
```
