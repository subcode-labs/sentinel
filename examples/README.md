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

| Framework | Language | Directory | Description |
|-----------|----------|-----------|-------------|
| **CrewAI** | Python | [`/crewai`](./crewai) | Integrating Sentinel into CrewAI tasks and agent workflows using Tools. |
| **LlamaIndex** | Python | [`/llamaindex`](./llamaindex) | Using Sentinel to secure RAG pipelines and vector stores. |
| **LangChain (Python)** | Python | [`/langchain`](./langchain) | Using Sentinel with LangChain Tools and ReAct agents. |
| **LangChain (JS)** | TypeScript | [`/langchain-js`](./langchain-js) | Using Sentinel with LangChain.js DynamicTools. |
| **Semantic Kernel** | Python | [`/semantic-kernel`](./semantic-kernel) | Injecting Sentinel secrets into Microsoft Semantic Kernel. |
| **AutoGen** | Python | [`/autogen`](./autogen) | Injecting Sentinel secrets into Microsoft AutoGen agents. |
| **Haystack** | Python | [`/haystack`](./haystack) | Injecting Sentinel secrets into Haystack components. |
| **AutoGPT** | Python | [`/autogpt`](./autogpt) | Using `sentinel run` to inject secrets into AutoGPT. |
| **Vercel AI SDK** | TypeScript | [`/vercel-ai-sdk`](./vercel-ai-sdk) | Integrating Sentinel with Vercel AI SDK Tools. |
| **Next.js App Router** | TypeScript | [`/nextjs-app-router`](./nextjs-app-router) | Using Sentinel in Server Actions for JIT access. |

## Running the Examples

Each example directory is self-contained. Navigate to the directory and follow its `README.md`.

### CrewAI (Python)

```bash
cd crewai
pip install -r requirements.txt
python main.py
```

### LangChain (Python)

```bash
cd langchain
pip install -r requirements.txt
python langchain_sentinel.py
```

### LangChain (JS)

```bash
cd langchain-js
bun install
bun run index.ts
```

### Vercel AI SDK (TypeScript)

```bash
cd vercel-ai-sdk
bun install
bun run index.ts
```

## Integration Pattern

The core pattern involves using the `Sentinel` client to request a secret with a specific "intent". If the request requires approval, the SDK handles the polling automatically (or returns a status indicating it's pending).

```python
from sentinel import Sentinel

client = Sentinel()

# Request the secret (blocks if pending approval)
response = client.secrets.get(
    "github_token",
    intent="Pushing release tags"
)

if response.secret:
    print(f"Got secret: {response.secret.value}")
```
