# Sentinel Multi-Agent Delegation Example

This example demonstrates how **Sentinel** acts as a "Wallet for Agents" in a multi-agent system.

## Scenario

1.  **Manager Agent (Alice):** Receives a high-level goal ("Competitor Analysis") and delegates it.
2.  **Worker Agent (Worker-01):** Is spawned to perform the task. It needs access to external tools (e.g., `SERPER_API_KEY`).
3.  **Sentinel:** Facilitates the secure access. The Worker "discovers" available credentials and requests access *just-in-time*, rather than having secrets hardcoded or passed via environment variables.

## Key Concepts Demonstrated

-   **Agent Identity:** Each agent (`manager-alice`, `worker-01`) has a unique identity in the logs.
-   **Resource Discovery:** The Worker proactively queries Sentinel (`list_resources`) to see what tools are available.
-   **Intent-Based Access:** The Worker provides a reason (`intent`) for why it needs the secret.
-   **Least Privilege:** The Worker only asks for what it needs, when it needs it.

## How to Run

1.  **Prerequisites:**
    -   Python 3.8+
    -   Sentinel Server running (locally or cloud)
    -   `SENTINEL_API_KEY` set

2.  **Install SDK:**
    ```bash
    pip install sentinel-client
    # Or from source:
    # pip install -e ../../sdks/python
    ```

3.  **Run the Simulation:**
    ```bash
    export SENTINEL_URL="http://localhost:3000" # or your cloud URL
    export SENTINEL_API_KEY="your-api-key"
    export SENTINEL_ENVIRONMENT="production"

    python main.py
    ```

## Expected Output

```text
--- Sentinel Multi-Agent Delegation Demo ---
Connecting to: http://localhost:3000
Environment:   production

[Manager-Alice] 🤖 Manager starting delegation sequence...
[Manager-Alice] Identifying task: 'Competitor Analysis'
[Manager-Alice] Spawning Worker Agent...

[Worker-01] 👷 Received task: 'Search for 'Sentinel SDK Features''
[Worker-01] 🔍 Discovering available secrets/tools in 'production'...
[Worker-01] 📜 Available Resources: ['SERPER_API_KEY', 'OPENAI_API_KEY']
[Worker-01] 🔐 Requesting access to 'SERPER_API_KEY'...
[Worker-01] ✅ Access GRANTED!
[Worker-01] 🗝️  Secret Value: sk-X... (redacted)
[Worker-01] 🚀 Executing task with secret...
[Worker-01] ✨ Task Complete.
```
