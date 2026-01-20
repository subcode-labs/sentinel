# Sentinel + Next.js App Router Example

This example demonstrates how to use Sentinel for **Just-In-Time (JIT) Secret Access** within a Next.js Server Action.

## Why this pattern?

In traditional apps, secrets (like `STRIPE_SECRET_KEY`) are loaded into environment variables at boot time. If the server is compromised, all secrets are leaked.

With Sentinel:
1.  **Zero Static Secrets:** Secrets are not stored in `.env` files.
2.  **JIT Access:** The application requests the secret *only* when needed (e.g., when the user clicks "Refund").
3.  **Audit Trail:** Every access is logged with the specific intent ("User requested refund").
4.  **Approval Workflows:** High-risk actions can trigger a human approval requirement before the secret is released.

## Structure

- **`lib/sentinel.ts`**: Initializes the Sentinel Client.
- **`app/actions.ts`**: A Server Action that requests the `stripe_api_key` using `sentinel.requestWithPolling()`.
- **`app/page.tsx`**: A simple UI to trigger the action.

## Usage

1.  Make sure Sentinel is running (see root README).
2.  Set environment variables:
    ```bash
    export SENTINEL_URL="http://localhost:3000"
    export SENTINEL_TOKEN="your-agent-token"
    ```
3.  Copy this code into your Next.js project.
