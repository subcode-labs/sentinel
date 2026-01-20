import { spawn } from "child_process";
import { describe, expect, test, beforeAll, afterAll } from "bun:test";
import { join } from "path";

const SENTINEL_PORT = 3042;
const SENTINEL_URL = `http://localhost:${SENTINEL_PORT}`;
const SENTINEL_TOKEN = "mcp_test_token";

let sentinelProcess: any;

// Helper to send JSON-RPC to MCP Server and wait for response
async function sendRequest(proc: any, request: any): Promise<any> {
  return new Promise((resolve, reject) => {
    let buffer = "";
    
    const onData = (data: Buffer) => {
      buffer += data.toString();
      const lines = buffer.split("\n");
      
      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const json = JSON.parse(line);
          // Check if this is the response to our request ID
          if (json.id === request.id) {
             proc.stdout.off("data", onData); // Stop listening
             resolve(json);
             return;
          }
        } catch (e) {
          // Partial JSON or unrelated output, ignore
        }
      }
    };

    proc.stdout.on("data", onData);
    
    const input = JSON.stringify(request) + "\n";
    proc.stdin.write(input);
    
    // Timeout safety
    setTimeout(() => {
        proc.stdout.off("data", onData);
        reject(new Error(`Timeout waiting for response to ${request.id}`));
    }, 5000);
  });
}

describe("MCP Server Integration", () => {
  beforeAll(async () => {
    console.log("Starting Sentinel Server...");
    // Start Sentinel Server relative to mcp-server dir
    // mcp-server is at sentinel/examples/mcp-server
    // server.ts is at sentinel/src/server.ts
    const serverPath = join(import.meta.dir, "../../../src/server.ts");
    
    sentinelProcess = spawn("bun", ["run", serverPath], {
      cwd: join(import.meta.dir, "../../.."), // Run from repo root
      env: {
        ...process.env,
        PORT: SENTINEL_PORT.toString(),
        SENTINEL_API_KEY: SENTINEL_TOKEN, // Use SENTINEL_API_KEY as per server.ts
        NODE_ENV: "test",
        DB_PATH: ":memory:" 
      },
      stdio: "pipe" 
    });
    
    // Wait for server to be ready
    await new Promise((resolve) => {
        sentinelProcess.stdout.on('data', (data: Buffer) => {
            // console.log("Server:", data.toString());
            if (data.toString().includes("Running on port")) {
                resolve(true);
            }
        });
        // Fallback timeout
        setTimeout(resolve, 3000);
    });
    console.log("Sentinel Server started.");
  });

  afterAll(() => {
    if (sentinelProcess) {
        sentinelProcess.kill();
        console.log("Sentinel Server stopped.");
    }
  });

  test("Should list secrets via MCP", async () => {
    const indexPath = join(import.meta.dir, "../dist/index.js");
    console.log("Starting MCP Server from:", indexPath);

    const mcpProcess = spawn("node", [indexPath], {
       env: {
         ...process.env,
         SENTINEL_URL: SENTINEL_URL,
         SENTINEL_TOKEN: SENTINEL_TOKEN,
         SENTINEL_PROJECT: "default",
         SENTINEL_ENV: "dev"
       },
       stdio: ['pipe', 'pipe', 'inherit'] // pipe stdin/out, inherit stderr
    });

    try {
        // 1. Initialize
        const initReq = {
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
            protocolVersion: "2024-11-05",
            capabilities: {},
            clientInfo: { name: "test-client", version: "1.0.0" }
        }
        };
        
        console.log("Sending initialize...");
        const initRes = await sendRequest(mcpProcess, initReq);
        expect(initRes.result.serverInfo.name).toBe("sentinel-mcp-server");

        // 2. Initialized Notification
        mcpProcess.stdin.write(JSON.stringify({
        jsonrpc: "2.0",
        method: "notifications/initialized"
        }) + "\n");

        // 3. List Tools
        const listToolsReq = {
        jsonrpc: "2.0",
        id: 2,
        method: "tools/list"
        };
        console.log("Sending tools/list...");
        const listToolsRes = await sendRequest(mcpProcess, listToolsReq);
        expect(listToolsRes.result.tools).toBeDefined();
        const toolNames = listToolsRes.result.tools.map((t: any) => t.name);
        expect(toolNames).toContain("list_secrets");
        expect(toolNames).toContain("get_secret");

        // 4. Call list_secrets (Should be empty initially)
        const callReq = {
        jsonrpc: "2.0",
        id: 3,
        method: "tools/call",
        params: {
            name: "list_secrets",
            arguments: {
            project: "default",
            environment: "dev"
            }
        }
        };
        
        console.log("Calling list_secrets (1)...");
        const callRes = await sendRequest(mcpProcess, callReq);
        const content = JSON.parse(callRes.result.content[0].text);
        expect(Array.isArray(content)).toBe(true);
        expect(content).toHaveLength(0);

        // 5. Call get_secret (Auto-approve for 'dev_secret')
        const getReq = {
            jsonrpc: "2.0",
            id: 4,
            method: "tools/call",
            params: {
                name: "get_secret",
                arguments: {
                    project: "default",
                    environment: "dev",
                    key: "dev_secret",
                    reason: "Integration Test"
                }
            }
        };
        console.log("Calling get_secret...");
        const getRes = await sendRequest(mcpProcess, getReq);
        const secretValue = getRes.result.content[0].text;
        expect(secretValue).toContain("secret_v1_");

        // 6. Call list_secrets again (Should contain dev_secret)
        const callReq2 = {
            jsonrpc: "2.0",
            id: 5,
            method: "tools/call",
            params: {
                name: "list_secrets",
                arguments: {
                project: "default",
                environment: "dev"
                }
            }
        };
        console.log("Calling list_secrets (2)...");
        const callRes2 = await sendRequest(mcpProcess, callReq2);
        const content2 = JSON.parse(callRes2.result.content[0].text);
        expect(content2).toContain("dev_secret");


    } finally {
        mcpProcess.kill();
    }
  });
});
