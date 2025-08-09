import numpy as np
import matplotlib.pyplot as plt

from quantitativelib.base import simulate_gbm, simulate_cir, simulate_heston, simulate_ou, simulate_merton_jump

def simulate_sde(model, params, T=1.0, N=1000, method='euler', plot=True, return_stats=False, plot_config=None, seed=None):
    """
    Simulate a stochastic process.

    Parameters:
    - model (str): One of 'gbm', 'cir', 'heston', 'ou', 'merton'
    - params (dict): Parameters for the chosen model
    - T (float): Time horizon
    - N (int): Number of time steps
    - method (str): Numerical method ('euler', 'milstein') for applicable models
    - plot (bool): Whether to plot the result
    - return_stats (bool): Whether to return summary statistics
    - plot_config (dict): Plot settings like figsize, title, savefig, etc.

    Returns:
    - tuple: Time grid and simulated path(s)
    """
    if seed is not None:
        np.random.seed(seed)

    if plot_config is None:
        plot_config = {}

    figsize = plot_config.get("figsize", (10, 6))
    title = plot_config.get("title", f"{model.upper()} Simulation")
    savefig = plot_config.get("savefig", None)

    if model == 'gbm':
        t, X = simulate_gbm(**params, T=T, N=N, method=method)

    elif model == 'cir':
        t, X = simulate_cir(**params, T=T, N=N)

    elif model == 'ou':
        t, X = simulate_ou(**params, T=T, N=N)

    elif model == 'merton':
        t, X = simulate_merton_jump(**params, T=T, N=N)

    elif model == 'heston':
        t, S, V = simulate_heston(**params, T=T, N=N)

        if plot:
            which = plot_config.get("which", "both")
            if which == "S":
                plt.figure(figsize=figsize)
                plt.plot(t, S, **plot_config.get("S", {}))
                plt.title(title)
                plt.xlabel("Time")
                plt.ylabel("S(t)")
                plt.grid(True)
                if savefig:
                    plt.savefig(savefig, dpi=300)
                plt.show()

            elif which == "V":
                plt.figure(figsize=figsize)
                plt.plot(t, V, **plot_config.get("V", {}))
                plt.title(title)
                plt.xlabel("Time")
                plt.ylabel("V(t)")
                plt.grid(True)
                if savefig:
                    plt.savefig(savefig, dpi=300)
                plt.show()

            elif which == "both":
                fig, axs = plt.subplots(2, 1, figsize=figsize, sharex=True)

                s_cfg = plot_config.get("S", {})
                v_cfg = plot_config.get("V", {})

                axs[0].plot(t, S, **s_cfg)
                axs[0].set_ylabel("Asset Price")
                axs[0].grid(True)

                axs[1].plot(t, V, **v_cfg)
                axs[1].set_ylabel("Variance")
                axs[1].set_xlabel("Time")
                axs[1].grid(True)

                axs[0].set_title(title)
                axs[0].legend(); axs[1].legend()

                plt.tight_layout()

                if savefig:
                    plt.savefig(savefig, dpi=300)
                plt.show()

            return (t, S, V)

    else:
        raise ValueError(f"Unsupported model: {model}")

    if plot:
        style = plot_config.get("X", {})
        plt.figure(figsize=figsize)
        plt.plot(t, X, **style)
        plt.title(title)
        plt.xlabel("Time")
        plt.ylabel("X(t)")
        plt.grid(True)
        if "label" in style:
            plt.legend()
        if savefig:
            plt.savefig(savefig, dpi=300)
        plt.show()

    if return_stats:
        stats = {
            'mean_final': np.mean(X[-1]),
            'std_final': np.std(X[-1])
        }
        return t, X, stats

    return t, X