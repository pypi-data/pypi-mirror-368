import numpy as np
import scipy.stats as stats
from quantitativelib._utils import _garch11_variance, _to_series, _negloglik
from scipy.optimize import minimize
from scipy.stats import norm, t as student_t
import pandas as pd
from arch import arch_model

__all__ = [
    "bs_call_price", "bs_call_delta", "bs_call_gamma", "bs_call_vega", "bs_call_rho", "bs_call_theta",
    "bs_put_price", "bs_put_delta", "bs_put_gamma", "bs_put_vega", "bs_put_rho", "bs_put_theta",
    "bs_forward_price", "bs_forward_delta", "bs_forward_gamma", "bs_forward_vega", "bs_forward_rho", "bs_forward_theta",
    "bs_binary_call_price", "bs_binary_call_delta", "bs_binary_call_gamma", "bs_binary_call_vega", "bs_binary_call_rho", "bs_binary_call_theta",
    "bs_binary_put_price", "bs_binary_put_delta", "bs_binary_put_gamma", "bs_binary_put_vega", "bs_binary_put_rho", "bs_binary_put_theta",
    "euler_maruyama", "milstein",
    "simulate_gbm", "simulate_cir", "simulate_ou", "simulate_heston", "simulate_merton_jump",
    "fit_garch", "forecast_garch", "backtest_garch",
]


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

def fit_garch(returns, dist="t", options=None):
    r = _to_series(returns).dropna()
    if r.empty:
        raise ValueError("returns is empty after NaN removal")
    am = arch_model(r, mean="zero", vol="GARCH", p=1, q=1, dist=dist, rescale=False)
    res = am.fit(update_freq=0, disp="off", show_warning=False, options=options or {})
    p = res.params.to_dict()
    variance = (res.conditional_volatility ** 2).rename("variance")
    residuals = res.std_resid.rename("std_resid")
    out_params = {
        "omega": p.get("omega"),
        "alpha": p.get("alpha[1]"),
        "beta":  p.get("beta[1]"),
    }
    if dist == "t" and "nu" in p:
        out_params["nu"] = p.get("nu")
    return {
        "params": out_params,
        "variance": variance,
        "residuals": residuals,
        "dist": dist,
        "success": (getattr(res, "convergence_flag", 1) == 0),
        "message": getattr(res, "message", ""),
        "model_result": res,
    }


def forecast_garch(fit_result, horizon=1):
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    res = fit_result["model_result"]
    fc = res.forecast(horizon=horizon, reindex=False)
    vf = fc.variance.values[-1]
    idx = pd.RangeIndex(1, horizon + 1, name="horizon")
    return pd.DataFrame({"variance": vf, "vol": np.sqrt(vf)}, index=idx)


def backtest_garch(returns, window=1000, horizon=1, refit=20, dist="t", alphas=(0.01, 0.05)):
    r = _to_series(returns).dropna()
    n = len(r)
    if n <= window + horizon:
        raise ValueError("Not enough data for the requested window and horizon")
    rv = (r ** 2).clip(lower=1e-12)
    rows_params, rows_fc = [], []
    res = None
    for t0 in range(window, n - horizon):
        if (t0 - window) % refit == 0:
            am = arch_model(r.iloc[t0 - window:t0], mean="zero", vol="GARCH", p=1, q=1, dist=dist, rescale=False)
            res = am.fit(update_freq=0, disp="off", show_warning=False)
            p = res.params
            cur = {
                "omega": float(p.get("omega")),
                "alpha": float(p.get("alpha[1]")),
                "beta":  float(p.get("beta[1]")),
                "date":  r.index[t0],
            }
            if dist == "t" and "nu" in p.index:
                cur["nu"] = float(p["nu"])
            rows_params.append(cur)
        f = res.forecast(horizon=horizon, reindex=False)
        vf = f.variance.values[-1]
        df_fc = pd.DataFrame(
            {"horizon": np.arange(1, horizon + 1, dtype=int),
             "variance": vf,
             "vol": np.sqrt(vf)}
        )
        df_fc["date"] = r.index[t0]
        rows_fc.append(df_fc.set_index(["date", "horizon"]))
    forecasts = pd.concat(rows_fc).sort_index()
    fitted_params = pd.DataFrame(rows_params).set_index("date").sort_index()

    def _var_from_varseries(var_arr, a, nu_arr=None):
        s = np.sqrt(var_arr)
        if nu_arr is None:
            return s * norm.ppf(a)
        z = student_t.ppf(a, df=nu_arr)
        scale = s * np.sqrt((nu_arr - 2.0) / nu_arr)
        return scale * z

    var_hits = {}
    for a in alphas:
        if dist == "t" and ("nu" in fitted_params.columns) and not fitted_params["nu"].isna().all():
            dates = forecasts.index.get_level_values(0)
            nu_seq = fitted_params["nu"].reindex(dates).ffill().to_numpy()
            vhat = forecasts["variance"].to_numpy()
            var_a = _var_from_varseries(vhat, a, nu_arr=nu_seq)
        else:
            var_a = _var_from_varseries(forecasts["variance"].to_numpy(), a)
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
    f1 = forecasts.xs(1, level="horizon")["variance"]
    rv_align, f_align = [], []
    for t in f1.index:
        i = r.index.get_indexer_for([t])[0]
        if i + 1 < n:
            rv_align.append(rv.iloc[i + 1])
            f_align.append(f1.loc[t])

    def _qlike(rv_, fv_):
        rv_ = np.maximum(np.asarray(rv_, float), 1e-12)
        fv_ = np.maximum(np.asarray(fv_, float), 1e-12)
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