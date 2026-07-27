# Project ChargeIQ (EVOxCharge Analytics Dashboard)

Streamlit app with two pages: the main analytics **dashboard** (`chargeiq_app.py`, always
the default landing page) and a **Forecasting** page (`pages/1_🔮_Forecasting.py`) reached
via the sidebar nav, added via Streamlit's `pages/` auto-discovery convention. Run with:

```bash
pip install -r requirements.txt
streamlit run chargeiq_app.py
```

## Dashboard (`chargeiq_app.py`)

Reads 6 bundled Excel exports (transactions, user details, wallet transactions, station
profile, charge point info, financials — see README for the full list/schema). Data files
are gitignored; the app gates on upload-or-bundled-file before rendering. `load_all()`
tries Excel first and falls back to CSV parsing for the transactions file (some exports
come through as `.csv` content despite the `.xlsx` name).

## Forecasting page (`pages/1_🔮_Forecasting.py` + `utils/`)

Ported from a standalone prototype (`Forecasting Model` project) into this repo as a
second page. **Self-contained** — it has its own sidebar file uploader for a
station-monitoring workbook (still its own upload, separate from the dashboard's bundled
`transactions.xlsx`, but as of 2026-07-28 the same column names as the dashboard's
transactions sheet: `STATIONNAME` / `STARTTIME` / `ENDTIME` / `ENERGY_KWH`, header row still
configurable in the sidebar). `Duration` is no longer a source column — it's derived as
`ENDTIME - STARTTIME` in `clean_and_aggregate()` before the duration-based row filters run.

- `utils/cleaning.py` — `clean_and_aggregate()`: filters (min session duration, max kWh
  outlier cap, min valid year, drops bad rows), then resamples to a daily series per
  station. Same rules as the analysis notebook (`ForecastingModel_CD_v2.ipynb`).
- `utils/models.py` — ETS Additive (Holt-Winters) and SARIMA (`pmdarima.auto_arima`), each
  returning point forecast + 80% interval (P10/P90). Backtest = last-N-days holdout.
- `utils/summary.py` — Station Profile panel, computed from the same cleaned data the
  model trains on (not raw transactions), so profile numbers stay consistent with whatever
  cleaning thresholds are set. Three optional columns feed the panel if present:
  `CONNECTOR_NUMBER` → "Number of Charging Points" (count of distinct values for the
  station), `CHARGE_TYPE` → "Charger Types", `AC_DC` → "Plug Types" (both of the latter just
  list whatever distinct values exist for the station, no counts).
- `utils/diagnostics.py` — residual diagnostics (ACF/PACF, Q-Q, Ljung-Box) for the
  Accuracy Check backtest.

### Deliberate scope boundaries — not bugs

Per the model documentation (draft doc, ask the user if you need the full write-up):

- **Only kWh (Energy Consumed) is forecast, not Amount/revenue.** Explicitly out of scope
  for the capstone; a future revenue forecast would combine the kWh forecast with external
  kWh-rate data rather than forecasting Amount directly.
- **No map on the Forecasting page yet — wanted, not forgotten.** The team wants the same
  visual map the dashboard has, blocked on the station-monitoring workbook having no
  Region/City/address/coordinate column. Station Profile shows "Not available in current
  dataset" for Region/City until that's added upstream.
- **Neither ETS Additive nor SARIMA is hardcoded as "the" model.** Backtested across 30
  stations: SARIMA won 16/30 (mean margin 6.1%), ETS Additive won 14/30 (mean margin 9.8%);
  most margins are within noise. The app deliberately lets the user compare both per
  station via the Accuracy Check tab instead of picking a default.
- **No holiday features** (e.g. Philippine long-weekend demand effects) in either the
  notebook or the app — known open item.
- The notebook's train/test split is a single last-month holdout, not a rolling backtest.

## Collaboration notes

Repo has two active contributors: the user (via Claude Code, mostly the forecasting-page
integration and dashboard data-loading logic) and `jamileaylacastro-cell` (CSS/theming
polish on the Forecasting page's sidebar, plus the Excel/CSV fallback in
`chargeiq_app.py`'s `load_all()`). Check `git log` before assuming which parts of the CSS
or data-loading logic are current — both files have been edited post-integration.
