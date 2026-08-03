import streamlit as st

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
# Set once here, in the router — individual pages must NOT call
# st.set_page_config() themselves once st.navigation() is in use.
st.set_page_config(page_title="Project ChargeIQ Analytics", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

# ── NAVIGATION ───────────────────────────────────────────────────────────────
# This file stays the deployment entry point (`streamlit run chargeiq_app.py`)
# so existing deployments pointing at this filename keep working. The actual
# dashboard content lives in dashboard.py; this file is just the router, which
# lets us set explicit sidebar nav labels instead of Streamlit's
# filename-derived defaults.
pg = st.navigation([
    st.Page("dashboard.py", title="Dashboard", default=True),
    st.Page("pages/1_🔮_Forecasting.py", title="Forecasting Model", icon="🔮"),
    st.Page("pages/2_📄_Documentation.py", title="Documentation", icon="📄"),
])
pg.run()
