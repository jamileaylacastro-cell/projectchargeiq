"""
ETS Additive and SARIMA model functions, each returning (point, lower, upper)
so the app can show forecast variability, not just a single line.

Used two ways:
  - Backtest: fit on a train slice, predict over a held-out test slice, compare to actuals.
  - Forward forecast: fit on the full clean history, predict beyond the last known date.
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_squared_error, mean_absolute_error
from math import sqrt
import pmdarima as pm

SEASON_LENGTH = 7


def _future_index(last_date: pd.Timestamp, horizon: int) -> pd.DatetimeIndex:
    return pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon, freq="D")


def run_ets_additive(series: pd.Series, horizon: int, target_index: pd.DatetimeIndex, n_sims: int = 250):
    """Fits ETS Additive on `series` and forecasts `horizon` steps, aligned to `target_index`."""
    fit = ExponentialSmoothing(
        series, seasonal="add", seasonal_periods=SEASON_LENGTH,
        trend="add", initialization_method="estimated",
    ).fit()
    point = pd.Series(fit.forecast(horizon).values, index=target_index)

    sims = fit.simulate(nsimulations=horizon, repetitions=n_sims, error="add")
    sims = np.asarray(sims)
    lower = pd.Series(np.percentile(sims, 10, axis=1), index=target_index)
    upper = pd.Series(np.percentile(sims, 90, axis=1), index=target_index)
    return point, lower, upper


def run_sarima(series: pd.Series, horizon: int, target_index: pd.DatetimeIndex):
    """Fits SARIMA (via auto_arima) on `series` and forecasts `horizon` steps, aligned to `target_index`."""
    model = pm.auto_arima(
        series, start_p=1, start_q=1, test="adf",
        max_p=3, max_q=3, m=SEASON_LENGTH, start_P=0, start_Q=0,
        max_P=2, max_Q=2, D=1, trace=False,
        error_action="ignore", suppress_warnings=True, stepwise=True,
    )
    forecast, conf_int = model.predict(n_periods=horizon, return_conf_int=True, alpha=0.2)
    point = pd.Series(np.asarray(forecast), index=target_index)
    lower = pd.Series(conf_int[:, 0], index=target_index)
    upper = pd.Series(conf_int[:, 1], index=target_index)
    return point, lower, upper


MODEL_RUNNERS = {
    "ETS Additive": run_ets_additive,
    "SARIMA": run_sarima,
}


def compute_metrics(y_true: pd.Series, y_pred: pd.Series):
    aligned = pd.concat([y_true.rename("actual"), y_pred.rename("pred")], axis=1).dropna()
    if aligned.empty:
        return None, None
    rmse = sqrt(mean_squared_error(aligned["actual"], aligned["pred"]))
    mae = mean_absolute_error(aligned["actual"], aligned["pred"])
    return rmse, mae


def run_backtest(daily_series: pd.Series, model_name: str, test_days: int = 30):
    """Splits off the last `test_days` as a holdout, fits on the rest, scores against actuals."""
    latest_date = daily_series.index.max()
    test_start = latest_date - pd.Timedelta(days=test_days - 1)
    train = daily_series[daily_series.index < test_start]
    test = daily_series[daily_series.index >= test_start]

    if len(train) < 30 or len(test) == 0:
        return None

    runner = MODEL_RUNNERS[model_name]
    point, lower, upper = runner(train, len(test), test.index)
    rmse, mae = compute_metrics(test, point)

    return {
        "train": train, "test": test,
        "point": point, "lower": lower, "upper": upper,
        "rmse": rmse, "mae": mae, "model": model_name,
    }


def run_forward_forecast(daily_series: pd.Series, model_name: str, horizon: int):
    """Fits on the FULL clean history and forecasts `horizon` days beyond the last known date."""
    last_date = daily_series.index.max()
    future_index = _future_index(last_date, horizon)

    runner = MODEL_RUNNERS[model_name]
    point, lower, upper = runner(daily_series, horizon, future_index)

    return {"point": point, "lower": lower, "upper": upper}
