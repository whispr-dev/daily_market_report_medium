def calculate_whispr_edge_score(
    ticker,
    reversal=None,
    squeeze=False,
    rs_score=None,
    confluence=False
):
    score = 0
    reasons = []

    if reversal == "bullish":
        score += 20
        reasons.append("Daily reversal")

    if squeeze:
        score += 25
        reasons.append("Volatility squeeze")

    if rs_score is not None:
        # Normalize: +10 for beating benchmark by ≥5%
        bonus = min(max(rs_score * 4, 0), 20)  # scale and clip
        score += bonus
        if bonus > 0:
            reasons.append(f"Strong RS: +{bonus:.1f}")

    if confluence:
        score += 25
        reasons.append("Multi-timeframe agreement")

    final = min(round(score), 100)
    return final, reasons
