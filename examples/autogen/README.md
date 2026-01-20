# Sentinel x AutoGen Integration

This example demonstrates how to use **Sentinel** to securely inject API keys into **Microsoft AutoGen** agents.

By using Sentinel, you avoid hardcoding `api_key` in your `OAI_CONFIG_LIST` or environment variables, allowing for centralized secret management, rotation, and access control.

## Prerequisites

1.  **Sentinel Installed:** Follow the instructions in the root README.
2.  **Sentinel Daemon Running:** `sentinel start`
3.  **OpenAI API Key:** You must have a secret named `OPENAI_API_KEY` stored in Sentinel.

## Setup

1.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    *Note: You may need to install the Sentinel SDK from source if not yet published to PyPI:*
    ```bash
    pip install ../../../sdks/python
    ```

2.  Run the example:

    ```bash
    python main.py
    ```

## How it Works

1.  The script initializes a `SentinelClient`.
2.  It requests the `OPENAI_API_KEY` using `client.get_secret()`.
3.  If the secret requires approval, Sentinel will trigger the workflow.
4.  Once retrieved, the key is injected dynamically into the AutoGen `llm_config`.
5.  The `AssistantAgent` uses this config to communicate with OpenAI.
