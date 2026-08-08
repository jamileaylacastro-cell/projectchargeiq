import pandas as pd
import io
import numpy as np


def load_dashboard_data(tx_b, cp_b, sp_b, ud_b, wt_b, fin_b):
    """Load and clean dashboard datasets from raw uploaded bytes."""
    try:
        tx = pd.read_excel(io.BytesIO(tx_b))
    except Exception:
        try:
            tx = pd.read_csv(io.BytesIO(tx_b))
        except Exception as e:
            raise ValueError(f"Failed to parse transactions file as Excel or CSV: {e}")

    cp = pd.read_excel(io.BytesIO(cp_b))
    sp = pd.read_excel(io.BytesIO(sp_b))
    ud = pd.read_excel(io.BytesIO(ud_b))
    wt = pd.read_excel(io.BytesIO(wt_b))
    fin = pd.read_excel(io.BytesIO(fin_b), sheet_name=None)

    tx["STARTTIME"] = pd.to_datetime(tx["STARTTIME"], errors="coerce")
    tx["ENDTIME"] = pd.to_datetime(tx["ENDTIME"], errors="coerce")
    tx = tx[tx["STARTTIME"].dt.year > 2020].copy()
    tx["DATE"] = tx["STARTTIME"].dt.date
    tx["MONTH"] = tx["STARTTIME"].dt.to_period("M")
    tx["HOUR"] = tx["STARTTIME"].dt.hour
    tx["DURATION_MIN"] = (tx["ENDTIME"] - tx["STARTTIME"]).dt.total_seconds() / 60

    _dur_bad = (tx["DURATION_MIN"] < 0) | (tx["DURATION_MIN"] > 1440)
    dur_excluded_count = int(_dur_bad.sum())
    tx.loc[_dur_bad, "DURATION_MIN"] = np.nan

    sp_coords = sp.groupby("STATIONNAME")[["LATITUDE", "LONGITUDE", "BUSINESS_START", "BUSINESS_END", "RATE_PER_KWH"]].first().reset_index()
    cp = cp.merge(sp_coords[["STATIONNAME", "BUSINESS_START", "BUSINESS_END"]], on="STATIONNAME", how="left")

    cp_coords = cp.groupby("STATIONNAME")[["LATITUDE", "LONGITUDE"]].first().reset_index()
    tx = tx.merge(cp_coords, on="STATIONNAME", how="left")

    sp_ll = sp.groupby("STATIONNAME")[["LATITUDE", "LONGITUDE"]].first().reset_index()
    missing_ll = tx["LATITUDE"].isna()
    tx_miss = tx[missing_ll].drop(columns=["LATITUDE", "LONGITUDE"]).merge(
        sp_ll, on="STATIONNAME", how="left")
    tx.loc[missing_ll, "LATITUDE"] = tx_miss["LATITUDE"].values
    tx.loc[missing_ll, "LONGITUDE"] = tx_miss["LONGITUDE"].values

    cp_cap = cp[
        cp["PLUG_TYPE"].notna() &
        (cp["PLUG_TYPE"].astype(str).str.strip() != "") &
        cp["CAPACITY_KW"].notna() &
        (cp["CAPACITY_KW"] > 0)
    ].copy()
    cp_excluded_count = len(cp) - len(cp_cap)

    fin_overall = fin["OVERALL"].dropna(subset=["CPO"]).copy()
    fin_overall.columns = ["CPO", "Revenue", "ActualElecCost", "EstElecCost",
                            "ActualRent", "EstRent", "EstIncome2026"]
    fin_overall = fin_overall[fin_overall["CPO"] != "SUB TOTAL:"].copy()

    opex = fin["ACTUAL OPEX (JAN-JUN)"].copy()
    opex.columns = ["CPO", "ElecJan", "ElecFeb", "ElecMar", "ElecApr", "ElecMay", "ElecJun",
                    "RentJan", "RentFeb", "RentMar", "RentApr", "RentMay", "RentJun", "Remarks"]
    opex = opex[opex["CPO"].notna() & (opex["CPO"] != "CPO") & (opex["CPO"] != "CPO - JV")].copy()

    fees = fin["FEES AND ASSUMPTIONS"].dropna(subset=["CPO"]).copy()
    fees = fees[fees["CPO"] != "CPO - JV"].copy()

    capex = fin["CAPEX"][["SITES", "TOTAL CAPEX"]].dropna(subset=["SITES"]).copy()
    capex.columns = ["STATIONNAME", "TOTAL_CAPEX"]
    capex = capex[~capex["STATIONNAME"].isin(["CPO"])].copy()

    tx_station_set = set(tx["STATIONNAME"].dropna().unique())
    fin_costs = fin_overall[["CPO", "Revenue", "ActualElecCost", "ActualRent"]].rename(
        columns={"CPO": "STATIONNAME"})
    payback_ref = capex.merge(fin_costs, on="STATIONNAME", how="inner")
    payback_ref = payback_ref[payback_ref["STATIONNAME"].isin(tx_station_set)].copy()
    payback_ref = payback_ref[payback_ref["TOTAL_CAPEX"] > 0].copy()

    return (
        tx, cp, cp_cap, sp, ud, wt, fin_overall, opex, fees, capex,
        payback_ref, cp_excluded_count, dur_excluded_count
    )
