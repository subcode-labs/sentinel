import os
from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError


def main():
    print("🤖 Sentinel x Haystack Integration Example")
    print("-----------------------------------------")

    # 1. Initialize Sentinel Client
    base_url = os.environ.get("SENTINEL_URL", "http://localhost:3000/api")
    api_token = os.environ.get("SENTINEL_API_KEY", "dummy_token")
    agent_id = "haystack-agent-001"

    client = SentinelClient(base_url=base_url, api_token=api_token, agent_id=agent_id)

    print("🔐 Fetching secrets from Sentinel...")

    # 2. Fetch the secret
    intent = AccessIntent(
        summary="Access OpenAI API Key for Haystack",
        description="Required to initialize the OpenAIGenerator component.",
        task_id="haystack-task-001",
    )

    try:
        secret_payload = client.request_secret("OPENAI_API_KEY", intent=intent)
        api_key_value = secret_payload.value
        print("✅ Sentinel: Secret retrieved successfully.")

    except SentinelDeniedError as e:
        print(f"❌ Access Denied: {e}")
        return
    except Exception as e:
        print(f"❌ Error: {e}")
        return

    # 3. Initialize Haystack Component
    # Haystack 2.0 uses 'Secret' types for secure handling
    generator = OpenAIGenerator(
        model="gpt-3.5-turbo", api_key=Secret.from_token(api_key_value)
    )

    print("✅ Haystack: OpenAIGenerator initialized with Sentinel secret.")

    # 4. Run (Mock)
    print("\nExample complete. The generator is ready to run pipelines.")


if __name__ == "__main__":
    main()
