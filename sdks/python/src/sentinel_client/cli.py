import argparse
import os
import sys
import json
from sentinel_client.client import SentinelClient
from sentinel_client.types import AccessIntent
from sentinel_client.exceptions import SentinelError


def main():
    parser = argparse.ArgumentParser(
        description="Sentinel CLI - Agent Secret Management"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # 'get' command
    get_parser = subparsers.add_parser("get", help="Request a secret")
    get_parser.add_argument(
        "resource_id", help="The ID of the secret/resource to request"
    )
    get_parser.add_argument(
        "--intent", "-i", default="CLI Access", help="Reason for access"
    )
    get_parser.add_argument(
        "--ttl", type=int, default=3600, help="Time-to-live in seconds"
    )
    get_parser.add_argument(
        "--format",
        choices=["text", "json", "env"],
        default="text",
        help="Output format (default: text)",
    )

    # Global args
    parser.add_argument(
        "--url",
        default=os.environ.get("SENTINEL_URL", "http://localhost:3000"),
        help="Sentinel Server URL",
    )
    parser.add_argument(
        "--token", default=os.environ.get("SENTINEL_TOKEN"), help="Sentinel API Token"
    )
    parser.add_argument(
        "--agent-id", default=os.environ.get("AGENT_ID", "cli-user"), help="Agent ID"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "get":
        if not args.token:
            print("Error: --token or SENTINEL_TOKEN is required.", file=sys.stderr)
            sys.exit(1)

        client = SentinelClient(
            base_url=args.url, api_token=args.token, agent_id=args.agent_id
        )

        try:
            intent = AccessIntent(
                summary=args.intent,
                description=f"Request via CLI by {args.agent_id}",
                task_id="cli-manual",
            )

            # Print status to stderr so stdout is clean for piping
            print(f"Requesting access to '{args.resource_id}'...", file=sys.stderr)

            secret = client.request_secret(
                resource_id=args.resource_id, intent=intent, ttl_seconds=args.ttl
            )

            if args.format == "json":
                print(json.dumps(secret.model_dump(), indent=2))
            elif args.format == "env":
                # Use resource_id as key since API doesn't return key name
                print(f"{args.resource_id}={secret.value}")
            else:
                # Text format: just the value
                print(secret.value)

        except SentinelError as e:
            print(f"Sentinel Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
