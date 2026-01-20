# Sentinel x FastAPI Integration

This example demonstrates how to securely inject secrets into a **FastAPI** application using the Sentinel Python SDK.

It uses FastAPI's [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/) system to resolve secrets just-in-time for request handlers.

## How it works

1. The `get_payment_provider_key` dependency calls `client.request_secret()`.
2. If the secret requires **approval**, the request blocks (polls) until an admin approves it via the Sentinel Dashboard.
3. Once approved (or if auto-approved), the secret value is injected into the `process_payment` handler.
4. FastAPI handles the blocking call in a threadpool, keeping the server responsive.

## Setup

1. Make sure you have the Sentinel Server running (`docker-compose up` in root).
2. Create a secret named `payment_provider_key` in the Sentinel Dashboard.

## Running the Example

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

## Testing

Use `curl` or the Swagger UI (`http://127.0.0.1:8000/docs`) to trigger a payment:

```bash
curl -X POST http://127.0.0.1:8000/pay \
  -H "Content-Type: application/json" \
  -d '{"amount": 100, "currency": "USD"}'
```

If the policy for `payment_provider_key` is set to `Always Require Approval`, the request will hang (pending) until you approve it in the Sentinel Dashboard.
