import numpy as np
import pymc3 as pm
import pandas as pd
import matplotlib.pyplot as plt

def bayesian_forecast(df, days=5):
    df = df.dropna()
    prices = df["close"].values[-30:]
    X = np.arange(len(prices))

    with pm.Model() as model:
        alpha = pm.Normal("alpha", mu=0, sigma=20)
        beta = pm.Normal("beta", mu=0, sigma=1)
        sigma = pm.HalfNormal("sigma", sigma=1)

        mu = alpha + beta * X
        Y_obs = pm.Normal("Y_obs", mu=mu, sigma=sigma, observed=prices)

        trace = pm.sample(1000, tune=1000, target_accept=0.9, cores=1, progressbar=False)

        # Forecast next `days` steps
        future_x = np.arange(len(prices), len(prices) + days)
        posterior_preds = trace["alpha"][:, None] + trace["beta"][:, None] * future_x

        # Credible interval (95%) and mean
        forecast_mean = np.mean(posterior_preds, axis=0)
        lower = np.percentile(posterior_preds, 2.5, axis=0)
        upper = np.percentile(posterior_preds, 97.5, axis=0)

        return forecast_mean, lower, upper
