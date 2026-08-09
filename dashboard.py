import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import io
import calendar
from pathlib import Path
from utils.cleaning_dashboard import load_dashboard_data

# ── BRAND PALETTE ────────────────────────────────────────────────────────────
# Lime #BEFF6C · Cream #FFF4EC · White #FFFFFF · Black #000000 (accent)
st.markdown("""
<style>
.stApp{background:#FFF4EC}
[data-testid="stAppViewContainer"] > .main { padding-top: 0 !important; }
div.block-container { padding-top: 0.5rem !important; }
section[data-testid="stSidebar"]{background:#000000}
section[data-testid="stSidebar"] *{color:#FFF4EC!important}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3{color:#BEFF6C!important}
.kpi-card{background:#fff;border-radius:6px;padding:14px 16px;
  border-left:4px solid #000000;box-shadow:0 1px 6px rgba(0,0,0,.07);height:100%}
.kpi-label{font-size:10px;color:#5C574D;text-transform:uppercase;
  letter-spacing:.06em;margin-bottom:3px}
.kpi-value{font-size:22px;font-weight:700;color:#000000;line-height:1}
.kpi-trend{font-size:10px;margin-top:3px}
.up{color:#4F7A1E}.dn{color:#C1443E}.warn{color:#A8710A}
.sec-hdr{background:#000000;color:#BEFF6C;padding:7px 14px;border-radius:4px;
  font-size:12px;font-weight:700;margin:16px 0 8px 0}
.row-hdr{font-size:10px;font-weight:700;color:#5C574D;text-transform:uppercase;
  letter-spacing:.06em;margin:10px 0 6px 2px}
.formula-box{background:#FFFFFF;border:1px solid #EAE0D0;border-radius:6px;
  padding:10px 14px;font-family:monospace;font-size:11px;
  color:#000000;white-space:pre-line;line-height:1.7}

/* ── Kill Streamlit's default red accents; guarantee readable text on
     every light/lime background, even inside the black sidebar ──────── */

/* Multiselect selected pills — lime bg, black text, everywhere */
span[data-baseweb="tag"], div[data-baseweb="tag"]{
    background-color:#BEFF6C!important; border-color:#000000!important;
}
span[data-baseweb="tag"] *, div[data-baseweb="tag"] *{ color:#000000!important; }
span[data-baseweb="tag"] svg, div[data-baseweb="tag"] svg{ fill:#000000!important; }

/* Extra-safe overrides: Streamlit/BaseWeb markup can vary across versions
     (class names / nesting change). Apply a few broad selectors scoped to the
     sidebar to guarantee the selected-pill appearance stays lime on every
     supported app host. These intentionally use high-specificity and
     !important to win over inline styles produced by the widget library. */
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] span,
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] div,
section[data-testid="stSidebar"] .stMultiSelect span,
section[data-testid="stSidebar"] [data-baseweb="tag"],
section[data-testid="stSidebar"] span[class*="tag"],
section[data-testid="stSidebar"] div[class*="tag"] {
    background-color: #BEFF6C !important;
    border-color: #000000 !important;
    color: #000000 !important;
}
/* Ensure the close icon remains visible */
section[data-testid="stSidebar"] .stMultiSelect button, 
section[data-testid="stSidebar"] [aria-label*="remove"],
section[data-testid="stSidebar"] svg {
    fill: #000000 !important;
    color: #000000 !important;
}

/* Select / multiselect closed box — white bg, black text, no red focus ring */
div[data-baseweb="select"] > div{
  border-color:#EAE0D0!important; background:#FFFFFF!important;
  outline:none!important;
}
div[data-baseweb="select"] > div *{ color:#000000!important; }
div[data-baseweb="select"]:focus-within > div,
div[data-baseweb="select"] > div:focus,
div[data-baseweb="select"] > div:focus-within{
  border-color:#BEFF6C!important; box-shadow:0 0 0 1px #BEFF6C!important;
  background:#FFFFFF!important; outline:none!important;
}
div[data-baseweb="select"] input{ outline:none!important; box-shadow:none!important; }
div[data-baseweb="select"] input::selection{ background:#BEFF6C!important; color:#000000!important; }

/* Dropdown option list — white bg by default, lime on hover/selected,
   text always black regardless of sidebar's cream override */
div[data-baseweb="popover"], div[data-baseweb="menu"]{ background:#FFFFFF!important; }
div[data-baseweb="popover"] *, div[data-baseweb="menu"] *{ color:#000000!important; }
div[data-baseweb="popover"] li, div[data-baseweb="menu"] li{ background:#FFFFFF!important; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="menu"] li:hover,
div[data-baseweb="popover"] li[aria-selected="true"],
div[data-baseweb="menu"] li[aria-selected="true"]{
  background-color:#BEFF6C!important;
}
div[data-baseweb="popover"] li:hover *, div[data-baseweb="menu"] li:hover *,
div[data-baseweb="popover"] li[aria-selected="true"] *,
div[data-baseweb="menu"] li[aria-selected="true"] *{ color:#000000!important; }

/* Radio buttons — style only the native input dot, not the row wrapper */
input[type="checkbox"], input[type="radio"]{ accent-color:#BEFF6C!important; }

/* Slider — thumb only; no track/rail background override (was painting
   a much wider box than intended, covering the min/max value labels) */
div[data-testid="stSlider"] div[role="slider"]{
  background-color:#000000!important; border-color:#000000!important;
}

/* Buttons — cover the inner text node too, not just the button element,
   since Streamlit wraps button text in its own <p>/<span> that the
   sidebar's blanket cream-text rule matches directly and wins by
   default inheritance rules unless explicitly overridden here */
button[kind="primary"]{ background-color:#BEFF6C!important; border-color:#000000!important; }
button[kind="primary"] *{ color:#000000!important; }
button[kind="secondary"]{ border-color:#000000!important; background:#FFFFFF!important; }
button[kind="secondary"] *{ color:#000000!important; }

/* File uploader — light bg, so force black text regardless of container */
div[data-testid="stFileUploader"] section{
  background:#FFFFFF!important; border:1px dashed #000000!important;
}
div[data-testid="stFileUploader"] section *{ color:#000000!important; }
div[data-testid="stFileUploader"] section small{ color:#5C574D!important; }
div[data-testid="stFileUploaderDropzoneInstructions"] *{ color:#000000!important; }
div[data-testid="stFileUploader"] button{
  background:#BEFF6C!important; color:#000000!important; border-color:#000000!important;
}
div[data-testid="stFileUploader"] button *{ color:#000000!important; }

/* ── Sidebar-scoped overrides — higher specificity than the blanket
     cream-text rule above, so anything sitting on a light/white
     background inside the black sidebar still reads in black ────────── */
section[data-testid="stSidebar"] div[data-baseweb="select"] *{ color:#000000!important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] input{ color:#000000!important; }
section[data-testid="stSidebar"] div[data-baseweb="popover"] *,
section[data-testid="stSidebar"] div[data-baseweb="menu"] *{ color:#000000!important; }
section[data-testid="stSidebar"] span[data-baseweb="tag"] *,
section[data-testid="stSidebar"] div[data-baseweb="tag"] *{ color:#000000!important; }
section[data-testid="stSidebar"] div[data-testid="stFileUploader"] section *{ color:#000000!important; }
section[data-testid="stSidebar"] button[kind="primary"] *{ color:#000000!important; }
section[data-testid="stSidebar"] button[kind="secondary"] *{ color:#000000!important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] input::selection{
  background:#BEFF6C!important; color:#000000!important;
}

/* ── FINAL PASS — target Streamlit's own stable widget wrappers directly.
     These data-testid values are assigned by Streamlit itself (not the
     BaseWeb internals, which can nest differently across versions), so
     this is the most reliable way to guarantee black text survives on
     every light-background widget inside the black sidebar. Placed last
     so it also wins any same-specificity source-order tie. ─────────── */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] *{ color:#000000!important; }
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] *{ color:#000000!important; }
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label *,
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] label,
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] label *{ color:#FFF4EC!important; }
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div{
  background:#FFFFFF!important;
}
</style>
""", unsafe_allow_html=True)

# ── DATA SOURCE CONFIG ──────────────────────────────────────────────────────
BASE = Path(__file__).parent

FILE_LABELS = {
    "transactions":    "Session Logs (transactions.xlsx)",
    "charge_points":   "Charge Point Information (.xlsx)",
    "station_profile": "Station Profile (.xlsx)",
    "user_details":    "User Details (.xlsx)",
    "wallet_txn":      "Wallet Transactions (.xlsx)",
    "financials":      "Financials Workbook (.xlsx)",
    "transactions_excluded": "Transactions to exclude (.xlsx)"
}
FILE_DEFAULTS = {
    "transactions":    "transactions.xlsx",
    "charge_points":   "Charge_Point_Information__Connector_Type__Charger_Type__Capacity__Fees_Rates_.xlsx",
    "station_profile": "Station_Profile.xlsx",
    "user_details":    "UserDetails.xlsx",
    "wallet_txn":      "walletTransactions.xlsx",
    "financials":      "ProjectChargeIQ_Financials.xlsx",
}

def disk_path(filename):
    for candidate in [BASE / filename, BASE / "data" / filename]:
        if candidate.exists():
            return candidate
    return None

bundled_status = {}
for key in FILE_LABELS.keys():
    if key in FILE_DEFAULTS:
        bundled_status[key] = disk_path(FILE_DEFAULTS[key]) is not None
    elif key == "transactions_excluded":
        bundled_status[key] = disk_path("Transactions_to_exclude.xlsx") is not None
    else:
        bundled_status[key] = False
all_bundled = all(v for k, v in bundled_status.items() if k in FILE_DEFAULTS)

if "chargeiq_data_ready" not in st.session_state:
    st.session_state.chargeiq_data_ready = False
if "chargeiq_file_bytes" not in st.session_state:
    st.session_state.chargeiq_file_bytes = {}

# ── DATA GATE — request files before the dashboard ever loads ──────────────
if not st.session_state.chargeiq_data_ready:
    col_ico, col_ttl = st.columns([1, 10])
    with col_ico:
        st.markdown("<div style='font-size:34px;text-align:center;margin-top:2px'>⚡</div>",
                    unsafe_allow_html=True)
    with col_ttl:
        st.markdown("<h2 style='margin:0;color:#000000'>Project ChargeIQ</h2>"
                    "<p style='margin:0;color:#5C574D;font-size:12px'>"
                    "Provide your data to begin — upload files below or use the bundled dataset.</p>",
                    unsafe_allow_html=True)
    st.markdown("---")

    if all_bundled:
        st.success("✅ Bundled dataset found alongside the app. You can start immediately, "
                   "or upload replacements for any file below before starting.")
    else:
        found = [FILE_DEFAULTS[k] for k, v in bundled_status.items() if k in FILE_DEFAULTS and v]
        need  = [FILE_DEFAULTS[k] for k, v in bundled_status.items() if k in FILE_DEFAULTS and not v]
        if found:
            st.info(f"Found {len(found)}/6 bundled files. Upload the remaining {len(need)} to continue.")
        else:
            st.warning("No bundled data found. Upload all 6 files below to continue.")

    st.markdown("<div class='sec-hdr'>Upload data files</div>", unsafe_allow_html=True)
    up_cols = st.columns(3)
    gate_uploaded = {}
    for i, (key, label) in enumerate(FILE_LABELS.items()):
        with up_cols[i % 3]:
            status = "✅ bundled" if bundled_status.get(key, False) else "⚠️ required"
            st.caption(f"{label} — {status}")
            gate_uploaded[key] = st.file_uploader(label, type=["xlsx"],
                                                  key=f"gate_up_{key}", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    ready_now = all(
        gate_uploaded.get(k) is not None or bundled_status[k]
        for k in FILE_DEFAULTS
    )

    btn_col1, btn_col2 = st.columns([1, 4])
    with btn_col1:
        clicked = st.button("Load Dashboard →", type="primary", disabled=not ready_now,
                            use_container_width=True)
    with btn_col2:
        if not ready_now:
            st.caption("Upload the remaining required files to enable this button.")

    if clicked:
        resolved = {}
        for key, fname in FILE_DEFAULTS.items():
            up = gate_uploaded.get(key)
            if up is not None:
                resolved[key] = up.getvalue()
            else:
                p = disk_path(fname)
                resolved[key] = p.read_bytes() if p else None
        # Optional excluded-transactions file
        excl_up = gate_uploaded.get("transactions_excluded")
        if excl_up is not None:
            resolved["transactions_excluded"] = excl_up.getvalue()
        else:
            p = disk_path("Transactions_to_exclude.xlsx")
            resolved["transactions_excluded"] = p.read_bytes() if p else None

        st.session_state.chargeiq_file_bytes = resolved
        st.session_state.chargeiq_data_ready = True
        st.rerun()

    st.stop()

file_bytes = st.session_state.chargeiq_file_bytes

# ── LOAD ALL DATA ──────────────────────────────────────────────────────────
@st.cache_data
def load_all(tx_b, cp_b, sp_b, ud_b, wt_b, fin_b, tx_excluded_b=None):
    return load_dashboard_data(tx_b, cp_b, sp_b, ud_b, wt_b, fin_b, tx_excluded_b)

# Prepare bytes and call the loader
tx_b   = file_bytes.get("transactions")
cp_b   = file_bytes.get("charge_points")
sp_b   = file_bytes.get("station_profile")
ud_b   = file_bytes.get("user_details")
wt_b   = file_bytes.get("wallet_txn")
fin_b  = file_bytes.get("financials")
excl_b = file_bytes.get("transactions_excluded")

(
    tx, cp, cp_cap, sp, ud, wt, fin_overall, opex, fees, capex,
    payback_ref, cp_excluded_count, dur_excluded_count
) = load_all(tx_b, cp_b, sp_b, ud_b, wt_b, fin_b, excl_b)

with st.sidebar:
    st.markdown("## Filters")
    view = st.radio("View", ["🏢  Company / Ops", "🏪  Host Partner Site"], horizontal=True)
    is_company = view.startswith("🏢")

    all_stations = sorted(tx["STATIONNAME"].dropna().unique().tolist())

    if is_company:
        sel_stations = st.multiselect("Stations", all_stations, default=all_stations)
        if not sel_stations:
            sel_stations = all_stations
    else:
        sel_station  = st.selectbox("Site", all_stations, index=0)
        sel_stations = [sel_station]

    all_months    = sorted(tx["MONTH"].dropna().unique().tolist(), reverse=True)
    month_labels  = [str(m) for m in all_months]
    sel_month_lbl = st.selectbox("Month", month_labels, index=0)
    sel_month     = all_months[month_labels.index(sel_month_lbl)]

    charge_types = st.multiselect("Charging Mode",
        tx["CHARGE_TYPE"].dropna().unique().tolist(),
        default=tx["CHARGE_TYPE"].dropna().unique().tolist())

    op_hours_fallback = st.slider(
        "Fallback operating hrs/day", 8, 24, 12,
        help="Only used for a station with missing or invalid Business Hours "
             "on file (e.g. identical start/end time) — real per-station hours "
             "from Station Profile are used wherever available.")
    force_24 = st.checkbox("Use 24-hr capacity for all stations", value=False,
                           help="Overrides real business hours for every station "
                                "— useful for a 'what if we were open 24/7' scenario.")

    # Target utilization: ONE network-wide target in Company/Ops view
    # (applies uniformly when comparing all selected stations), or a
    # target PER STATION in Host Partner view — each station's slider
    # keeps its own remembered value (via its own widget key) when you
    # switch between sites, rather than sharing one global setting.
    #
    # Range and default reflect published EV charger utilization
    # benchmarks, not an assumption of high usage: public charger
    # utilization typically sits at 5–15%, McKinsey cites ~15% as the
    # threshold for economic viability, and even the most mature EU
    # markets peak around 30%. Source: Topal, O. (2025), "A comprehensive
    # analysis of capacity utilization rates of fast-charging stations in
    # shopping malls," Int J Low-Carbon Tech, 20, 1646–1660.
    # https://doi.org/10.1093/ijlct/ctaf100
    if is_company:
        target_util = st.slider("Network Target Utilization %", 1, 40, 15,
                                key="target_network")
    else:
        station_key = sel_stations[0]
        target_util = st.slider(
            f"Target Utilization % — {station_key[:22]}", 1, 40, 15,
            key=f"target_station_{station_key}")
    st.caption("📚 Range reflects published benchmarks: public EV chargers "
              "typically run 5–15% utilization; ~15% is the threshold "
              "commonly cited for economic viability ([source](https://doi.org/10.1093/ijlct/ctaf100)).")

    if st.button("Change data source", use_container_width=True):
        st.session_state.chargeiq_data_ready = False
        st.rerun()

st.markdown("---")
days_in_month = tx[tx["MONTH"] == sel_month]["DATE"].nunique()
n_uploaded = sum(1 for k in FILE_DEFAULTS if st.session_state.get(f"gate_up_{k}") is not None)
src_label = "Bundled data" if n_uploaded == 0 else f"{n_uploaded}/6 files uploaded"
st.markdown(f"<small style='color:#FFF4EC'>Period: **{sel_month}**<br>"
            f"Active days: **{days_in_month}**<br>"
            f"Source: {src_label}</small>",
            unsafe_allow_html=True)

# ── PER-STATION OPERATING HOURS ─────────────────────────────────────────────
# Real business hours from Station Profile, not one manual number applied
# uniformly to every station — a mall at 10am-10pm and a 24-hr highway
# stop have very different real capacity, and a single flat multiplier
# for both systematically skews utilization % for whichever type is
# "wrong" for that station.
def _parse_time_minutes(val):
    if pd.isna(val) or str(val).strip() == "":
        return None
    parsed = pd.to_datetime(str(val), errors="coerce")
    return parsed.hour * 60 + parsed.minute if pd.notna(parsed) else None
 
def _station_daily_hours(station_name):
    """Returns (hours, used_fallback)."""
    if force_24:
        return 24.0, False
    row = sp[sp["STATIONNAME"] == station_name]
    if len(row) == 0 or "BUSINESS_START" not in row.columns or "BUSINESS_END" not in row.columns:
        return float(op_hours_fallback), True
    b_start = _parse_time_minutes(row["BUSINESS_START"].iloc[0])
    b_end   = _parse_time_minutes(row["BUSINESS_END"].iloc[0])
    if b_start is None or b_end is None or b_start == b_end:
        # Missing data, or identical start/end time — a known placeholder
        # pattern in this data (roughly 1 in 3 stations), not a real
        # 0-hour site. Fall back rather than propagate a 0-hour capacity
        # that would break utilization % (division by zero) downstream.
        return float(op_hours_fallback), True
    hrs = (b_end - b_start) / 60
    if hrs <= 0:
        hrs += 24  # overnight wraparound — end time is technically after midnight
    return round(hrs, 2), False
 
_station_hours_results = {s: _station_daily_hours(s) for s in tx["STATIONNAME"].dropna().unique()}
station_hours   = {s: v[0] for s, v in _station_hours_results.items()}
_uses_fallback  = {s for s, v in _station_hours_results.items() if v[1]}

# ── FILTER ─────────────────────────────────────────────────────────────────
days = max(days_in_month, 1)

df = tx[
    (tx["STATIONNAME"].isin(sel_stations)) &
    (tx["MONTH"] == sel_month) &
    (tx["CHARGE_TYPE"].isin(charge_types)) &
    (~tx["ISERROR"].astype(bool))
].copy()

df_all = tx[
    (tx["STATIONNAME"].isin(sel_stations)) &
    (tx["MONTH"] == sel_month)
].copy()

prior_month = sel_month - 1
df_prior = tx[
    (tx["STATIONNAME"].isin(sel_stations)) &
    (tx["MONTH"] == prior_month) &
    (tx["CHARGE_TYPE"].isin(charge_types)) &
    (~tx["ISERROR"].astype(bool))
].copy()

# ── CORE METRICS ─────────────────────────────────────────────────────────────
# cp_sel = all data-quality-valid connectors at the selected station(s),
# regardless of online/offline (used for total counts + reliability KPIs)
cp_sel = cp_cap[cp_cap["STATIONNAME"].isin(sel_stations)]
# Only ONLINE connectors contribute real, usable capacity for the period
cp_sel_online = cp_sel[cp_sel["NETWORK_STATUS"] == "Online"]

# Per-station capacity, using each station's OWN real operating hours —
# summing capacity first and multiplying by one flat hours figure (the
# old approach) is only valid if every station has identical hours, which
# they don't.
total_avail_kwh = sum(
    cp_sel_online[cp_sel_online["STATIONNAME"] == s]["CAPACITY_KW"].sum()
    * station_hours.get(s, op_hours_fallback) * days
    for s in cp_sel_online["STATIONNAME"].unique()
)
#total_avail_kwh = cp_sel_online["CAPACITY_KW"].sum() * op_hours * days

actual_kwh      = df["ENERGY_KWH"].sum()
prior_kwh       = df_prior["ENERGY_KWH"].sum()
net_util        = (actual_kwh / total_avail_kwh * 100) if total_avail_kwh > 0 else 0
util_gap        = net_util - target_util

total_rev  = df["TOTALAMOUNT"].sum()
prior_rev  = df_prior["TOTALAMOUNT"].sum()
mom_rev    = (total_rev - prior_rev) / prior_rev * 100 if prior_rev > 0 else 0
total_sess = len(df)
prior_sess = len(df_prior)
mom_sess   = (total_sess - prior_sess) / prior_sess * 100 if prior_sess > 0 else 0
error_rate = (df_all["ISERROR"].astype(bool).sum() / len(df_all) * 100) if len(df_all) > 0 else 0
total_cps   = len(cp_sel)
online_cps  = len(cp_sel_online)
offline_cps = len(cp_sel[cp_sel["NETWORK_STATUS"] == "Offline"])
faulty_cps  = len(cp_sel[cp_sel["CONNECTOR_STATUS"] == "Faulty"])
uptime_pct  = (online_cps / total_cps * 100) if total_cps > 0 else 0
avg_dur     = df["DURATION_MIN"].mean() if len(df) else 0
avg_dur     = 0 if pd.isna(avg_dur) else avg_dur

# Peak hour
if len(df):
    hourly_kwh = df.groupby("HOUR")["ENERGY_KWH"].sum()
    peak_hour  = int(hourly_kwh.idxmax()) if len(hourly_kwh) else 0
    peak_share = (hourly_kwh.max() / hourly_kwh.sum() * 100) if hourly_kwh.sum() > 0 else 0
else:
    peak_hour, peak_share = 0, 0

# Revenue detail (safe column lookups — some exports may not include every fee column)
avg_rev_session = (total_rev / total_sess) if total_sess > 0 else 0
overstay_rev = df["OVERSTAYFEE"].sum() if "OVERSTAYFEE" in df.columns else None

# Refunds (from wallet transactions, scoped to the selected month where possible)
if "TRANSACTION_DATE" in wt.columns:
    wt2 = wt.copy()
    wt2["TRANSACTION_DATE"] = pd.to_datetime(wt2["TRANSACTION_DATE"], errors="coerce")
    wt_period = wt2[wt2["TRANSACTION_DATE"].dt.to_period("M") == sel_month]
else:
    wt_period = wt
refund_count = wt_period["REFUNDEDTRANSACTIONNO"].notna().sum() if "REFUNDEDTRANSACTIONNO" in wt_period.columns else 0
refund_total = len(wt_period)
refund_rate  = (refund_count / refund_total * 100) if refund_total > 0 else 0

# Customer metrics — scoped to selected station(s) + month
unique_customers  = df["USERID"].nunique() if "USERID" in df.columns else 0
sessions_per_user = df.groupby("USERID").size() if "USERID" in df.columns and len(df) else pd.Series(dtype=int)
repeat_customers  = (sessions_per_user > 1).sum() if len(sessions_per_user) else 0
repeat_rate        = (repeat_customers / unique_customers * 100) if unique_customers > 0 else 0
avg_rev_per_cust    = (total_rev / unique_customers) if unique_customers > 0 else 0

active = len(ud[ud["ACCOUNT_STATUS"]=="Active"]) if "ACCOUNT_STATUS" in ud.columns else len(ud)
avg_wallet = ud["WALLET_BALANCE"].mean() if "WALLET_BALANCE" in ud.columns else 0

# ── HEADER ──────────────────────────────────────────────────────────────────
col_ico, col_ttl = st.columns([1, 12])
with col_ico:
    st.markdown("<div style='font-size:34px;text-align:center;margin-top:2px'>⚡</div>",
                unsafe_allow_html=True)
with col_ttl:
    title = "Network Dashboard" if is_company else f"Site Dashboard — {sel_stations[0]}"
    if is_company:
        _hrs_label = f"{force_24 and '24' or 'per-station'} hrs/day"
    else:
        _hrs_label = f"{station_hours.get(sel_stations[0], op_hours_fallback):.1f}h/day"
        if sel_stations[0] in _uses_fallback:
            _hrs_label += " (fallback)"
    st.markdown(f"<h2 style='margin:0;color:#000000'>Project ChargeIQ — {title}</h2>"
                f"<p style='margin:0;color:#5C574D;font-size:11px'>"
                f"{sel_month} · {days} active days · Op hrs: {_hrs_label}</p>",
                unsafe_allow_html=True)
st.markdown("---")

# ── STATION PROFILE — Host Partner Site view only ───────────────────────────
if not is_company:
    import re as _re
    _station = sel_stations[0]

    _sp_row = sp[sp["STATIONNAME"] == _station]

    # Region/City — Station Profile has no dedicated field, so it's derived
    # from ADDRESS (last two comma-separated segments, zip code stripped).
    def _region_city(addr):
        if not isinstance(addr, str) or not addr.strip():
            return "—"
        parts = [p.strip() for p in addr.split(",")]
        if len(parts) >= 2:
            tail = parts[-1]
            tail = _re.sub(r"\d{4,}$", "", tail).strip()
            return f"{parts[-2]}, {tail}" if tail else parts[-2]
        return addr

    region_city = _region_city(_sp_row["ADDRESS"].iloc[0]) if len(_sp_row) and "ADDRESS" in _sp_row.columns else "—"

    # Status — from Station Profile's STATION_ACTIVE flag
    is_active = bool(_sp_row["STATION_ACTIVE"].iloc[0]) if len(_sp_row) and "STATION_ACTIVE" in _sp_row.columns else True

    # First / Last year of operation — derived from actual session history,
    # since Station Profile has no explicit launch/decommission date field
    _station_sessions = tx[tx["STATIONNAME"] == _station]
    if len(_station_sessions):
        first_year = int(_station_sessions["STARTTIME"].dt.year.min())
        last_year  = int(_station_sessions["STARTTIME"].dt.year.max())
    else:
        first_year, last_year = None, None
    last_op_display = "-" if is_active else (str(last_year) if last_year else "-")

    # Operating hours — BUSINESS_START/END can come through as a plain
    # time string ("09:00:00") OR a full datetime with a placeholder date
    # ("1900-01-02 09:00:00"), depending on how the source file was
    # exported. Parse robustly and keep only the TIME component either way.
    def _time_only(val):
        if pd.isna(val) or str(val).strip() == "":
            return None
        parsed = pd.to_datetime(str(val), errors="coerce")
        return parsed.strftime("%H:%M") if pd.notna(parsed) else None

    if len(_sp_row) and "BUSINESS_START" in _sp_row.columns and "BUSINESS_END" in _sp_row.columns:
        b_start = _time_only(_sp_row["BUSINESS_START"].iloc[0])
        b_end   = _time_only(_sp_row["BUSINESS_END"].iloc[0])
        if b_start and b_end:
            op_hrs_display = "24 Hours" if (b_start == "00:00" and b_end in ("23:59","00:00")) else f"{b_start} – {b_end}"
        else:
            op_hrs_display = "—"
    else:
        op_hrs_display = "—"

    # Charge points + capacity — from the corrected connector-level cp_cap.
    # Capacity shown is the AVERAGE across this station's charge points,
    # not the total network capacity (that's used separately for the
    # utilization denominator).
    _station_cps = cp_cap[cp_cap["STATIONNAME"] == _station]
    n_charge_points = len(_station_cps)
    avg_capacity    = _station_cps["CAPACITY_KW"].mean() if len(_station_cps) else 0

    # Rate per kWh by plug type — RATE_PER_KWH can genuinely differ by
    # plug type at the same station (confirmed in the data), so show it
    # broken out rather than a single station-wide figure.
    if len(_station_cps) and "RATE_PER_KWH" in _station_cps.columns:
        _rate_by_plug = (_station_cps.groupby("PLUG_TYPE")["RATE_PER_KWH"]
                         .mean().round(2).sort_index())
        rate_rows = "".join(
            f"<div style='display:flex;justify-content:space-between;font-size:11px;"
            f"padding:3px 0;border-bottom:1px solid #EAE0D0'>"
            f"<span style='color:#5C574D'>{plug}</span>"
            f"<span style='color:#000;font-weight:600'>₱{rate:,.2f} / kWh</span></div>"
            for plug, rate in _rate_by_plug.items()
        )
    else:
        rate_rows = "<div style='font-size:11px;color:#5C574D'>No rate data available</div>"

    status_color = "#4F7A1E" if is_active else "#C1443E"
    status_label = "🟢 Active" if is_active else "🔴 Inactive"

    st.markdown(f"""
    <div style='background:#fff;border-radius:8px;padding:16px 20px;
                border-left:4px solid #000000;box-shadow:0 1px 6px rgba(0,0,0,.07);
                margin-bottom:16px'>
      <div style='font-size:14px;font-weight:700;color:#000;margin-bottom:12px'>
        🏪 Station Profile — {_station}
      </div>
      <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:14px 24px'>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Station Name</div>
          <div style='font-size:13px;color:#000;font-weight:600'>{_station}</div>
        </div>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Region / City</div>
          <div style='font-size:13px;color:#000;font-weight:600'>{region_city}</div>
        </div>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Status</div>
          <div style='font-size:13px;color:{status_color};font-weight:600'>{status_label}</div>
        </div>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Operating Hours</div>
          <div style='font-size:13px;color:#000;font-weight:600'>{op_hrs_display}</div>
        </div>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Year of First Operation</div>
          <div style='font-size:13px;color:#000;font-weight:600'>{first_year if first_year else '—'}</div>
        </div>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Year of Last Operation</div>
          <div style='font-size:13px;color:#000;font-weight:600'>{last_op_display}</div>
        </div>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Number of Charge Points</div>
          <div style='font-size:13px;color:#000;font-weight:600'>{n_charge_points}</div>
        </div>
        <div>
          <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em'>Avg Charger Capacity</div>
          <div style='font-size:13px;color:#000;font-weight:600'>{avg_capacity:,.1f} kW</div>
        </div>
      </div>
      <hr style='margin:14px 0 10px;border-color:#EAE0D0'>
      <div style='font-size:9px;color:#5C574D;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px'>
        Rate per kWh by Plug Type
      </div>
      <div style='display:grid;grid-template-columns:repeat(2,1fr);gap:0 24px'>
        {rate_rows}
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── FORMULA EXPANDER ────────────────────────────────────────────────────────
with st.expander("📐 Energy-Based Utilization Formula", expanded=False):
    if is_company:
        _hrs_note = (f"× each station's OWN real Business Hours (Station Profile)"
                    if not force_24 else "× 24 hrs/day (forced override)")
    else:
        _sh = station_hours.get(sel_stations[0], op_hours_fallback)
        _hrs_note = f"× {_sh:.1f} hrs/day"
        if sel_stations[0] in _uses_fallback:
            _hrs_note += f" (fallback — no valid Business Hours on file for this station)"
 
    st.markdown(f"""<div class='formula-box'>
Utilization Rate (%) = Σ Actual kWh Charged ÷ Total Available Capacity × 100
 
Σ Actual kWh Charged     = {actual_kwh:,.1f} kWh  (ENERGY_KWH where ISERROR=0)
Total Available Capacity = Σ per station [ Online Connectors × CAPACITY_KW {_hrs_note} × {days} days ]
                         = {total_avail_kwh:,.0f} kWh
Network Utilization      = {actual_kwh:,.1f} ÷ {total_avail_kwh:,.0f} × 100 = {net_util:.1f}%
Gap vs {target_util}% target   = {util_gap:+.1f} pp
</div>""", unsafe_allow_html=True)
    st.caption(
        f"📋 **Connector data quality:** {len(cp):,} raw rows in Charge Point Information → "
        f"{len(cp_cap):,} valid (has PLUG_TYPE and CAPACITY_KW > 0) → "
        f"{cp_excluded_count:,} excluded for missing/zero capacity data. "
        f"Of the valid connectors, {total_cps:,} belong to your current selection, "
        f"of which {online_cps:,} are Online and count toward available capacity "
        f"({offline_cps:,} Offline, {faulty_cps:,} Faulty)."
    )
    _n_fallback_selected = len([s for s in sel_stations if s in _uses_fallback])
    if _n_fallback_selected > 0 and not force_24:
        st.caption(
            f"📋 **Operating hours data quality:** {_n_fallback_selected} of {len(sel_stations)} "
            f"selected station(s) have missing or placeholder Business Hours on file "
            f"(identical BUSINESS_START/BUSINESS_END is a known data gap affecting roughly "
            f"1 in 3 stations) — the {op_hours_fallback}h/day fallback is used for those, "
            f"real hours are used for the rest."
        )
    if dur_excluded_count > 0:
        st.caption(
            f"📋 **Session data quality:** {dur_excluded_count:,} sessions network-wide "
            f"have invalid duration or energy values and are excluded from dashboard metrics. "
            f"This helps ensure the charts and utilization calculations only reflect clean charging "
            f"sessions."
        )

# ── KPI HELPER ────────────────────────────────────────────────────────────────
def kpi(col, label, value, trend, tclass="up", border="#000000"):
    col.markdown(
        f"<div class='kpi-card' style='border-left-color:{border}'>"
        f"<div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"<div class='kpi-trend {tclass}'>{trend}</div></div>",
        unsafe_allow_html=True)

st.markdown("<div class='sec-hdr'>Key Performance Indicators</div>", unsafe_allow_html=True)

# ── TOP PERFORMER LEADERBOARD — Company view, multiple stations only.
#    "Best vs prior month" tells you if a station is improving; it says
#    nothing about how it stacks up against its peers right now. This
#    computes one headline number per selected station for each KPI
#    section, so the section can call out whoever's leading — a smaller,
#    purpose-built version of the same per-station math the map/table
#    below does, kept separate to avoid touching that logic.
_leaderboard = {}
if is_company and len(sel_stations) > 1:
    _lb_rows = []
    for s in sel_stations:
        s_df = df[df["STATIONNAME"] == s]
        s_cp = cp_cap[cp_cap["STATIONNAME"] == s]
        s_cp_online = s_cp[s_cp["NETWORK_STATUS"] == "Online"]
        s_kwh = s_df["ENERGY_KWH"].sum()
        s_avail = s_cp_online["CAPACITY_KW"].sum() * station_hours.get(s, op_hours_fallback) * days
        s_util = (s_kwh / s_avail * 100) if s_avail > 0 else 0
        s_uptime = (len(s_cp_online) / len(s_cp) * 100) if len(s_cp) > 0 else 0
        s_rev = s_df["TOTALAMOUNT"].sum()
        s_users = s_df["USERID"].dropna().nunique()
        s_spu = s_df.groupby("USERID").size()
        s_repeat = ((s_spu > 1).sum() / s_users * 100) if s_users > 0 else 0
        _lb_rows.append({"station": s, "util": s_util, "uptime": s_uptime,
                         "revenue": s_rev, "repeat": s_repeat, "users": s_users})
    _lb_df = pd.DataFrame(_lb_rows)

    def _top_performer(metric_col, min_users=0, fmt="{:.1f}%", round_dp=1):
        pool = _lb_df[_lb_df["users"] >= min_users] if min_users else _lb_df
        if len(pool) == 0 or pool[metric_col].max() <= 0:
            return None
        # Compare at the same precision the value is displayed at — two
        # stations can differ by a tiny float fraction but still show as
        # the identical number, and should count as tied rather than
        # arbitrarily picking one as "the" winner.
        rounded = pool[metric_col].round(round_dp)
        max_val = rounded.max()
        tied = pool.loc[rounded == max_val].sort_values(metric_col, ascending=False)
        names = tied["station"].tolist()
        top_val = tied[metric_col].iloc[0]
        label = f"🏆 Top: {names[0]} ({fmt.format(top_val)})"
        if len(names) == 2:
            label += f" and {names[1]}"
        elif len(names) > 2:
            label += f" and {names[1]} +{len(names)-2} more"
        return label

    _leaderboard["util"]    = _top_performer("util")
    _leaderboard["uptime"]  = _top_performer("uptime")
    _leaderboard["revenue"] = _top_performer("revenue", fmt="₱{:,.0f}", round_dp=0)
    _leaderboard["repeat"]  = _top_performer("repeat", min_users=5)  # avoid a 1-user "100%" outlier

def _row_hdr_with_leaderboard(title, key):
    tag = _leaderboard.get(key) if is_company else None
    if tag:
        st.markdown(f"<div class='row-hdr'>{title} &nbsp;·&nbsp; "
                    f"<span style='color:#4F7A1E;text-transform:none;font-weight:700'>{tag}</span></div>",
                    unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='row-hdr'>{title}</div>", unsafe_allow_html=True)

# ── ROW 1: UTILIZATION ───────────────────────────────────────────────────────
_row_hdr_with_leaderboard("Utilization", "util")
r1c1,r1c2,r1c3,r1c4 = st.columns(4)
gap_cls = "up" if util_gap >= 0 else ("warn" if util_gap >= -10 else "dn")
kpi(r1c1,"Network Utilization",f"{net_util:.1f}%",
    f"{'▲' if util_gap>=0 else '▼'} {util_gap:+.1f} pp vs {target_util}% target",
    gap_cls, "#BEFF6C" if util_gap>=0 else "#C1443E")
kpi(r1c2,"Actual kWh Charged",f"{actual_kwh:,.0f}",
    f"{'▲' if actual_kwh>prior_kwh else '▼'} vs prior month",
    "up" if actual_kwh>=prior_kwh else "dn","#BEFF6C")
kpi(r1c3,"Avg Session Duration",f"{avg_dur:.0f} min",
    f"Peak hour: {peak_hour:02d}:00 ({peak_share:.0f}% of daily kWh)",
    "up","#BEFF6C")
kpi(r1c4,"Total Sessions",f"{total_sess:,}",
    f"{'▲' if mom_sess>=0 else '▼'} {abs(mom_sess):.1f}% MoM",
    "up" if mom_sess>=0 else "dn","#BEFF6C")

# ── ROW 2: RELIABILITY ───────────────────────────────────────────────────────
_row_hdr_with_leaderboard("Reliability", "uptime")
r2c1,r2c2,r2c3,r2c4 = st.columns(4)
kpi(r2c1,"Charger Uptime",f"{uptime_pct:.1f}%",
    f"{online_cps}/{total_cps} connectors online",
    "up" if uptime_pct>=90 else ("warn" if uptime_pct>=75 else "dn"),
    "#BEFF6C" if uptime_pct>=90 else ("#A8710A" if uptime_pct>=75 else "#C1443E"))
kpi(r2c2,"Chargers Offline",f"{offline_cps}",
    f"of {total_cps} total connectors",
    "up" if offline_cps==0 else "dn",
    "#BEFF6C" if offline_cps==0 else "#C1443E")
kpi(r2c3,"Faulty Connectors",f"{faulty_cps}",
    "Flagged in Charge Point Info",
    "up" if faulty_cps==0 else "dn",
    "#BEFF6C" if faulty_cps==0 else "#C1443E")
kpi(r2c4,"Error Session Rate",f"{error_rate:.1f}%",
    "▼ needs attention" if error_rate>5 else "Within threshold",
    "dn" if error_rate>5 else "up","#C1443E" if error_rate>5 else "#BEFF6C")

# ── ROW 3: REVENUE ───────────────────────────────────────────────────────────
_row_hdr_with_leaderboard("Revenue", "revenue")
r3c1,r3c2,r3c3,r3c4 = st.columns(4)
kpi(r3c1,"Total Revenue",f"₱{total_rev:,.0f}",
    f"{'▲' if mom_rev>=0 else '▼'} {abs(mom_rev):.1f}% MoM",
    "up" if mom_rev>=0 else "dn","#BEFF6C")
kpi(r3c2,"Avg Revenue / Session",f"₱{avg_rev_session:,.0f}",
    f"{total_sess:,} sessions this period",
    "up","#BEFF6C")
kpi(r3c3,"Refund Rate",f"{refund_rate:.1f}%",
    f"{refund_count:,} of {refund_total:,} wallet txns",
    "dn" if refund_rate>3 else "up","#C1443E" if refund_rate>3 else "#BEFF6C")
if overstay_rev is not None:
    kpi(r3c4,"Overstay Fee Revenue",f"₱{overstay_rev:,.0f}",
        "Parking demand signal","up","#BEFF6C")
else:
    kpi(r3c4,"Overstay Fee Revenue","—",
        "OVERSTAYFEE column not found","warn","#A8710A")

# ── ROW 4: CUSTOMER ──────────────────────────────────────────────────────────
_row_hdr_with_leaderboard("Customer", "repeat")
r4c1,r4c2,r4c3,r4c4 = st.columns(4)
if is_company:
    kpi(r4c1,"Registered Users",f"{len(ud):,}",f"{active:,} active accounts","up","#000000")
    kpi(r4c2,"Active Users (period)",f"{unique_customers:,}",
        "Distinct users this month","up","#BEFF6C")
    kpi(r4c3,"Repeat Customer Rate",f"{repeat_rate:.1f}%",
        f"{repeat_customers:,} of {unique_customers:,} customers","up","#BEFF6C")
    kpi(r4c4,"Avg Wallet Balance",f"₱{avg_wallet:,.0f}","Across active users","up","#000000")
else:
    kpi(r4c1,"Unique Customers",f"{unique_customers:,}","At this site this month","up","#000000")
    kpi(r4c2,"Repeat Customer Rate",f"{repeat_rate:.1f}%",
        f"{repeat_customers:,} of {unique_customers:,} customers","up","#BEFF6C")
    kpi(r4c3,"Avg Revenue / Customer",f"₱{avg_rev_per_cust:,.0f}","This site, this month","up","#BEFF6C")
    top_pm = df_all["PAYMENT_METHOD"].value_counts().index[0] if len(df_all) and "PAYMENT_METHOD" in df_all.columns else "—"
    kpi(r4c4,"Top Payment Method",top_pm,"Most used at this site","up","#000000")

st.markdown("<br>", unsafe_allow_html=True)

# ── CUSTOMER BEHAVIOR ─────────────────────────────────────────────────────────
# Engagement stats + how customers charge, pay, and fund their wallet — one
# story about customer choices. Equipment/vehicle-side preferences (Power
# Supply Mode, Plug Type, Car Brand) live separately in Charging Preferences
# further down: that's "what hardware gets used," this is "how customers
# behave." Repeat Rate stays in the Customer KPI row above, not repeated here.
st.markdown("<div class='sec-hdr'>Customer Behavior</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
col1.metric("Avg Session Duration (min)", f"{avg_dur:.0f}")
col2.metric("Sessions / User (period)", f"{(sessions_per_user.mean() if len(sessions_per_user) else 0):.2f}")
avg_kwh_session = (total_kwh:=df['ENERGY_KWH'].sum()) / total_sess if total_sess>0 else 0
col3.metric("Avg kWh / Session", f"{avg_kwh_session:.2f}")

cb1, cb2 = st.columns(2)
with cb1:
    st.markdown("**Energy (kWh) by Charging Mode**")
    ct = df.groupby("CHARGE_TYPE")["ENERGY_KWH"].sum().reset_index()
    ct.columns = ["Charging Mode","kWh"]
    if len(ct): st.bar_chart(ct.set_index("Charging Mode"), color="#BEFF6C", height=200)
with cb2:
    st.markdown("**Payment Method Mix**")
    pm = df_all.groupby("PAYMENT_METHOD").size().reset_index(name="Count")
    if len(pm): st.bar_chart(pm.set_index("PAYMENT_METHOD"), color="#000000", height=200)

st.markdown("<div class='row-hdr'>Wallet Top-Up</div>", unsafe_allow_html=True)
_has_type = "TRANSACTION_TYPE" in wt.columns
_has_status = "STATUS" in wt.columns
if not _has_type:
    st.info("`TRANSACTION_TYPE` column not found in walletTransactions.xlsx — can't isolate top-ups from other transaction types.")
else:
    _topups = wt[wt["TRANSACTION_TYPE"] == "Wallet Top up"].copy()
    if _has_status:
        _topups = _topups[_topups["STATUS"] == "Completed"]
    if not is_company:
        # Scope to users who actually transacted at this station this period
        # — wallet data has no STATIONNAME of its own since a top-up isn't
        # tied to a location.
        _wallet_user_ids = set(df["USERID"].dropna().astype(float).unique())
        _topups = _topups[_topups["USERID"].astype(float).isin(_wallet_user_ids)]
        st.caption(f"📋 Scoped to top-ups made by the {len(_wallet_user_ids):,} users with a "
                  f"matching session at this station this period — wallet transactions have "
                  f"no station of their own.")
    if len(_topups) == 0:
        st.info("No completed top-up transactions match the current selection.")
    else:
        wc1, wc2, wc3, wc4 = st.columns(4)
        _avg_topup = _topups["AMOUNT"].mean()
        _med_topup = _topups["AMOUNT"].median()
        _n_topups  = len(_topups)
        _n_topup_users = _topups["USERID"].nunique()
        kpi(wc1, "Avg Top-Up Amount", f"₱{_avg_topup:,.0f}", f"Median: ₱{_med_topup:,.0f}", "up", "#BEFF6C")
        kpi(wc2, "Total Top-Ups", f"{_n_topups:,}", f"{_n_topup_users:,} unique users", "up", "#BEFF6C")
        kpi(wc3, "Top-Ups per User", f"{(_n_topups/_n_topup_users):.1f}" if _n_topup_users else "—",
            "Avg completed top-ups per user", "up", "#000000")
        if "PAYMENT_METHOD" in _topups.columns and len(_topups):
            _top_method = _topups["PAYMENT_METHOD"].value_counts().index[0]
            kpi(wc4, "Top Funding Method", _top_method, "Most used for top-ups", "up", "#000000")
        else:
            kpi(wc4, "Top Funding Method", "—", "PAYMENT_METHOD not found", "warn", "#A8710A")


# ── UTILIZATION TREND — daily line across the full available date range,
#    not just the selected month (closes the "trends by time period" gap).
#    Company view aggregates across the selected stations; Host Partner
#    view is naturally single-station since sel_stations has one entry.
st.markdown("<div class='sec-hdr'>📈 Utilization Trend</div>", unsafe_allow_html=True)
 
_trend_base = tx[
    (tx["STATIONNAME"].isin(sel_stations)) &
    (tx["CHARGE_TYPE"].isin(charge_types)) &
    (~tx["ISERROR"].astype(bool))
].copy()
 
if len(_trend_base):
    _daily_kwh = _trend_base.groupby("DATE")["ENERGY_KWH"].sum()
    # Same connector set used for the KPI-row denominator, held constant
    # across the trend (a station's connector count rarely changes day to
    # day within the data we have — this avoids a misleading capacity
    # figure driven by an accidental gap in Charge Point Info coverage).
    # Per-day capacity uses each station's own real hours, same as the
    # network-wide KPI above.
    _trend_cap_kwh_per_day = sum(
        cp_sel_online[cp_sel_online["STATIONNAME"] == s]["CAPACITY_KW"].sum()
        * station_hours.get(s, op_hours_fallback)
        for s in cp_sel_online["STATIONNAME"].unique()
    )
    _daily_util = (_daily_kwh / _trend_cap_kwh_per_day * 100).round(1) if _trend_cap_kwh_per_day > 0 else _daily_kwh * 0    
    _trend_df = _daily_util.reset_index()
    _trend_df.columns = ["Date", "Utilization %"]
    _trend_df = _trend_df.sort_values("Date")

    # Chart-specific window selector (defaults to the full year of the
    # currently selected month). Options: Last month (selected month),
    # Last 3 months (selected + 2 prior months), Full year (calendar year).
    trend_window = st.radio("Trend window",
                            ["Last month", "Last 3 months", "Full year"],
                            index=2, horizontal=True, key="trend_window")

    # Compute start/end dates based on the selected window and the
    # `sel_month` Period selected in the sidebar filters.
    if trend_window == "Full year":
        start = pd.Timestamp(year=int(sel_month.year), month=1, day=1).date()
        end = pd.Timestamp(year=int(sel_month.year), month=12, day=31).date()
    elif trend_window == "Last 3 months":
        start_period = sel_month - 2
        start = start_period.to_timestamp(how="start").date()
        end = sel_month.to_timestamp(how="end").date()
    else:  # Last month
        start = sel_month.to_timestamp(how="start").date()
        end = sel_month.to_timestamp(how="end").date()

    _trend_plot = _trend_df[(_trend_df["Date"] >= start) & (_trend_df["Date"] <= end)].copy()
    if len(_trend_plot) == 0:
        st.info("No sessions in the selected trend window for the current station/charge-type selection.")
    else:
        _trend_plot = _trend_plot.assign(
            Month=_trend_plot["Date"].apply(lambda d: d.replace(day=1))
        )
        month_breaks = _trend_plot["Month"].drop_duplicates().sort_values().tolist()

        line = alt.Chart(_trend_plot).mark_line(color="#BEFF6C", strokeWidth=3).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Utilization %:Q", title="Utilization %"),
            tooltip=[alt.Tooltip("Date:T", title="Date"),
                     alt.Tooltip("Utilization %:Q", title="Utilization %")]
        )

        rules = alt.Chart(pd.DataFrame({"Date": month_breaks})).mark_rule(color="#A1A1A1", strokeDash=[4,4]).encode(
            x="Date:T"
        )

        chart = alt.layer(line, rules).resolve_scale(y="shared").properties(height=280)
        st.altair_chart(chart, use_container_width=True)
        st.caption(
            f"Showing {trend_window} — {start} to {end} ({len(_trend_plot):,} days). "
            f"Full data range: {_trend_df['Date'].min()} to {_trend_df['Date'].max()}. "
            f"Capacity denominator uses the current Operating hrs/day setting; connector set held constant.")
else:
    st.info("No sessions match the current station/charge-type selection to plot a trend.")

# ── MAP DATA (built for both views — the Site Performance table below needs
#    it regardless of whether the map itself is shown) ─────────────────────
station_rows = []
for sname in sel_stations:
    s_df  = df[df["STATIONNAME"] == sname]
    s_cp  = cp_cap[cp_cap["STATIONNAME"] == sname]
    s_all = df_all[df_all["STATIONNAME"] == sname]
    s_kwh  = s_df["ENERGY_KWH"].sum()
    s_cap  = s_cp[s_cp["NETWORK_STATUS"]=="Online"]["CAPACITY_KW"].sum()
    s_avail = s_cap * station_hours.get(sname, op_hours_fallback) * days
    s_util  = round(s_kwh / s_avail * 100, 1) if s_avail > 0 else 0
    s_rev   = s_df["TOTALAMOUNT"].sum()
    s_err   = round(s_all["ISERROR"].astype(bool).sum() / max(len(s_all),1)*100, 1)
    lat = s_df["LATITUDE"].dropna().mean()
    lon = s_df["LONGITUDE"].dropna().mean()
    if pd.isna(lat):
        ll = s_cp[["LATITUDE","LONGITUDE"]].dropna()
        if len(ll): lat, lon = ll.iloc[0]["LATITUDE"], ll.iloc[0]["LONGITUDE"]
    if pd.isna(lat): continue
    color = [143,203,62,220] if s_util>=target_util else ([168,113,10,210] if s_util>=target_util*0.7 else [193,68,62,220])
    station_rows.append({
        "STATIONNAME": sname, "LATITUDE": lat, "LONGITUDE": lon,
        "util_pct": s_util, "energy_kwh": round(s_kwh,1),
        "avail_kwh": round(s_avail,1), "revenue": round(s_rev,0),
        "sessions": len(s_df), "error_rate": s_err,
        "color": color,
        "radius": max(int(s_kwh/max(actual_kwh,1)*1200)+150, 120),
        "weight": round(s_kwh/max(actual_kwh,1), 3),
    })
map_df = pd.DataFrame(station_rows)

# ── GEOGRAPHIC HEATMAP — Company / Ops view only ────────────────────────────
if is_company:
    st.markdown("<div class='sec-hdr'>📍 Geographic Heatmap — Utilization by Location</div>",
                unsafe_allow_html=True)

    if map_df["LATITUDE"].isna().all() or len(map_df) == 0:
        st.warning("No station coordinates found for the current selection. "
                  "Check that LATITUDE/LONGITUDE are populated in Station Profile "
                  "or Charge Point Information for these stations.")
    else:
        map_col, bar_col = st.columns([3, 2])

        with map_col:
            map_mode = st.radio("Map layer",
                ["🔥 Heatmap (Utilization)","🔵 Bubbles (Utilization %)"],
                horizontal=True)
            center_lat = map_df["LATITUDE"].mean()
            center_lon = map_df["LONGITUDE"].mean()
            view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon,
                                       zoom=9.5, pitch=35 if "Bubble" in map_mode else 0)
            if "Heatmap" in map_mode:
                pts = []
                for _, r in map_df.iterrows():
                    w = max(r["util_pct"] / 100, 0.05)
                    n = max(1, int(w*100))
                    for _ in range(n):
                        pts.append({"lat": r["LATITUDE"]+np.random.uniform(-.004,.004),
                                     "lon": r["LONGITUDE"]+np.random.uniform(-.004,.004)})
                layer  = pdk.Layer("HeatmapLayer", data=pd.DataFrame(pts),
                    get_position=["lon","lat"], aggregation="SUM",
                    opacity=0.75, threshold=0.03,
                    color_range=[[193,68,62,170],[168,113,10,190],[190,255,108,200],
                                 [143,203,62,220],[79,122,30,240]])
                layers = [layer]
                tooltip = None
            else:
                layer  = pdk.Layer("ScatterplotLayer", data=map_df,
                    get_position=["LONGITUDE","LATITUDE"],
                    get_fill_color="color", get_radius="radius",
                    radius_min_pixels=6, radius_max_pixels=90, pickable=True)
                labels = pdk.Layer("TextLayer", data=map_df,
                    get_position=["LONGITUDE","LATITUDE"],
                    get_text="STATIONNAME", get_size=12,
                    get_color=[0,0,0,230], get_pixel_offset=[0,-24], billboard=True)
                layers  = [layer, labels]
                tooltip = {"html":"""<div style='background:#000000;padding:10px 14px;
                  border-radius:6px;color:#FFF4EC;font-size:12px;min-width:180px'>
                  <b style='color:#BEFF6C'>⚡ {STATIONNAME}</b><hr style='border-color:#BEFF6C;margin:5px 0'>
                  Utilization: <b>{util_pct}%</b><br>kWh actual: <b>{energy_kwh}</b><br>
                  Sessions: <b>{sessions}</b><br>Revenue: <b>₱{revenue}</b><br>
                  Error rate: <b>{error_rate}%</b></div>"""}

            # Free CARTO basemap — no Mapbox token required, unlike mapbox:// styles
            deck = pdk.Deck(
                layers=layers, initial_view_state=view_state,
                map_provider="carto", map_style="light",
                tooltip=tooltip,
            )
            st.pydeck_chart(deck, use_container_width=True)
            l1,l2,l3 = st.columns(3)
            if "Heatmap" in map_mode:
                l1.markdown("🟩 High utilization"); l2.markdown("🟧 Near target"); l3.markdown("🟥 Low utilization")
            else:
                l1.markdown("🟩 ≥ Target"); l2.markdown("🟧 Near target"); l3.markdown("🟥 Below target")

        with bar_col:
            n_total = len(map_df)
            title_suffix = f" (Top 10 of {n_total})" if n_total > 10 else ""
            st.markdown(f"**Utilization by Station vs {target_util}% target**{title_suffix}")
            for _, r in map_df.sort_values("util_pct", ascending=False).head(10).iterrows():
                u = r["util_pct"]; g = u - target_util
                bc = "#BEFF6C" if u>=target_util else ("#A8710A" if u>=target_util*0.7 else "#C1443E")
                gc = "#4F7A1E" if g>=0 else "#C1443E"
                st.markdown(
                    f"<div style='margin-bottom:9px'>"
                    f"<div style='display:flex;justify-content:space-between;font-size:11px;"
                    f"color:#000000;margin-bottom:2px'>"
                    f"<b>{r['STATIONNAME'][:30]}</b>"
                    f"<span style='color:{gc}'>{'▲' if g>=0 else '▼'}{abs(g):.1f}pp</span></div>"
                    f"<div style='background:#EAE0D0;border-radius:2px;height:12px;overflow:hidden'>"
                    f"<div style='width:{min(u,100)}%;height:100%;background:{bc};border-radius:2px'></div></div>"
                    f"<div style='display:flex;justify-content:space-between;font-size:9px;"
                    f"color:#5C574D;margin-top:1px'>"
                    f"<span>{r['energy_kwh']:,.0f} kWh</span><b>{u}%</b></div></div>",
                    unsafe_allow_html=True)

# ── CHARTS ──────────────────────────────────────────────────────────────────
st.markdown("<div class='sec-hdr'>Session & Energy Analysis</div>", unsafe_allow_html=True)

st.markdown("<div class='row-hdr'>Session Timing</div>", unsafe_allow_html=True)
t1,t2 = st.columns(2)
with t1:
    st.markdown("**Avg Sessions by Hour of Day**")
    h = df.groupby("HOUR").size().reset_index(name="Sessions")
     # Raw totals accumulate across every day in the selected month (hour 8
    # would sum ~30 days' worth of 8am sessions) — divide by the number of
    # days in the period (same `days` used for the capacity denominator
    # elsewhere) so this reads as "typical sessions at this hour," not a
    # monthly total that's bigger just because the month is longer.
    h["Sessions"] = (h["Sessions"] / days).round(1)
    if len(h): st.bar_chart(h.set_index("HOUR"), color="#BEFF6C", height=200)
with t2:
    st.markdown("**Avg Sessions by Day of Week**")
    _dow_order = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    dow = df.copy()
    dow["DOW"] = pd.Categorical(dow["STARTTIME"].dt.strftime("%a"),
                                categories=_dow_order, ordered=True)
    dow_ct = dow.groupby("DOW", observed=False).size().reset_index(name="Sessions")
    # Months don't have equal counts of each weekday (a 31-day month can
    # have 5 Saturdays but only 4 Tuesdays) — dividing by raw session
    # totals alone would inflate whichever weekday happens to occur one
    # extra time, independent of actual demand. Use the TRUE calendar
    # count of each weekday within the selected month as the denominator.
    _y, _m = sel_month.year, sel_month.month
    _n_days_calendar = calendar.monthrange(_y, _m)[1]
    _month_dates = pd.date_range(start=f"{_y}-{_m:02d}-01", periods=_n_days_calendar, freq="D")
    _dow_occurrences = pd.Series(_month_dates.strftime("%a")).value_counts()
    dow_ct["Occurrences"] = dow_ct["DOW"].astype(str).map(_dow_occurrences).fillna(1)
    dow_ct["Sessions"] = (dow_ct["Sessions"] / dow_ct["Occurrences"]).round(1)
    if len(dow_ct): st.bar_chart(dow_ct.set_index("DOW")[["Sessions"]], color="#BEFF6C", height=200)

st.markdown("<div class='row-hdr'>Charging Preferences</div>", unsafe_allow_html=True)
st.caption("Equipment and vehicle mix.")

_charger_type_map = cp_cap.groupby("CHARGER_ID")["CHARGER_TYPE"].first()
_df_psm = df.copy()
_df_psm["POWER_SUPPLY_MODE"] = _df_psm["CHARGER_ID"].map(_charger_type_map)


# Plug Type and Car Brand are USER attributes (from UserDetails), not
# session attributes — that table has no STATIONNAME, so "station-level"
# means scoping to users who had a matching session under the current
# filters (works the same in either view; Host Partner just has a
# smaller, single-station pool).
_filtered_user_ids = set(df["USERID"].dropna().astype(float).unique())
ud_scoped = ud[ud["USERID"].astype(float).isin(_filtered_user_ids)]
 
# Plug Type is only meaningful where 2+ plug types are actually installed
# at the selected station(s) — with only one plug type on site, "which
# plug do our customers have" is circular (only compatible customers can
# charge there at all). With 2+ types installed, the split among
# compatible customers becomes a real signal for connector planning.
_installed_plug_types = cp_cap[cp_cap["STATIONNAME"].isin(sel_stations)]["PLUG_TYPE"].nunique()

p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("**Power Supply Mode**")
    psm_ct = _df_psm.groupby("POWER_SUPPLY_MODE").size().reset_index(name="Sessions")
    psm_ct = psm_ct[psm_ct["POWER_SUPPLY_MODE"].notna()]
    if len(psm_ct):
        st.bar_chart(psm_ct.set_index("POWER_SUPPLY_MODE"), color="#BEFF6C", height=200)
        _psm_dur = _df_psm.groupby("POWER_SUPPLY_MODE")["DURATION_MIN"].mean()
        _dur_bits = [f"{k}: {v:.0f} min avg" for k, v in _psm_dur.items() if pd.notna(v)]
        if _dur_bits:
            st.caption(" · ".join(_dur_bits) + f" — explains the {avg_dur:.0f} min network average above.")
    else:
        st.info("No Power Supply Mode data — CHARGER_TYPE not available for these chargers in "
               "Charge Point Info.")
with p2:
    st.markdown("**Plug Type Distribution**")
    if _installed_plug_types < 2:
        st.caption(f"Only {_installed_plug_types} plug type installed at the selected "
                  f"station(s) — a distribution here would be circular (only compatible "
                  f"customers can charge here at all). This shows only when 2+ types are installed.")
    elif len(ud_scoped) and "PLUG_TYPE" in ud_scoped.columns:
        plugs = ud_scoped["PLUG_TYPE"].value_counts().reset_index()
        plugs.columns = ["Plug Type","Users"]
        st.bar_chart(plugs.set_index("Plug Type"), color="#BEFF6C", height=200)
        st.caption("Demand split among your installed chargers to know what your customers actually have.")
    else:
        st.info("No users match the current filter selection.")
with p3:
    st.markdown("**Car Brand Distribution (Top 10)**")
    if len(ud_scoped) and "CARBRAND" in ud_scoped.columns:
        brands = ud_scoped["CARBRAND"].value_counts().head(10).reset_index()
        brands.columns = ["Brand","Users"]
        st.bar_chart(brands.set_index("Brand"), color="#BEFF6C", height=200)
    else:
        st.info("No users match the current filter selection.")

st.caption(f"📋 Plug type & car brand scoped to the {len(ud_scoped):,} users with at least "
           f"one matching session under the current filters — not all {len(ud):,} "
           f"registered users.")


# ── ANOMALY CHECK ────────────────────────────────────────────────────────────
# Rate-based (kWh delivered per minute), not duration-based. Duration alone
# doesn't define whether a session looks wrong: a DC session that runs long
# but also delivers a lot of energy is normal (a big battery can legitimately
# take a while, even on fast charging); the real signal is a LOW delivery
# rate, regardless of how long the session ran. Same logic applies
# symmetrically to AC — a short AC session isn't suspicious on its own, but
# one that delivers energy at DC-like speed is. (A full AC charge in this
# data typically runs ~3.5 hours once you filter to sessions of a
# meaningful size — a plain "AC session took >X minutes" check would have
# flagged most ordinary AC charging as anomalous.)
#
# Data cleaning applied before computing any rate: sessions under 1 minute
# are logging artifacts, not real charges (a handful in this data show
# ENERGY_KWH delivered in under a second — division by near-zero duration
# produces an infinite or absurd rate). Sessions above 200 kWh are also
# excluded — a typical EV battery is 20-100 kWh, so a single-session value
# far beyond that is almost certainly a unit or decimal data-entry error
# (one row in this network shows 35,000+ kWh for a single session) rather
# than a genuine large-vehicle charge. Recommend EVOxCharge investigate
# both patterns at the source system level, since they will quietly inflate
# or corrupt any rate/efficiency metric computed from ENERGY_KWH / duration.
def _rate_valid(frame):
    return frame[
        (frame["DURATION_MIN"] >= 1) &
        (frame["ENERGY_KWH"] > 0) &
        (frame["ENERGY_KWH"] <= 200)
    ].copy()

_baseline = tx[(~tx["ISERROR"].astype(bool)) & tx["DURATION_MIN"].notna()].copy()
_baseline["POWER_SUPPLY_MODE"] = _baseline["CHARGER_ID"].map(_charger_type_map)
_baseline = _rate_valid(_baseline)
_baseline["RATE"] = _baseline["ENERGY_KWH"] / _baseline["DURATION_MIN"]
_ac_median_rate = _baseline.loc[_baseline["POWER_SUPPLY_MODE"]=="AC", "RATE"].median()
_dc_median_rate = _baseline.loc[_baseline["POWER_SUPPLY_MODE"]=="DC", "RATE"].median()

_scope = _rate_valid(_df_psm[_df_psm["DURATION_MIN"].notna()])
_scope["RATE"] = _scope["ENERGY_KWH"] / _scope["DURATION_MIN"]
_dc_slow = (_scope[(_scope["POWER_SUPPLY_MODE"]=="DC") & (_scope["RATE"] < _ac_median_rate)]
           if pd.notna(_ac_median_rate) else _scope.iloc[0:0])
_ac_fast = (_scope[(_scope["POWER_SUPPLY_MODE"]=="AC") & (_scope["RATE"] > _dc_median_rate*0.5)]
           if pd.notna(_dc_median_rate) else _scope.iloc[0:0])
_n_anom = len(_dc_slow) + len(_ac_fast)
_n_excluded = len(_df_psm[_df_psm["DURATION_MIN"].notna()]) - len(_scope)

if _n_anom > 0:
    st.markdown(
        f"<div style='background:#FEF3DC;border-left:3px solid #A8710A;border-radius:4px;"
        f"padding:8px 12px;margin-top:4px;font-size:11px;color:#000'>"
        f"⚠️ <b>{_n_anom} anomal{'y' if _n_anom==1 else 'ies'} in current selection "
        f"(rate-based, not duration-based):</b> "
        f"{len(_dc_slow)} DC session(s) delivered energy slower than a typical AC session "
        f"(&lt;{_ac_median_rate:.2f} kWh/min) — possible mislabeled or underperforming fast "
        f"charger; {len(_ac_fast)} AC session(s) delivered energy at DC-like speed "
        f"(&gt;{_dc_median_rate*0.5:.2f} kWh/min) — possible mislabeled connector or data error."
        f"</div>", unsafe_allow_html=True
    )
    with st.expander(f"View the {min(_n_anom,20)} flagged sessions", expanded=False):
        _flagged = pd.concat([
            _dc_slow.assign(**{"Flag": "DC running slow"}),
            _ac_fast.assign(**{"Flag": "AC running fast"}),
        ]).sort_values("RATE").head(20)
        _flagged["Charger"] = _flagged["CHARGER_ID"].astype(str)
        _flagged_display = _flagged[["STATIONNAME","Charger","POWER_SUPPLY_MODE",
                                     "DURATION_MIN","ENERGY_KWH","RATE","Flag"]].rename(columns={
            "STATIONNAME":"Station","POWER_SUPPLY_MODE":"Type",
            "DURATION_MIN":"Duration (min)","ENERGY_KWH":"kWh","RATE":"kWh/min"})
        st.dataframe(_flagged_display, use_container_width=True, hide_index=True)
    if _n_excluded > 0:
        st.caption(f"📋 {_n_excluded:,} session(s) in this selection excluded from rate analysis "
                  f"for data quality (near-instant duration or implausible energy value) — see "
                  f"the section notes above for recommended data cleaning.")

# ── SITE PERFORMANCE TABLE ───────────────────────────────────────────────────
st.markdown("<div class='sec-hdr'>Site Performance — Energy Utilization vs Capacity</div>",
            unsafe_allow_html=True)
if len(map_df):
    tbl = map_df[["STATIONNAME","util_pct","energy_kwh","avail_kwh",
                   "sessions","revenue","error_rate"]].copy()
    tbl["gap_pp"] = (tbl["util_pct"] - target_util).round(1)
    tbl["action"] = tbl["util_pct"].apply(
        lambda u: "✅ Expand" if u>=target_util
        else ("🟡 Monitor" if u>=target_util*0.7
        else ("⚠️ Optimize" if u>=target_util*0.4 else "🔴 Review")))
    tbl = tbl.rename(columns={
        "STATIONNAME":"Station","util_pct":"Util %","energy_kwh":"kWh Actual",
        "avail_kwh":"kWh Available","sessions":"Sessions",
        "revenue":"Revenue (₱)","error_rate":"Error %",
        "gap_pp":"Gap (pp)","action":"Action"
    }).sort_values("Util %", ascending=False)
    st.dataframe(tbl, use_container_width=True, hide_index=True)

    _t70 = round(target_util*0.7, 1)
    _t40 = round(target_util*0.4, 1)
    st.markdown(f"""
    <div style='background:#fff;border-radius:6px;padding:10px 14px;
                border:1px solid #EAE0D0;margin-top:6px;font-size:10px;color:#5C574D'>
      <b style='color:#000'>Action legend</b> — thresholds scale with your current
      {target_util}% target:
      &nbsp; <span style='color:#4F7A1E;font-weight:600'>✅ Expand</span> ≥ {target_util}%
      &nbsp;·&nbsp; <span style='color:#A8710A;font-weight:600'>🟡 Monitor</span> ≥ {_t70}%
      &nbsp;·&nbsp; <span style='color:#A8710A;font-weight:600'>⚠️ Optimize</span> ≥ {_t40}%
      &nbsp;·&nbsp; <span style='color:#C1443E;font-weight:600'>🔴 Review</span> &lt; {_t40}%
    </div>
    """, unsafe_allow_html=True)

# ── PER-CHARGER ERROR RATE RANKING ───────────────────────────────────────────
st.markdown("<div class='sec-hdr'>⚠️ Charger Error Rate Ranking</div>", unsafe_allow_html=True)
 
_err_scope = df_all[df_all["STATIONNAME"].isin(sel_stations)]
if len(_err_scope) and "CHARGER_ID" in _err_scope.columns:
    _cp_err = _err_scope.groupby("CHARGER_ID").agg(
        Sessions=("SESSION_ID", "count") if "SESSION_ID" in _err_scope.columns else ("ISERROR", "count"),
        Errors=("ISERROR", lambda x: x.astype(bool).sum()),
    ).reset_index()
    _cp_err["Error Rate %"] = (_cp_err["Errors"] / _cp_err["Sessions"] * 100).round(1)
    _cp_err = _cp_err[_cp_err["Sessions"] >= 3]  # drop chargers with too few sessions to be meaningful
    _cp_err = _cp_err.sort_values("Error Rate %", ascending=False).head(10)
 
    if len(_cp_err) == 0:
        st.info("No chargers in the current selection have enough sessions (≥3) this period to rank.")
    else:
        st.caption("Top 10 chargers by error rate this period (min. 3 sessions)")
        for _, r in _cp_err.iterrows():
            rate = r["Error Rate %"]
            bc = "#C1443E" if rate > 10 else ("#A8710A" if rate > 5 else "#BEFF6C")
            st.markdown(
                f"<div style='margin-bottom:7px'>"
                f"<div style='display:flex;justify-content:space-between;font-size:11px;color:#000'>"
                f"<b>{r['CHARGER_ID']}</b><span>{rate:.1f}% ({int(r['Errors'])}/{int(r['Sessions'])})</span></div>"
                f"<div style='background:#EAE0D0;border-radius:2px;height:8px;overflow:hidden'>"
                f"<div style='width:{min(rate,100)}%;height:100%;background:{bc};border-radius:2px'></div></div>"
                f"</div>", unsafe_allow_html=True)
else:
    st.info("No CHARGER_ID data available for the current selection.")

# ── FINANCIALS (CPO breakdown table — network-wide, Company view only) ──────
if is_company:
    st.markdown("<div class='sec-hdr'>💰 Financials — Revenue & Operating Costs by CPO (Jan–Jun 2026)</div>",
                unsafe_allow_html=True)
    fd = fin_overall[["CPO","Revenue","ActualElecCost","ActualRent","EstIncome2026"]].copy()
    fd.columns = ["CPO / Station","Revenue (₱)","Elec Cost (₱)","Rent/Share (₱)","Est. Income 2026 (₱)"]
    for col in fd.columns[1:]:
        fd[col] = fd[col].apply(lambda x: f"₱{x:,.0f}" if pd.notna(x) and isinstance(x,(int,float)) else "—")
    st.dataframe(fd.dropna(subset=["CPO / Station"]), use_container_width=True, hide_index=True)
    _n_matched = payback_ref["STATIONNAME"].nunique()
    st.caption(
        f"📋 **Source:** figures above are reported directly from the Financials workbook "
        f"(`{FILE_DEFAULTS['financials']}`), not computed from Session Logs — they are not "
        f"currently reconciled against the transaction-based Revenue KPIs shown elsewhere in "
        f"this dashboard. Only {_n_matched} of the {len(fin_overall):,} entries here have a name "
        f"matching an actual station in your session data ({', '.join(sorted(payback_ref['STATIONNAME'].unique())) if _n_matched else 'none'}); "
        f"the rest have no corresponding transaction history to cross-check against."
    )

# ── SITE PAYBACK TRACKER — Host Partner Site view only ──────────────────────
if not is_company:
    _station = sel_stations[0]
    st.markdown("<div class='sec-hdr'>💰 Site Payback Tracker</div>", unsafe_allow_html=True)

    _match = payback_ref[payback_ref["STATIONNAME"] == _station]

    if len(_match) == 0:
        st.info(
            f"⚠️ Payback can't be computed for **{_station}** — its name doesn't have a "
            f"matching entry with recorded CapEx in the Financials workbook (`{FILE_DEFAULTS['financials']}`), "
            f"or no investment amount is on file for it. Payback tracking currently only works for "
            f"the {len(payback_ref)} stations whose Financials-workbook name matches an actual "
            f"station in your session data: {', '.join(sorted(payback_ref['STATIONNAME'].unique()))}."
        )
    else:
        _capex   = float(_match["TOTAL_CAPEX"].iloc[0])
        _elec    = float(_match["ActualElecCost"].iloc[0])
        _rent    = float(_match["ActualRent"].iloc[0])

        # Revenue from the SAME Jan–Jun 2026 window the Financials workbook's
        # actual cost figures cover — using all-time transaction revenue
        # against only 6 months of cost data would overstate progress.
        _jj = tx[
            (tx["STATIONNAME"] == _station) &
            (tx["STARTTIME"] >= pd.Timestamp("2026-01-01")) &
            (tx["STARTTIME"] <  pd.Timestamp("2026-07-01")) &
            (~tx["ISERROR"].astype(bool))
        ]
        _jj_revenue = _jj["TOTALAMOUNT"].sum()
        _months_covered = _jj["MONTH"].nunique() if len(_jj) else 0

        _contribution = _jj_revenue - _elec - _rent
        _payback_pct  = (_contribution / _capex * 100) if _capex > 0 else 0
        _monthly_contrib = (_contribution / _months_covered) if _months_covered > 0 else 0
        _months_left = ((_capex - _contribution) / _monthly_contrib) if _monthly_contrib > 0 else None

        pc1, pc2 = st.columns([2,1])
        with pc1:
            st.markdown(f"""
            <div style='background:#fff;border-radius:8px;padding:16px 20px;
                        border-left:4px solid #000;box-shadow:0 1px 6px rgba(0,0,0,.07)'>
              <div style='font-size:11px;color:#5C574D'>Jan–Jun 2026 Revenue (from transactions)</div>
              <div style='font-size:15px;font-weight:700;color:#000'>₱{_jj_revenue:,.0f}</div>
              <div style='display:flex;gap:24px;margin-top:8px'>
                <div><div style='font-size:10px;color:#5C574D'>− Electricity Cost</div>
                     <div style='font-size:13px;color:#C1443E;font-weight:600'>₱{_elec:,.0f}</div></div>
                <div><div style='font-size:10px;color:#5C574D'>− Rent / Share</div>
                     <div style='font-size:13px;color:#C1443E;font-weight:600'>₱{_rent:,.0f}</div></div>
                <div><div style='font-size:10px;color:#5C574D'>= Contribution</div>
                     <div style='font-size:13px;color:#4F7A1E;font-weight:700'>₱{_contribution:,.0f}</div></div>
              </div>
              <hr style='margin:10px 0;border-color:#EAE0D0'>
              <div style='font-size:10px;color:#5C574D'>Total CapEx (Financials workbook)</div>
              <div style='font-size:13px;color:#000;font-weight:600'>₱{_capex:,.0f}</div>
              <div style='background:#EAE0D0;border-radius:4px;height:14px;margin-top:8px;overflow:hidden'>
                <div style='width:{min(max(_payback_pct,0),100)}%;height:100%;
                            background:{"#BEFF6C" if _payback_pct>=0 else "#C1443E"};border-radius:4px'></div>
              </div>
              <div style='font-size:10px;color:#5C574D;margin-top:4px'>
                {_payback_pct:.1f}% recovered
                {f"· ~{_months_left:.0f} months remaining at current rate" if _months_left and _months_left>0 else ""}
              </div>
            </div>
            """, unsafe_allow_html=True)
        with pc2:
            st.caption(
                f"📋 Based on {_months_covered} month(s) of matched actual cost data "
                f"(Jan–Jun 2026). Revenue is computed from your transaction data for the "
                f"same window, not the Financials workbook's own Revenue figure — so this "
                f"may differ from the number shown in the network-wide Financials table."
            )

# ── HOST PARTNER CONNECTOR DETAIL ────────────────────────────────────────────
if not is_company:
    st.markdown(f"<div class='sec-hdr'>🔌 Connector Detail — {sel_stations[0]}</div>",
                unsafe_allow_html=True)
    # Charge Point Info is connector-level (a charger can have multiple plug
    # rows), but Session Logs only track CHARGER_ID — so group here by
    # charger for display, summing capacity and listing all its plug types,
    # rather than showing one card per port (which would double-count
    # that charger's sessions across cards).
    site_rows = cp_cap[cp_cap["STATIONNAME"]==sel_stations[0]]
    if len(site_rows):
        site_cps = site_rows.groupby("CHARGER_ID").agg(
            CAPACITY_KW=("CAPACITY_KW","sum"),
            PLUG_TYPE=("PLUG_TYPE", lambda x: " + ".join(sorted(set(x)))),
            CHARGER_TYPE=("CHARGER_TYPE","first"),
            NETWORK_STATUS=("NETWORK_STATUS","first"),
            CONNECTOR_STATUS=("CONNECTOR_STATUS","first"),
            PORTS=("PLUG_TYPE","count"),
        ).reset_index()
    else:
        site_cps = site_rows
    if len(site_cps):
        cols = st.columns(min(len(site_cps),5))
        for i,(_, row) in enumerate(site_cps.iterrows()):
            if i>=5: break
            sc = "#4F7A1E" if row.get("NETWORK_STATUS")=="Online" else "#C1443E"
            cs = row.get("CONNECTOR_STATUS","—")
            cs_col = "#4F7A1E" if cs=="Available" else ("#000000" if cs=="Charging" else "#C1443E")
            cp_sess = df[df["CHARGER_ID"]==row["CHARGER_ID"]]
            cp_kwh  = cp_sess["ENERGY_KWH"].sum()
            cp_avail = row.get("CAPACITY_KW",0) * station_hours.get(sel_stations[0], op_hours_fallback)  * days
            cp_util  = round(cp_kwh/cp_avail*100,1) if cp_avail>0 else 0
            ports_label = f" · {int(row['PORTS'])} ports" if row.get("PORTS",1) > 1 else ""
            cols[i].markdown(
                f"<div style='background:white;border-radius:6px;padding:11px;"
                f"border-top:3px solid {sc};box-shadow:0 1px 4px rgba(0,0,0,.07)'>"
                f"<div style='font-size:11px;font-weight:600;color:#000000'>{row['CHARGER_ID']}</div>"
                f"<div style='font-size:9px;color:#5C574D'>{row.get('CHARGER_TYPE','—')} · {row.get('CAPACITY_KW','—')}kW{ports_label}</div>"
                f"<div style='font-size:9px;color:#5C574D'>{row.get('PLUG_TYPE','—')}</div>"
                f"<div style='font-size:9px;color:{cs_col};margin-top:3px'>● {cs}</div>"
                f"<hr style='margin:5px 0;border-color:#EAE0D0'>"
                f"<div style='font-size:9px;color:#5C574D'>Util: <b style='color:#000000'>{cp_util}%</b></div>"
                f"<div style='font-size:9px;color:#5C574D'>kWh: <b style='color:#000000'>{cp_kwh:,.0f}</b></div>"
                f"<div style='font-size:9px;color:#5C574D'>Sessions: <b style='color:#000000'>{len(cp_sess)}</b></div>"
                f"</div>", unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:10px;color:#8A8377'>"
    "Project ChargeIQ Analytics · AIM MAIDA Capstone · "
    "Built with Streamlit + PyDeck</div>",
    unsafe_allow_html=True)