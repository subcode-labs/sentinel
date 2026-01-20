import os
import sys
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError

# 1. Initialize Sentinel Client
# In a real app, these would come from env vars or config
sentinel = SentinelClient(
    base_url=os.getenv("SENTINEL_URL", "http://localhost:3000/api"),
    api_token=os.getenv("SENTINEL_TOKEN", "sentinel_dev_key"),
    agent_id="pydantic-ai-agent",
)


def get_secure_key(resource_id: str, reason: str) -> str:
    """Helper to fetch keys from Sentinel with intent."""
    print(f"[*] Requesting access to '{resource_id}'...")
    try:
        intent = AccessIntent(
            summary="PydanticAI Execution",
            description=reason,
            task_id="pydantic-ai-task-001",
        )
        secret = sentinel.request_secret(resource_id=resource_id, intent=intent)
        print(f"[*] Successfully retrieved '{resource_id}'")
        return secret.value
    except Exception as e:
        print(f"[!] Failed to retrieve secret for {resource_id}: {e}")
        # In a real app, you might handle this more gracefully
        sys.exit(1)


@dataclass
class MyDeps:
    sentinel: SentinelClient


def main():
    print("--- Starting PydanticAI + Sentinel Demo ---")

    # 2. Bootstrap: Get LLM Key
    # This is the "Bootstrapping" phase where we get credentials to start the agent
    openai_key = get_secure_key("OPENAI_API_KEY", "Needed to initialize the LLM agent")
    os.environ["OPENAI_API_KEY"] = openai_key

    # 3. Define Agent
    # We inject the Sentinel Client as a dependency
    agent = Agent(
        "openai:gpt-3.5-turbo",
        deps_type=MyDeps,
        system_prompt="You are a helpful assistant. Use your tools to look up weather information.",
    )

    # 4. Define Tool that uses Sentinel
    @agent.tool
    async def get_weather(ctx: RunContext[MyDeps], city: str) -> str:
        """Get the weather for a city."""

        print(f"\n[Tool] get_weather called for {city}")

        # Securely fetch the API key *only when needed* (Just-in-Time Access)
        try:
            intent = AccessIntent(
                summary=f"Get weather for {city}",
                description="Need WEATHER_API_KEY to call the Weather Service",
                task_id="weather-lookup",
            )

            # Request the secret via the injected Sentinel client
            # Note: We're reusing OPENAI_API_KEY here for demonstration if WEATHER_API_KEY doesn't exist
            # in your local dev setup. In production, use the real key name.
            key_name = "OPENAI_API_KEY"
            print(f"[Tool] Requesting JIT access to {key_name}...")

            secret = ctx.deps.sentinel.request_secret(
                resource_id=key_name, intent=intent
            )

            # Simulate using the key
            masked_key = secret.value[:3] + "..." + secret.value[-3:]
            return f"Weather in {city} is Sunny (authenticated with key {masked_key})"

        except Exception as e:
            return f"Failed to get weather data: {str(e)}"

    # 5. Run the Agent
    deps = MyDeps(sentinel=sentinel)

    prompt = "What's the weather in Tokyo?"
    print(f"\nUser: {prompt}")

    # Run the agent (run_sync handles the async event loop for us)
    result = agent.run_sync(prompt, deps=deps)

    print(f"\nAgent: {result.data}")


if __name__ == "__main__":
    main()
