export interface AccessIntent {
  summary: string;
  description: string;
  task_id: string;
}

export interface AccessRequest {
  agent_id: string;
  resource_id: string;
  intent: AccessIntent;
  ttl_seconds: number;
}

export interface SecretPayload {
  type: string;
  value: string;
  expires_at: string;
}

export type AccessStatus = "APPROVED" | "PENDING_APPROVAL" | "DENIED";

export interface AccessResponse {
  request_id: string;
  status: AccessStatus;
  secret?: SecretPayload;
  message?: string;
  polling_url?: string;
  reason?: string;
}

export interface SentinelClientConfig {
  /**
   * Base URL for self-hosted / local Sentinel Vault server (handshake API).
   * Example: http://localhost:3000
   */
  baseUrl?: string;
  /**
   * API token / project key used for Authorization: Bearer ...
   * - Local mode: typically `sentinel_dev_key`
   * - Cloud mode: typically `sentinel_sk_...`
   */
  apiToken?: string;
  agentId?: string;
  pollingIntervalMs?: number;
  pollingTimeoutMs?: number;

  /**
   * Enable cloud mode by setting a Sentinel Cloud base URL.
   * Example: https://sentinel-cloud.vercel.app
   */
  cloudUrl?: string;
  /**
   * Optional default environment for cloud secret fetches.
   * Defaults to `production`.
   */
  environment?: string;
}

export interface RequestSecretOptions {
  resourceId: string;
  intent: AccessIntent;
  ttlSeconds?: number;
}

export interface FetchSecretsOptions {
  environment?: string;
}

export class SentinelError extends Error {
  public override readonly cause?: unknown;

  constructor(message: string, cause?: unknown) {
    super(message);
    this.name = "SentinelError";
    this.cause = cause;
  }
}

export class SentinelAuthError extends SentinelError {
  constructor(message: string, cause?: unknown) {
    super(message, cause);
    this.name = "SentinelAuthError";
  }
}

export class SentinelNetworkError extends SentinelError {
  constructor(message: string, cause?: unknown) {
    super(message, cause);
    this.name = "SentinelNetworkError";
  }
}

export class SentinelTimeoutError extends SentinelError {
  constructor(message: string) {
    super(message);
    this.name = "SentinelTimeoutError";
  }
}
