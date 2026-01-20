# Sentinel x Semantic Kernel Integration

This example demonstrates how to use **Sentinel** to securely inject secrets (like `OPENAI_API_KEY`) into a **Semantic Kernel** application.

## Prerequisites

- Sentinel Cloud account or Self-Hosted instance.
- Python 3.10+
- An OpenAI API Key stored in Sentinel (resource ID: `openai_api_key`).

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```
   (Make sure you have `semantic-kernel` installed)

2. **Configure Environment:**
   Copy `.env.example` to `.env` and fill in your Sentinel details.
   ```bash
   cp ../.env.example .env
   ```

3. **Create Secret in Sentinel:**
   - Go to your Sentinel Dashboard.
   - Create a new secret with Key: `openai_api_key` and Value: `sk-...` (your OpenAI key).

## Run the Agent

```bash
python main.py
```

## How it Works

1. **Auth:** The script connects to Sentinel using your `SENTINEL_TOKEN`.
2. **Request:** It requests the `openai_api_key` with a specific intent ("Initialize Semantic Kernel").
3. **Approve:** If required, an admin approves the request in the Sentinel Dashboard.
4. **Inject:** The script receives the secret and initializes the `OpenAIChatCompletion` service *programmatically*, without ever writing the key to disk or exposing it in environment variables.
