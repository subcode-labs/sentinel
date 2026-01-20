import os
import sys
import logging
from sentinel_client import SentinelClient, AccessIntent, SentinelError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Configuration
    base_url = os.getenv("SENTINEL_URL", "http://localhost:3000")
    api_token = os.getenv("SENTINEL_API_KEY", "sentinel_dev_key")
    agent_id = "demo-python-agent"

    logger.info(f"Connecting to Sentinel at {base_url}")

    client = SentinelClient(base_url=base_url, api_token=api_token, agent_id=agent_id)

    # Define Intent
    intent = AccessIntent(
        summary="Database Access",
        description="Need access to read user records for weekly report",
        task_id="task-101",
    )

    resource_id = "prod/database/readonly"

    try:
        logger.info(f"Requesting secret for {resource_id}...")
        secret = client.request_secret(
            resource_id=resource_id, intent=intent, ttl_seconds=300
        )

        logger.info("Access Granted!")
        logger.info(f"Secret Value: {secret.value}")
        logger.info(f"Expires At: {secret.expires_at}")

    except SentinelError as e:
        logger.error(f"Failed to get secret: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
