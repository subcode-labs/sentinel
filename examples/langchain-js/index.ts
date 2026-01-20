import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import { SentinelClient } from "@subcode/sentinel-client";

// Initialize Sentinel Client
const client = new SentinelClient({
  baseUrl: process.env.SENTINEL_URL || "http://localhost:3000",
  apiToken: process.env.SENTINEL_API_KEY || "sentinel_dev_key",
  agentId: "langchain-agent-js",
});

export const createSentinelTool = (resourceId: string) => {
  return new DynamicStructuredTool({
    name: `get_secret_${resourceId}`,
    description: `Request access to the ${resourceId} secret securely. Use this when you need the API key for ${resourceId}.`,
    schema: z.object({
      task_id: z.string().describe("The ID of the task being performed"),
      reason: z.string().describe("Why you need this secret"),
    }),
    func: async ({ task_id, reason }) => {
      console.log(`[Sentinel] Requesting access to ${resourceId}...`);
      
      try {
        const response = await client.requestWithPolling({
          resourceId,
          intent: {
            task_id,
            summary: `Access request for ${resourceId}`,
            description: reason,
          },
        });

        if (response.status === "APPROVED" && response.secret) {
          console.log(`[Sentinel] Access GRANTED for ${resourceId}`);
          return response.secret.value;
        } else {
          console.log(`[Sentinel] Access DENIED: ${response.message || response.reason}`);
          return `Access Denied: ${response.message || response.reason}`;
        }
      } catch (error: any) {
        console.error(`[Sentinel] Error: ${error.message}`);
        return `Error requesting access: ${error.message}`;
      }
    },
  });
};

async function main() {
  console.log("Starting Sentinel + LangChain.js Demo...");

  const tool = createSentinelTool("github_api_token");

  // Mock Agent invocation
  console.log("\nInvoking tool with intent...");
  const result = await tool.invoke({
    task_id: "TASK-101",
    reason: "Need to fetch repository issues",
  });

  console.log("Tool Result:", result);
}

if (require.main === module) {
  main().catch(console.error);
}
