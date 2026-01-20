import asyncio
import os
import sys
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SENTINEL_URL = os.getenv("SENTINEL_URL", "http://localhost:3000")
SENTINEL_TOKEN = os.getenv("SENTINEL_TOKEN")
AGENT_ID = os.getenv("AGENT_ID", "semantic-kernel-agent-01")

if not SENTINEL_TOKEN:
    print("Error: SENTINEL_TOKEN environment variable is required.")
    sys.exit(1)


async def main():
    print(f"🤖 Starting Semantic Kernel x Sentinel Integration")
    print("------------------------------------------------")

    # 1. Initialize Sentinel Client
    print(f"📡 Connecting to Sentinel at {SENTINEL_URL}...")
    sentinel = SentinelClient(
        base_url=SENTINEL_URL, api_token=SENTINEL_TOKEN, agent_id=AGENT_ID
    )

    # 2. Request OpenAI API Key from Sentinel
    resource_id = "openai_api_key"
    print(f"🔐 Requesting access to '{resource_id}'...")

    try:
        secret = sentinel.request_secret(
            resource_id=resource_id,
            intent=AccessIntent(
                summary="Initialize Semantic Kernel for AI reasoning",
                description="Agent requires OpenAI API key to perform chat completion tasks via Semantic Kernel.",
                task_id="sk-init-001",
            ),
            timeout=60,  # Wait for human approval
        )
        print(f"✅ Access GRANTED. Secret received (length: {len(secret.value)}).")
        openai_api_key = secret.value

    except SentinelDeniedError as e:
        print(f"❌ Access DENIED: {e}")
        return
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return

    # 3. Configure Semantic Kernel with the retrieved secret
    print("\n🧠 Initializing Semantic Kernel...")
    kernel = Kernel()

    # Add OpenAI Chat Completion Service
    service_id = "chat-gpt"
    kernel.add_service(
        OpenAIChatCompletion(
            service_id=service_id,
            ai_model_id="gpt-3.5-turbo",
            api_key=openai_api_key,
        )
    )

    # 4. Define and Run a Semantic Function
    print("⚡ Running semantic function...")

    # Simple prompt
    prompt = "Explain why key management is important for autonomous AI agents in one sentence."

    try:
        # Create a simple function from prompt
        # Note: SK API changes frequently, this is the standard way as of late 2024/2025
        # Depending on version, it might be invoke_prompt or similar.
        # We'll use the invoke method on the service or kernel.

        from semantic_kernel.functions import KernelArguments

        # Create a function from the prompt
        chat_function = kernel.add_function(
            prompt=prompt, plugin_name="SecurityPlugin", function_name="ExplainKeyMgmt"
        )

        # Invoke the function
        result = await kernel.invoke(chat_function)

        print("\n📝 Agent Response:")
        print(f"> {result}")

    except Exception as e:
        print(f"❌ Error running Semantic Kernel: {e}")


if __name__ == "__main__":
    asyncio.run(main())
