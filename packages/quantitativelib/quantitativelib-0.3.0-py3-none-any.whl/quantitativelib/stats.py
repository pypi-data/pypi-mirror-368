import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

def analyse(
    ticker, 
    start_date, 
    end_date,
    fig_size=(10, 5),
    show_stats=True,
    show_plots=True,
    stats=None,
    round_decimals=4,
    plot_kwargs=None,
    overlay_price=False
):
    """
    Analyse stock data for one or more tickers between specified dates.

    Parameters:
    ticker (str or list): One or more stock ticker symbols.
    start_date (str): Start date in 'YYYY-MM-DD' format.
    end_date (str): End date in 'YYYY-MM-DD' format.
    fig_size (tuple): Size of the plots (width, height).
    show_stats (bool): Whether to print the statistics table.
    show_plots (bool): Whether to display the plots.
    stats (list or None): Subset of statistics to show. Options:
        ['mean', 'std', 'skew', 'kurt', 'sharpe', 'cumulative', 'drawdown']
    round_decimals (int or None): Number of decimal places for stats.
    plot_kwargs (dict or None): Custom kwargs for matplotlib plot.
    overlay_price (bool): If True, overlay all tickers' price plots on one figure.
    """

    if isinstance(ticker, str):
        tickers = [ticker]
    else:
        tickers = list(ticker)

    results = {}
    price_df = pd.DataFrame()

    for t in tickers:
        data = yf.download(t, start=start_date, end=end_date, auto_adjust=True, progress=False)

        if data.empty or 'Close' not in data.columns:
            print(f"[{t}] No data found between {start_date} and {end_date}.")
            continue

        data['Returns'] = data['Close'].pct_change().dropna()

        # Save price data for overlay
        price_df[t] = data['Close']

        # Default stats list
        if stats is None:
            stats = ['mean', 'std', 'skew', 'kurt', 'sharpe', 'cumulative', 'drawdown']

        computed = {}
        if 'mean' in stats:
            computed['Mean Return'] = data['Returns'].mean()
        if 'std' in stats:
            computed['Std Dev'] = data['Returns'].std()
        if 'skew' in stats:
            computed['Skewness'] = data['Returns'].skew()
        if 'kurt' in stats:
            computed['Kurtosis'] = data['Returns'].kurtosis()
        if 'sharpe' in stats:
            computed['Sharpe Ratio'] = data['Returns'].mean() / data['Returns'].std() * (252 ** 0.5)
        if 'cumulative' in stats:
            computed['Cumulative Return'] = data['Close'].iloc[-1] / data['Close'].iloc[0] - 1
        if 'drawdown' in stats:
            computed['Max Drawdown'] = (data['Close'] / data['Close'].cummax() - 1).min()

        df_stats = pd.DataFrame(computed, index=[t])
        if round_decimals is not None:
            df_stats = df_stats.round(round_decimals)

        results[t] = df_stats

        if show_plots:
            plot_kwargs = plot_kwargs or {}

            if not overlay_price:
                data['Close'].plot(figsize=fig_size, title=f"{t} Price", **plot_kwargs)
                plt.show()

            data['Returns'].plot(figsize=fig_size, title=f"{t} Daily Returns", **plot_kwargs)
            plt.show()

        if show_stats:
            print(df_stats)
            print()

    if show_plots and overlay_price and not price_df.empty:
        price_df.plot(figsize=fig_size, title="Overlayed Prices", **(plot_kwargs or {}))
        plt.show()

    if len(results) == 1:
        return list(results.values())[0]
    else:
        return pd.concat(results.values())
