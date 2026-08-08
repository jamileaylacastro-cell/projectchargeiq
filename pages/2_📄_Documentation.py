import streamlit as st

st.markdown("## 📄 Project ChargeIQ — Documentation")
st.caption(
    "Reference for how the Dashboard and Forecasting Model pages work — what each metric "
    "means, what data they expect, and known limitations."
)
st.markdown("---")

tab_dash, tab_forecast = st.tabs(["📊 Dashboard", "🔮 Forecasting Model"])

# ── DASHBOARD TAB ─────────────────────────────────────────────────────────────
with tab_dash:
    st.markdown("### What it is")
    st.markdown(
        "Network-wide and per-site analytics for the EVOxCharge charging network: "
        "utilization, reliability, revenue, and customer KPIs, built from six bundled "
        "Excel exports. Data files are never committed to the repo — the app either finds "
        "them bundled alongside `chargeiq_app.py` (or in a `/data` subfolder) or asks you "
        "to upload them before it will render anything."
    )

    st.markdown("### Required data files")
    st.markdown(
        """
| File | Source | Key columns |
|---|---|---|
| `transactions.xlsx` | Session Logs export | `STATIONNAME`, `STARTTIME`, `ENDTIME`, `ENERGY_KWH`, `CHARGE_TYPE`, `ISERROR`, `TOTALAMOUNT`, `USERID`, `CHARGER_ID` |
| `Transactions_to_exclude.xlsx` | Optional exclusion list | Any columns overlapping with `transactions.xlsx`; rows matching on the shared columns are removed from the dashboard session data |
| `UserDetails.xlsx` | User Profile export | `ACCOUNT_STATUS`, `WALLET_BALANCE`, `CARBRAND`, `PLUG_TYPE` |
| `walletTransactions.xlsx` | Transaction Logs export | `TRANSACTION_DATE`, `REFUNDEDTRANSACTIONNO` |
| `Station_Profile.xlsx` | Station Profile export | `STATIONNAME`, `LATITUDE`, `LONGITUDE`, `BUSINESS_START`, `BUSINESS_END`, `RATE_PER_KWH`, `ADDRESS`, `STATION_ACTIVE` |
| `Charge_Point_Information_...xlsx` | Charge Point Info export | `STATIONNAME`, `CHARGER_ID`, `CHARGER_TYPE`, `PLUG_TYPE`, `CAPACITY_KW`, `NETWORK_STATUS`, `CONNECTOR_STATUS`, optional `RATE_PER_KWH` |
| `ProjectChargeIQ_Financials.xlsx` | Financials workbook | sheets: `OVERALL`, `ACTUAL OPEX (JAN-JUN)`, `FEES AND ASSUMPTIONS`, `CAPEX`; key columns include `CPO`, `Revenue`, `ActualElecCost`, `ActualRent`, `TOTAL CAPEX` |
"""
    )
    st.caption(
        "The transactions file is parsed as Excel first, with a fallback to CSV parsing "
        "if the upload is actually a `.csv` file saved with an `.xlsx` name."
    )

    st.markdown("### Optional excluded-transactions file")
    st.markdown(
        "Use `Transactions_to_exclude.xlsx` to remove rows from `transactions.xlsx` before "
        "the dashboard computes utilization, revenue, and reliability metrics. The app matches "
        "rows between the two files on whichever columns they share and excludes any exact "
        "matches found in the exclusion file."
    )

    st.markdown("### Two views")
    st.markdown(
        "- **🏢 Company / Ops** — network-wide, multiple stations at once (multiselect, "
        "up to all of them). Shows the geographic heatmap, financials table, and user "
        "segment charts.\n"
        "- **🏪 Host Partner Site** — one station at a time. Shows a Station Profile card, "
        "a payback tracker, and per-connector detail cards instead of the network-wide "
        "sections."
    )

    st.markdown("### Filters (sidebar)")
    st.markdown(
        "- **Stations** (Company view) or **Site** (Host Partner view)\n"
        "- **Month** — all KPIs are scoped to one selected month, compared against the "
        "prior month for MoM deltas\n"
        "- **Charge Type** — Quick Charge, Set Time, Set Energy, Continuous Charging, Set "
        "Amount\n"
        "- **Operating hrs/day** (8–24, or a *Use 24-hr capacity* override) — the "
        "denominator input for utilization\n"
        "- **Target Utilization %** — one network-wide slider in Company view, or a "
        "per-station remembered slider in Host Partner view. Default range 1–40%, default "
        "15%, reflecting published EV fast-charger utilization benchmarks (public chargers "
        "typically run 5–15%; ~15% is commonly cited as the threshold for economic "
        "viability)."
    )

    st.markdown("### Utilization formula")
    st.markdown(
        """
```
Utilization Rate (%) = Σ Actual kWh Charged ÷ Total Available Capacity × 100

Σ Actual kWh Charged     = ENERGY_KWH summed over sessions where ISERROR = 0
Total Available Capacity = Online Connectors × CAPACITY_KW × op_hours/day × active days
```
"""
    )
    st.caption(
        "Only connectors with a real PLUG_TYPE and CAPACITY_KW > 0 count as valid; of "
        "those, only ones with NETWORK_STATUS = Online contribute to available capacity "
        "for the period (offline connectors are still counted and shown, just excluded "
        "from the utilization denominator)."
    )

    st.markdown("### KPI sections")
    st.markdown(
        "- **Utilization** — Network Utilization %, Actual kWh Charged, Avg Session "
        "Duration, Total Sessions\n"
        "- **Reliability** — Charger Uptime %, Chargers Offline, Faulty Connectors, Error "
        "Session Rate\n"
        "- **Revenue** — Total Revenue, Avg Revenue/Session, Refund Rate, Overstay Fee "
        "Revenue\n"
        "- **Customer** — Company view: Registered Users, Active Users, Repeat Customer "
        "Rate, Avg Wallet Balance. Host Partner view: Unique Customers, Repeat Customer "
        "Rate, Avg Revenue/Customer, Top Payment Method."
    )
    st.caption(
        "Session durations with a corrupted ENDTIME (defaulting to a placeholder date, "
        "producing a negative or implausible duration) are excluded from Avg Session "
        "Duration only — their revenue, energy, and session counts still count everywhere "
        "else."
    )

    st.markdown("### Other sections")
    st.markdown(
        "- **📍 Geographic Heatmap** (Company view) — a PyDeck map (heatmap or bubble "
        "mode) of utilization by station location, using the free CARTO basemap (no "
        "Mapbox token needed), plus a ranked utilization bar list.\n"
        "- **Site Performance table** — every selected station's utilization, energy, "
        "revenue, and error rate, with an action tag (✅ Expand / 🟡 Monitor / ⚠️ "
        "Optimize / 🔴 Review) whose thresholds scale with the current target utilization.\n"
        "- **💰 Financials** (Company view) — revenue and operating costs by CPO, reported "
        "directly from the Financials workbook (not reconciled against the "
        "transaction-based Revenue KPIs shown elsewhere).\n"
        "- **👤 User Segments** (Company view) — car brand and plug type distribution "
        "charts.\n"
        "- **💰 Site Payback Tracker** (Host Partner view) — CapEx recovery % for the "
        "selected station, computed from Jan–Jun 2026 transaction revenue minus "
        "electricity/rent costs, only available for stations whose Financials-workbook "
        "name matches an actual station in the session data.\n"
        "- **🔌 Connector Detail** (Host Partner view) — per-charger cards (grouped from "
        "connector-level rows) showing status, utilization, kWh, and sessions."
    )

# ── FORECASTING MODEL TAB ─────────────────────────────────────────────────────
with tab_forecast:
    st.markdown("### What it is")
    st.markdown(
        "Time-series forecasting of EV charging demand — the target variable is always "
        "**ENERGY_KWH** (Amount/revenue forecasting is explicitly out of scope). It answers "
        "two business questions: *which sites are performing well and will keep performing "
        "well* (revenue/payback outlook), and *which sites can be improved* to increase "
        "usage or demand."
    )

    st.markdown("### Data source")
    st.markdown(
        "A transactions-format workbook — the same schema as the dashboard's own "
        "`transactions.xlsx`. The page reads it with its own sidebar uploader, not the "
        "dashboard's bundled files, since the two pages don't share loaded data."
    )
    st.markdown(
        """
| Column | Description |
|---|---|
| `STATIONNAME` | Station identifier — one model is fit per selected station |
| `STARTTIME` / `ENDTIME` | Session start/end timestamps |
| `ENERGY_KWH` | Target variable — energy delivered during the session |
| `CHARGE_TYPE` | Session/charge mode filter used by the dashboard schema |
| `ISERROR` | Error flag for excluding invalid sessions from utilization and revenue |
| `TOTALAMOUNT` | Revenue per session, used for revenue KPIs in the dashboard schema |
| `USERID` | Customer identifier used for repeat-customer and active-user metrics |
| `CHARGER_ID` | Connector-level session grouping for the Site view |
| *(derived)* `Duration` | `ENDTIME − STARTTIME`, computed before the cleaning checks run — not a source column |
"""
    )
    st.caption(
        "The header-row setting in the sidebar defaults to 0 (headers on the first row), "
        "since that's how the transactions sheet is formatted — adjust it if a future "
        "export shifts the header position."
    )

    st.markdown("### Cleaning rules (`utils/cleaning.py`, editable in the sidebar)")
    st.markdown(
        """
| Rule | Default | Rationale |
|---|---|---|
| Minimum session duration | 10 minutes | Drops accidental plug-ins / near-instant disconnects |
| Maximum kWh per session | 100 kWh | Caps implausible single-session outliers (data errors, meter glitches) |
| Minimum valid year | 2020 | Drops corrupted/placeholder dates |
| Row validity | n/a | Drops unparseable Start/End Time, or End Time before Start Time |
"""
    )
    st.markdown(
        "After filtering, sessions for a station are indexed by `STARTTIME` and resampled "
        "to a **daily total** (days with zero sessions become 0, not missing) — that daily "
        "series is what every model trains on. Cleaning and aggregation always happen "
        "per-station, never across the whole file."
    )

    st.markdown("### Models")
    st.markdown(
        """
| Model | Type | How it forecasts |
|---|---|---|
| ETS Additive | Statistical (Holt-Winters) | Additive trend + weekly seasonality + error components |
| SARIMA | Statistical (`pmdarima.auto_arima`) | Auto-searches (p,d,q)(P,D,Q,7) seasonal ARIMA orders |
"""
    )
    st.markdown(
        "Both return an 80% uncertainty interval (P10–P90), sourced differently per model: "
        "ETS Additive simulates 250 future scenarios and takes the 10th/90th percentile at "
        "each date; SARIMA uses `pmdarima`'s built-in confidence interval (`alpha=0.2`)."
    )

    st.markdown("### Accuracy Check (backtest) & diagnostics")
    st.markdown(
        "Holds out the last *N* days (sidebar slider, default 30) as a test set, fits the "
        "chosen model on everything before that, and reports **RMSE** and **MAE** (in kWh) "
        "against what actually happened. The Residuals tab (available after running a "
        "backtest) adds ACF/PACF plots, a Q-Q plot, and a Ljung-Box test on the backtest "
        "residuals."
    )
    st.markdown(
        "- **RMSE** penalizes large misses more heavily (useful for flagging a model "
        "that's usually fine but occasionally badly wrong)\n"
        "- **MAE** is the average absolute miss — easier to explain (\"off by about X "
        "kWh/day on average\")"
    )

    st.markdown("### Results — ETS Additive vs. SARIMA")
    st.markdown(
        "Backtested head-to-head across 30 stations, the two models are close to evenly "
        "matched:"
    )
    st.markdown(
        """
| Model | Times it won (of 30) | Mean win margin | Median win margin |
|---|---|---|---|
| SARIMA | 16 | 6.1% | 6.1% |
| ETS Additive | 14 | 9.8% | 4.3% |
"""
    )
    st.caption(
        "Margins are thin in both directions — several stations are decided by under 1% "
        "RMSE difference, well within month-to-month noise. A handful of stations show a "
        "clearly decisive margin (e.g. one site favored ETS Additive by 33%, another "
        "favored SARIMA by 16.5%), but no consistent site characteristic predicts which "
        "model wins at a new station. **Practical recommendation:** use the Accuracy Check "
        "tab to backtest both for a given station before trusting either forecast; treat "
        "results within ~5% as comparable rather than picking a universal winner."
    )

    st.markdown("### App layout")
    st.markdown(
        "- **Sidebar** — upload workbook, header row, station, model choice, cleaning "
        "thresholds, backtest holdout length, forecast horizon\n"
        "- **Station Profile panel** — computed from the same *cleaned* data the model "
        "trains on (not raw transactions), so it stays consistent with whatever cleaning "
        "thresholds are set. Includes Number of Charging Points (distinct "
        "`CONNECTOR_NUMBER` values), Charger Types (`CHARGE_TYPE`), and Plug Types "
        "(`AC_DC`) where those optional columns are present\n"
        "- **History tab** — daily trend chart with a 30-day rolling average\n"
        "- **Accuracy Check tab** — backtest RMSE/MAE with an 80% interval band\n"
        "- **Residuals tab** — diagnostics from the most recent backtest\n"
        "- **Forecast tab** — fits on the full clean history, projects forward by the "
        "chosen horizon, with a downloadable forecast CSV"
    )

    st.markdown("### Known limitations / open items")
    st.markdown(
        "- **No map yet** — wanted (matching the dashboard's geographic heatmap), but "
        "blocked on the source workbook having no Region/City/address/coordinate column. "
        "Station Profile shows *\"Not available in current dataset\"* for Region/City "
        "until that data exists upstream.\n"
        "- **No holiday features** — Philippine long-weekend/holiday demand effects aren't "
        "modeled in either the notebook or the app.\n"
        "- **Single train/test split** — the last-month holdout is one snapshot, not a "
        "rolling backtest across multiple periods; RMSE/MAE for a given station/model "
        "could shift with a different test window.\n"
        "- **Revenue forecasting is out of scope** — a future version could combine the "
        "kWh forecast with external kWh-rate data rather than forecasting Amount directly."
    )
