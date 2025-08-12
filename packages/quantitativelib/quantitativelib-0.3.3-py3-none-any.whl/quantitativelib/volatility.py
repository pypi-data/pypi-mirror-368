from quantitativelib.base import fit_garch, forecast_garch, backtest_garch
from quantitativelib._utils import _to_series
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import numpy as np

__all__ = ["analyse_volatility"]

def analyse_volatility(
    returns=None,
    ticker=None,
    start_date=None,
    end_date=None,
    horizon=1,
    window=1000,
    refit=20,
    dist="t",
    alphas=(0.01, 0.05),
    plot=True,
    plot_modes=("var_vs_r2",),
    plot_config=None,
    roll_window=21,
    alpha_plot=0.05,
):
    """
    Analyse volatility using a GARCH(1,1) model.

    Parameters:
    - returns (pd.Series, optional): Time series of returns.
    - ticker (str, optional): Stock ticker symbol for fetching data.
    - start_date (str, optional): Start date for fetching data.
    - end_date (str, optional): End date for fetching data.
    - horizon (int): Forecast horizon.
    - window (int): Rolling window size for backtesting.
    - refit (int): Frequency of model refitting.
    - dist (str): Distribution for GARCH model ('normal' or 't').
    - alphas (tuple): Significance levels for backtesting.
    - plot (bool): Whether to produce plots.
    - plot_modes (tuple): One or more plot types to produce. Supported:
        'var_vs_r2' - Forecast variance vs realised r².
        'var_vs_realised_var_roll' - Forecast variance vs rolling realised variance.
        'vol_vs_realised_vol_roll' - Forecast volatility vs rolling realised volatility.
        'fit_variance' - Conditional variance from one-shot fit.
        'var_hits_cum' - Cumulative VaR hit rate vs nominal level.
    - plot_config (dict, optional): Configuration for plotting (e.g., figsize, styles, titles).
    - roll_window (int): Window length for rolling realised variance/volatility.
    - alpha_plot (float): VaR level to use for the 'var_hits_cum' plot.

    Returns:
    - dict: Contains:
        'fit' - One-shot fit results from `fit_garch`.
        'forecast' - h-step forecast from `forecast_garch`.
        'backtest' - Rolling backtest results from `backtest_garch`.
    """

    if returns is None:
        if ticker is None or start_date is None or end_date is None:
            raise ValueError("Provide either returns OR ticker + start_date + end_date")
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, progress=False)
        if data.empty or "Close" not in data.columns:
            raise ValueError(f"No price data found for {ticker}")
        returns = data["Close"].pct_change().dropna()

    fit = fit_garch(returns, dist=dist)
    fc = forecast_garch(fit, horizon=horizon)
    bt = backtest_garch(
        returns,
        window=window,
        horizon=horizon,
        refit=refit,
        dist=dist,
        alphas=alphas
    )

    if plot:
        cfg = plot_config or {}
        figsize = cfg.get("figsize", (10, 6))

        f1_var = bt["forecasts"].xs(1, level="horizon")["variance"]
        f1_vol = np.sqrt(f1_var)
        r = _to_series(returns)
        rv = r ** 2

        idx_align, rv1_align, f1_align = [], [], []
        for t in f1_var.index:
            i = r.index.get_indexer_for([t])[0]
            if i + 1 < len(r):
                idx_align.append(t)
                rv1_align.append(rv.iloc[i + 1])
                f1_align.append(f1_var.loc[t])

        if "var_vs_r2" in plot_modes and f1_align:
            plt.figure(figsize=figsize)
            pd.Series(f1_align, index=idx_align).plot(label="Forecast var (h=1)", **cfg.get("style_var", {}))
            pd.Series(rv1_align, index=idx_align).plot(label="Realised r^2", alpha=0.7, **cfg.get("style_rv", {}))
            plt.title(cfg.get("title_var", "Variance forecast vs realised r^2 (h=1)"))
            plt.grid(True); plt.legend(); plt.show()

        if ("var_vs_realised_var_roll" in plot_modes or "vol_vs_realised_vol_roll" in plot_modes) and f1_align:
            rv_roll = rv.rolling(roll_window).mean()
            rv_roll_align = []
            for t in idx_align:
                i = r.index.get_indexer_for([t])[0]
                if i + 1 < len(rv_roll):
                    rv_roll_align.append(rv_roll.iloc[i + 1])

            if "var_vs_realised_var_roll" in plot_modes and len(rv_roll_align) == len(idx_align):
                plt.figure(figsize=figsize)
                pd.Series(f1_align, index=idx_align).plot(label="Forecast var (h=1)", **cfg.get("style_var", {}))
                pd.Series(rv_roll_align, index=idx_align).plot(label=f"Realised var (rolling {roll_window})", alpha=0.7, **cfg.get("style_rv_roll", {}))
                plt.title(cfg.get("title_var_roll", f"Variance forecast vs rolling realised variance (h=1, W={roll_window})"))
                plt.grid(True); plt.legend(); plt.show()

            if "vol_vs_realised_vol_roll" in plot_modes and len(rv_roll_align) == len(idx_align):
                plt.figure(figsize=figsize)
                pd.Series(np.sqrt(f1_align), index=idx_align).plot(label="Forecast vol (h=1)", **cfg.get("style_vol", {}))
                pd.Series(np.sqrt(rv_roll_align), index=idx_align).plot(label=f"Realised vol (rolling {roll_window})", alpha=0.7, **cfg.get("style_rv_roll_vol", {}))
                plt.title(cfg.get("title_vol_roll", f"Vol forecast vs rolling realised vol (h=1, W={roll_window})"))
                plt.grid(True); plt.legend(); plt.show()

        if "fit_variance" in plot_modes and isinstance(fit.get("variance"), pd.Series):
            plt.figure(figsize=figsize)
            fit["variance"].plot(label="Cond. var (one-shot fit)", **cfg.get("style_fitvar", {}))
            plt.title(cfg.get("title_fitvar", "Conditional variance from one-shot fit"))
            plt.grid(True); plt.legend(); plt.show()

        if "var_hits_cum" in plot_modes and alpha_plot in bt["alphas"]:
            hits = bt["backtest"]["var_hits"] if "backtest" in bt else bt["var_hits"]
            if (alpha_plot in hits.columns) and ("horizon" in hits.index.names):
                h1 = hits.xs(1, level="horizon")[alpha_plot].sort_index()
                cum_rate = h1.expanding().mean()
                plt.figure(figsize=figsize)
                cum_rate.plot(label=f"Cumulative hit rate (alpha={alpha_plot})", **cfg.get("style_hits", {}))
                pd.Series(alpha_plot, index=cum_rate.index).plot(label="Nominal", linestyle="--", alpha=0.7, **cfg.get("style_nominal", {}))
                plt.title(cfg.get("title_hits", f"Cumulative VaR hits vs nominal (h=1, alpha={alpha_plot})"))
                plt.grid(True); plt.legend(); plt.show()

    return {"fit": fit, "forecast": fc, "backtest": bt}