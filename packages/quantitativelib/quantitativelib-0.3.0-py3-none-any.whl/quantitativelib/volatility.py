from quantitativelib.base import fit_garch, forecast_garch, backtest_garch
from quantitativelib._utils import _to_series
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf


def analyse_volatility(returns=None,
                       ticker=None,
                       start_date=None,
                       end_date=None,
                       horizon=1,
                       window=1000,
                       refit=20,
                       dist="t",
                       alphas=(0.01, 0.05),
                       plot=True,
                       plot_config=None,
                       seed=None):
    """
    Analyse volatility using GARCH model.
    
    Parameters:
    - returns (pd.Series): Time series of returns.
    - ticker (str): Stock ticker symbol for fetching data.
    - start_date (str): Start date for fetching data.
    - end_date (str): End date for fetching data.
    - horizon (int): Forecast horizon.
    - window (int): Rolling window size for backtesting.
    - refit (int): Frequency of model refitting.
    - dist (str): Distribution for GARCH model ('normal' or 't').
    - alphas (tuple): Significance levels for backtesting.
    - plot (bool): Whether to plot results.
    - plot_config (dict): Configuration for plotting.
    - seed (int): Random seed for reproducibility.

    Returns:
    - dict: Contains fitted model, forecasts, and backtest results.
    """
    if returns is None:
        if ticker is None or start_date is None or end_date is None:
            raise ValueError("Provide either returns OR ticker + start_date + end_date")
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, progress=False)
        if data.empty or "Close" not in data.columns:
            raise ValueError(f"No price data found for {ticker}")
        returns = data["Close"].pct_change().dropna()

    fit = fit_garch(returns, dist=dist, seed=seed)
    fc = forecast_garch(fit, horizon=horizon)
    bt = backtest_garch(returns, window=window, horizon=horizon, refit=refit, dist=dist, alphas=alphas, seed=seed)

    if plot:
        cfg = plot_config or {}
        figsize = cfg.get("figsize", (10, 6))
        f1 = bt["forecasts"].xs(1, level="horizon")["variance"]
        r = _to_series(returns)
        rv = r ** 2
        rv_align, f_align = [], []
        for t in f1.index:
            i = r.index.get_indexer_for([t])[0]
            if i + 1 < len(r):
                rv_align.append(rv.iloc[i + 1])
                f_align.append(f1.loc[t])
        if f_align:
            plt.figure(figsize=figsize)
            pd.Series(f_align, index=f1.index[:len(f_align)]).plot(label="Forecast var (h=1)", **cfg.get("style_var", {}))
            pd.Series(rv_align, index=f1.index[:len(f_align)]).plot(label="Realised r^2", alpha=0.7, **cfg.get("style_rv", {}))
            plt.title(cfg.get("title_var", "Variance forecast vs realised r^2 (h=1)"))
            plt.grid(True)
            plt.legend()
            if cfg.get("savefig"):
                plt.savefig(cfg["savefig"], dpi=300)
            plt.show()

    return {"fit": fit, "forecast": fc, "backtest": bt}