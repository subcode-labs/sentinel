import { z } from 'zod';
import { tool, generateText } from 'ai';
import { openai } from '@ai-sdk/openai'; // Example provider
import { SentinelClient } from '../../sdks/typescript/src'; // Relative import for this repo example

// Initialize Sentinel Client
const sentinel = new SentinelClient({
  baseUrl: process.env.SENTINEL_URL || 'http://localhost:3000',
  apiToken: process.env.SENTINEL_TOKEN || 'your-agent-token',
  agentId: 'vercel-ai-agent'
});

/**
 * A secure tool that wraps the Sentinel handshake.
 * 
 * The agent MUST provide a 'reason' for why it needs to use this tool.
 * This reason is logged by Sentinel and can require human approval.
 */
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
      console.log(`[System] Authenticated with token: ${token.substring(0, 4)}...`);
      
      // Simulate API latency
      await new Promise(resolve => setTimeout(resolve, 500));

      return `Found 3 repositories for "${query}" in ${orgName}:
      1. sentinel-core
      2. sentinel-sdk
      3. sentinel-docs`;

    } catch (error) {
      return `Security Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  },
});

/**
 * Example Usage
 */
async function main() {
  // Check if OPENAI_API_KEY is set, otherwise mock the agent loop
  if (!process.env.OPENAI_API_KEY) {
    console.log("OPENAI_API_KEY not set. Running mock execution of the tool directly...");
    
    // Mock execution
    const result = await searchGithubTool.execute({
        orgName: "subcode-labs",
        query: "sentinel",
        reason: "User asked to find the sentinel repositories"
    }, { toolCallId: '1', messages: [] });
    
    console.log("\nTool Result:", result);
    return;
  }

  // Real Agent Loop
  const result = await generateText({
    model: openai('gpt-4-turbo'),
    tools: {
      searchGithub: searchGithubTool,
    },
    prompt: 'Please find the sentinel repositories in the subcode-labs organization.',
    maxSteps: 5,
  });

  console.log(result.text);
}

if (require.main === module) {
  main().catch(console.error);
}
