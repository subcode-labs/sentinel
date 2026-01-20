# Sentinel x CrewAI Integration

This example demonstrates how to give a **CrewAI** agent secure, on-demand access to secrets using Sentinel.

The agent uses a custom tool (`Request Secret`) to ask Sentinel for credentials only when needed. Sentinel enforces policy (approval workflows, logging, etc.) before returning the secret.

## Prerequisites

1.  **Sentinel Server**: Running locally or in the cloud.
2.  **Sentinel Token**: An API token for your agent (create one in the Sentinel Dashboard).
3.  **OpenAI API Key**: For the CrewAI agent LLM.

## Setup

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure environment**:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your `SENTINEL_TOKEN` and `OPENAI_API_KEY`.

3.  **Ensure a Secret Exists**:
    Make sure your Sentinel project has a secret with the resource ID `demo_api_key`.

## Run

```bash
python main.py
```

## How it works

1.  The CrewAI agent is initialized with a `Request Secret` tool.
2.  The agent analyzes its task and realizes it needs the `demo_api_key`.
3.  It calls the tool with a reason (e.g., "Running integration tests").
4.  The tool calls `sentinel.request_secret()`.
5.  If the request is approved (auto-approved or manually approved by a human admin), the secret is returned.
6.  The agent uses the secret to complete the task.
