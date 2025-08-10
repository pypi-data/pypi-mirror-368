import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.stats import norm, t as student_t

def validate_inputs(S, K, T, r, sigma, q):
    if S <= 0: raise ValueError("Spot price must be positive.")
    if K <= 0: raise ValueError("Strike must be positive.")
    if T <= 0: raise ValueError("Maturity must be positive.")
    if sigma <= 0: raise ValueError("Volatility must be positive.")
    if r < 0: raise ValueError("Risk-free rate cannot be negative.")
    if q < 0: raise ValueError("Dividend yield cannot be negative.")


def _to_series(x):
    if isinstance(x, pd.Series):
        return x.dropna()
    return pd.Series(np.asarray(x).ravel()).dropna()

def _garch11_variance(theta, r):
    """Variance recursion for GARCH(1,1). theta = [omega, alpha, beta]."""
    omega, alpha, beta = theta
    T = r.shape[0]
    v = np.empty(T)
    v0 = r.var(ddof=1) if T > 1 else max(1e-8, float(r**2))
    v[0] = omega + (alpha + beta) * v0
    for t in range(1, T):
        v[t] = omega + alpha * r[t - 1] ** 2 + beta * v[t - 1]
    return v

def _negloglik(params, r, dist):
    """Negative log-likelihood for Normal or Student-t innovations."""
    if dist == "t":
        if params[-1] <= 2.01:
            return np.inf
        nu = params[-1]
        theta = params[:-1]
    else:
        theta = params

    if theta[0] <= 0 or theta[1] < 0 or theta[2] < 0:
        return np.inf
    if theta[1] + theta[2] >= 0.9999:
        return np.inf

    v = _garch11_variance(theta, r)
    if np.any(v <= 0):
        return np.inf

    s = np.sqrt(v)
    if dist == "normal":
        ll = norm.logpdf(r, loc=0.0, scale=s)
    elif dist == "t":
        scale = s * np.sqrt((nu - 2.0) / nu)
        ll = student_t.logpdf(r / scale, df=nu) - np.log(scale)
    else:
        return np.inf

    return -np.sum(ll)

