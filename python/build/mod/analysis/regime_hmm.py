import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

def detect_regimes(df, n_states=3):
    df["returns"] = df["close"].pct_change()
    df["volatility"] = df["returns"].rolling(5).std()
    df = df.dropna()

    X = df[["returns", "volatility"]].values

    model = GaussianHMM(n_components=n_states, covariance_type="full", n_iter=1000)
    model.fit(X)
    hidden_states = model.predict(X)

    df = df.iloc[-len(hidden_states):]
    df["regime"] = hidden_states

    return df[["regime"]], model
