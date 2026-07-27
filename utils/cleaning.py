"""
Cleaning + aggregation for transaction-level EV charging data.
Same rules as the analysis notebook (ForecastingModel_CD_v2.ipynb), factored
out so the Streamlit app and the notebook can both call the same logic.
"""

import pandas as pd


def clean_and_aggregate(
    source_df: pd.DataFrame,
    station_name: str,
    target_col: str = "ENERGY_KWH",
    min_duration_minutes: int = 10,
    max_energy_kwh: float = 100,
    min_year: int = 2020,
):
    """Filter transaction-level rows for one station and return (df_ts, daily_series).
    Returns (None, None) if nothing survives the filters."""
    station_df = source_df[source_df["STATIONNAME"] == station_name].copy()
    if station_df.empty:
        return None, None

    station_df["STARTTIME"] = pd.to_datetime(station_df["STARTTIME"], errors="coerce")
    station_df["ENDTIME"] = pd.to_datetime(station_df["ENDTIME"], errors="coerce")

    # Duration is no longer a column in the source file — derive it from
    # ENDTIME - STARTTIME before the existing duration-based checks run.
    station_df["Duration"] = station_df["ENDTIME"] - station_df["STARTTIME"]

    station_df = station_df.dropna(subset=["STARTTIME", "ENDTIME", "Duration"])
    if station_df.empty:
        return None, None

    station_df = station_df[station_df["STARTTIME"].dt.year >= min_year]
    station_df = station_df[station_df["ENDTIME"].dt.year >= min_year]
    station_df = station_df[station_df["ENDTIME"] >= station_df["STARTTIME"]]
    station_df = station_df[station_df["Duration"] >= pd.Timedelta(minutes=min_duration_minutes)]

    if target_col == "ENERGY_KWH":
        station_df = station_df[station_df[target_col] <= max_energy_kwh]
    elif target_col == "Amount":
        station_df[target_col] = (
            station_df[target_col].astype(str).str.replace(r"[₱,]", "", regex=True).astype(float)
        )

    if station_df.empty:
        return None, None

    df_ts = station_df.set_index("STARTTIME").sort_index()
    daily_series = df_ts[target_col].resample("D").sum()

    return df_ts, daily_series
