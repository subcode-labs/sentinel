import { describe, expect, test, mock, beforeAll, afterAll } from "bun:test";
import { SentinelClient } from "./index";

describe("SentinelClient", () => {
  const originalFetch = global.fetch;

  afterAll(() => {
    global.fetch = originalFetch;
  });

  test("listResources returns array of strings", async () => {
    const mockFetch = mock(async (url) => {
      if (url.toString().includes("/v1/resources")) {
        return new Response(JSON.stringify(["res1", "res2"]), {
          status: 200,
        });
      }
      return new Response("Not Found", { status: 404 });
    });

    global.fetch = mockFetch;

    const client = new SentinelClient({
      apiToken: "test-token",
      baseUrl: "http://localhost:3000",
    });

    const resources = await client.listResources();
    expect(resources).toEqual(["res1", "res2"]);
    expect(mockFetch).toHaveBeenCalled();
  });

  test("listResources handles 401", async () => {
    const mockFetch = mock(async () => {
      return new Response("Unauthorized", { status: 401 });
    });

    global.fetch = mockFetch;

    const client = new SentinelClient({
      apiToken: "invalid",
      baseUrl: "http://localhost:3000",
    });

    try {
      await client.listResources();
      expect(true).toBe(false); // Should not reach here
    } catch (e: any) {
      expect(e.name).toBe("SentinelAuthError");
    }
  });
});
