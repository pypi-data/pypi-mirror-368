# quantitativelib

A simple Python library for quantitative finance.

This functions mainly as a test to learn how packages are made, and hopefully to develop a customised quantitative finance library suited to my needs. Lots more to be added.

---

## Installation

```bash
pip install quantitativelib
```

## Features

Core Functionality
Fetches historical stock data, computes returns and volatility, and generates basic price and return plots with summary statistics.

Options Pricing
Implements Black–Scholes pricing for calls, puts, forwards, and binary options. Computes all standard Greeks with support for dividend yield and parameter validation.

Stochastic Calculus Simulations
Supports simulation of SDEs using Euler–Maruyama and Milstein schemes. Includes built-in models such as GBM, CIR, OU, Heston, and Merton jump diffusion, with a unified interface for simulation, plotting, and statistical output.