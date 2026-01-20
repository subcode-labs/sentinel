import type {
  AccessRequest,
  AccessResponse,
  FetchSecretsOptions,
  RequestSecretOptions,
  SentinelClientConfig,
} from "./types";
import {
  SentinelAuthError,
  SentinelError,
  SentinelNetworkError,
  SentinelTimeoutError,
} from "./types";

export type SentinelSecrets = Record<string, string>;

type CloudSecretsResponse = {
  secrets: SentinelSecrets;
};

export class SentinelClient {
  private readonly baseUrl: string;
  private readonly apiToken: string;
  private readonly agentId: string;
  private readonly pollingIntervalMs: number;
  private readonly pollingTimeoutMs: number;
  private readonly cloudUrl: string;
  private readonly environment: string;

  constructor(config: SentinelClientConfig = {}) {
    this.baseUrl =
      config.baseUrl ?? process.env.SENTINEL_URL ?? "http://localhost:3000";
    this.apiToken = config.apiToken ?? process.env.SENTINEL_TOKEN ?? "";
    this.agentId = config.agentId ?? process.env.AGENT_ID ?? "unknown-agent";
    this.pollingIntervalMs = config.pollingIntervalMs ?? 2000;
    this.pollingTimeoutMs = config.pollingTimeoutMs ?? 300000;

    this.cloudUrl =
      config.cloudUrl ??
      process.env.SENTINEL_CLOUD_URL ??
      "https://sentinel-cloud.vercel.app";
    this.environment =
      config.environment ?? process.env.SENTINEL_ENVIRONMENT ?? "production";

    if (!this.apiToken) {
      throw new SentinelError(
        "API token is required. Provide via config.apiToken or SENTINEL_TOKEN env var.",
      );
    }
  }

  /**
   * Cloud mode: fetch all secrets for a project/environment.
   *
   * Endpoint:
   * - GET {cloudUrl}/api/v1/secrets?environment=production
   * - Authorization: Bearer sentinel_sk_...
   */
  async fetchSecrets(
    options: FetchSecretsOptions = {},
  ): Promise<SentinelSecrets> {
    const environment = options.environment ?? this.environment;
    const url = new URL("/api/v1/secrets", this.cloudUrl);
    url.searchParams.set("environment", environment);

    try {
      const response = await fetch(url.toString(), {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${this.apiToken}`,
        },
      });

      if (response.status === 401 || response.status === 403) {
        const errorText = await response.text().catch(() => "Unauthorized");
        throw new SentinelAuthError(
          `Unauthorized (status ${response.status}). Check your Sentinel Cloud API key: ${errorText}`,
        );
      }

      if (!response.ok) {
        const errorText = await response.text().catch(() => "Unknown error");
        throw new SentinelError(
          `Cloud secrets fetch failed with status ${response.status}: ${errorText}`,
        );
      }

      const data = (await response.json()) as CloudSecretsResponse;
      if (
        !data ||
        typeof data !== "object" ||
        !data.secrets ||
        typeof data.secrets !== "object"
      ) {
        throw new SentinelError(
          "Unexpected response from Sentinel Cloud: missing `secrets` object.",
        );
      }

      return data.secrets;
    } catch (error) {
      if (error instanceof SentinelError) {
        throw error;
      }

      throw new SentinelNetworkError(
        `Failed to fetch secrets from Sentinel Cloud at ${this.cloudUrl}: ${
          error instanceof Error ? error.message : String(error)
        }`,
        error,
      );
    }
  }

  /**
   * Local / self-hosted mode: request access to a secret with intent logging.
   * Returns the immediate response without polling for PENDING_APPROVAL status.
   */
  async requestSecret(options: RequestSecretOptions): Promise<AccessResponse> {
    const { resourceId, intent, ttlSeconds = 3600 } = options;

    const payload: AccessRequest = {
      agent_id: this.agentId,
      resource_id: resourceId,
      intent,
      ttl_seconds: ttlSeconds,
    };

    try {
      const response = await fetch(`${this.baseUrl}/v1/access/request`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.apiToken}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok && response.status !== 403 && response.status !== 202) {
        if (response.status === 404) {
          throw new SentinelError(
            "Endpoint not found. Check baseUrl configuration.",
          );
        }
        const errorText = await response.text().catch(() => "Unknown error");
        throw new SentinelError(
          `Request failed with status ${response.status}: ${errorText}`,
        );
      }

      return (await response.json()) as AccessResponse;
    } catch (error) {
      if (error instanceof SentinelError) {
        throw error;
      }

      throw new SentinelNetworkError(
        `Failed to connect to Sentinel at ${this.baseUrl}: ${
          error instanceof Error ? error.message : String(error)
        }`,
        error,
      );
    }
  }

  /**
   * Poll a pending access request until it's approved or denied.
   * Throws SentinelTimeoutError if polling exceeds the configured timeout.
   */
  async pollRequest(requestId: string): Promise<AccessResponse> {
    const startTime = Date.now();

    while (true) {
      if (Date.now() - startTime > this.pollingTimeoutMs) {
        throw new SentinelTimeoutError(
          `Polling timeout after ${this.pollingTimeoutMs}ms for request ${requestId}`,
        );
      }

      try {
        const response = await fetch(
          `${this.baseUrl}/v1/access/requests/${requestId}`,
          {
            headers: {
              Authorization: `Bearer ${this.apiToken}`,
            },
          },
        );

        if (!response.ok) {
          if (response.status === 404) {
            throw new SentinelError(`Request ${requestId} not found`);
          }
          const errorText = await response.text().catch(() => "Unknown error");
          throw new SentinelError(
            `Poll failed with status ${response.status}: ${errorText}`,
          );
        }

        const data = (await response.json()) as AccessResponse;
        if (data.status !== "PENDING_APPROVAL") {
          return data;
        }

        await this.sleep(this.pollingIntervalMs);
      } catch (error) {
        if (error instanceof SentinelError) {
          throw error;
        }

        throw new SentinelNetworkError(
          `Failed to poll request ${requestId}: ${
            error instanceof Error ? error.message : String(error)
          }`,
          error,
        );
      }
    }
  }

  /**
   * Request a secret and automatically poll if status is PENDING_APPROVAL.
   */
  async requestWithPolling(
    options: RequestSecretOptions,
  ): Promise<AccessResponse> {
    const response = await this.requestSecret(options);

    if (response.status === "PENDING_APPROVAL") {
      return await this.pollRequest(response.request_id);
    }

    return response;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export * from "./types";
