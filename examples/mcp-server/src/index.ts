#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import { SentinelClient } from "@subcode/sentinel-client";

// Configuration from environment
const SENTINEL_TOKEN = process.env.SENTINEL_TOKEN;
const SENTINEL_PROJECT = process.env.SENTINEL_PROJECT;
// SENTINEL_ENV is picked up by the SDK automatically as default, but we can also use it for validation

if (!SENTINEL_TOKEN) {
  console.error("Error: SENTINEL_TOKEN environment variable is required.");
  process.exit(1);
}

// Initialize Sentinel Client
// The client will automatically pick up SENTINEL_TOKEN, SENTINEL_URL, SENTINEL_CLOUD_URL etc. from env
const client = new SentinelClient();

const server = new Server(
  {
    name: "sentinel-mcp-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define Tools
const LIST_SECRETS_TOOL = {
  name: "list_secrets",
  description: "List all available secrets in a project/environment.",
  inputSchema: {
    type: "object",
    properties: {
      project: {
        type: "string",
        description: "Project slug",
      },
      environment: {
        type: "string",
        description: "Environment slug (e.g., 'dev', 'prod')",
      },
    },
    required: ["project", "environment"],
  },
};

const GET_SECRET_TOOL = {
  name: "get_secret",
  description: "Retrieve the sensitive value of a specific secret. Requesting access will generate an audit log and may require approval.",
  inputSchema: {
    type: "object",
    properties: {
      project: {
        type: "string",
        description: "Project slug",
      },
      environment: {
        type: "string",
        description: "Environment slug (e.g., 'dev', 'prod')",
      },
      key: {
        type: "string",
        description: "The secret key name",
      },
      version: {
        type: "integer",
        description: "Specific version of the secret to fetch (optional)",
      },
      reason: {
        type: "string",
        description: "Reason for accessing this secret (for audit logs)",
      },
    },
    required: ["project", "environment", "key"],
  },
};

// Handle List Tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [LIST_SECRETS_TOOL, GET_SECRET_TOOL],
  };
});

// Handle Call Tool
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (!args) {
    throw new McpError(ErrorCode.InvalidParams, "Missing arguments");
  }

  try {
    if (name === "list_secrets") {
      const { project, environment } = args as { project: string; environment: string };

      if (!project || !environment) {
        throw new McpError(ErrorCode.InvalidParams, "Missing required arguments: project, environment");
      }

      // Optional: Validate project if SENTINEL_PROJECT is set
      if (SENTINEL_PROJECT && project !== SENTINEL_PROJECT) {
        console.error(`Warning: Requested project '${project}' does not match configured SENTINEL_PROJECT '${SENTINEL_PROJECT}'. Using configured token scope.`);
      }

      const secretKeys = await client.listResources({ environment });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(secretKeys, null, 2),
          },
        ],
      };
    }

    if (name === "get_secret") {
      const { project, environment, key, version, reason } = args as {
        project: string;
        environment: string;
        key: string;
        version?: number;
        reason?: string;
      };

      if (!project || !environment || !key) {
        throw new McpError(ErrorCode.InvalidParams, "Missing required arguments: project, environment, key");
      }

      if (SENTINEL_PROJECT && project !== SENTINEL_PROJECT) {
        console.error(`Warning: Requested project '${project}' does not match configured SENTINEL_PROJECT '${SENTINEL_PROJECT}'.`);
      }

      // Use requestSecret to support versioning and intent
      const response = await client.requestSecret({
        resourceId: key,
        version,
        environment,
        intent: {
          summary: reason || "Accessed via MCP",
          description: `Agent requested secret ${key} via MCP Tool`,
          task_id: "mcp-task-" + Date.now(),
        },
      });

      if (response.status === "APPROVED" && response.secret) {
        return {
          content: [
            {
              type: "text",
              text: response.secret.value,
            },
          ],
        };
      }

      if (response.status === "PENDING_APPROVAL") {
        return {
          content: [
            {
              type: "text",
              text: `Access Request Pending. Please approve the request here: ${
                process.env.SENTINEL_CLOUD_URL ||
                "https://sentinel-cloud.vercel.app"
              }/dashboard`,
            },
          ],
          isError: true,
        };
      }

      throw new McpError(
        ErrorCode.InvalidRequest,
        `Access Denied: ${response.message || response.reason}`
      );
    }

    throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  } catch (error) {
    if (error instanceof McpError) throw error;

    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [
        {
          type: "text",
          text: `Error processing request: ${errorMessage}`,
        },
      ],
      isError: true,
    };
  }
});

// Start Server
async function run() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Sentinel MCP Server running on stdio");
}

run().catch((error) => {
  console.error("Fatal error running server:", error);
  process.exit(1);
});
