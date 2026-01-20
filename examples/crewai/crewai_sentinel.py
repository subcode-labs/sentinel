import os
import sys
from crewai import Agent, Task, Crew
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError

# Initialize Sentinel Client
sentinel = SentinelClient(
    base_url=os.getenv("SENTINEL_URL", "http://localhost:3000"),
    api_token=os.getenv("SENTINEL_TOKEN", "sentinel_dev_key"),
    agent_id="crewai-agent",
)


def request_secret(resource_name: str) -> str:
    """Helper to request a secret and handle the response."""
    print(f"[*] Requesting secret: {resource_name}...")
    try:
        intent = AccessIntent(
            summary="CrewAI secure action",
            description=f"Agent needs {resource_name} to perform a secure operation",
            task_id="crewai-demo-1",
        )

        # request_secret handles polling automatically
        secret = sentinel.request_secret(resource_id=resource_name, intent=intent)

        print(f"[+] Access granted for {resource_name}")
        return secret.value

    except SentinelDeniedError as e:
        raise RuntimeError(f"Sentinel Access Denied: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to get secret: {e}")


def secure_action():
    """Example of a function that requires a secret from Sentinel."""
    try:
        # Requesting a secret that might require approval (e.g. contains 'prod')
        secret = request_secret("production_api_key")
        return f"Secure action executed successfully with secret: {secret[:4]}***"
    except Exception as e:
        return f"Secure action failed: {str(e)}"


# Define the Secure Agent
agent = Agent(
    role="Security Specialist",
    goal="Perform high-stakes operations using protected credentials",
    backstory="You are an expert at managing sensitive data and follow strict security protocols.",
    allow_delegation=False,
    verbose=True,
)

# Define the Task
task = Task(
    description="Execute the secure_action function to demonstrate Sentinel integration.",
    expected_output="A confirmation message showing the action was performed or failed due to security.",
    agent=agent,
)

if __name__ == "__main__":
    print("--- Starting CrewAI + Sentinel Demo ---")
    # CrewAI tasks can use functions directly or via Tools.
    # For this simple demo, we demonstrate the logic inside the task execution.

    # Note: In a real CrewAI setup, you'd wrap secure_action in a @tool

    # We monkey-patch the task execution for this demo since we aren't using the full Tool definition
    # In a real app, you would define secure_action as a Tool.
    print("[*] Simulating agent execution calling the secure tool...")
    result_text = secure_action()

    print("\nFinal Result:")
    print(result_text)
