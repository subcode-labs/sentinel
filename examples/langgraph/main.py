import os
import sys
from typing import Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError

# --- Sentinel Setup ---
# In a real application, these would come from environment variables
# or be injected via a configuration provider.
sentinel = SentinelClient(
    base_url=os.getenv("SENTINEL_URL", "http://localhost:3000"),
    api_token=os.getenv("SENTINEL_TOKEN", "sentinel_dev_key"),
    agent_id="langgraph-agent",
)


def get_secure_key(resource_id: str) -> str:
    """
    Fetches a sensitive key from Sentinel with intent logging.
    This ensures that every access to the secret is logged and authenticated.
    """
    print(f"\n[Sentinel] Requesting access to '{resource_id}'...")
    try:
        intent = AccessIntent(
            summary="LangGraph tool execution",
            description=f"Agent needs {resource_id} to perform a secure search",
            task_id="langgraph-task-001",
        )

        # request_secret handles polling automatically if the request is PENDING_APPROVAL
        secret = sentinel.request_secret(resource_id=resource_id, intent=intent)

        print(f"[Sentinel] Access GRANTED. Secret: {secret.value[:4]}...")
        return secret.value

    except SentinelDeniedError as e:
        raise Exception(f"Sentinel denied access to {resource_id}: {e}")
    except Exception as e:
        raise Exception(f"Failed to retrieve secret for {resource_id}: {e}")


# --- Tools ---
@tool
def secure_search(query: str):
    """
    Searches a secure database.
    This tool requires authentication via Sentinel to access the database key.
    """
    print(f"[*] Tool '{secure_search.name}' invoked with query: '{query}'")

    # Just-in-time secret retrieval
    # The agent doesn't hold the key; it requests it only when this tool runs.
    api_key = get_secure_key("secure_db_key")

    return (
        f"Secure Results for '{query}' using key {api_key[:4]}***: [Result A, Result B]"
    )


tools = [secure_search]

# --- Graph Definition ---


class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


graph_builder = StateGraph(State)

# Initialize LLM with tools
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", ToolNode(tools=tools))

# Add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")

graph = graph_builder.compile()

# --- Execution ---
if __name__ == "__main__":
    print("--- Sentinel x LangGraph Integration Example ---")

    if not os.getenv("OPENAI_API_KEY"):
        print("[-] OPENAI_API_KEY environment variable not set.")
        print(
            "[*] Running mock tool execution to demonstrate Sentinel integration without LLM:"
        )
        try:
            print(secure_search.invoke({"query": "Sentinel Protocol"}))
        except Exception as e:
            print(f"[!] Error: {e}")
            print("Make sure Sentinel is running and 'secure_db_key' exists.")
        sys.exit(0)

    print("[*] Starting Agent loop...")
    user_input = "Please search the secure database for 'Project Sentinel'"
    print(f"\nUser: {user_input}")

    # Stream the graph execution
    for event in graph.stream({"messages": [("user", user_input)]}):
        for key, value in event.items():
            if "messages" in value:
                last_msg = value["messages"][-1]
                if hasattr(last_msg, "content") and last_msg.content:
                    print(f"\nAgent ({key}): {last_msg.content}")
                elif hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    print(
                        f"\nAgent ({key}) -> calling tools: {[tc['name'] for tc in last_msg.tool_calls]}"
                    )

    print("\n--- Execution Complete ---")
