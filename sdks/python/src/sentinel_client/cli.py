import argparse
import os
import sys
import json
import subprocess
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
        "--version", "-v", type=int, help="Specific version to request"
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

    resources_parser = subparsers.add_parser(
        "resources", help="List available resources"
    )
    resources_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    # 'run' command
    run_parser = subparsers.add_parser(
        "run", help="Run a command with secrets injected into the environment"
    )
    run_parser.add_argument(
        "cmd_args",
        nargs=argparse.REMAINDER,
        help="Command to run (e.g. -- python script.py)",
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
    parser.add_argument(
        "--environment",
        "-e",
        default=os.environ.get("SENTINEL_ENVIRONMENT"),
        help="Target Environment (default: production)",
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
                resource_id=args.resource_id,
                intent=intent,
                version=args.version,
                environment=args.environment,
                ttl_seconds=args.ttl,
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

    elif args.command == "resources":
        if not args.token:
            print("Error: --token or SENTINEL_TOKEN is required.", file=sys.stderr)
            sys.exit(1)

        client = SentinelClient(
            base_url=args.url, api_token=args.token, agent_id=args.agent_id
        )

        try:
            resources = client.list_resources(environment=args.environment)

            if args.format == "json":
                print(json.dumps(resources, indent=2))
            else:
                for r in resources:
                    print(r)

        except SentinelError as e:
            print(f"Sentinel Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "run":
        if not args.token:
            print("Error: --token or SENTINEL_TOKEN is required.", file=sys.stderr)
            sys.exit(1)

        if not args.cmd_args:
            print("Error: No command specified.", file=sys.stderr)
            sys.exit(1)

        # Remove the '--' separator if present
        cmd_args = args.cmd_args
        if cmd_args[0] == "--":
            cmd_args = cmd_args[1:]

        if not cmd_args:
            print("Error: No command specified after --", file=sys.stderr)
            sys.exit(1)

        client = SentinelClient(
            base_url=args.url, api_token=args.token, agent_id=args.agent_id
        )

        try:
            # Fetch secrets
            print("Fetching secrets from Sentinel...", file=sys.stderr)
            secrets = client.fetch_secrets(environment=args.environment)

            # Prepare environment
            env = os.environ.copy()
            env.update(secrets)

            # Execute command
            # We use execvp to replace the current process, preserving signals/PID
            os.execvpe(cmd_args[0], cmd_args, env)

        except SentinelError as e:
            print(f"Sentinel Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Execution Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
