import os
import sys
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain import hub

# Add parent directory to path so we can import sentinel_utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sentinel_utils import SentinelClient

# Initialize Sentinel Client
sentinel = SentinelClient(
    base_url="http://localhost:3000",
    api_token="sentinel_dev_key",
    agent_id="langchain-agent",
)


def get_secure_key(resource_id: str) -> str:
    """
    Fetches a sensitive key from Sentinel with intent logging.
    In a real app, this would be called inside a Tool's _run method.
    """
    result = sentinel.request_with_polling(
        resource_id=resource_id,
        intent={
            "task_id": "langchain-agent-task",
            "summary": "LangChain tool execution",
            "description": f"Agent needs {resource_id} to interact with a protected service",
        },
    )

    if result["status"] == "APPROVED":
        return result["secret"]["value"]
    else:
        raise Exception(f"Sentinel denied access to {resource_id}")


def github_search(query: str) -> str:
    """A mock tool that requires a secret from Sentinel."""
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
        prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        agent_executor.invoke({"input": "Search GitHub for the sentinel repository"})
