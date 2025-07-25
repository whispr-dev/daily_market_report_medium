def compute_composite_score(predicted, forecast_slope, reversal_tier, confidence):
    """
    All inputs normalized:
    - predicted: 0–100
    - forecast_slope: % change over 5d
    - reversal_tier: 'high', 'neutral', 'low'
    - confidence: 0–100
    """
    score = 0
    reasons = []

    # Base ML prediction
    score += predicted * 0.4
    reasons.append(f"ML Predicted: {predicted}")

    # Forecast slope: scale -5% to +5% into 0–20
    slope_score = max(min(forecast_slope, 5), -5) * 2
    score += slope_score
    reasons.append(f"Forecast Slope: {forecast_slope}%")

    # Reversal tier weight
    if reversal_tier == "low":
        score += 10
        reasons.append("Low reversal risk")
    elif reversal_tier == "high":
        score -= 10
        reasons.append("High reversal risk")

    # Confidence
    score += confidence * 0.2 / 100
    reasons.append(f"Confidence: {confidence}%")

    return round(max(0, min(score, 100)), 1), reasons

import os
import csv
from datetime import datetime

COMPOSITE_LOG = "logs/whispr_edge_composites.csv"

def log_composite_scores(scores):
    os.makedirs("logs", exist_ok=True)
    with open(COMPOSITE_LOG, "a", newline="") as f:
        writer = csv.writer(f)
        now = datetime.utcnow().isoformat()
        for entry in scores:
            writer.writerow([
                now,
                entry["ticker"],
                entry["edge_score"],
                "; ".join(entry["explanation"])
            ])

