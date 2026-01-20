import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sentinel_client import (
    SentinelClient,
    AccessIntent,
    SentinelDeniedError,
    SentinelTimeoutError,
)

# Initialize Sentinel Client
# In a real app, these would come from the environment
SENTINEL_URL = os.getenv("SENTINEL_URL", "http://localhost:3000")
SENTINEL_TOKEN = os.getenv("SENTINEL_TOKEN", "sentinel_dev_key")
AGENT_ID = os.getenv("AGENT_ID", "fastapi-service-001")

# Initialize the client globally
client = SentinelClient(
    base_url=SENTINEL_URL, api_token=SENTINEL_TOKEN, agent_id=AGENT_ID
)

app = FastAPI(title="Sentinel x FastAPI Example")


class PaymentRequest(BaseModel):
    amount: float
    currency: str


# Dependency to get the API key securely
# We use 'def' (synchronous) so FastAPI runs this in a threadpool.
# This is important because client.request_secret() is blocking (polls for approval).
def get_payment_provider_key():
    try:
        # Request the secret.
        # If the policy requires approval, this will block and poll until approved/denied/timeout.
        secret = client.request_secret(
            resource_id="payment_provider_key",
            intent=AccessIntent(
                summary="Process payment",
                description="Processing user payment request via FastAPI",
                task_id="req-fastapi-001",
            ),
            ttl_seconds=300,  # Keep it valid for 5 minutes
        )
        return secret.value
    except SentinelDeniedError as e:
        raise HTTPException(status_code=403, detail=f"Access Denied: {str(e)}")
    except SentinelTimeoutError as e:
        raise HTTPException(
            status_code=408,
            detail="Access Request Timeout: Approval was not granted in time.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentinel Error: {str(e)}")


@app.post("/pay")
def process_payment(
    payment: PaymentRequest, api_key: str = Depends(get_payment_provider_key)
):
    """
    Simulate processing a payment.
    The api_key is injected securely via Sentinel.
    """
    # Simulate using the secret (e.g., calling Stripe API)
    # detailed usage logs would go here

    masked_key = api_key[:3] + "..." + api_key[-3:] if len(api_key) > 6 else "***"

    return {
        "status": "success",
        "message": f"Processed {payment.amount} {payment.currency}",
        "gateway_auth": f"Authenticated using {masked_key}",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
