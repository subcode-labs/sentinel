import { describe, expect, it } from "bun:test";
import { app } from "./server";
import type { AccessResponse } from "./types";

const API_TOKEN = "sentinel_dev_key";

describe("Sentinel Server", () => {
  const authHeaders = {
    Authorization: `Bearer ${API_TOKEN}`,
    "Content-Type": "application/json",
  };

  describe("POST /v1/access/request", () => {
    it("should grant access to non-sensitive resources (status 200)", async () => {
      const res = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "test_agent",
          resource_id: "dev_db",
          intent: {
            summary: "Read dev data",
            description: "Debugging local issue",
            task_id: "task_123",
          },
          ttl_seconds: 3600,
        }),
      });

      expect(res.status).toBe(200);
      const data = (await res.json()) as AccessResponse;
      expect(data.status).toBe("APPROVED");
      expect(data.secret).toBeDefined();
      expect(data.secret?.value).toMatch(/^secret_v1_/);
    });

    it("should return 202 for prod resources (PENDING_APPROVAL)", async () => {
      const res = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "test_agent",
          resource_id: "prod_db",
          intent: {
            summary: "Critical fix",
            description: "Fixing prod outage",
            task_id: "outage_456",
          },
          ttl_seconds: 3600,
        }),
      });

      expect(res.status).toBe(202);
      const data = (await res.json()) as AccessResponse;
      expect(data.status).toBe("PENDING_APPROVAL");
      expect(data.polling_url).toBeDefined();
      expect(data.request_id).toBeDefined();
    });

    it("should return 403 for forbidden resources (DENIED)", async () => {
      const res = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "test_agent",
          resource_id: "forbidden_resource",
          intent: {
            summary: "Hacking",
            description: "Attempting to access forbidden resource",
            task_id: "hack_789",
          },
          ttl_seconds: 3600,
        }),
      });

      expect(res.status).toBe(403);
      const data = (await res.json()) as AccessResponse;
      expect(data.status).toBe("DENIED");
      expect(data.reason).toBeDefined();
    });

    it("should return 401 for invalid token", async () => {
      const res = await app.request("/v1/access/request", {
        method: "POST",
        headers: {
          ...authHeaders,
          Authorization: "Bearer wrong_token",
        },
        body: JSON.stringify({}),
      });

      expect(res.status).toBe(401);
    });
  });

  describe("Admin Flow", () => {
    it("should list requests and filter by status", async () => {
      // Create a pending request first
      const reqRes = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "admin_test_agent",
          resource_id: "prod_server",
          intent: {
            summary: "Admin test",
            description: "Testing admin list",
            task_id: "admin_1",
          },
          ttl_seconds: 3600,
        }),
      });
      const reqData = (await reqRes.json()) as AccessResponse;
      const requestId = reqData.request_id;

      // List all
      const listRes = await app.request("/v1/admin/requests", {
        headers: authHeaders,
      });
      expect(listRes.status).toBe(200);
      const allRequests = (await listRes.json()) as any[];
      expect(allRequests.length).toBeGreaterThan(0);
      expect(allRequests.find((r) => r.id === requestId)).toBeDefined();

      // Filter by status
      const filterRes = await app.request(
        "/v1/admin/requests?status=PENDING_APPROVAL",
        {
          headers: authHeaders,
        },
      );
      const pendingRequests = (await filterRes.json()) as any[];
      expect(
        pendingRequests.every((r) => r.status === "PENDING_APPROVAL"),
      ).toBe(true);
    });

    it("should approve a pending request", async () => {
      // 1. Create pending request
      const reqRes = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "approver_agent",
          resource_id: "sensitive_data",
          intent: { summary: "Need access", description: "...", task_id: "t1" },
          ttl_seconds: 3600,
        }),
      });
      const requestId = ((await reqRes.json()) as any).request_id;

      // 2. Approve it
      const approveRes = await app.request(
        `/v1/admin/requests/${requestId}/approve`,
        {
          method: "POST",
          headers: authHeaders,
        },
      );
      expect(approveRes.status).toBe(200);
      const approveData = (await approveRes.json()) as AccessResponse;
      expect(approveData.status).toBe("APPROVED");
      expect(approveData.secret).toBeDefined();

      // 3. Verify polling returns approved
      const pollRes = await app.request(`/v1/access/requests/${requestId}`, {
        headers: authHeaders,
      });
      const pollData = (await pollRes.json()) as AccessResponse;
      expect(pollData.status).toBe("APPROVED");
      expect(pollData.secret).toBeDefined();
    });

    it("should deny a pending request", async () => {
      // 1. Create pending request
      const reqRes = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "denier_agent",
          resource_id: "sensitive_data_2",
          intent: { summary: "Need access", description: "...", task_id: "t2" },
          ttl_seconds: 3600,
        }),
      });
      const requestId = ((await reqRes.json()) as any).request_id;

      // 2. Deny it
      const denyRes = await app.request(
        `/v1/admin/requests/${requestId}/deny`,
        {
          method: "POST",
          headers: authHeaders,
        },
      );
      expect(denyRes.status).toBe(200);
      const denyData = (await denyRes.json()) as AccessResponse;
      expect(denyData.status).toBe("DENIED");

      // 3. Verify polling returns denied
      const pollRes = await app.request(`/v1/access/requests/${requestId}`, {
        headers: authHeaders,
      });
      const pollData = (await pollRes.json()) as AccessResponse;
      expect(pollData.status).toBe("DENIED");
      expect(pollData.reason).toBeDefined();
    });
  });

  describe("Secret Rotation", () => {
    it("should rotate secrets for a resource", async () => {
      const resourceId = "rotatable_resource";

      // 1. Get initial secret (by requesting it)
      const res1 = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "test_agent",
          resource_id: resourceId,
          intent: { summary: "...", description: "...", task_id: "..." },
          ttl_seconds: 3600,
        }),
      });
      const data1 = (await res1.json()) as AccessResponse;
      const val1 = data1.secret?.value;

      // 2. Rotate secret
      const rotateRes = await app.request(
        `/v1/admin/secrets/${resourceId}/rotate`,
        {
          method: "POST",
          headers: authHeaders,
        },
      );
      expect(rotateRes.status).toBe(200);
      const rotateData = (await rotateRes.json()) as any;
      expect(rotateData.status).toBe("ROTATED");
      expect(rotateData.version).toBe(2);

      // 3. Request again and verify it's different
      const res2 = await app.request("/v1/access/request", {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({
          agent_id: "test_agent",
          resource_id: resourceId,
          intent: { summary: "...", description: "...", task_id: "..." },
          ttl_seconds: 3600,
        }),
      });
      const data2 = (await res2.json()) as AccessResponse;
      const val2 = data2.secret?.value;

      expect(val2).not.toBe(val1);
      expect(val2).toMatch(/^secret_v2_/);
    });

    it("should list all secrets (Admin)", async () => {
      // Ensure we have secrets
      await app.request(`/v1/admin/secrets/rotatable_resource/rotate`, {
        method: "POST",
        headers: authHeaders,
      });

      const res = await app.request("/v1/admin/secrets", {
        headers: authHeaders,
      });

      expect(res.status).toBe(200);
      const secrets = (await res.json()) as any[];
      expect(secrets.length).toBeGreaterThan(0);

      const resourceSecrets = secrets.filter(
        (s) => s.resource_id === "rotatable_resource",
      );
      expect(resourceSecrets.length).toBeGreaterThanOrEqual(2);
    });
  });
});
