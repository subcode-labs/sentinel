import time
import os
from typing import Optional, Dict, Any
import httpx

from .types import (
    AccessIntent,
    AccessRequest,
    AccessResponse,
    AccessStatus,
    SecretPayload,
)
from .exceptions import (
    SentinelError,
    SentinelAuthError,
    SentinelNetworkError,
    SentinelTimeoutError,
    SentinelDeniedError,
)


class SentinelClient:
    def __init__(
        self,
        base_url: str,
        api_token: str,
        agent_id: str,
        timeout: float = 30.0,
        environment: Optional[str] = None,
    ):
        """
        Initialize the Sentinel Client.

        Args:
            base_url: The URL of the Sentinel server (e.g., "http://localhost:3000").
            api_token: The API token for authentication.
            agent_id: The ID of the agent using this client.
            timeout: Default request timeout in seconds.
            environment: Default environment to use (defaults to "production" or SENTINEL_ENVIRONMENT env var).
        """
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.agent_id = agent_id
        self.timeout = timeout
        self.environment = (
            environment or os.environ.get("SENTINEL_ENVIRONMENT") or "production"
        )
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "User-Agent": f"SentinelPythonSDK/0.1.1 Agent/{agent_id}",
        }

    def request_secret(
        self,
        resource_id: str,
        intent: AccessIntent,
        version: Optional[int] = None,
        environment: Optional[str] = None,
        ttl_seconds: int = 3600,
        polling_interval: float = 2.0,
        polling_timeout: float = 60.0,
    ) -> SecretPayload:
        """
        Request a secret for a specific resource.

        If the request is PENDING_APPROVAL, this method will poll until
        the request is APPROVED, DENIED, or times out.

        Args:
            resource_id: The ID of the resource to access.
            intent: The intent details (summary, description, task_id).
            version: Optional version number to request.
            environment: Optional environment to request (defaults to client environment).
            ttl_seconds: Time-to-live for the secret in seconds.
            polling_interval: Seconds to wait between polling attempts.
            polling_timeout: Maximum seconds to wait for approval.

        Returns:
            SecretPayload containing the secret value and metadata.

        Raises:
            SentinelDeniedError: If the request is denied.
            SentinelTimeoutError: If polling times out.
            SentinelError: For other API errors.
        """
        request_body = AccessRequest(
            agent_id=self.agent_id,
            resource_id=resource_id,
            version=version,
            environment=environment or self.environment,
            intent=intent,
            ttl_seconds=ttl_seconds,
        )

        try:
            response = httpx.post(
                f"{self.base_url}/v1/access/request",
                headers=self.headers,
                json=request_body.model_dump(),
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            access_response = AccessResponse(**data)

            if access_response.status == AccessStatus.APPROVED:
                if not access_response.secret:
                    raise SentinelError("Approved response missing secret payload")
                return access_response.secret

            elif access_response.status == AccessStatus.DENIED:
                raise SentinelDeniedError(
                    f"Request denied: {access_response.reason or 'No reason provided'}"
                )

            elif access_response.status == AccessStatus.PENDING_APPROVAL:
                return self._poll_for_approval(
                    access_response.request_id, polling_interval, polling_timeout
                )

            else:
                raise SentinelError(f"Unknown status: {access_response.status}")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise SentinelAuthError("Invalid API Token") from e
            elif e.response.status_code == 403:
                # Try to extract the reason from the response body
                try:
                    error_data = e.response.json()
                    # The Sentinel server returns the full AccessResponse object on 403,
                    # so we check for 'reason' or 'message'
                    reason = error_data.get("reason") or error_data.get("message")
                    if reason:
                        raise SentinelDeniedError(reason) from e
                except SentinelDeniedError:
                    raise
                except Exception:
                    # JSON parsing failed or structure unexpected
                    pass
                raise SentinelDeniedError("Access Forbidden") from e
            raise SentinelError(f"HTTP Error: {e}") from e
        except httpx.RequestError as e:
            raise SentinelNetworkError(f"Network error: {e}") from e
        except Exception as e:
            # re-raise known exceptions
            if isinstance(e, SentinelError):
                raise
            raise SentinelError(f"Unexpected error: {e}") from e

    def fetch_secrets(self, environment: Optional[str] = None) -> Dict[str, str]:
        """
        Fetch all latest secrets for the current environment/project.
        Useful for injecting secrets into a process environment.

        Args:
            environment: Optional environment to fetch secrets for (defaults to client environment).

        Returns:
            Dict[str, str]: A dictionary mapping resource IDs to secret values.
        """
        target_environment = environment or self.environment
        params = {"environment": target_environment} if target_environment else {}

        try:
            response = httpx.get(
                f"{self.base_url}/v1/secrets",
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise SentinelAuthError("Invalid API Token") from e
            raise SentinelError(f"HTTP Error: {e}") from e
        except httpx.RequestError as e:
            raise SentinelNetworkError(f"Network error: {e}") from e
        except Exception as e:
            raise SentinelError(f"Unexpected error: {e}") from e

    def list_resources(self, environment: Optional[str] = None) -> list[str]:
        """
        List all available resource IDs that can be requested.

        Args:
            environment: Optional environment to list resources for (defaults to client environment).

        Returns:
            list[str]: A list of resource IDs.
        """
        target_environment = environment or self.environment
        params = {"environment": target_environment} if target_environment else {}

        try:
            response = httpx.get(
                f"{self.base_url}/v1/resources",
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise SentinelAuthError("Invalid API Token") from e
            raise SentinelError(f"HTTP Error: {e}") from e
        except httpx.RequestError as e:
            raise SentinelNetworkError(f"Network error: {e}") from e
        except Exception as e:
            raise SentinelError(f"Unexpected error: {e}") from e

    def _poll_for_approval(
        self, request_id: str, interval: float, timeout: float
    ) -> SecretPayload:
        """Poll the request status until approved, denied, or timeout."""
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            time.sleep(interval)

            try:
                response = httpx.get(
                    f"{self.base_url}/v1/access/requests/{request_id}",
                    headers=self.headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()
                access_response = AccessResponse(**data)

                if access_response.status == AccessStatus.APPROVED:
                    if not access_response.secret:
                        raise SentinelError("Approved response missing secret payload")
                    return access_response.secret

                elif access_response.status == AccessStatus.DENIED:
                    raise SentinelDeniedError(
                        f"Request denied: {access_response.reason or 'No reason provided'}"
                    )

                # If still PENDING_APPROVAL, continue loop

            except httpx.RequestError:
                # transient network errors during polling can be ignored or counted
                continue
            except httpx.HTTPStatusError as e:
                # 404 or other non-transient errors should abort
                raise SentinelError(f"Error during polling: {e}") from e

        raise SentinelTimeoutError(f"Polling timed out after {timeout} seconds")
