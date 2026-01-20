# Sentinel Integration Examples

This directory contains examples showing how to integrate Sentinel's intent-based secret management into popular AI agent frameworks.

## Why use Sentinel with AI Agents?

Autonomous agents often need access to sensitive credentials (API keys, DB passwords, cloud tokens). Hardcoding these in environment variables or configuration files is risky, especially when agents have non-deterministic behavior.

Sentinel provides:
1. **Isolation**: Agents only get secrets when they explicitly request them.
2. **Intent Context**: Every request includes a description of *why* the secret is needed.
3. **Human-in-the-loop**: Sensitive requests can be held for human approval.
4. **Auditability**: Complete logs of all secret access with full context.

## Prerequisites

You need the Sentinel Python SDK (`sentinel-client`) and the respective framework libraries.

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: This installs the `sentinel-client` SDK from the local `../sdk/python` directory.*

2. **Start Sentinel Server**:
   Ensure you have the Sentinel server running locally (or set `SENTINEL_URL` to your cloud instance).
   ```bash
   cd ../..
   bun install
   bun run src/server.ts
   ```

## Available Examples

| Framework | Directory | Description |
|-----------|-----------|-------------|
| **LangChain** | [`/langchain`](./langchain) | Using Sentinel with LangChain Tools and ReAct agents. |
| **CrewAI** | [`/crewai`](./crewai) | Integrating Sentinel into CrewAI tasks and agent workflows. |
| **Vercel AI SDK** | [`/vercel-ai-sdk`](./vercel-ai-sdk) | **(TypeScript)** Integrating Sentinel with Vercel AI SDK Tools. |
| **Next.js App Router** | [`/nextjs-app-router`](./nextjs-app-router) | **(TypeScript)** Using Sentinel in Server Actions for JIT access. |

## Running the Examples

### Next.js App Router

See the [README](./nextjs-app-router/README.md) in the directory for setup instructions. This example requires a Next.js environment to run fully, but demonstrates the code structure.

### Vercel AI SDK (TypeScript)

This example shows how to use Sentinel to secure tools in the Vercel AI SDK.

```bash
cd vercel-ai-sdk
# Ensure dependencies are installed
bun install
# Run the example
bun run index.ts
```

### LangChain

This example demonstrates a ReAct agent that uses a custom Tool to request a GitHub token from Sentinel.

```bash
cd langchain
# Optional: Set OPENAI_API_KEY to run the real agent loop
export OPENAI_API_KEY=sk-...
python langchain_sentinel.py
```

### CrewAI

This example demonstrates a CrewAI agent requesting a production API key as part of a secure task.

```bash
cd crewai
python crewai_sentinel.py
```

## Integration Pattern

The core pattern involves using the `SentinelClient` to request a secret with a specific "intent". If the request requires approval, the SDK handles the polling automatically.

```python
from sentinel_client import SentinelClient, AccessIntent

client = SentinelClient(
    base_url="http://localhost:3000",
    api_token="...",
    agent_id="my-agent"
)

# 1. Define the intent
intent = AccessIntent(
    summary="Pushing release tags",
    description="Agent needs to tag the new release on GitHub",
    task_id="DEPLOY-123"
)

# 2. Request the secret (blocks if pending approval)
secret = client.request_secret(
    resource_id="github_token",
    intent=intent
)

print(f"Got secret: {secret.value}")
```
