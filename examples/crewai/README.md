# Sentinel + CrewAI Example

This example demonstrates how to use Sentinel to protect high-stakes operations within a CrewAI workflow.

## How it works

1. A `SentinelClient` is initialized with the agent's identity.
2. A `secure_action` function is defined which requires a production API key.
3. When called, `secure_action` requests the key from Sentinel, explaining that the agent needs it for a "secure operation".
4. CrewAI executes the task, triggering the Sentinel request.
5. Sentinel's policy engine evaluates the request (e.g., resources containing "prod" might require human approval).

## Prerequisites

- Python 3.8+
- `requests` library
- `crewai` library

## Running the example

```bash
# Install dependencies
pip install requests crewai

# Run the demo
python crewai_sentinel.py
```
