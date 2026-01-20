# Sentinel x Streamlit Integration

This example demonstrates how to use **Sentinel** to secure a [Streamlit](https://streamlit.io/) application.

Instead of storing secrets in `secrets.toml` or environment variables where they exist for the lifetime of the application, Sentinel allows you to fetch secrets **Just-In-Time** only when a specific user action requires them.

## Features

- **Dynamic Access:** Secrets are not loaded at startup.
- **Intent Binding:** Every secret access is logged with a specific user intent (e.g., "Generate Report").
- **Policy Enforcement:** Access can be blocked by Sentinel policies even if the app has the token.

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Sentinel**
   Make sure your Sentinel instance is running locally or in the cloud.
   ```bash
   # From the root of the repo
   docker-compose up -d
   ```

3. **Run the App**
   ```bash
   streamlit run app.py
   ```

4. **Configure**
   Use the sidebar to point to your Sentinel instance (default: `http://localhost:3000/api`).
