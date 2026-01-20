# Sentinel x Django Integration

This example demonstrates how to use [Sentinel](https://github.com/subcode-labs/sentinel) to manage secrets in a Django application.

It covers two common patterns:
1.  **Startup Configuration:** Loading `settings.py` secrets (like `SECRET_KEY`, `DEBUG`, Database credentials) from Sentinel.
2.  **Runtime Access:** Fetching secrets on-demand within views/tasks using the Sentinel Client.

## Prerequisites

- Python 3.8+
- A running Sentinel instance (Self-hosted or Cloud)
- `SENTINEL_API_KEY`

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Sentinel:**

    Ensure you have `SENTINEL_API_KEY` (and `SENTINEL_ENDPOINT` if self-hosting) set in your environment.

    ```bash
    export SENTINEL_API_KEY="your_api_key_here"
    # export SENTINEL_ENDPOINT="http://localhost:8000" # If self-hosting
    ```

3.  **Create Secrets in Sentinel:**

    For this demo to work fully, create the following secrets in your Sentinel project:
    - `django_secret_key`: Any random string (e.g., "django-insecure-...")
    - `django_debug`: "True" or "False"
    - `demo_api_key`: Any string value

4.  **Run the Server:**

    ```bash
    python manage.py runserver
    ```

5.  **Verify:**

    - Visit `http://127.0.0.1:8000/` to see the startup configuration loaded from Sentinel.
    - Visit `http://127.0.0.1:8000/runtime-secret/` to see a runtime secret fetch.

## Key Code

Check `mysite/settings.py` to see how the client is initialized and used to override standard Django settings.

```python
# mysite/settings.py
from sentinel_sdk import SentinelClient

try:
    client = SentinelClient()
    django_secret = client.get_secret("django_secret_key")
    if django_secret:
        SECRET_KEY = django_secret.value
# ...
```
