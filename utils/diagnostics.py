"""
Residual diagnostics for a backtest result (actual vs. predicted over the
holdout period). Mirrors the diagnostics section of the analysis notebook,
computed here so the app can render them with Plotly for a consistent look.
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox


def compute_residuals(test: pd.Series, point: pd.Series) -> pd.Series:
    """Actual minus predicted, aligned on shared dates, NaNs dropped."""
    aligned = pd.concat([test.rename("actual"), point.rename("pred")], axis=1).dropna()
    return (aligned["actual"] - aligned["pred"]).rename("residual")


def acf_pacf_data(residuals: pd.Series, max_lags: int = 20, alpha: float = 0.05):
    """Returns (lags, acf_values, acf_conf, pacf_values, pacf_conf) for plotting.
    conf arrays are the +/- band half-width at each lag (same for all lags under
    the default large-sample approximation used by statsmodels)."""
    n = len(residuals)
    lags = min(max_lags, n // 2 - 1)
    if lags < 1:
        return None

    acf_vals, acf_confint = acf(residuals, nlags=lags, alpha=alpha, fft=False)
    pacf_vals, pacf_confint = pacf(residuals, nlags=lags, alpha=alpha)

    # statsmodels returns confint as [lower, upper] absolute bounds around each acf value;
    # convert to a symmetric +/- half-width band for a simple shaded region in the chart.
    acf_band = (acf_confint[:, 1] - acf_confint[:, 0]) / 2
    pacf_band = (pacf_confint[:, 1] - pacf_confint[:, 0]) / 2

    lag_index = list(range(lags + 1))
    return {
        "lags": lag_index,
        "acf": acf_vals.tolist(),
        "acf_band": acf_band.tolist(),
        "pacf": pacf_vals.tolist(),
        "pacf_band": pacf_band.tolist(),
    }


def qq_plot_data(residuals: pd.Series):
    """Returns (theoretical_quantiles, sample_quantiles, line_x, line_y) for a Q-Q plot
    against a normal distribution."""
    osm, osr = stats.probplot(residuals, dist="norm", fit=False)
    # Reference line through the theoretical quantiles, fit via least squares on (osm, osr)
    slope, intercept = np.polyfit(osm, osr, 1)
    line_x = np.array([osm.min(), osm.max()])
    line_y = slope * line_x + intercept
    return osm, osr, line_x, line_y


def ljung_box_test(residuals: pd.Series, max_lags: int = 10) -> pd.DataFrame:
    lags = min(max_lags, len(residuals) // 2 - 1)
    if lags < 1:
        return pd.DataFrame()
    return acorr_ljungbox(residuals, lags=lags)
