# Sentinel + AutoGPT Integration

This example demonstrates how to use Sentinel to securely inject credentials into [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) (or any other agent framework) at runtime.

Instead of storing sensitive keys like `OPENAI_API_KEY` in a plaintext `.env` file, you can use the Sentinel CLI to fetch them dynamically and inject them into the AutoGPT process.

## Prerequisites

- Sentinel Server running (Cloud or Self-Hosted)
- Sentinel Python SDK installed (`pip install sentinel-client`)
- AutoGPT installed

## How it Works

The `sentinel run` command fetches all secrets available to your agent/project and injects them as environment variables into the command you specify.

## Usage

### 1. Set up your Sentinel environment

Ensure your Sentinel project has the necessary secrets (e.g., `OPENAI_API_KEY`, `GITHUB_ACCESS_TOKEN`).

### 2. Run AutoGPT with Sentinel

```bash
export SENTINEL_URL="http://localhost:3000"
export SENTINEL_TOKEN="your_sentinel_api_key"

# Run AutoGPT wrapped by Sentinel
sentinel run -- python -m autogpt
```

### 3. Verify

AutoGPT will start with all your managed secrets available as environment variables. It will never know they came from Sentinel, and they won't persist on disk.

## Example (Mock)

We've included a `mock_autogpt.py` script to demonstrate the concept without needing the full AutoGPT installation.

```bash
# 1. Start Sentinel Server (if not running)
cd ../..
bun run src/server.ts &

# 2. Add a secret (using admin API for demo purposes)
curl -X POST http://localhost:3000/v1/admin/secrets/OPENAI_API_KEY/rotate

# 3. Run the mock agent
export SENTINEL_URL="http://localhost:3000"
export SENTINEL_TOKEN="sentinel_dev_key"

# Using the SDK from source (for dev)
python3 -m sentinel_client.cli run -- python3 examples/autogpt/mock_autogpt.py
```
