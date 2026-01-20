import os
import autogen
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError


def main():
    print("🤖 Sentinel x AutoGen Integration Example")
    print("-----------------------------------------")

    # 1. Initialize Sentinel Client
    # In a real app, you might use 'http://localhost:3000/api' or a cloud URL
    base_url = os.environ.get("SENTINEL_URL", "http://localhost:3000/api")
    api_token = os.environ.get("SENTINEL_API_KEY", "dummy_token")
    agent_id = "autogen-agent-001"

    client = SentinelClient(base_url=base_url, api_token=api_token, agent_id=agent_id)

    print("🔐 Fetching secrets from Sentinel...")

    # 2. Fetch API Key securely
    intent = AccessIntent(
        summary="Access OpenAI API Key for AutoGen",
        description="Required to run the AutoGen AssistantAgent for user queries.",
        task_id="autogen-task-001",
    )

    try:
        # This will trigger an Access Request and poll if required
        secret_payload = client.request_secret("OPENAI_API_KEY", intent=intent)
        openai_api_key = secret_payload.value
        print("✅ Secret 'OPENAI_API_KEY' retrieved successfully")

    except SentinelDeniedError as e:
        print(f"❌ Access Denied: {e}")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        print(
            "\nTip: Ensure you have the Sentinel server running and the secret exists."
        )
        return

    # 3. Configure AutoGen with the retrieved secret
    config_list = [{"model": "gpt-3.5-turbo", "api_key": openai_api_key}]

    llm_config = {
        "config_list": config_list,
        "temperature": 0.7,
        "timeout": 120,
    }

    # 4. Create Agents
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config=llm_config,
        system_message="You are a helpful AI assistant. You are concise and professional.",
    )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config={"work_dir": "coding", "use_docker": False},
        is_termination_msg=lambda x: x.get("content", "")
        .rstrip()
        .endswith("TERMINATE"),
    )

    # 5. Initiate Chat (Mock)
    print("\n💬 Starting conversation (Mock)...")
    print("   User: 'Tell me a joke about computer security.'")
    print("-----------------------------------------")

    # NOTE: In a real environment with a valid key, you would uncomment this:
    # try:
    #     user_proxy.initiate_chat(
    #         assistant, message="Tell me a joke about computer security."
    #     )
    # except Exception as e:
    #     print(f"AutoGen Error: {e}")

    print("(Skipping actual AutoGen call to avoid OpenAI charges in example)")


if __name__ == "__main__":
    main()
