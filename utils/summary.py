"""
Station-level business summary stats (Station Profile panel).

Computed from the CLEANED, filtered data for a station -- the same `df_ts` /
`daily_series` produced by `clean_and_aggregate()` and used for modeling --
not the raw transaction log. This keeps the profile numbers consistent with
whatever cleaning rules are set in the sidebar (duration cutoff, kWh outlier
cap, minimum year), rather than mixing unfiltered totals with a filtered
forecast.
"""

import pandas as pd

# Column names to look for if the workbook happens to include a region/city field.
# None of these are guaranteed to be present in the schema shared so far.
REGION_COLUMN_CANDIDATES = ["Region/City", "Region", "City", "Location", "Site Region", "Region / City"]


def _find_region_column(columns) -> str | None:
    for cand in REGION_COLUMN_CANDIDATES:
        if cand in columns:
            return cand
    return None


def compute_station_summary(
    df_ts: pd.DataFrame,
    daily_series: pd.Series,
    station_name: str,
    target_col: str = "ENERGY_KWH",
):
    """Returns an ordered dict of label -> value for the Station Profile panel,
    built from already-cleaned data. Returns None if there's nothing to summarize.

    df_ts: the cleaned, station-filtered transaction-level dataframe (indexed by STARTTIME),
           as returned by clean_and_aggregate().
    daily_series: the cleaned daily-aggregated series for the same station/target, also from
                  clean_and_aggregate().
    """
    if df_ts is None or df_ts.empty or daily_series is None or daily_series.dropna().empty:
        return None

    first_date = df_ts.index.min()
    last_date = df_ts.index.max()
    duration_days = max((last_date - first_date).days, 1)
    duration_months = duration_days / 30.44

    total_sessions = len(df_ts)
    has_target = target_col in df_ts.columns
    total_energy = df_ts[target_col].sum() if has_target else None

    region_col = _find_region_column(df_ts.columns)
    region_value = None
    if region_col:
        vals = df_ts[region_col].dropna()
        region_value = vals.iloc[0] if not vals.empty else None

    n_points = df_ts["CONNECTOR_NUMBER"].nunique() if "CONNECTOR_NUMBER" in df_ts.columns else None
    charger_types = (
        sorted(df_ts["CHARGE_TYPE"].dropna().unique().tolist())
        if "CHARGE_TYPE" in df_ts.columns else []
    )
    plug_types = (
        sorted(df_ts["AC_DC"].dropna().unique().tolist())
        if "AC_DC" in df_ts.columns else []
    )

    summary = {
        "Station Name": station_name,
        "Region/City": region_value if region_value else "Not available in current dataset",
        "First Operating Date": str(first_date.date()),
        "Last Operating Date": str(last_date.date()),
        "Operating Duration": f"{duration_days} days (~{duration_months:.1f} months)",
        "Number of Charging Points": n_points if n_points is not None else "N/A",
        "Total Charging Sessions": f"{total_sessions:,}",
        "Average Sessions per Day": f"{total_sessions / duration_days:.2f}",
    }

    if has_target:
        summary[f"Total {target_col} Delivered"] = f"{total_energy:,.1f}"
        summary[f"Average {target_col} per Session"] = f"{(total_energy / total_sessions):.2f}" if total_sessions else "0"
        summary[f"Average Monthly {target_col}"] = f"{(total_energy / duration_months):,.1f}"
        summary[f"Average Daily {target_col}"] = f"{daily_series.mean():,.2f}"
        summary[f"Maximum Daily {target_col}"] = f"{daily_series.max():,.2f}"

    summary["Charger Types"] = ", ".join(charger_types) if charger_types else "N/A"
    summary["Plug Types"] = ", ".join(plug_types) if plug_types else "N/A"

    return summary
