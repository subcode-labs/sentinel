import os
import time
from sentinel_sdk import SentinelClient
from sentinel_sdk.types import AccessIntent

# --- Mock Agent Framework ---


class Agent:
    def __init__(self, name: str, role: str, sentinel_client: SentinelClient):
        self.name = name
        self.role = role
        self.sentinel = sentinel_client


class ManagerAgent(Agent):
    def delegate(self):
        print(f"\n[{self.name}] 🤖 Manager starting delegation sequence...")
        print(f"[{self.name}] Identifying task: 'Competitor Analysis'")
        print(f"[{self.name}] Spawning Worker Agent...")

        # In a real system, we might spawn a new process/container.
        # The Worker is initialized with its own identity ("worker-01").
        # We share the API Token for this simulation, but in production,
        # the Worker might have a restricted token or inherit one.
        worker_client = SentinelClient(
            base_url=self.sentinel.base_url,
            api_token=self.sentinel.api_token,
            agent_id="worker-01",
            environment=self.sentinel.environment,
        )

        worker = WorkerAgent("Worker-01", "Researcher", worker_client)
        worker.work("Search for 'Sentinel SDK Features'")


class WorkerAgent(Agent):
    def work(self, task: str):
        print(f"\n[{self.name}] 👷 Received task: '{task}'")

        # Step 1: Discovery
        # The agent checks what resources are available to it in this environment.
        print(
            f"[{self.name}] 🔍 Discovering available secrets/tools in '{self.sentinel.environment}'..."
        )
        try:
            resources = self.sentinel.list_resources()
            print(f"[{self.name}] 📜 Available Resources: {resources}")
        except Exception as e:
            print(f"[{self.name}] ❌ Discovery Failed: {e}")
            return

        # Step 2: Identification
        # The agent identifies it needs a search tool.
        # In this demo, we look for 'SERPER_API_KEY' or fallback to a test key.
        target_secret = "SERPER_API_KEY"
        if target_secret not in resources:
            print(
                f"[{self.name}] ⚠️  '{target_secret}' not found in discovery list. Attempting request anyway..."
            )

        # Step 3: Access Request
        # The agent explicitly requests access to the specific resource for this specific task.
        print(f"[{self.name}] 🔐 Requesting access to '{target_secret}'...")

        try:
            secret = self.sentinel.request_secret(
                resource_id=target_secret,
                intent=AccessIntent(
                    summary=f"Performing task: {task}",
                    description="Worker needs access to external search tool to complete research.",
                    task_id="job-123",
                ),
            )

            # Step 4: Execution
            print(f"[{self.name}] ✅ Access GRANTED!")
            print(f"[{self.name}] 🗝️  Secret Value: {secret.value[:4]}... (redacted)")
            print(f"[{self.name}] 🚀 Executing task with secret...")
            time.sleep(1)  # Simulate work
            print(f"[{self.name}] ✨ Task Complete.")

        except Exception as e:
            print(f"[{self.name}] ❌ Access DENIED or Error: {e}")
            print(f"[{self.name}] 🛑 Worker halting.")


# --- Main Entry Point ---


def main():
    base_url = os.environ.get("SENTINEL_URL", "http://localhost:3000")
    api_token = os.environ.get("SENTINEL_API_KEY")
    environment = os.environ.get("SENTINEL_ENVIRONMENT", "production")

    if not api_token:
        print("Error: SENTINEL_API_KEY not set.")
        print("Please set SENTINEL_API_KEY and run again.")
        return

    print(f"--- Sentinel Multi-Agent Delegation Demo ---")
    print(f"Connecting to: {base_url}")
    print(f"Environment:   {environment}")

    # Manager initializes its client
    manager_client = SentinelClient(
        base_url=base_url,
        api_token=api_token,
        agent_id="manager-alice",
        environment=environment,
    )

    manager = ManagerAgent("Manager-Alice", "Overseer", manager_client)
    manager.delegate()


if __name__ == "__main__":
    main()
