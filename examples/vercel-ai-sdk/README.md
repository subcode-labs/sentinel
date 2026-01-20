# Sentinel + Vercel AI SDK Example

This example demonstrates how to integrate Sentinel into a Vercel AI SDK application using the `tool` API.

## How it works

1. We define a Vercel AI SDK `tool` that performs a sensitive operation (e.g., accessing GitHub).
2. Inside the tool's `execute` function, we use the `SentinelClient` to request a secret.
3. Sentinel captures the "intent" (why the agent needs the secret) and enforces policies (e.g., human approval).
4. If approval is needed, the `requestWithPolling` method waits until a human approves the request in the Sentinel Dashboard.
5. Once granted, the tool uses the secret to perform the action, ensuring the secret never leaks into the agent's prompt history or logs.

## Prerequisites

- Node.js 18+
- [Sentinel Server](https://github.com/subcode-labs/sentinel) running locally or in the cloud.
- Vercel AI SDK (`ai` package).

## Integration Code

```typescript
import { z } from 'zod';
import { tool } from 'ai';
import { SentinelClient } from '@subcode/sentinel-client';

// Initialize Sentinel Client
const sentinel = new SentinelClient({
  baseUrl: process.env.SENTINEL_URL || 'http://localhost:3000',
  apiToken: process.env.SENTINEL_TOKEN || 'your-agent-token',
  agentId: 'vercel-ai-agent'
});

// Define a secure tool
export const searchGithubTool = tool({
  description: 'Search for repositories in a GitHub organization. Requires secure access.',
  parameters: z.object({
    orgName: z.string().describe('The GitHub organization to search'),
    query: z.string().describe('Search query for repositories'),
    reason: z.string().describe('Explanation of why this search is necessary (for security audit)')
  }),
  execute: async ({ orgName, query, reason }) => {
    try {
      // 1. Request Secret with Intent
      console.log(`[Sentinel] Requesting GitHub token for: "${reason}"`);
      
      const access = await sentinel.requestWithPolling({
        resourceId: 'github_token',
        intent: {
          summary: `Search GitHub: ${orgName}/${query}`,
          description: reason,
          task_id: `task-${Date.now()}`
        }
      });

      if (access.status !== 'APPROVED' || !access.secret) {
        return `Error: Access to GitHub token was ${access.status}.`;
      }

      // 2. Use the Secret (The token is ephemeral and only exists in this scope)
      const token = access.secret.value;
      
      // Mocking the GitHub API call for this example
      // In a real app, you would use: fetch('https://api.github.com/...', { headers: { Authorization: `Bearer ${token}` } })
      console.log(`[System] Authenticated with token: ${token.substring(0, 4)}...`);
      
      return `Found 3 repositories for "${query}" in ${orgName}:
      1. sentinel-core
      2. sentinel-sdk
      3. sentinel-docs`;

    } catch (error) {
      return `Security Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  },
});
```
