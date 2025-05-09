from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_from_headlines(headlines):
    scores = []

    for hl in headlines:
        vs = analyzer.polarity_scores(hl)
        scores.append(vs["compound"])

    if not scores:
        return 0.0

    return round(sum(scores) / len(scores), 3)

def get_sample_sentiment(ticker="SPY"):
    try:
        # Replace with your news API or real headlines later
        headlines = [
            f"{ticker} rallies after earnings beat",
            f"{ticker} faces regulatory pressure",
            f"Analysts bullish on {ticker}'s long-term growth"
        ]
        return analyze_sentiment_from_headlines(headlines)
    except Exception as e:
        print(f"Sentiment error: {e}")
        return 0.0
