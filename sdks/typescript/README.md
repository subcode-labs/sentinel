# Sentinel TypeScript Client

The official TypeScript SDK for [Sentinel](https://github.com/subcode-labs/sentinel), the secure secret management vault for AI agents.

## Installation

```bash
npm install @subcode/sentinel-client
# or
bun add @subcode/sentinel-client
```

## Usage

### Cloud Mode (Recommended)

Fetch secrets securely from Sentinel Cloud.

```typescript
import { SentinelClient } from "@subcode/sentinel-client";

const client = new SentinelClient({
  // Defaults to process.env.SENTINEL_TOKEN
  apiToken: "sentinel_sk_...", 
});

async function main() {
  // Fetch all secrets for the production environment
  const secrets = await client.fetchSecrets({ environment: "production" });
  
  console.log(secrets.DATABASE_URL);
}

main();
```

### Local Mode (Agent Handshake)

Request access to specific secrets from a local Sentinel Vault with human-in-the-loop approval.

```typescript
import { SentinelClient } from "@subcode/sentinel-client";

const client = new SentinelClient({
  baseUrl: "http://localhost:3000", // Local Sentinel Vault
  apiToken: "sentinel_dev_key",
  agentId: "my-coding-agent"
});

async function main() {
  const response = await client.requestWithPolling({
    resourceId: "stripe_api_key",
    intent: {
      summary: "Process subscription",
      description: "Need Stripe key to charge user for plan",
      task_id: "task-123"
    }
  });

  if (response.status === "APPROVED" && response.secret) {
    console.log("Secret received:", response.secret.value);
  } else {
    console.log("Access denied or failed:", response.message);
  }
}
```

### Discover Resources

List available resource IDs that you can request.

```typescript
const resources = await client.listResources();
console.log("Available resources:", resources);
```
