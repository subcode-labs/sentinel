import os
import logging
from typing import Optional, Type

# Check for LangChain availability
try:
    from langchain.tools import BaseTool
    from langchain.pydantic_v1 import (
        BaseModel,
        Field,
    )  # LangChain often uses v1 internally, or v2.

    # Let's try standard pydantic if langchain specific fails, or rely on environment.
    # Actually, modern LangChain supports Pydantic v2.
    from pydantic import BaseModel, Field
except ImportError:
    print("LangChain not installed. This example requires 'langchain'.")
    print("pip install langchain")
    exit(1)

from sentinel_client import SentinelClient, AccessIntent, SentinelError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinel-langchain")


class SentinelAccessInput(BaseModel):
    """Input for the Sentinel Access Tool."""

    resource_id: str = Field(
        ...,
        description="The unique identifier of the protected resource (e.g., 'aws/prod/s3-readonly', 'database/postgres/connection-string').",
    )
    reason: str = Field(
        ...,
        description="A clear explanation of why the agent needs access to this resource.",
    )
    task_id: Optional[str] = Field(
        None, description="The ID of the current task being executed, if available."
    )


class SentinelAccessTool(BaseTool):
    """
    A LangChain Tool that allows an agent to request secrets/access from Sentinel.

    This tool handles the "Handshake Protocol":
    1. Sends an intent and resource request to Sentinel.
    2. If required, waits for Human-in-the-Loop approval (polling).
    3. Returns the secret value (e.g., API key, connection string) to the agent.
    """

    name: str = "sentinel_get_secret"
    description: str = (
        "Use this tool to get secrets, API keys, or database credentials. "
        "Input requires the 'resource_id' and a 'reason' for access. "
        "This tool may take time if human approval is required."
    )
    args_schema: Type[BaseModel] = SentinelAccessInput

    # Private client instance
    client: SentinelClient = Field(exclude=True)

    def _run(self, resource_id: str, reason: str, task_id: Optional[str] = None) -> str:
        """Synchronous execution of the tool."""
        intent = AccessIntent(
            summary=reason[:60] + ("..." if len(reason) > 60 else ""),
            description=reason,
            task_id=task_id or "agent-task",
        )

        logger.info(f"Agent requesting access to '{resource_id}' for '{reason}'")

        try:
            # The client handles polling automatically if the request is PENDING_APPROVAL
            secret = self.client.request_secret(
                resource_id=resource_id,
                intent=intent,
                ttl_seconds=300,  # 5 minutes default for agent ops
            )

            logger.info("Access GRANTED by Sentinel.")
            return secret.value

        except SentinelError as e:
            logger.error(f"Access DENIED or FAILED: {e}")
            return f"Error: Could not obtain secret. Sentinel replied: {str(e)}"

    async def _arun(
        self, resource_id: str, reason: str, task_id: Optional[str] = None
    ) -> str:
        """Asynchronous execution (not yet fully implemented in SDK, falls back to sync)."""
        # In a real async implementation, we'd use an async client.
        # For now, we wrap the sync call.
        return self._run(resource_id, reason, task_id)


def main():
    """
    Example of how to initialize and use the tool.
    In a real app, you would pass 'tool' to your LangChain agent.
    """

    # 1. Setup Sentinel Client
    base_url = os.getenv("SENTINEL_URL", "http://localhost:3000")
    api_token = os.getenv("SENTINEL_API_KEY", "sentinel_dev_key")
    agent_id = "langchain-agent-001"

    client = SentinelClient(base_url=base_url, api_token=api_token, agent_id=agent_id)

    # 2. Create the Tool
    sentinel_tool = SentinelAccessTool(client=client)

    print(f"Tool Created: {sentinel_tool.name}")
    print(f"Description: {sentinel_tool.description}")

    # 3. Simulate Agent Usage (Direct Call)
    print("\n--- Simulating Agent Call ---")
    resource = "prod/database/readonly"
    reason = "I need to query the 'users' table to generate the weekly report."

    try:
        result = sentinel_tool.invoke(
            {"resource_id": resource, "reason": reason, "task_id": "task-abc-123"}
        )

        # NOTE: In a real run, we don't print the secret to logs,
        # but for this demo we show that we got it.
        masked_result = (
            result[:4] + "*" * (len(result) - 4) if len(result) > 4 else "****"
        )
        print(f"Tool Result: Secret obtained! Value: {masked_result}")

    except Exception as e:
        print(f"Tool Execution Failed: {e}")


if __name__ == "__main__":
    main()
