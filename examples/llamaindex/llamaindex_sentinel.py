import os
import sys
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.openai import OpenAI
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError

# Initialize Sentinel Client
# In a real app, these would come from env vars or config
sentinel = SentinelClient(
    base_url=os.getenv("SENTINEL_URL", "http://localhost:3000"),
    api_token=os.getenv("SENTINEL_TOKEN", "sentinel_dev_key"),
    agent_id="llamaindex-agent",
)


def get_secure_key(resource_id: str) -> str:
    """
    Fetches a sensitive key from Sentinel with intent logging.
    """
    print(f"[*] Requesting access to '{resource_id}'...")
    try:
        intent = AccessIntent(
            summary="LlamaIndex initialization",
            description=f"Agent needs {resource_id} to initialize LLM/Embeddings",
            task_id="llamaindex-startup",
        )

        # request_secret handles polling automatically if the request is PENDING_APPROVAL
        secret = sentinel.request_secret(resource_id=resource_id, intent=intent)
        print(f"[*] Successfully retrieved '{resource_id}'")
        return secret.value

    except SentinelDeniedError as e:
        print(f"[!] Sentinel denied access to {resource_id}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Failed to retrieve secret for {resource_id}: {e}")
        sys.exit(1)


def main():
    print("--- Starting LlamaIndex + Sentinel Demo ---")

    # 1. Fetch OpenAI Key from Sentinel
    openai_key = get_secure_key("openai_api_key")

    # 2. Configure LlamaIndex Global Settings
    # We set the api_key directly on the LLM class or via env var
    os.environ["OPENAI_API_KEY"] = openai_key

    Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0)

    # 3. Create a simple index (Proof of Life)
    print("\n[*] Creating Vector Store Index from dummy data...")
    documents = [
        Document(
            text="Sentinel is a secure key management system for autonomous AI agents."
        ),
        Document(text="LlamaIndex is a data framework for LLM-based applications."),
        Document(text="SubCode Ventures builds tools for the agentic future."),
    ]

    # This will use the OpenAI key for embeddings
    try:
        index = VectorStoreIndex.from_documents(documents)

        # 4. Query the index
        query_engine = index.as_query_engine()
        query = "What is Sentinel?"
        print(f"\n[*] Querying: '{query}'")

        response = query_engine.query(query)
        print(f"\n[>] Response: {response}")

    except Exception as e:
        print(f"\n[!] Error during LlamaIndex execution: {e}")
        print(
            "    (Note: This error might happen if the retrieved key is invalid or lacks quota)"
        )


if __name__ == "__main__":
    main()
