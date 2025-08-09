import numpy as np
import scipy.stats as stats
from quantitativelib._utils import _garch11_variance, _to_series, _negloglik
from scipy.optimize import minimize
from scipy.stats import norm, t as student_t
import pandas as pd

# === Helper functions ===
def _d1(S, K, T, r, sigma, q=0.0):
    return (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))

def _d2(S, K, T, r, sigma, q=0.0):
    return _d1(S, K, T, r, sigma, q) - sigma * np.sqrt(T)

def _phi_d1(S, K, T, r, sigma, q=0.0):
    return stats.norm.pdf(_d1(S, K, T, r, sigma, q))

def _phi_d2(S, K, T, r, sigma, q=0.0):
    return stats.norm.pdf(_d2(S, K, T, r, sigma, q))

def _Nd1(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(_d1(S, K, T, r, sigma, q))

def _Nd2(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(_d2(S, K, T, r, sigma, q))

def _Nmd1(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(-_d1(S, K, T, r, sigma, q))

def _Nmd2(S, K, T, r, sigma, q=0.0):
    return stats.norm.cdf(-_d2(S, K, T, r, sigma, q))


# === Black-Scholes Call Option ===
def bs_call_price(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option price."""
    return S * np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q) - K * np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)

def bs_call_delta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option delta."""
    return np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q)

def bs_call_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option gamma."""
    return (np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_call_vega(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option vega."""
    return S * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) * np.sqrt(T)

def bs_call_rho(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option rho."""
    return K * T * np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)

def bs_call_theta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes call option theta."""
    return (
        -S * sigma * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) / (2 * np.sqrt(T))
        - r * K * np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)
        + q * S * np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q)
    )


# === Black-Scholes Put Option ===
def bs_put_price(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option price."""
    return K * np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q) - S * np.exp(-q * T) * _Nmd1(S, K, T, r, sigma, q)

def bs_put_delta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option delta."""
    return -np.exp(-q * T) * _Nmd1(S, K, T, r, sigma, q)

def bs_put_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option gamma."""
    return (np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_put_vega(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option vega."""
    return S * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) * np.sqrt(T)

def bs_put_rho(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option rho."""
    return -K * T * np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q)

def bs_put_theta(S, K, T, r, sigma, q=0.0):
    """Calculate Black-Scholes put option theta."""
    return (
        -S * sigma * np.exp(-q * T) * _phi_d1(S, K, T, r, sigma, q) / (2 * np.sqrt(T))
        + r * K * np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q)
        - q * S * np.exp(-q * T) * _Nd1(S, K, T, r, sigma, q)
    )


# === Forward Contracts ===
def bs_forward_price(S, K, T, r, q=0.0):
    """Calculate forward price."""
    return S * np.exp(-q * T) - K * np.exp(-r * T)

def bs_forward_delta(S, K, T, r, q=0.0):
    """Calculate forward delta."""
    return np.exp(-q * T)

def bs_forward_gamma(S, K, T, r, q=0.0):
    """Calculate forward gamma."""
    return 0.0

def bs_forward_vega(S, K, T, r, q=0.0):
    """Calculate forward vega."""
    return 0.0

def bs_forward_rho(S, K, T, r, q=0.0):
    """Calculate forward rho."""
    return K * T * np.exp(-r * T)

def bs_forward_theta(S, K, T, r, q=0.0):
    """Calculate forward theta."""
    return q * S * np.exp(-q * T) - r * K * np.exp(-r * T)


# === Binary Call Options ===
def bs_binary_call_price(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option price."""
    return np.exp(-r * T) * _Nd2(S, K, T, r, sigma, q)

def bs_binary_call_delta(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option delta."""
    return (np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_binary_call_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option gamma."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -(np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2) / (S**2 * sigma**2 * T)

def bs_binary_call_vega(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option vega."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2 / sigma

def bs_binary_call_rho(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option rho."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -T * np.exp(-r * T) * stats.norm.cdf(d2) + np.exp(-r * T) * stats.norm.pdf(d2) * np.sqrt(T) / sigma

def bs_binary_call_theta(S, K, T, r, sigma, q=0.0):
    """Calculate binary call option theta."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -np.exp(-r * T) * (
        -r * stats.norm.cdf(d2) + stats.norm.pdf(d2) * ((r - q - 0.5 * sigma**2) / (sigma * np.sqrt(T)) - d2 / (2 * T))
    )


# === Binary Put Options ===
def bs_binary_put_price(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option price."""
    return np.exp(-r * T) * _Nmd2(S, K, T, r, sigma, q)

def bs_binary_put_delta(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option delta."""
    return -(np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q)) / (S * sigma * np.sqrt(T))

def bs_binary_put_gamma(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option gamma."""
    d2 = _d2(S, K, T, r, sigma, q)
    return (np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2) / (S**2 * sigma**2 * T)

def bs_binary_put_vega(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option vega."""
    d2 = _d2(S, K, T, r, sigma, q)
    return np.exp(-r * T) * _phi_d2(S, K, T, r, sigma, q) * d2 / sigma

def bs_binary_put_rho(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option rho."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -T * np.exp(-r * T) * stats.norm.cdf(-d2) - np.exp(-r * T) * stats.norm.pdf(d2) * np.sqrt(T) / sigma

def bs_binary_put_theta(S, K, T, r, sigma, q=0.0):
    """Calculate binary put option theta."""
    d2 = _d2(S, K, T, r, sigma, q)
    return -np.exp(-r * T) * (
        r * stats.norm.cdf(-d2) + stats.norm.pdf(d2) * ((r - q - 0.5 * sigma**2) / (sigma * np.sqrt(T)) + d2 / (2 * T))
    )

# === Stochastic Functions ===
# General-purpose numerical SDE solvers

def euler_maruyama(mu, sigma, X0, T, N, dW=None):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    X = np.zeros(N + 1)
    X[0] = X0
    if dW is None:
        dW = np.random.normal(0, np.sqrt(dt), size=N)
    for i in range(N):
        X[i + 1] = X[i] + mu(t[i], X[i]) * dt + sigma(t[i], X[i]) * dW[i]
    return t, X

def milstein(mu, sigma, sigma_dx, X0, T, N, dW=None):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    X = np.zeros(N + 1)
    X[0] = X0
    if dW is None:
        dW = np.random.normal(0, np.sqrt(dt), size=N)
    for i in range(N):
        X[i + 1] = (
            X[i]
            + mu(t[i], X[i]) * dt
            + sigma(t[i], X[i]) * dW[i]
            + 0.5 * sigma(t[i], X[i]) * sigma_dx(t[i], X[i]) * (dW[i]**2 - dt)
        )
    return t, X

# Model-specific simulators using the above schemes 

def simulate_gbm(S0, mu, sigma, T, N, method="euler"):
    def drift(t, S): return mu * S
    def diffusion(t, S): return sigma * S
    def diffusion_dx(t, S): return sigma

    if method == "euler":
        return euler_maruyama(drift, diffusion, S0, T, N)
    elif method == "milstein":
        return milstein(drift, diffusion, diffusion_dx, S0, T, N)
    else:
        raise ValueError("Unknown method: use 'euler' or 'milstein'")

def simulate_cir(X0, kappa, theta, sigma, T, N, method="euler"):
    def drift(t, X): return kappa * (theta - X)
    def diffusion(t, X): return sigma * np.sqrt(max(X, 0))
    def diffusion_dx(t, X): return 0.5 * sigma / np.sqrt(max(X, 1e-8))

    if method == "euler":
        return euler_maruyama(drift, diffusion, X0, T, N)
    elif method == "milstein":
        return milstein(drift, diffusion, diffusion_dx, X0, T, N)
    else:
        raise ValueError("Unknown method: use 'euler' or 'milstein'")

def simulate_ou(X0, mu, theta, sigma, T, N, method="euler"):
    def drift(t, X): return mu * (theta - X)
    def diffusion(t, X): return sigma
    def diffusion_dx(t, X): return 0.0

    if method == "euler":
        return euler_maruyama(drift, diffusion, X0, T, N)
    elif method == "milstein":
        return milstein(drift, diffusion, diffusion_dx, X0, T, N)
    else:
        raise ValueError("Unknown method: use 'euler' or 'milstein'")

def simulate_heston(S0, V0, mu, kappa, theta, xi, rho, T, N):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    S = np.zeros(N + 1)
    V = np.zeros(N + 1)
    S[0], V[0] = S0, V0

    for i in range(N):
        Z1 = np.random.normal()
        Z2 = np.random.normal()
        dW_v = np.sqrt(dt) * Z1
        dW_s = np.sqrt(dt) * (rho * Z1 + np.sqrt(1 - rho**2) * Z2)

        V[i + 1] = V[i] + kappa * (theta - V[i]) * dt + xi * np.sqrt(max(V[i], 0)) * dW_v
        S[i + 1] = S[i] + mu * S[i] * dt + np.sqrt(max(V[i], 0)) * S[i] * dW_s

    return t, S, V

def simulate_merton_jump(S0, mu, sigma, lambd, m, v, T, N):
    dt = T / N
    t = np.linspace(0, T, N + 1)
    S = np.zeros(N + 1)
    S[0] = S0

    for i in range(N):
        dW = np.random.normal(0, np.sqrt(dt))
        J = np.random.poisson(lambd * dt)
        jump = np.sum(np.random.normal(m, np.sqrt(v), J)) if J > 0 else 0
        S[i + 1] = S[i] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * dW + jump)

    return t, S

# === GARCH Functions === 

def fit_garch(returns, dist="t", seed=None, options=None):
    """
    Fit a GARCH(1,1) model by MLE.
    """
    r = _to_series(returns).values
    if r.size == 0:
        raise ValueError("returns is empty after NaN removal")

    if seed is not None:
        np.random.seed(seed)

    v = r.var(ddof=1) if r.size > 1 else 1e-4
    x0 = np.array([0.05 * v, 0.05, 0.90])
    bounds = [(1e-12, None), (1e-8, 1 - 1e-6), (1e-8, 1 - 1e-6)]
    if dist == "t":
        x0 = np.r_[x0, 8.0]
        bounds += [(2.01, 200.0)]
    elif dist != "normal":
        raise ValueError("dist must be 'normal' or 't'")

    res = minimize(_negloglik, x0, args=(r, dist), method="L-BFGS-B",
                   bounds=bounds, options=options or {"maxiter": 2000})

    theta = res.x
    if dist == "t":
        theta_main, nu = theta[:-1], float(theta[-1])
    else:
        theta_main, nu = theta, None

    vhat = _garch11_variance(theta_main, r)
    shat = np.sqrt(vhat)
    resid = r / shat

    s = _to_series(returns)
    variance = pd.Series(vhat, index=s.index, name="variance")
    residuals = pd.Series(resid, index=s.index, name="std_resid")

    params = {"omega": float(theta_main[0]), "alpha": float(theta_main[1]), "beta": float(theta_main[2])}
    if nu is not None:
        params["nu"] = nu

    return {
        "params": params,
        "variance": variance,
        "residuals": residuals,
        "dist": dist,
        "success": bool(res.success),
        "message": str(res.message),
    }


def forecast_garch(fit_result, horizon=1):
    """
    Multi-step variance forecasts for GARCH(1,1).
    """
    if horizon < 1:
        raise ValueError("horizon must be >= 1")

    omega = fit_result["params"]["omega"]
    alpha = fit_result["params"]["alpha"]
    beta = fit_result["params"]["beta"]
    last_var = float(fit_result["variance"].iloc[-1])

    vf = np.empty(horizon)
    vf[0] = omega + (alpha + beta) * last_var
    for h in range(1, horizon):
        vf[h] = omega + (alpha + beta) * vf[h - 1]

    idx = pd.RangeIndex(1, horizon + 1, name="horizon")
    return pd.DataFrame({"variance": vf, "vol": np.sqrt(vf)}, index=idx)


def backtest_garch(returns, window=1000, horizon=1, refit=20, dist="t", alphas=(0.01, 0.05), seed=None):
    """
    Rolling GARCH(1,1) backtest with periodic refits and multi-step forecasts.
    """
    r = _to_series(returns)
    n = len(r)
    if n <= window + horizon:
        raise ValueError("Not enough data for the requested window and horizon")

    rv = (r ** 2)
    rows_params = []
    rows_fc = []

    # Rolling
    for t0 in range(window, n - horizon):
        # Refit every 'refit' steps; only append params when we actually refit
        if (t0 - window) % refit == 0:
            fit = fit_garch(r.iloc[t0 - window:t0], dist=dist, seed=seed)
            cur_params = fit["params"].copy()
            cur_params["date"] = r.index[t0]
            rows_params.append(cur_params)

        # Always produce a forecast for this date
        fc = forecast_garch(fit, horizon=horizon).assign(date=r.index[t0])
        rows_fc.append(fc.reset_index().set_index(["date", "horizon"]))

    forecasts = pd.concat(rows_fc).sort_index()
    fitted_params = pd.DataFrame(rows_params).set_index("date").sort_index()

    # Helper to get VaR from variance series
    def _var_from_varseries(var_arr, a, nu_arr=None):
        s = np.sqrt(var_arr)
        if dist == "normal":
            z = norm.ppf(a)
            return s * z
        else:
            z = student_t.ppf(a, df=nu_arr)
            scale = s * np.sqrt((nu_arr - 2.0) / nu_arr)
            return scale * z

    var_hits = {}
    for a in alphas:
        if dist == "t":

            dates = forecasts.index.get_level_values(0)
            nu_per_date = fitted_params["nu"].groupby(level=0).last()
            nu_unique = nu_per_date.reindex(dates.unique()).ffill()
            nu_seq = nu_unique.reindex(dates).to_numpy()

            vhat = forecasts["variance"].values
            var_a = _var_from_varseries(vhat, a, nu_arr=nu_seq)
        else:
            var_a = _var_from_varseries(forecasts["variance"].values, a)

        idx_list, hit_list = [], []
        for (t, h), vhat_h in zip(forecasts.index, var_a):
            i = r.index.get_indexer_for([t])[0]
            if i + h >= n:
                continue
            rtph = r.iloc[i + h]
            hit_list.append(1 if rtph < vhat_h else 0)
            idx_list.append((t, h))
        var_hits[a] = pd.Series(hit_list, index=pd.MultiIndex.from_tuples(idx_list, names=["date", "horizon"]))
    var_hits = pd.DataFrame(var_hits).sort_index()

    # Simple metrics for h=1
    f1 = forecasts.xs(1, level="horizon")["variance"]
    rv_align, f_align = [], []
    for t in f1.index:
        i = r.index.get_indexer_for([t])[0]
        if i + 1 < n:
            rv_align.append(rv.iloc[i + 1])
            f_align.append(f1.loc[t])

    def _qlike(rv_, fv_):
        rv_ = np.asarray(rv_)
        fv_ = np.asarray(fv_)
        return float(np.mean(rv_ / fv_ + np.log(fv_) - np.log(rv_) - 1.0))

    metrics = {}
    if f_align:
        metrics["QLIKE_h1"] = _qlike(rv_align, f_align)

    return {
        "fitted_params": fitted_params,
        "forecasts": forecasts,
        "var_hits": var_hits,
        "metrics": metrics,
        "alphas": tuple(alphas),
    }