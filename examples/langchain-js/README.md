# Sentinel + LangChain.js Example

This example demonstrates how to integrate Sentinel into a LangChain.js agent using custom Tools.

## How it works

1. We use the `SentinelClient` from `@subcode/sentinel-client`.
2. We wrap `client.requestWithPolling` in a `DynamicStructuredTool`.
3. The agent can invoke this tool when it needs a secret, providing context (Intent).
4. Sentinel handles the approval workflow (including human-in-the-loop if configured) and returns the secret.

## Prerequisites

- Node.js 18+
- Sentinel Server running (locally or cloud)

## Running the example

```bash
# Install dependencies
npm install

# Run the demo
npm start
```

## Integration Code

```typescript
export const createSentinelTool = (resourceId: string) => {
  return new DynamicStructuredTool({
    name: `get_secret_${resourceId}`,
    description: `Request access to the ${resourceId} secret securely.`,
    schema: z.object({
      task_id: z.string().describe("The ID of the task being performed"),
      reason: z.string().describe("Why you need this secret"),
    }),
    func: async ({ task_id, reason }) => {
      // ... Sentinel Client logic ...
    },
  });
};
```
