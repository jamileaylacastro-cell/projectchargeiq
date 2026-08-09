import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

from utils.cleaning import clean_and_aggregate
from utils.models import run_backtest, run_forward_forecast
from utils.summary import compute_station_summary
from utils.diagnostics import compute_residuals, acf_pacf_data, qq_plot_data, ljung_box_test

# Page config is set once by the router (chargeiq_app.py) before st.navigation
# runs this page — calling it again here would raise a StreamlitAPIException.

# ---------------------------------------------------------------------------
# Theme (aligned to the dashboard color palette)
# ---------------------------------------------------------------------------
ACCENT = "#BEFF6C"
BG = "#FFF4EC"
PANEL = "#FFFFFF"
GRID = "#EAE0D0"
TEXT = "#000000"
MUTED = "#5C574D"
MUTED_DARK = "#5C574D"
WARN = "#C1443E"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: {BG}; color: {TEXT}; }}
    .stApp {{ background-color: {BG}; }}
    section[data-testid="stSidebar"] {{ background-color: #000000; }}
    section[data-testid="stSidebar"] * {{ color: #FFF4EC!important; }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {{ color: {ACCENT}!important; }}
    .cq-header {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; letter-spacing: 0.15em;
        color: {MUTED}; text-transform: uppercase; margin-bottom: -6px; }}
    .cq-title {{ font-size: 30px; font-weight: 700; color: {TEXT}; margin-top: 0; }}
    .cq-metric-box {{ background-color: {PANEL}; border: 1px solid {GRID}; border-left: 3px solid {ACCENT}; border-radius: 4px; padding: 14px 18px; }}
    .cq-metric-label {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.08em; }}
    .cq-metric-value {{ font-family: 'JetBrains Mono', monospace; font-size: 24px; font-weight: 700; color: {TEXT}; }}
    .cq-section-label {{ font-family: 'JetBrains Mono', monospace; font-size: 12px; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.1em; margin: 1.2rem 0 0.4rem 0; }}
    div[data-testid="stTabs"] button {{ font-family: 'JetBrains Mono', monospace; font-size: 13px; }}
    hr {{ border-color: {GRID}; }}

    /* Widget styling to match the dashboard page */
    span[data-baseweb="tag"], div[data-baseweb="tag"] {{ background-color:{ACCENT}!important; border-color:#000000!important; }}
    span[data-baseweb="tag"] *, div[data-baseweb="tag"] * {{ color:#000000!important; }}
    span[data-baseweb="tag"] svg, div[data-baseweb="tag"] svg {{ fill:#000000!important; }}
    div[data-baseweb="select"] > div {{ border-color:{GRID}!important; background:#FFFFFF!important; outline:none!important; }}
    div[data-baseweb="select"] > div * {{ color:#000000!important; }}
    div[data-baseweb="select"]:focus-within > div,
    div[data-baseweb="select"] > div:focus,
    div[data-baseweb="select"] > div:focus-within {{ border-color:{ACCENT}!important; box-shadow:0 0 0 1px {ACCENT}!important; background:#FFFFFF!important; outline:none!important; }}
    div[data-baseweb="select"] input {{ outline:none!important; box-shadow:none!important; }}
    div[data-baseweb="select"] input::selection {{ background:{ACCENT}!important; color:#000000!important; }}
    div[data-baseweb="popover"], div[data-baseweb="menu"] {{ background:#FFFFFF!important; }}
    div[data-baseweb="popover"] *, div[data-baseweb="menu"] * {{ color:#000000!important; }}
    div[data-baseweb="popover"] li, div[data-baseweb="menu"] li {{ background:#FFFFFF!important; }}
    div[data-baseweb="popover"] li:hover, div[data-baseweb="menu"] li:hover,
    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="menu"] li[aria-selected="true"] {{ background-color:{ACCENT}!important; }}
    div[data-baseweb="popover"] li:hover *, div[data-baseweb="menu"] li:hover *,
    div[data-baseweb="popover"] li[aria-selected="true"] *,
    div[data-baseweb="menu"] li[aria-selected="true"] * {{ color:#000000!important; }}
    input[type="checkbox"], input[type="radio"] {{ accent-color:{ACCENT}!important; }}
    div[data-testid="stSlider"] div[role="slider"] {{ background-color:#000000!important; border-color:#000000!important; }}
    button[kind="primary"] {{ background-color:{ACCENT}!important; border-color:#000000!important; }}
    button[kind="primary"] * {{ color:#000000!important; }}
    button[kind="secondary"] {{ border-color:#000000!important; background:#FFFFFF!important; }}
    button[kind="secondary"] * {{ color:#000000!important; }}
    div[data-testid="stFileUploader"] section {{ background:#FFFFFF!important; border:1px dashed #000000!important; }}
    div[data-testid="stFileUploader"] section * {{ color:#000000!important; }}
    div[data-testid="stFileUploader"] section small {{ color:{MUTED}!important; }}
    div[data-testid="stFileUploaderDropzoneInstructions"] * {{ color:#000000!important; }}
    div[data-testid="stFileUploader"] button {{ background:{ACCENT}!important; color:#000000!important; border-color:#000000!important; }}
    div[data-testid="stFileUploader"] button * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] input {{ color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-baseweb="popover"] *,
    section[data-testid="stSidebar"] div[data-baseweb="menu"] * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] span[data-baseweb="tag"] *,
    section[data-testid="stSidebar"] div[data-baseweb="tag"] * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-testid="stFileUploader"] section * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] button[kind="primary"] * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] button[kind="secondary"] * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] input::selection {{ background:{ACCENT}!important; color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] * {{ color:#000000!important; }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label,
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label *,
    section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] label,
    section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] label * {{ color:#FFF4EC!important; }}
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{ background:#FFFFFF!important; }}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_summary_table(summary: dict):
    rows_html = "".join(
        f"<tr>"
        f"<td style='padding:9px 16px; font-weight:600; border-bottom:1px solid {GRID}; width:40%; color:{TEXT};'>{k}</td>"
        f"<td style='padding:9px 16px; border-bottom:1px solid {GRID}; color:{MUTED};'>{v}</td>"
        f"</tr>"
        for k, v in summary.items()
    )
    st.markdown(
        f"""
        <div style="background-color:{PANEL}; border:1px solid {GRID}; border-radius:6px; overflow:hidden; margin-bottom:1rem;">
        <table style="width:100%; border-collapse:collapse; font-family:'JetBrains Mono', monospace; font-size:13px;">
        {rows_html}
        </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_base_layout(fig, height=440):
    fig.update_layout(
        height=height, plot_bgcolor=PANEL, paper_bgcolor=PANEL,
        font=dict(family="JetBrains Mono, monospace", color=TEXT, size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    )
    return fig


@st.cache_data
def load_workbook(file, header_row):
    return pd.read_excel(file, header=header_row)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.markdown("<div class='cq-header'>PROJECT CHARGEIQ</div>", unsafe_allow_html=True)
st.sidebar.markdown("### 🔮 Forecasting Control Panel")

uploaded = st.sidebar.file_uploader(
    "Station monitoring workbook (.xlsx)", type=["xlsx"],
    help="Transactions sheet with STATIONNAME, STARTTIME, ENDTIME, and ENERGY_KWH columns "
         "(same schema as the dashboard's transactions.xlsx). Duration is computed automatically.",
)
header_row = st.sidebar.number_input(
    "Header row (0-indexed)", min_value=0, max_value=20, value=0,
    help="Row where the actual column headers start in the sheet. The transactions sheet "
         "has headers on the first row (0), so that's the default — adjust if a future "
         "export shifts them.",
)

# Automatically reuse the dashboard's uploaded transactions file when available.
dashboard_tx_bytes = None
if "chargeiq_file_bytes" in st.session_state:
    dashboard_tx_bytes = st.session_state.chargeiq_file_bytes.get("transactions")

if uploaded is None and dashboard_tx_bytes is not None:
    st.sidebar.info("No forecasting upload detected — using the dashboard's uploaded transactions file.")
    uploaded = io.BytesIO(dashboard_tx_bytes)

if uploaded is None:
    st.sidebar.info("Upload the station monitoring workbook to get started.")
    st.markdown("<div class='cq-header'>EV CHARGING · MODEL SELECTOR</div>", unsafe_allow_html=True)
    st.markdown("<div class='cq-title'>Waiting for data</div>", unsafe_allow_html=True)
    st.info("Upload your station monitoring `.xlsx` file in the sidebar to begin.")
    st.stop()

raw = load_workbook(uploaded, header_row)
# Duration is derived (ENDTIME - STARTTIME), not a column in the source file,
# so it's not required here.
required_cols = {"STATIONNAME", "STARTTIME", "ENDTIME", "ENERGY_KWH"}
missing = required_cols - set(raw.columns)
if missing:
    st.error(f"The uploaded file is missing expected columns: {sorted(missing)}. Check the header row setting.")
    st.stop()

target_column = "ENERGY_KWH"  # kWh is the only supported target (Amount was dropped as an option)

stations = sorted(raw["STATIONNAME"].dropna().unique())
selected_station = st.sidebar.selectbox("Charging station", stations)

model_choice = st.sidebar.radio("Forecasting model", ["ETS Additive", "SARIMA"])

st.sidebar.markdown("---")
st.sidebar.markdown("##### Cleaning rules")
min_duration = st.sidebar.number_input("Min session duration (minutes)", min_value=0, value=10)
max_energy = st.sidebar.number_input("Max kWh per session (outlier cap)", min_value=1, value=100)
min_year = st.sidebar.number_input("Earliest valid year", min_value=2000, max_value=2100, value=2020)

st.sidebar.markdown("---")
st.sidebar.markdown("##### Forecast settings")
backtest_days = st.sidebar.slider("Backtest holdout (days)", 7, 60, 30)
forecast_horizon = st.sidebar.slider("Forecast horizon (days ahead)", 7, 90, 30)

# ---------------------------------------------------------------------------
# Clean + aggregate for the selected station
# ---------------------------------------------------------------------------
df_ts, daily_series = clean_and_aggregate(
    raw, selected_station, target_col=target_column,
    min_duration_minutes=min_duration, max_energy_kwh=max_energy, min_year=min_year,
)

st.markdown("<div class='cq-header'>EV CHARGING · MODEL SELECTOR</div>", unsafe_allow_html=True)
st.markdown(f"<div class='cq-title'>{selected_station}</div>", unsafe_allow_html=True)

if daily_series is None or daily_series.dropna().shape[0] < backtest_days + 30:
    n = 0 if daily_series is None else daily_series.dropna().shape[0]
    st.warning(
        f"Not enough clean data for this station after filtering ({n} days). "
        f"Need at least {backtest_days + 30} days for a {backtest_days}-day backtest. "
        "Try a different station, or loosen the cleaning rules in the sidebar."
    )
    st.stop()

station_summary = compute_station_summary(df_ts, daily_series, selected_station, target_col=target_column)
if station_summary is not None:
    st.markdown("<div class='cq-section-label'>Station Profile — based on cleaned modeling data</div>",
                unsafe_allow_html=True)
    render_summary_table(station_summary)
    if station_summary["Region/City"] == "Not available in current dataset":
        st.caption(
            "No Region/City column was found in this workbook, so that field can't be populated yet. "
            "Map integration is on hold until location data (region, address, or coordinates) is available."
        )

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='cq-metric-box'><div class='cq-metric-label'>Clean days</div>"
            f"<div class='cq-metric-value'>{daily_series.dropna().shape[0]}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='cq-metric-box'><div class='cq-metric-label'>Date range</div>"
            f"<div class='cq-metric-value' style='font-size:15px;'>{daily_series.index.min().date()} → "
            f"{daily_series.index.max().date()}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='cq-metric-box'><div class='cq-metric-label'>Avg daily {target_column.split(' ')[0]}</div>"
            f"<div class='cq-metric-value'>{daily_series.mean():,.1f}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='cq-metric-box'><div class='cq-metric-label'>Model</div>"
            f"<div class='cq-metric-value'>{model_choice}</div></div>", unsafe_allow_html=True)

tab_trend, tab_backtest, tab_residuals, tab_forecast = st.tabs(
    ["📈 HISTORY", "🎯 ACCURACY CHECK", "🔬 RESIDUALS", "🔮 FORECAST"]
)

# ---------------------------------------------------------------------------
with tab_trend:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_series.index, y=daily_series, mode="lines",
                              line=dict(color=ACCENT, width=1.5), name=target_column))
    roll = daily_series.rolling(30).mean()
    fig.add_trace(go.Scatter(x=daily_series.index, y=roll, mode="lines",
                              line=dict(color=TEXT, width=2, dash="dot"), name="30d avg"))
    fig.update_layout(title=f"Daily {target_column} — {selected_station}")
    st.plotly_chart(plotly_base_layout(fig), use_container_width=True)
    st.dataframe(daily_series.tail(15).rename(target_column), use_container_width=True, height=220)

# ---------------------------------------------------------------------------
with tab_backtest:
    st.caption(
        f"Holds out the last {backtest_days} days, fits {model_choice} on everything before that, "
        "and checks the forecast against what actually happened."
    )
    if st.button("Run accuracy check", type="primary"):
        with st.spinner(f"Fitting {model_choice} and backtesting..."):
            try:
                result = run_backtest(daily_series, model_choice, test_days=backtest_days)
            except Exception as e:
                st.error(f"{model_choice} failed on this station's data: {e}")
                result = None
        st.session_state["backtest_result"] = result

    result = st.session_state.get("backtest_result")
    if result is not None:
        m1, m2 = st.columns(2)
        m1.markdown(f"<div class='cq-metric-box'><div class='cq-metric-label'>RMSE</div>"
                    f"<div class='cq-metric-value'>{result['rmse']:.2f}</div></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='cq-metric-box'><div class='cq-metric-label'>MAE</div>"
                    f"<div class='cq-metric-value'>{result['mae']:.2f}</div></div>", unsafe_allow_html=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=result["train"].index, y=result["train"], mode="lines",
                                   line=dict(color=MUTED, width=1), name="Training history"))
        fig2.add_trace(go.Scatter(x=result["test"].index, y=result["test"], mode="lines",
                                   line=dict(color=TEXT, width=2), name="Actual (holdout)"))
        fig2.add_trace(go.Scatter(
            x=list(result["point"].index) + list(result["point"].index[::-1]),
            y=list(result["upper"]) + list(result["lower"][::-1]),
            fill="toself", fillcolor="rgba(196,241,53,0.15)", line=dict(color="rgba(0,0,0,0)"),
            name="80% interval", showlegend=True,
        ))
        fig2.add_trace(go.Scatter(x=result["point"].index, y=result["point"], mode="lines",
                                   line=dict(color=ACCENT, width=2, dash="dash"), name=f"{model_choice} forecast"))
        fig2.update_layout(title=f"{model_choice} backtest — last {backtest_days} days")
        st.plotly_chart(plotly_base_layout(fig2), use_container_width=True)
    else:
        st.info("Click **Run accuracy check** to backtest this model against recent history.")

# ---------------------------------------------------------------------------
with tab_residuals:
    result = st.session_state.get("backtest_result")
    if result is None:
        st.info("Run the **Accuracy Check** tab first — residual diagnostics are computed from that backtest.")
    else:
        residuals = compute_residuals(result["test"], result["point"])
        if len(residuals) < 5:
            st.warning("Not enough overlapping backtest points to compute meaningful residual diagnostics.")
        else:
            st.caption(f"Diagnostics for the {result['model']} backtest ({len(residuals)} residual points).")

            # --- Residuals over time ---
            fig_resid = go.Figure()
            fig_resid.add_trace(go.Scatter(x=residuals.index, y=residuals, mode="lines+markers",
                                            line=dict(color=ACCENT, width=1.5), marker=dict(size=4),
                                            name="Residual (actual − predicted)"))
            fig_resid.add_hline(y=0, line=dict(color=MUTED, width=1, dash="dash"))
            fig_resid.update_layout(title="Residuals over time")
            st.plotly_chart(plotly_base_layout(fig_resid, height=340), use_container_width=True)

            col_a, col_b = st.columns(2)

            # --- Residual distribution ---
            with col_a:
                fig_hist = go.Figure()
                fig_hist.add_trace(go.Histogram(x=residuals, marker=dict(color=ACCENT), nbinsx=20))
                fig_hist.update_layout(title="Residual distribution")
                st.plotly_chart(plotly_base_layout(fig_hist, height=320), use_container_width=True)

            # --- Q-Q plot ---
            with col_b:
                osm, osr, line_x, line_y = qq_plot_data(residuals)
                fig_qq = go.Figure()
                fig_qq.add_trace(go.Scatter(x=osm, y=osr, mode="markers",
                                             marker=dict(color=ACCENT, size=5), name="Residuals"))
                fig_qq.add_trace(go.Scatter(x=line_x, y=line_y, mode="lines",
                                             line=dict(color=TEXT, width=1.5, dash="dash"), name="Reference line"))
                fig_qq.update_layout(title="Q-Q plot (vs. normal)",
                                      xaxis_title="Theoretical quantiles", yaxis_title="Sample quantiles")
                st.plotly_chart(plotly_base_layout(fig_qq, height=320), use_container_width=True)

            # --- ACF / PACF ---
            acf_data = acf_pacf_data(residuals, max_lags=20)
            if acf_data is not None:
                col_c, col_d = st.columns(2)
                with col_c:
                    fig_acf = go.Figure()
                    fig_acf.add_trace(go.Bar(x=acf_data["lags"], y=acf_data["acf"], marker=dict(color=ACCENT)))
                    band = acf_data["acf_band"][0]
                    fig_acf.add_hline(y=band, line=dict(color=MUTED, width=1, dash="dot"))
                    fig_acf.add_hline(y=-band, line=dict(color=MUTED, width=1, dash="dot"))
                    fig_acf.update_layout(title="ACF of residuals", xaxis_title="Lag")
                    st.plotly_chart(plotly_base_layout(fig_acf, height=300), use_container_width=True)
                with col_d:
                    fig_pacf = go.Figure()
                    fig_pacf.add_trace(go.Bar(x=acf_data["lags"], y=acf_data["pacf"], marker=dict(color=ACCENT)))
                    band_p = acf_data["pacf_band"][0]
                    fig_pacf.add_hline(y=band_p, line=dict(color=MUTED, width=1, dash="dot"))
                    fig_pacf.add_hline(y=-band_p, line=dict(color=MUTED, width=1, dash="dot"))
                    fig_pacf.update_layout(title="PACF of residuals", xaxis_title="Lag")
                    st.plotly_chart(plotly_base_layout(fig_pacf, height=300), use_container_width=True)
                st.caption(
                    "Dotted lines mark the ~95% significance band. Bars poking outside the band suggest "
                    "leftover autocorrelation the model didn't capture."
                )

            # --- Ljung-Box test ---
            lb = ljung_box_test(residuals, max_lags=10)
            if not lb.empty:
                st.markdown("<div class='cq-section-label'>Ljung-Box test (autocorrelation check)</div>",
                            unsafe_allow_html=True)
                st.dataframe(lb.style.format({"lb_stat": "{:.3f}", "lb_pvalue": "{:.4f}"}),
                             use_container_width=True, height=min(300, 40 + 35 * len(lb)))
                st.caption(
                    "A p-value below 0.05 at a given lag suggests the residuals still have autocorrelation "
                    "at that lag — i.e. the model left some structure on the table. All p-values comfortably "
                    "above 0.05 is a good sign."
                )

# ---------------------------------------------------------------------------
with tab_forecast:
    st.caption(f"Fits {model_choice} on the full clean history and projects {forecast_horizon} days forward.")
    if st.button("⚡ Generate forecast", type="primary"):
        with st.spinner(f"Fitting {model_choice} on full history..."):
            try:
                fc = run_forward_forecast(daily_series, model_choice, forecast_horizon)
            except Exception as e:
                st.error(f"{model_choice} failed on this station's data: {e}")
                fc = None
        st.session_state["forecast_result"] = fc

    fc = st.session_state.get("forecast_result")
    if fc is not None:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=daily_series.index, y=daily_series, mode="lines",
                                   line=dict(color=MUTED, width=1), name="History"))
        fig3.add_trace(go.Scatter(
            x=list(fc["point"].index) + list(fc["point"].index[::-1]),
            y=list(fc["upper"]) + list(fc["lower"][::-1]),
            fill="toself", fillcolor="rgba(196,241,53,0.15)", line=dict(color="rgba(0,0,0,0)"),
            name="80% interval", showlegend=True,
        ))
        fig3.add_trace(go.Scatter(x=fc["point"].index, y=fc["point"], mode="lines+markers",
                                   line=dict(color=ACCENT, width=3), marker=dict(size=4),
                                   name=f"{model_choice} forecast (+{forecast_horizon}d)"))
        fig3.update_layout(title=f"{selected_station} — {forecast_horizon}-day forecast ({model_choice})")
        st.plotly_chart(plotly_base_layout(fig3), use_container_width=True)

        forecast_table = pd.DataFrame({
            "date": fc["point"].index, f"forecast_{target_column}": fc["point"].values,
            "lower_80": fc["lower"].values, "upper_80": fc["upper"].values,
        })
        st.dataframe(forecast_table, use_container_width=True, height=250)
        st.download_button(
            "Download forecast CSV", forecast_table.to_csv(index=False).encode("utf-8"),
            file_name=f"forecast_{selected_station}_{model_choice.replace(' ', '')}_{forecast_horizon}d.csv",
        )
    else:
        st.info("Click **Generate forecast** to project future demand for this station.")

# ── Dashboard Utilization Reference ─────────────────────────────────────────
if "chargeiq_file_bytes" in st.session_state:
    dashboard_files = st.session_state.chargeiq_file_bytes
    cp_bytes = dashboard_files.get("charge_points")
    sp_bytes = dashboard_files.get("station_profile")
    if cp_bytes is not None and sp_bytes is not None:
        try:
            cp_ref = pd.read_excel(io.BytesIO(cp_bytes))
            sp_ref = pd.read_excel(io.BytesIO(sp_bytes))
        except Exception:
            cp_ref = None
            sp_ref = None
        if cp_ref is not None and sp_ref is not None:
            station_cp = cp_ref[cp_ref["STATIONNAME"] == selected_station]
            station_sp = sp_ref[sp_ref["STATIONNAME"] == selected_station]
            if len(station_cp) and len(station_sp):
                online_capacity = station_cp[station_cp["NETWORK_STATUS"] == "Online"]["CAPACITY_KW"].sum()
                def _parse_time_minutes(val):
                    if pd.isna(val) or str(val).strip() == "":
                        return None
                    parsed = pd.to_datetime(str(val), errors="coerce")
                    return parsed.hour * 60 + parsed.minute if pd.notna(parsed) else None
                b_start = _parse_time_minutes(station_sp["BUSINESS_START"].iloc[0])
                b_end = _parse_time_minutes(station_sp["BUSINESS_END"].iloc[0])
                if b_start is not None and b_end is not None and b_start != b_end:
                    hours = (b_end - b_start) / 60
                    if hours <= 0:
                        hours += 24
                    capacity_kwh_per_day = online_capacity * hours
                    if capacity_kwh_per_day > 0:
                        util_series = daily_series / capacity_kwh_per_day * 100
                        util_fig = go.Figure()
                        util_fig.add_trace(go.Scatter(x=util_series.index, y=util_series,
                                                      mode="lines", line=dict(color=ACCENT, width=2),
                                                      name="Utilization %"))
                        util_fig.update_layout(title=f"Utilization Trend reference — {selected_station}",
                                               yaxis_title="Utilization %",
                                               xaxis_title="Date")
                        st.markdown("---")
                        st.markdown("### Dashboard Utilization Reference")
                        st.plotly_chart(plotly_base_layout(util_fig, height=320), use_container_width=True)
                        st.caption(
                            "This reference chart uses the dashboard's station profile and charge point "
                            "data to translate the selected site's daily kWh into an estimated daily utilization rate."
                        )
                    else:
                        st.info("Cannot compute utilization reference: selected station has no online capacity in the dashboard charge point data.")
                else:
                    st.info("Cannot compute utilization reference: selected station has invalid or missing business hours in the dashboard station profile.")
            else:
                st.info("Dashboard station profile / charge point data is available, but not for the selected station.")
        else:
            st.info("Dashboard station profile or charge point workbook could not be parsed for the utilization reference.")
    else:
        st.info("Load the dashboard's Station Profile and Charge Point information files for the utilization reference chart.")
else:
    st.info("Dashboard upload state is not available; the utilization reference chart requires the shared dashboard files.")
