import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import io
from pathlib import Path

# ── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Project ChargeIQ Analytics", page_icon="⚡",
                   layout="wide", initial_sidebar_state="expanded")

# ── BRAND PALETTE ────────────────────────────────────────────────────────────
# Lime #BEFF6C · Cream #FFF4EC · White #FFFFFF · Black #000000 (accent)
st.markdown("""
<style>
.stApp{background:#FFF4EC}
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

/* ── Kill Streamlit's default red accents everywhere ─────────────────── */
span[data-baseweb="tag"], div[data-baseweb="tag"]{
  background-color:#BEFF6C!important; color:#000000!important;
  border-color:#000000!important;
}
span[data-baseweb="tag"] svg, div[data-baseweb="tag"] svg{ fill:#000000!important; }
div[data-baseweb="select"] > div{ border-color:#EAE0D0!important; background:#fff!important; }
div[data-baseweb="select"]:focus-within > div{
  border-color:#BEFF6C!important; box-shadow:0 0 0 1px #BEFF6C!important;
}
div[data-baseweb="popover"] li:hover, div[data-baseweb="menu"] li:hover{
  background-color:#FFF4EC!important;
}
div[role="radiogroup"] label div:first-child{ border-color:#000000!important; }
div[role="radiogroup"] label div:first-child > div{ background-color:#000000!important; }
input[type="checkbox"], input[type="radio"]{ accent-color:#BEFF6C!important; }
div[data-testid="stSlider"] div[role="slider"]{
  background-color:#000000!important; border-color:#000000!important;
}
div[data-testid="stSlider"] > div > div > div{ background-color:#BEFF6C!important; }
div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"]{ color:inherit!important; }
button[kind="primary"]{ background-color:#000000!important; color:#BEFF6C!important; border-color:#000000!important; }
button[kind="secondary"]{ border-color:#000000!important; color:#000000!important; }
div[data-testid="stFileUploader"] section{
  background:#FFF4EC!important; border:1px dashed #000000!important;
}
</style>
""", unsafe_allow_html=True)

# ── DATA SOURCE: uploaded files OR files beside this script ────────────────
BASE = Path(__file__).parent

FILE_LABELS = {
    "transactions":    "Session Logs (transactions.xlsx)",
    "charge_points":   "Charge Point Information (.xlsx)",
    "station_profile": "Station Profile (.xlsx)",
    "user_details":    "User Details (.xlsx)",
    "wallet_txn":      "Wallet Transactions (.xlsx)",
    "financials":      "Financials Workbook (.xlsx)",
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

with st.sidebar:
    st.markdown("## ⚡ Project ChargeIQ")
    st.markdown("---")
    with st.expander("📤 Upload data (optional)", expanded=False):
        st.caption("Upload your own Excel exports here, or leave blank to use "
                   "the files already bundled with the app.")
        uploaded = {}
        for key, label in FILE_LABELS.items():
            uploaded[key] = st.file_uploader(label, type=["xlsx"], key=f"up_{key}")

# Resolve each source: uploaded file takes priority over the bundled file
file_bytes = {}
missing = []
for key, fname in FILE_DEFAULTS.items():
    up = uploaded.get(key)
    if up is not None:
        file_bytes[key] = up.getvalue()
    else:
        p = disk_path(fname)
        if p is not None:
            file_bytes[key] = p.read_bytes()
        else:
            file_bytes[key] = None
            missing.append(fname)

# ── MISSING FILE GUARD ──────────────────────────────────────────────────────
if missing:
    st.error("❌ Missing data files. Upload them using **📤 Upload data** in the "
             "sidebar, or place these in the same folder as `chargeiq_app.py` "
             "(or in a `/data` subfolder):")
    for f in missing:
        st.markdown(f"- `{f}`")
    st.info("📁 If bundling locally, your folder should look like:\n```\n"
           "chargeiq_app.py\nrequirements.txt\ntransactions.xlsx\nUserDetails.xlsx\n"
           "walletTransactions.xlsx\nStation_Profile.xlsx\n"
           "Charge_Point_Information_...xlsx\nProjectChargeIQ_Financials.xlsx\n```")
    st.stop()

# ── LOAD ALL DATA ──────────────────────────────────────────────────────────
@st.cache_data
def load_all(tx_b, cp_b, sp_b, ud_b, wt_b, fin_b):
    tx = pd.read_excel(io.BytesIO(tx_b), sheet_name="transactions.csv")
    cp = pd.read_excel(io.BytesIO(cp_b))
    sp = pd.read_excel(io.BytesIO(sp_b))
    ud = pd.read_excel(io.BytesIO(ud_b))
    wt = pd.read_excel(io.BytesIO(wt_b))
    fin = pd.read_excel(io.BytesIO(fin_b), sheet_name=None)

    tx["STARTTIME"] = pd.to_datetime(tx["STARTTIME"], errors="coerce")
    tx["ENDTIME"]   = pd.to_datetime(tx["ENDTIME"],   errors="coerce")
    tx = tx[tx["STARTTIME"].dt.year > 2020].copy()
    tx["DATE"]  = tx["STARTTIME"].dt.date
    tx["MONTH"] = tx["STARTTIME"].dt.to_period("M")
    tx["HOUR"]  = tx["STARTTIME"].dt.hour
    tx["DURATION_MIN"] = (tx["ENDTIME"] - tx["STARTTIME"]).dt.total_seconds() / 60

    sp_coords = sp.groupby("STATIONNAME")[["LATITUDE","LONGITUDE","BUSINESS_START","BUSINESS_END","RATE_PER_KWH"]].first().reset_index()
    cp = cp.merge(sp_coords[["STATIONNAME","BUSINESS_START","BUSINESS_END"]], on="STATIONNAME", how="left")

    cp_coords = cp.groupby("STATIONNAME")[["LATITUDE","LONGITUDE"]].first().reset_index()
    tx = tx.merge(cp_coords, on="STATIONNAME", how="left")

    sp_ll = sp.groupby("STATIONNAME")[["LATITUDE","LONGITUDE"]].first().reset_index()
    missing_ll = tx["LATITUDE"].isna()
    tx_miss = tx[missing_ll].drop(columns=["LATITUDE","LONGITUDE"]).merge(
        sp_ll, on="STATIONNAME", how="left")
    tx.loc[missing_ll, "LATITUDE"]  = tx_miss["LATITUDE"].values
    tx.loc[missing_ll, "LONGITUDE"] = tx_miss["LONGITUDE"].values

    cp_cap = cp.groupby("CHARGER_ID").agg(
        CAPACITY_KW=("CAPACITY_KW","first"),
        CHARGER_TYPE=("CHARGER_TYPE","first"),
        PLUG_TYPE=("PLUG_TYPE","first"),
        STATIONNAME=("STATIONNAME","first"),
        CHARGER_ACTIVE=("CHARGER_ACTIVE","first"),
        NETWORK_STATUS=("NETWORK_STATUS","first"),
        CONNECTOR_STATUS=("CONNECTOR_STATUS","first"),
        LATITUDE=("LATITUDE","first"),
        LONGITUDE=("LONGITUDE","first"),
    ).reset_index()

    fin_overall = fin["OVERALL"].dropna(subset=["CPO"]).copy()
    fin_overall.columns = ["CPO","Revenue","ActualElecCost","EstElecCost",
                            "ActualRent","EstRent","EstIncome2026"]
    fin_overall = fin_overall[fin_overall["CPO"] != "SUB TOTAL:"].copy()

    opex = fin["ACTUAL OPEX (JAN-JUN)"].copy()
    opex.columns = ["CPO","ElecJan","ElecFeb","ElecMar","ElecApr","ElecMay","ElecJun",
                    "RentJan","RentFeb","RentMar","RentApr","RentMay","RentJun","Remarks"]
    opex = opex[opex["CPO"].notna() & (opex["CPO"] != "CPO") & (opex["CPO"] != "CPO - JV")].copy()

    fees = fin["FEES AND ASSUMPTIONS"].dropna(subset=["CPO"]).copy()
    fees = fees[fees["CPO"] != "CPO - JV"].copy()

    return tx, cp, cp_cap, sp, ud, wt, fin_overall, opex, fees

tx, cp, cp_cap, sp, ud, wt, fin_overall, opex_df, fees_df = load_all(
    file_bytes["transactions"], file_bytes["charge_points"], file_bytes["station_profile"],
    file_bytes["user_details"], file_bytes["wallet_txn"], file_bytes["financials"]
)

# ── SIDEBAR FILTERS ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filters")
    view = st.radio("Dashboard View",
                    ["🏢  Company / Ops", "🏪  Host Partner Site"])
    is_company = view.startswith("🏢")

    all_stations = sorted(tx["STATIONNAME"].dropna().unique().tolist())

    if is_company:
        sel_stations = st.multiselect("Stations", all_stations, default=all_stations[:10])
        if not sel_stations:
            sel_stations = all_stations
    else:
        sel_station  = st.selectbox("Site", all_stations, index=0)
        sel_stations = [sel_station]

    all_months    = sorted(tx["MONTH"].dropna().unique().tolist(), reverse=True)
    month_labels  = [str(m) for m in all_months]
    sel_month_lbl = st.selectbox("Month", month_labels, index=0)
    sel_month     = all_months[month_labels.index(sel_month_lbl)]

    charge_types = st.multiselect("Charge Type",
        tx["CHARGE_TYPE"].dropna().unique().tolist(),
        default=tx["CHARGE_TYPE"].dropna().unique().tolist())

    op_hours = st.slider("Operating hrs / day", 8, 24, 12)
    if st.checkbox("Use 24-hr capacity", value=False):
        op_hours = 24

    target_util = st.slider("Target Utilization %", 50, 90, 70)

    st.markdown("---")
    days_in_month = tx[tx["MONTH"] == sel_month]["DATE"].nunique()
    st.markdown(f"<small style='color:#FFF4EC'>Period: **{sel_month}**<br>"
                f"Active days: **{days_in_month}**<br>"
                f"Source: {'Uploaded files' if any(uploaded.values()) else 'Bundled data'}</small>",
                unsafe_allow_html=True)

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
cp_sel = cp_cap[cp_cap["STATIONNAME"].isin(sel_stations) & (cp_cap["CHARGER_ACTIVE"] == 1)]
total_avail_kwh = cp_sel["CAPACITY_KW"].sum() * op_hours * days
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
online_cps  = len(cp_sel[cp_sel["NETWORK_STATUS"] == "Online"])
offline_cps = len(cp_sel[cp_sel["NETWORK_STATUS"] == "Offline"])
faulty_cps  = len(cp[cp["STATIONNAME"].isin(sel_stations) & (cp["CONNECTOR_STATUS"] == "Faulty")])
uptime_pct  = (online_cps / total_cps * 100) if total_cps > 0 else 0
avg_dur     = df["DURATION_MIN"].mean() if len(df) else 0

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
    st.markdown("<div style='background:#BEFF6C;border-radius:8px;padding:8px 10px;"
                "font-size:22px;text-align:center;margin-top:6px'>⚡</div>",
                unsafe_allow_html=True)
with col_ttl:
    title = "Network Dashboard" if is_company else f"Site Dashboard — {sel_stations[0]}"
    st.markdown(f"<h2 style='margin:0;color:#000000'>Project ChargeIQ — {title}</h2>"
                f"<p style='margin:0;color:#5C574D;font-size:11px'>"
                f"{sel_month} · {days} active days · Op hrs: {op_hours}h/day</p>",
                unsafe_allow_html=True)
st.markdown("---")

# ── FORMULA EXPANDER ────────────────────────────────────────────────────────
with st.expander("📐 Energy-Based Utilization Formula", expanded=False):
    st.markdown(f"""<div class='formula-box'>
Utilization Rate (%) = Σ Actual kWh Charged ÷ Total Available Capacity × 100

Σ Actual kWh Charged     = {actual_kwh:,.1f} kWh  (ENERGY_KWH where ISERROR=0)
Total Available Capacity = Active Connectors × CAPACITY_KW × {op_hours} hrs/day × {days} days
                         = {total_avail_kwh:,.0f} kWh
Network Utilization      = {actual_kwh:,.1f} ÷ {total_avail_kwh:,.0f} × 100 = {net_util:.1f}%
Gap vs {target_util}% target   = {util_gap:+.1f} pp
</div>""", unsafe_allow_html=True)

# ── KPI HELPER ────────────────────────────────────────────────────────────────
def kpi(col, label, value, trend, tclass="up", border="#000000"):
    col.markdown(
        f"<div class='kpi-card' style='border-left-color:{border}'>"
        f"<div class='kpi-label'>{label}</div>"
        f"<div class='kpi-value'>{value}</div>"
        f"<div class='kpi-trend {tclass}'>{trend}</div></div>",
        unsafe_allow_html=True)

st.markdown("<div class='sec-hdr'>Key Performance Indicators</div>", unsafe_allow_html=True)

# ── ROW 1: UTILIZATION ───────────────────────────────────────────────────────
st.markdown("<div class='row-hdr'>Utilization</div>", unsafe_allow_html=True)
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
st.markdown("<div class='row-hdr'>Reliability</div>", unsafe_allow_html=True)
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
st.markdown("<div class='row-hdr'>Revenue</div>", unsafe_allow_html=True)
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
st.markdown("<div class='row-hdr'>Customer</div>", unsafe_allow_html=True)
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

# ── MAP DATA (built for both views — the Site Performance table below needs
#    it regardless of whether the map itself is shown) ─────────────────────
station_rows = []
for sname in sel_stations:
    s_df  = df[df["STATIONNAME"] == sname]
    s_cp  = cp_cap[cp_cap["STATIONNAME"] == sname]
    s_all = df_all[df_all["STATIONNAME"] == sname]
    s_kwh  = s_df["ENERGY_KWH"].sum()
    s_cap  = s_cp[s_cp["CHARGER_ACTIVE"]==1]["CAPACITY_KW"].sum()
    s_avail = s_cap * op_hours * days
    s_util  = round(s_kwh / s_avail * 100, 1) if s_avail > 0 else 0
    s_rev   = s_df["TOTALAMOUNT"].sum()
    s_err   = round(s_all["ISERROR"].astype(bool).sum() / max(len(s_all),1)*100, 1)
    lat = s_df["LATITUDE"].dropna().mean()
    lon = s_df["LONGITUDE"].dropna().mean()
    if pd.isna(lat):
        ll = s_cp[["LATITUDE","LONGITUDE"]].dropna()
        if len(ll): lat, lon = ll.iloc[0]["LATITUDE"], ll.iloc[0]["LONGITUDE"]
    if pd.isna(lat): continue
    color = [143,203,62,220] if s_util>=target_util else ([168,113,10,210] if s_util>=target_util-10 else [193,68,62,220])
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
            st.markdown(f"**Utilization by Station vs {target_util}% target**")
            for _, r in map_df.sort_values("util_pct", ascending=False).iterrows():
                u = r["util_pct"]; g = u - target_util
                bc = "#8FCB3E" if u>=target_util else ("#A8710A" if u>=target_util-10 else "#C1443E")
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
c1,c2,c3 = st.columns(3)
with c1:
    st.markdown("**Sessions by Hour of Day**")
    h = df.groupby("HOUR").size().reset_index(name="Sessions")
    if len(h): st.bar_chart(h.set_index("HOUR"), color="#BEFF6C", height=200)
with c2:
    st.markdown("**Energy (kWh) by Charge Type**")
    ct = df.groupby("CHARGE_TYPE")["ENERGY_KWH"].sum().reset_index()
    ct.columns = ["Charge Type","kWh"]
    if len(ct): st.bar_chart(ct.set_index("Charge Type"), color="#8FCB3E", height=200)
with c3:
    st.markdown("**Payment Method Mix**")
    pm = df_all.groupby("PAYMENT_METHOD").size().reset_index(name="Count")
    if len(pm): st.bar_chart(pm.set_index("PAYMENT_METHOD"), color="#000000", height=200)

# ── SITE PERFORMANCE TABLE ───────────────────────────────────────────────────
st.markdown("<div class='sec-hdr'>Site Performance — Energy Utilization vs Capacity</div>",
            unsafe_allow_html=True)
if len(map_df):
    tbl = map_df[["STATIONNAME","util_pct","energy_kwh","avail_kwh",
                   "sessions","revenue","error_rate"]].copy()
    tbl["gap_pp"] = (tbl["util_pct"] - target_util).round(1)
    tbl["action"] = tbl["util_pct"].apply(
        lambda u: "✅ Expand" if u>=target_util
        else ("🟡 Monitor" if u>=target_util-10
        else ("⚠️ Optimize" if u>=target_util-25 else "🔴 Review")))
    tbl = tbl.rename(columns={
        "STATIONNAME":"Station","util_pct":"Util %","energy_kwh":"kWh Actual",
        "avail_kwh":"kWh Available","sessions":"Sessions",
        "revenue":"Revenue (₱)","error_rate":"Error %",
        "gap_pp":"Gap (pp)","action":"Action"
    }).sort_values("Util %", ascending=False)
    st.dataframe(tbl, use_container_width=True, hide_index=True)

# ── FINANCIALS (CPO breakdown table — network-wide, Company view only) ──────
if is_company:
    st.markdown("<div class='sec-hdr'>💰 Financials — Revenue & Operating Costs by CPO (Jan–Jun 2026)</div>",
                unsafe_allow_html=True)
    fd = fin_overall[["CPO","Revenue","ActualElecCost","ActualRent","EstIncome2026"]].copy()
    fd.columns = ["CPO / Station","Revenue (₱)","Elec Cost (₱)","Rent/Share (₱)","Est. Income 2026 (₱)"]
    for col in fd.columns[1:]:
        fd[col] = fd[col].apply(lambda x: f"₱{x:,.0f}" if pd.notna(x) and isinstance(x,(int,float)) else "—")
    st.dataframe(fd.dropna(subset=["CPO / Station"]), use_container_width=True, hide_index=True)

# ── USER SEGMENTS (charts — Company view only) ───────────────────────────────
if is_company:
    st.markdown("<div class='sec-hdr'>👤 User Segments</div>", unsafe_allow_html=True)
    br1,br2 = st.columns(2)
    with br1:
        st.markdown("**Car Brand Distribution (Top 10)**")
        if "CARBRAND" in ud.columns:
            brands = ud["CARBRAND"].value_counts().head(10).reset_index()
            brands.columns = ["Brand","Users"]
            st.bar_chart(brands.set_index("Brand"), color="#BEFF6C", height=200)
    with br2:
        st.markdown("**Plug Type Distribution**")
        if "PLUG_TYPE" in ud.columns:
            plugs = ud["PLUG_TYPE"].value_counts().reset_index()
            plugs.columns = ["Plug Type","Users"]
            st.bar_chart(plugs.set_index("Plug Type"), color="#8FCB3E", height=200)

# ── HOST PARTNER CONNECTOR DETAIL ────────────────────────────────────────────
if not is_company:
    st.markdown(f"<div class='sec-hdr'>🔌 Connector Detail — {sel_stations[0]}</div>",
                unsafe_allow_html=True)
    site_cps = cp[cp["STATIONNAME"]==sel_stations[0]].drop_duplicates("CHARGER_ID")
    if len(site_cps):
        cols = st.columns(min(len(site_cps),5))
        for i,(_, row) in enumerate(site_cps.iterrows()):
            if i>=5: break
            sc = "#4F7A1E" if row.get("NETWORK_STATUS")=="Online" else "#C1443E"
            cs = row.get("CONNECTOR_STATUS","—")
            cs_col = "#4F7A1E" if cs=="Available" else ("#000000" if cs=="Charging" else "#C1443E")
            cp_sess = df[df["CHARGER_ID"]==row["CHARGER_ID"]]
            cp_kwh  = cp_sess["ENERGY_KWH"].sum()
            cp_avail = row.get("CAPACITY_KW",0) * op_hours * days
            cp_util  = round(cp_kwh/cp_avail*100,1) if cp_avail>0 else 0
            cols[i].markdown(
                f"<div style='background:white;border-radius:6px;padding:11px;"
                f"border-top:3px solid {sc};box-shadow:0 1px 4px rgba(0,0,0,.07)'>"
                f"<div style='font-size:11px;font-weight:600;color:#000000'>{row['CHARGER_ID']}</div>"
                f"<div style='font-size:9px;color:#5C574D'>{row.get('CHARGER_TYPE','—')} · {row.get('CAPACITY_KW','—')}kW</div>"
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
