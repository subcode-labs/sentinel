import { Database } from "bun:sqlite";
import { join } from "node:path";
import { Hono } from "hono";
import { bearerAuth } from "hono/bearer-auth";
import { z } from "zod";
import { adminHtml } from "./admin_ui";
import type { AccessResponse, AccessStatus } from "./types";

const app = new Hono();

// Persistence: SQLite
const dbPath =
  process.env.NODE_ENV === "test"
    ? ":memory:"
    : process.env.DB_PATH || join(import.meta.dir, "../sentinel.db");
const db = new Database(dbPath);

// Initialize schema
db.run(`
  CREATE TABLE IF NOT EXISTS requests (
    id TEXT PRIMARY KEY,
    agent_id TEXT,
    resource_id TEXT,
    intent TEXT,
    status TEXT,
    response TEXT,
    created_at TEXT
  )
`);

db.run(`
  CREATE TABLE IF NOT EXISTS secrets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id TEXT,
    version INTEGER,
    value TEXT,
    created_at TEXT
  )
`);

function getOrCreateSecret(resourceId: string): {
  value: string;
  version: number;
} {
  const secret = db
    .query(
      "SELECT * FROM secrets WHERE resource_id = ? ORDER BY version DESC LIMIT 1",
    )
    .get(resourceId) as any;
  if (secret) {
    return { value: secret.value, version: secret.version };
  }

  const value = `secret_v1_${Math.random().toString(36).substring(2)}`;
  db.prepare(
    "INSERT INTO secrets (resource_id, version, value, created_at) VALUES (?, ?, ?, ?)",
  ).run(resourceId, 1, value, new Date().toISOString());
  return { value, version: 1 };
}

// Secret key for dev
const API_TOKEN = process.env.SENTINEL_API_KEY || "sentinel_dev_key";

if (process.env.NODE_ENV !== "test" && API_TOKEN === "sentinel_dev_key") {
  console.warn(
    "WARNING: Running with default insecure API token 'sentinel_dev_key'. Set SENTINEL_API_KEY for production.",
  );
}

// Middleware: Logger & Auth
app.use("/v1/*", bearerAuth({ token: API_TOKEN }));

// Serve Admin Dashboard
app.get("/admin", (c) => c.html(adminHtml));

const AccessIntentSchema = z.object({
  summary: z.string(),
  description: z.string(),
  task_id: z.string(),
});

const AccessRequestSchema = z.object({
  agent_id: z.string(),
  resource_id: z.string(),
  intent: AccessIntentSchema,
  ttl_seconds: z.number().positive(),
});

app.post("/v1/access/request", async (c) => {
  try {
    const rawBody = await c.req.json();
    const validation = AccessRequestSchema.safeParse(rawBody);

    if (!validation.success) {
      return c.json(
        { error: "Invalid Request", details: validation.error },
        400,
      );
    }

    const body = validation.data;
    const requestId = `req_${Math.random().toString(36).substring(2, 9)}`;
    const now = new Date().toISOString();

    // 1. Audit Logging (The "Intent")
    console.log(
      `[AUDIT] Request from ${body.agent_id} for ${body.resource_id}`,
    );
    console.log(
      `[AUDIT] Intent: ${body.intent.summary} (${body.intent.task_id})`,
    );

    // 2. Policy Engine (Mock)
    let status: AccessStatus = "APPROVED";
    let response: AccessResponse = {
      request_id: requestId,
      status: "APPROVED",
    };

    if (
      body.resource_id.includes("prod") ||
      body.resource_id.includes("sensitive")
    ) {
      status = "PENDING_APPROVAL";
      response = {
        request_id: requestId,
        status: "PENDING_APPROVAL",
        message: "This resource requires human approval. Check status later.",
        polling_url: `/v1/access/requests/${requestId}`,
      };

      // Notify Admin via Webhook (if configured)
      const webhookUrl = process.env.SENTINEL_WEBHOOK_URL;
      if (webhookUrl) {
        // Fire and forget - don't block the response
        fetch(webhookUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text: `🛡️ **Sentinel Access Request**\n\n**Agent:** ${body.agent_id}\n**Resource:** ${body.resource_id}\n**Intent:** ${body.intent.summary}\n\nApprove: ${process.env.SENTINEL_URL || "http://localhost:3000"}/admin`,
          }),
        }).catch((e) => console.error("[Webhook] Failed to send notification:", e));
      }
    } else if (body.resource_id.includes("forbidden")) {
      status = "DENIED";
      response = {
        request_id: requestId,
        status: "DENIED",
        reason: "Policy Violation: Blocked by static policy.",
      };
    } else {
      // Approved
      const { value } = getOrCreateSecret(body.resource_id);
      response.secret = {
        type: "managed_secret",
        value: value,
        expires_at: new Date(
          Date.now() + body.ttl_seconds * 1000,
        ).toISOString(),
      };
    }

    // Store state
    const insert = db.prepare(`
      INSERT INTO requests (id, agent_id, resource_id, intent, status, response, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `);
    insert.run(
      requestId,
      body.agent_id,
      body.resource_id,
      JSON.stringify(body.intent),
      status,
      JSON.stringify(response),
      now,
    );

    return c.json(
      response,
      status === "DENIED" ? 403 : status === "PENDING_APPROVAL" ? 202 : 200,
    );
  } catch (err) {
    console.error(err);
    return c.json({ error: "Invalid Request" }, 400);
  }
});

app.get("/v1/access/requests/:id", (c) => {
  const id = c.req.param("id");
  const record = db.query("SELECT * FROM requests WHERE id = ?").get(id) as any;

  if (!record) {
    return c.json({ error: "Request not found" }, 404);
  }

  return c.json(JSON.parse(record.response));
});

// --- Admin API ---

// List all requests
app.get("/v1/admin/requests", (c) => {
  const statusFilter = c.req.query("status");
  let query = "SELECT * FROM requests";
  const params: string[] = [];

  if (statusFilter) {
    query += " WHERE status = ?";
    params.push(statusFilter);
  }

  query += " ORDER BY created_at DESC";

  const requests = db.query(query).all(...params);

  // Parse payload for each
  const results = requests.map((r: any) => ({
    ...r,
    intent: JSON.parse(r.intent),
    response: JSON.parse(r.response),
  }));

  return c.json(results);
});

// Approve request
app.post("/v1/admin/requests/:id/approve", (c) => {
  const id = c.req.param("id");
  const record = db.query("SELECT * FROM requests WHERE id = ?").get(id) as any;

  if (!record) {
    return c.json({ error: "Request not found" }, 404);
  }

  if (record.status !== "PENDING_APPROVAL") {
    return c.json(
      { error: `Cannot approve request with status ${record.status}` },
      400,
    );
  }

  const _response = JSON.parse(record.response);
  const resourceId = record.resource_id;

  // Update logic
  const newStatus = "APPROVED";
  // Standard TTL for admin approval: 1 hour (mock)
  const expiresAt = new Date(Date.now() + 3600 * 1000).toISOString();

  const newPayload: AccessResponse = {
    request_id: id,
    status: newStatus,
    secret: {
      type: "dummy_secret",
      value: `super_secret_value_for_${resourceId}`,
      expires_at: expiresAt,
    },
  };

  db.prepare("UPDATE requests SET status = ?, response = ? WHERE id = ?").run(
    newStatus,
    JSON.stringify(newPayload),
    id,
  );

  return c.json(newPayload);
});

// Deny request
app.post("/v1/admin/requests/:id/deny", (c) => {
  const id = c.req.param("id");
  const record = db.query("SELECT * FROM requests WHERE id = ?").get(id) as any;

  if (!record) {
    return c.json({ error: "Request not found" }, 404);
  }

  if (record.status !== "PENDING_APPROVAL") {
    return c.json(
      { error: `Cannot deny request with status ${record.status}` },
      400,
    );
  }

  const newStatus = "DENIED";
  const newPayload: AccessResponse = {
    request_id: id,
    status: newStatus,
    reason: "Denied by administrator.",
  };

  db.prepare("UPDATE requests SET status = ?, response = ? WHERE id = ?").run(
    newStatus,
    JSON.stringify(newPayload),
    id,
  );

  return c.json(newPayload);
});

// Rotate secret
app.post("/v1/admin/secrets/:resource_id/rotate", (c) => {
  const resourceId = c.req.param("resource_id");
  const { version } = getOrCreateSecret(resourceId); // Ensure at least v1 exists
  const newVersion = version + 1;
  const newValue = `secret_v${newVersion}_${Math.random().toString(36).substring(2)}`;

  db.prepare(
    "INSERT INTO secrets (resource_id, version, value, created_at) VALUES (?, ?, ?, ?)",
  ).run(resourceId, newVersion, newValue, new Date().toISOString());

  return c.json({
    resource_id: resourceId,
    version: newVersion,
    status: "ROTATED",
  });
});

// List all secrets
app.get("/v1/admin/secrets", (c) => {
  const secrets = db
    .query("SELECT * FROM secrets ORDER BY resource_id ASC, version DESC")
    .all();
  return c.json(secrets);
});

export { app };

export default {
  port: parseInt(process.env.PORT || "3000", 10),
  fetch: app.fetch,
};
