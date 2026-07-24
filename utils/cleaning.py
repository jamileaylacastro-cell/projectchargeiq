"""
Cleaning + aggregation for transaction-level EV charging data.
Same rules as the analysis notebook (ForecastingModel_CD_v2.ipynb), factored
out so the Streamlit app and the notebook can both call the same logic.
"""

import pandas as pd


def clean_and_aggregate(
    source_df: pd.DataFrame,
    station_name: str,
    target_col: str = "Energy Consumed (kWh)",
    min_duration_minutes: int = 10,
    max_energy_kwh: float = 100,
    min_year: int = 2020,
):
    """Filter transaction-level rows for one station and return (df_ts, daily_series).
    Returns (None, None) if nothing survives the filters."""
    station_df = source_df[source_df["Charging Station Name"] == station_name].copy()
    if station_df.empty:
        return None, None

    station_df["Start Time"] = pd.to_datetime(
        station_df["Start Time"], format="%B %d, %Y %I:%M:%S %p", errors="coerce"
    )
    station_df["End Time"] = pd.to_datetime(
        station_df["End Time"], format="%B %d, %Y %I:%M:%S %p", errors="coerce"
    )
    station_df["Duration"] = pd.to_timedelta(station_df["Duration"], errors="coerce")

    station_df = station_df.dropna(subset=["Start Time", "End Time", "Duration"])
    if station_df.empty:
        return None, None

    station_df = station_df[station_df["Start Time"].dt.year >= min_year]
    station_df = station_df[station_df["End Time"].dt.year >= min_year]
    station_df = station_df[station_df["End Time"] >= station_df["Start Time"]]
    station_df = station_df[station_df["Duration"] >= pd.Timedelta(minutes=min_duration_minutes)]

    if target_col == "Energy Consumed (kWh)":
        station_df = station_df[station_df[target_col] <= max_energy_kwh]
    elif target_col == "Amount":
        station_df[target_col] = (
            station_df[target_col].astype(str).str.replace(r"[₱,]", "", regex=True).astype(float)
        )

    if station_df.empty:
        return None, None

    df_ts = station_df.set_index("Start Time").sort_index()
    daily_series = df_ts[target_col].resample("D").sum()

    return df_ts, daily_series
