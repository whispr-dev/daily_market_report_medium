import numpy as np
import pandas as pd
from pykalman import KalmanFilter

def apply_kalman_filter(df):
    prices = df["close"].values
    kf = KalmanFilter(
        transition_matrices=[1],
        observation_matrices=[1],
        initial_state_mean=prices[0],
        initial_state_covariance=1,
        observation_covariance=1,
        transition_covariance=0.01
    )
    state_means, _ = kf.filter(prices)
    df["kalman_smooth"] = state_means.flatten()
    return df
