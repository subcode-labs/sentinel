import streamlit as st
import os
import time
from sentinel_client import SentinelClient, AccessIntent, SentinelDeniedError

# Page Config
st.set_page_config(page_title="Sentinel x Streamlit", page_icon="🔒", layout="wide")

# Sidebar - Configuration
st.sidebar.header("🔌 Connection Settings")
sentinel_url = st.sidebar.text_input(
    "Sentinel URL", value=os.getenv("SENTINEL_URL", "http://localhost:3000/api")
)
sentinel_token = st.sidebar.text_input(
    "Sentinel Token",
    value=os.getenv("SENTINEL_TOKEN", "sentinel_dev_key"),
    type="password",
)


# Initialize Client
@st.cache_resource
def get_sentinel_client(url, token):
    return SentinelClient(base_url=url, api_token=token)


client = get_sentinel_client(sentinel_url, sentinel_token)

# Main UI
st.title("🔒 Sentinel Identity-Aware Secrets")
st.markdown("""
This app demonstrates **Just-In-Time (JIT) Secret Access**. 
Instead of loading all secrets at startup (e.g., via `secrets.toml`), 
we request them only when a specific action is performed.
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Define Intent")
    st.info(
        "Every access request requires an **Intent** - a reason why the secret is needed right now."
    )

    intent_summary = st.text_input("Summary", "Generate Weekly Report")
    intent_desc = st.text_area(
        "Description", "Need database access to aggregate sales figures for Q3."
    )

    resource_key = st.selectbox(
        "Resource to Access", ["DATABASE_URL", "OPENAI_API_KEY", "STRIPE_SECRET_KEY"]
    )

with col2:
    st.subheader("2. Secure Access")

    if st.button("🔓 Request Access & Execute", type="primary"):
        with st.status("Contacting Sentinel Policy Engine...") as status:
            try:
                # 1. Define Intent
                status.write("📝 Packaging intent context...")
                intent = AccessIntent(
                    summary=intent_summary,
                    description=intent_desc,
                    task_id=f"streamlit-{int(time.time())}",
                )
                time.sleep(0.5)  # UX pause

                # 2. Request Secret
                status.write(f"🛡️ Requesting access to `{resource_key}`...")
                secret = client.request_secret(resource_id=resource_key, intent=intent)

                status.write("✅ Access Granted! Secret retrieved.")
                status.update(label="Operation Successful", state="complete")

                # 3. Display Result (Masked)
                st.success("Operation executed successfully using the secret.")

                # Show details
                with st.expander("Debugging Information (Secure)"):
                    masked_value = (
                        f"{secret.value[:4]}...{secret.value[-4:]}"
                        if len(secret.value) > 8
                        else "***"
                    )
                    st.code(
                        f"""
# Access Metadata
Key: {secret.key}
Version: {secret.version}
Value: {masked_value} 
                    """,
                        language="yaml",
                    )

            except SentinelDeniedError as e:
                status.update(label="Access Denied", state="error")
                st.error(
                    f"🛑 **Policy Blocked:** Sentinel denied this request.\n\nReason: {str(e)}"
                )
            except Exception as e:
                status.update(label="Error", state="error")
                st.error(f"An error occurred: {str(e)}")

st.divider()

st.subheader("Code Example")
st.code(
    """
from sentinel_client import SentinelClient, AccessIntent

# 1. Initialize
client = SentinelClient(base_url="...", api_token="...")

# 2. Define Context
intent = AccessIntent(
    summary="Generate Weekly Report",
    description="Need database access...",
    task_id="task-123"
)

# 3. Request Secret (Raises SentinelDeniedError if rejected)
secret = client.request_secret("DATABASE_URL", intent=intent)

# 4. Use Secret
connect_db(secret.value)
""",
    language="python",
)
