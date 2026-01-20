import os
from smolagents import CodeAgent, tool, HfApiModel
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError

# Initialize Sentinel Client
# Assumes SENTINEL_URL and SENTINEL_API_KEY are set in environment
sentinel = SentinelClient(
    base_url=os.getenv("SENTINEL_URL", "http://localhost:3000/api"),
    api_token=os.getenv("SENTINEL_API_KEY", "your_sentinel_token_here"),
    agent_id="smolagents-demo",
)


@tool
def get_secret(key: str, reason: str) -> str:
    """
    Securely retrieves a secret from the Sentinel vault.
    Use this tool when you need an API key, password, or secret token to perform a task.

    Args:
        key: The unique identifier (name) of the secret to retrieve (e.g., 'OPENAI_API_KEY').
        reason: A brief explanation of why this secret is needed.
    """
    try:
        intent = AccessIntent(
            summary=f"SmolAgents access to {key}",
            description=reason,
            task_id="smolagents-task-dynamic",
        )
        # Using request_secret which handles the access flow
        secret_payload = sentinel.request_secret(key, intent=intent)
        return secret_payload.value
    except SentinelDeniedError:
        return f"Error: Access to secret '{key}' was DENIED by policy."
    except Exception as e:
        return f"Error retrieving secret '{key}': {str(e)}"


# Define the model (Using Hugging Face Inference API)
# You need a HUGGING_FACE_HUB_TOKEN env var or pass token=...
model = HfApiModel()

# Create the Agent with the Sentinel tool
agent = CodeAgent(
    tools=[get_secret],
    model=model,
    additional_authorized_imports=["requests", "json"],  # Allow imports if needed
)


def main():
    print("🤖 Sentinel x Smolagents Integration")
    print("-----------------------------------")

    task = """
    I need to 'simulate' a request to the OpenAI API. 
    1. Retrieve the secret named 'OPENAI_API_KEY' using the get_secret tool. 
       (Reason: 'Simulating API call for user')
    2. Print the first 5 characters of the key to prove you have it (do not print the whole key!).
    3. Return a success message.
    """

    print(f"Task: {task}")
    print("Running agent...\n")

    try:
        result = agent.run(task)
        print(f"\n✅ Result: {result}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
