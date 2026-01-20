import os
import sys
from crewai import Agent, Task, Crew

# Add parent directory to path so we can import sentinel_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentinel_utils import SentinelClient

# Initialize Sentinel Client
sentinel = SentinelClient(
    base_url="http://localhost:3000",
    api_token="sentinel_dev_key",
    agent_id="crewai-agent",
)


def request_secret(resource_name: str) -> str:
    """Helper to request a secret and handle the response."""
    print(f"[*] Requesting secret: {resource_name}...")
    result = sentinel.request_with_polling(
        resource_id=resource_name,
        intent={
            "task_id": "crewai-demo-1",
            "summary": "CrewAI secure action",
            "description": f"Agent needs {resource_name} to perform a secure operation",
        },
    )

    if result["status"] == "APPROVED":
        print(f"[+] Access granted for {resource_name}")
        return result["secret"]["value"]
    else:
        reason = result.get("reason", "Access denied by policy")
        raise RuntimeError(f"Sentinel Access Denied: {reason}")


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

    crew = Crew(agents=[agent], tasks=[task], verbose=True)

    result = crew.kickoff()
    print("\nFinal Result:")
    print(result)
