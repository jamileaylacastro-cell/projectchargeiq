import streamlit as st
from pathlib import Path

# Thin router: set page config then delegate to page scripts.
st.set_page_config(page_title="Project ChargeIQ Analytics", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

pg = st.navigation([
    st.Page("dashboard.py", title="Dashboard", default=True),
    st.Page("pages/1_🔮_Forecasting.py", title="Forecasting Model", icon="🔮"),
    st.Page("pages/2_📄_Documentation.py", title="Documentation", icon="📄"),
])
pg.run()
