import numpy as np
import pandas as pd
from quantitativelib import base as qt
from quantitativelib._utils import validate_inputs

def black_scholes(option_type, K, S, r, T, sigma, q=0.0, precision=4, show_table=False):
    """
    Calculate Black-Scholes option prices and Greeks using qt.base module.

    Parameters:
    - option_type (str or list of str): Types: 'call', 'put', 'forward', 'binary_call', 'binary_put'
    - K (float): Strike price
    - S (float): Spot price
    - r (float): Risk-free rate
    - T (float): Time to maturity (in years)
    - sigma (float): Volatility
    - q (float): Dividend yield (default 0.0)
    - precision (int): Decimal places to round to
    - show_table (bool): Whether to print a DataFrame

    Returns:
    - dict or DataFrame: Option prices and Greeks
    """
    validate_inputs(S, K, T, r, sigma, q)

    if isinstance(option_type, str):
        option_type = [option_type]

    results = {'Price': {}, 'Delta': {}, 'Gamma': {}, 'Vega': {}, 'Rho': {}, 'Theta': {}}

    for opt in option_type:
        if opt == 'call':
            price = qt.bs_call_price(S, K, T, r, sigma, q)
            delta = qt.bs_call_delta(S, K, T, r, sigma, q)
            gamma = qt.bs_call_gamma(S, K, T, r, sigma, q)
            vega = qt.bs_call_vega(S, K, T, r, sigma, q)
            rho = qt.bs_call_rho(S, K, T, r, sigma, q)
            theta = qt.bs_call_theta(S, K, T, r, sigma, q)

        elif opt == 'put':
            price = qt.bs_put_price(S, K, T, r, sigma, q)
            delta = qt.bs_put_delta(S, K, T, r, sigma, q)
            gamma = qt.bs_put_gamma(S, K, T, r, sigma, q)
            vega = qt.bs_put_vega(S, K, T, r, sigma, q)
            rho = qt.bs_put_rho(S, K, T, r, sigma, q)
            theta = qt.bs_put_theta(S, K, T, r, sigma, q)

        elif opt == 'forward':
            price = qt.bs_forward_price(S, K, T, r, q)
            delta = qt.bs_forward_delta(S, K, T, r, q)
            gamma = qt.bs_forward_gamma(S, K, T, r, q)
            vega = qt.bs_forward_vega(S, K, T, r, q)
            rho = qt.bs_forward_rho(S, K, T, r, q)
            theta = qt.bs_forward_theta(S, K, T, r, q)

        elif opt == 'binary_call':
            price = qt.bs_binary_call_price(S, K, T, r, sigma, q)
            delta = qt.bs_binary_call_delta(S, K, T, r, sigma, q)
            gamma = qt.bs_binary_call_gamma(S, K, T, r, sigma, q)
            vega = qt.bs_binary_call_vega(S, K, T, r, sigma, q)
            rho = qt.bs_binary_call_rho(S, K, T, r, sigma, q)
            theta = qt.bs_binary_call_theta(S, K, T, r, sigma, q)

        elif opt == 'binary_put':
            price = qt.bs_binary_put_price(S, K, T, r, sigma, q)
            delta = qt.bs_binary_put_delta(S, K, T, r, sigma, q)
            gamma = qt.bs_binary_put_gamma(S, K, T, r, sigma, q)
            vega = qt.bs_binary_put_vega(S, K, T, r, sigma, q)
            rho = qt.bs_binary_put_rho(S, K, T, r, sigma, q)
            theta = qt.bs_binary_put_theta(S, K, T, r, sigma, q)

        else:
            raise ValueError(f"Unknown option type: {opt}")

        label = opt.replace('_', ' ').title()
        results['Price'][label] = round(price, precision)
        results['Delta'][label] = round(delta, precision)
        results['Gamma'][label] = round(gamma, precision)
        results['Vega'][label] = round(vega, precision)
        results['Rho'][label] = round(rho, precision)
        results['Theta'][label] = round(theta, precision)

    df = pd.DataFrame(results).T
    if show_table:
        print(df)
    return df
