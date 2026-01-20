import time
import requests
from typing import Optional, Dict, Any


class SentinelClient:
    def __init__(self, base_url: str, api_token: str, agent_id: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }
        self.agent_id = agent_id

    def request_secret(
        self, resource_id: str, intent: Dict[str, str], ttl_seconds: int = 3600
    ) -> Dict[str, Any]:
        """
        Request a secret from Sentinel.
        Returns the raw API response.
        """
        payload = {
            "agent_id": self.agent_id,
            "resource_id": resource_id,
            "intent": intent,
            "ttl_seconds": ttl_seconds,
        }

        response = requests.post(
            f"{self.base_url}/v1/access/request", json=payload, headers=self.headers
        )

        if response.status_code not in [200, 202]:
            raise Exception(
                f"Sentinel request failed: {response.status_code} {response.text}"
            )

        return response.json()

    def get_request_status(self, request_id: str) -> Dict[str, Any]:
        """Check the status of a pending request."""
        response = requests.get(
            f"{self.base_url}/v1/access/requests/{request_id}", headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(
                f"Failed to get request status: {response.status_code} {response.text}"
            )

        return response.json()

    def request_with_polling(
        self,
        resource_id: str,
        intent: Dict[str, str],
        ttl_seconds: int = 3600,
        interval: int = 2,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Request a secret and poll until it is APPROVED, DENIED, or timeout is reached.
        """
        result = self.request_secret(resource_id, intent, ttl_seconds)

        if result["status"] != "PENDING_APPROVAL":
            return result

        request_id = result["request_id"]
        start_time = time.time()

        print(
            f"[*] Request {request_id} pending human approval. Polling every {interval}s..."
        )

        while time.time() - start_time < timeout:
            time.sleep(interval)
            status_result = self.get_request_status(request_id)

            if status_result["status"] != "PENDING_APPROVAL":
                return status_result

        raise TimeoutError(f"Timed out waiting for approval of request {request_id}")
