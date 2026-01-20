import os
import sys
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError

# Initialize Sentinel Client
# In a real app, these would come from env vars
sentinel = SentinelClient(
    base_url=os.getenv("SENTINEL_URL", "http://localhost:3000"),
    api_token=os.getenv("SENTINEL_TOKEN", "sentinel_dev_key"),
    agent_id="langchain-agent",
)


def get_secure_key(resource_id: str) -> str:
    """
    Fetches a sensitive key from Sentinel with intent logging.
    In a real app, this would be called inside a Tool's _run method.
    """
    try:
        intent = AccessIntent(
            summary="LangChain tool execution",
            description=f"Agent needs {resource_id} to interact with a protected service",
            task_id="langchain-agent-task",
        )

        # request_secret handles polling automatically if the request is PENDING_APPROVAL
        secret = sentinel.request_secret(resource_id=resource_id, intent=intent)
        return secret.value

    except SentinelDeniedError as e:
        raise Exception(f"Sentinel denied access to {resource_id}: {e}")
    except Exception as e:
        raise Exception(f"Failed to retrieve secret for {resource_id}: {e}")


def github_search(query: str) -> str:
    """A mock tool that requires a secret from Sentinel."""
    print(f"[*] Tool requesting access to 'github_api_token'...")
    # This call will block until approved if a human review is required
    api_key = get_secure_key("github_api_token")
    return f"Results for '{query}' using key {api_key[:4]}***"


# Define LangChain Tools
tools = [
    Tool(
        name="GitHubSearch",
        func=github_search,
        description="Useful for searching code on GitHub. Requires a secret token from Sentinel.",
    )
]

if __name__ == "__main__":
    print("--- Starting LangChain + Sentinel Demo ---")

    # This example requires OPENAI_API_KEY to run the agent logic
    if not os.getenv("OPENAI_API_KEY"):
        print("[*] Note: OPENAI_API_KEY not set. Running mock tool execution only.")
        print(github_search("sentinel repository"))
    else:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        # Get a standard prompt for React agents
        prompt = hub.pull("hwchase17/react")

        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        print("\n[*] Agent Task: 'Search GitHub for the sentinel repository'")
        agent_executor.invoke({"input": "Search GitHub for the sentinel repository"})
