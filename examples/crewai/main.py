import os
import time
from crewai import Agent, Task, Crew
from langchain.tools import tool
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SENTINEL_URL = os.getenv("SENTINEL_URL", "http://localhost:3000")
SENTINEL_TOKEN = os.getenv("SENTINEL_TOKEN")
AGENT_ID = os.getenv("AGENT_ID", "crewai-agent-01")

if not SENTINEL_TOKEN:
    print("Error: SENTINEL_TOKEN environment variable is required.")
    exit(1)

# Initialize Sentinel Client
print(f"Connecting to Sentinel at {SENTINEL_URL}...")
sentinel = SentinelClient(
    base_url=SENTINEL_URL, api_token=SENTINEL_TOKEN, agent_id=AGENT_ID
)


# Define the Tool
@tool("Request Secret")
def request_secret(resource_id: str, reason: str) -> str:
    """
    Request a secret from Sentinel Security.
    Args:
        resource_id: The ID of the protected resource (e.g., 'github_api_key').
        reason: A clear explanation of why you need this secret.
    Returns:
        The secret value if approved, or an error message if denied.
    """
    print(f"\n🔐 [Sentinel] Requesting access to '{resource_id}'...")
    print(f"   Reason: {reason}")

    try:
        secret = sentinel.request_secret(
            resource_id=resource_id,
            intent=AccessIntent(
                summary=reason,
                description="CrewAI Agent requires access to complete task",
                task_id=f"task-{int(time.time())}",
            ),
            timeout=60,  # Wait up to 60s for human approval if needed
        )
        print(f"✅ [Sentinel] Access GRANTED.")
        return secret.value
    except SentinelDeniedError as e:
        print(f"❌ [Sentinel] Access DENIED: {e}")
        return f"Access Denied: {str(e)}"
    except Exception as e:
        print(f"⚠️ [Sentinel] Error: {e}")
        return f"Error requesting secret: {str(e)}"


# Define the Agent
# We give the agent the 'Request Secret' tool so it can autonomously request access.
developer = Agent(
    role="Senior Integration Developer",
    goal="Retrieve necessary credentials and verify they work",
    backstory="""You are a developer agent responsible for setting up integrations. 
    You strictly follow security protocols and never hardcode secrets. 
    You always use the Sentinel Security system to request access to credentials when needed.""",
    tools=[request_secret],
    verbose=True,
    allow_delegation=False,
)

# Define the Task
# We intentionally ask for a resource that might require approval or exist in the system.
# The user should ensure a secret with resource_id 'demo_api_key' exists.
task = Task(
    description="""
    1. Identify that you need the 'demo_api_key' to proceed with the integration.
    2. Use the 'Request Secret' tool to ask for the 'demo_api_key'. Provide a valid professional reason (e.g., 'Running integration tests').
    3. If you get the secret, print the first 3 characters and the length of the secret (DO NOT print the full secret).
    4. If you are denied, report the denial reason.
    """,
    agent=developer,
    expected_output="A status report confirming whether the secret was retrieved and verified.",
)

# Instantiate the Crew
crew = Crew(agents=[developer], tasks=[task], verbose=True)

# Run the Crew
if __name__ == "__main__":
    print("\n🤖 Starting CrewAI Sentinel Integration Demo")
    print("---------------------------------------------")
    result = crew.kickoff()
    print("\n\n########################")
    print("## Final Result ##")
    print("########################\n")
    print(result)
