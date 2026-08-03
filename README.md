# EVOxCharge Analytics Dashboard

Built with Streamlit + PyDeck. Includes a **Forecasting Model** page (ETS Additive / SARIMA
demand forecasting) and a **Documentation** page alongside the main dashboard — the
dashboard is always the default landing page; the other two are reached via the sidebar
page nav.

## Setup

```bash
pip install -r requirements.txt
streamlit run chargeiq_app.py
```

## Required data files

Place these Excel files in the **same folder** as `chargeiq_app.py`
(or in a `/data` subfolder):

| File | Source |
|------|--------|
| `transactions.xlsx` | Session Logs export |
| `UserDetails.xlsx` | User Profile export |
| `walletTransactions.xlsx` | Transaction Logs export |
| `Station_Profile.xlsx` | Station Profile export |
| `Charge_Point_Information_...xlsx` | Charge Point Info export |
| `Financials.xlsx` | Financials workbook |

The **Forecasting Model** page (`pages/1_🔮_Forecasting.py`, routed as "Forecasting Model"
in the sidebar) is self-contained — it uses its own sidebar file uploader for a
transactions-format workbook (same schema as `transactions.xlsx` above: `STATIONNAME`,
`STARTTIME`, `ENDTIME`, `ENERGY_KWH`), rather than the bundled files above.

## Security — DO NOT commit data files to GitHub

Add `*.xlsx` to your `.gitignore` (already included here).
For deployment, use one of the options below.

## Deployment options

### Option A — Streamlit Community Cloud (recommended for sharing)
1. Push `chargeiq_app.py` (entry point), `dashboard.py`, `pages/`, `utils/`,
   `requirements.txt`, `.gitignore` to GitHub — deploy pointing at `chargeiq_app.py`
2. Upload data files as Streamlit Secrets or use a private Google Sheet
3. Deploy at share.streamlit.io

### Option B — Private GitHub repo + Streamlit Cloud
1. Make the GitHub repo **private**
2. Add all files including data
3. Streamlit Cloud can still deploy from private repos (free tier)

### Option C — Azure / internal hosting
For internal EVOxCharge use with access control.
