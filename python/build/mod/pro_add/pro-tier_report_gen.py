"""
Enhanced Pro-Tier Report Generator for DailyStonks
Adds premium features for Pro subscribers
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime, timedelta
import logging
import os
import traceback
import json
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pro_features.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def generate_pro_features(report_data, subscriber_email=None):
    """
    Generate Pro-tier features to enhance the report.
    
    Args:
        report_data: Existing report data
        subscriber_email: Subscriber email for watermarking
        
    Returns:
        dict: Enhanced report data with Pro features
    """
    try:
        logger.info("Generating Pro-tier features")
        
        # Create a copy of the report data
        enhanced_data = report_data.copy()
        
        # Add Pro-tier features
        enhanced_data.update({
            'pro_features': True,
            'anomaly_detection': generate_anomaly_detection(),
            'volume_profile': generate_volume_profile(),
            'correlation_matrix': generate_correlation_matrix(),
            'options_analysis': generate_options_analysis(),
            'ai_insights': generate_ai_insights(),
            'sentiment_analysis': generate_sentiment_analysis(),
            'crypto_dashboard': generate_crypto_dashboard()
        })
        
        # Generate enhanced chart images
        enhanced_data['images'].update({
            'correlation_chart': generate_correlation_chart(subscriber_email),
            'volume_profile_chart': generate_volume_profile_chart(subscriber_email),
            'options_chart': generate_options_chart(subscriber_email),
            'sentiment_chart': generate_sentiment_chart(subscriber_email),
            'crypto_chart': generate_crypto_chart(subscriber_email)
        })
        
        logger.info("Pro-tier features generated successfully")
        
        return enhanced_data
        
    except Exception as e:
        logger.error(f"Error generating Pro-tier features: {e}")
        traceback.print_exc()
        return report_data  # Return original data if enhancement fails

def generate_anomaly_detection():
    """
    Generate anomaly detection analysis.
    
    Returns:
        dict: Anomaly detection results
    """
    try:
        # In a real implementation, this would use actual market data and algorithms
        # For now, we'll generate synthetic data for demonstration
        
        # List of major tickers
        tickers = ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA']
        
        # Generate random anomalies (approximately 30% of tickers)
        anomaly_count = max(1, len(tickers) // 3)
        anomaly_tickers = np.random.choice(tickers, anomaly_count, replace=False)
        
        # Generate anomaly data
        anomalies = []
        for ticker in anomaly_tickers:
            # Generate random anomaly type
            anomaly_types = ['Volume Spike', 'Price Gap', 'Volatility Expansion', 'Momentum Divergence']
            anomaly_type = np.random.choice(anomaly_types)
            
            # Generate random deviation percentage
            deviation = np.random.uniform(2.5, 15.0)
            
            # Generate random significance score (0-100)
            significance = np.random.uniform(60, 95)
            
            # Add to anomalies list
            anomalies.append({
                'ticker': ticker,
                'anomaly_type': anomaly_type,
                'deviation': deviation,
                'significance': significance,
                'detection_time': datetime.now().strftime('%Y-%m-%d'),
                'description': f"{ticker} showed abnormal {anomaly_type.lower()} pattern with {deviation:.1f}% deviation from expected behavior."
            })
        
        return {
            'anomalies': anomalies,
            'anomaly_count': len(anomalies),
            'monitored_tickers': len(tickers),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating anomaly detection: {e}")
        traceback.print_exc()
        return {'anomalies': [], 'anomaly_count': 0, 'monitored_tickers': 0}

def generate_volume_profile():
    """
    Generate volume profile analysis.
    
    Returns:
        dict: Volume profile results
    """
    try:
        # In a real implementation, this would use actual market data
        # For now, we'll generate synthetic data for demonstration
        
        # Generate price levels
        price_levels = np.linspace(400, 500, 20)  # Example price range for S&P 500 ETF
        
        # Generate volume profile (volumes at each price level)
        # Create a normal distribution centered around a random price level
        center_idx = np.random.randint(5, len(price_levels) - 5)
        volumes = np.random.normal(100, 30, len(price_levels))
        volumes = volumes * np.exp(-0.2 * np.abs(np.arange(len(price_levels)) - center_idx))
        volumes = volumes.astype(int)
        
        # Ensure volumes are positive
        volumes = np.maximum(volumes, 10)
        
        # Calculate value area (70% of volume)
        sorted_indices = np.argsort(volumes)[::-1]
        cumulative_volume = np.cumsum(volumes[sorted_indices])
        value_area_indices = sorted_indices[cumulative_volume <= 0.7 * cumulative_volume[-1]]
        
        value_area_high = price_levels[max(value_area_indices)]
        value_area_low = price_levels[min(value_area_indices)]
        point_of_control = price_levels[np.argmax(volumes)]
        
        # Create profile data
        profile_data = [
            {'price': float(price), 'volume': int(vol)}
            for price, vol in zip(price_levels, volumes)
        ]
        
        return {
            'profile_data': profile_data,
            'value_area_high': float(value_area_high),
            'value_area_low': float(value_area_low),
            'point_of_control': float(point_of_control),
            'total_volume': int(np.sum(volumes)),
            'timeframe': 'daily',
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating volume profile: {e}")
        traceback.print_exc()
        return {'profile_data': [], 'value_area_high': 0, 'value_area_low': 0, 'point_of_control': 0}

def generate_correlation_matrix():
    """
    Generate correlation matrix between assets.
    
    Returns:
        dict: Correlation matrix results
    """
    try:
        # List of assets
        assets = ['SPY', 'QQQ', 'GLD', 'TLT', 'USO', 'UUP', 'BTC-USD', 'ETH-USD']
        
        # Generate random correlation matrix
        # In a real implementation, this would calculate actual correlations
        np.random.seed(datetime.now().day)  # Semi-random seed for some consistency
        
        # Start with random values
        corr_matrix = np.random.uniform(-0.8, 0.8, (len(assets), len(assets)))
        
        # Make it symmetric
        corr_matrix = (corr_matrix + corr_matrix.T) / 2
        
        # Set diagonal to 1
        np.fill_diagonal(corr_matrix, 1)
        
        # Apply some meaningful correlations
        # SPY and QQQ are highly correlated
        corr_matrix[0, 1] = corr_matrix[1, 0] = 0.85 + np.random.uniform(-0.05, 0.05)
        
        # Gold and Treasuries often move together
        corr_matrix[2, 3] = corr_matrix[3, 2] = 0.6 + np.random.uniform(-0.1, 0.1)
        
        # Crypto assets are correlated with each other
        corr_matrix[6, 7] = corr_matrix[7, 6] = 0.75 + np.random.uniform(-0.1, 0.1)
        
        # USD and Gold often have negative correlation
        corr_matrix[2, 5] = corr_matrix[5, 2] = -0.4 + np.random.uniform(-0.15, 0.15)
        
        # Create matrix data
        matrix_data = []
        for i, asset1 in enumerate(assets):
            for j, asset2 in enumerate(assets):
                matrix_data.append({
                    'asset1': asset1,
                    'asset2': asset2,
                    'correlation': float(corr_matrix[i, j])
                })
        
        # Find strongest correlations
        strongest_positive = []
        strongest_negative = []
        
        for i in range(len(assets)):
            for j in range(i+1, len(assets)):  # Only check upper triangle of matrix
                corr = corr_matrix[i, j]
                pair = {'asset1': assets[i], 'asset2': assets[j], 'correlation': float(corr)}
                
                if corr > 0.5:
                    strongest_positive.append(pair)
                elif corr < -0.3:
                    strongest_negative.append(pair)
        
        # Sort by absolute correlation
        strongest_positive.sort(key=lambda x: x['correlation'], reverse=True)
        strongest_negative.sort(key=lambda x: x['correlation'])
        
        return {
            'matrix_data': matrix_data,
            'assets': assets,
            'strongest_positive': strongest_positive[:3],  # Top 3 positive correlations
            'strongest_negative': strongest_negative[:3],  # Top 3 negative correlations
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating correlation matrix: {e}")
        traceback.print_exc()
        return {'matrix_data': [], 'assets': [], 'strongest_positive': [], 'strongest_negative': []}

def generate_options_analysis():
    """
    Generate options market analysis.
    
    Returns:
        dict: Options analysis results
    """
    try:
        # In a real implementation, this would use actual options data
        # For now, we'll generate synthetic data for demonstration
        
        # List of major tickers
        tickers = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META']
        
        # Generate option activity data
        option_activity = []
        for ticker in tickers:
            # Generate random option type
            option_type = np.random.choice(['Call', 'Put'])
            
            # Generate random strike price
            base_price = 100 + np.random.uniform(-20, 80)  # Random base price
            strike_price = base_price * (1 + np.random.uniform(-0.1, 0.1))  # Strike within 10% of base
            
            # Generate random expiration
            days_to_expiry = np.random.choice([7, 14, 30, 45, 60, 90])
            expiry_date = (datetime.now() + timedelta(days=days_to_expiry)).strftime('%Y-%m-%d')
            
            # Generate random volume and open interest
            volume = int(np.random.uniform(1000, 50000))
            open_interest = int(volume * np.random.uniform(1.5, 5))
            
            # Generate implied volatility
            implied_volatility = np.random.uniform(0.15, 0.6)
            
            # Calculate put/call ratio
            put_call_ratio = np.random.uniform(0.5, 2.0)
            
            # Add to activity list
            option_activity.append({
                'ticker': ticker,
                'option_type': option_type,
                'strike_price': float(strike_price),
                'expiry_date': expiry_date,
                'days_to_expiry': days_to_expiry,
                'volume': volume,
                'open_interest': open_interest,
                'implied_volatility': float(implied_volatility),
                'put_call_ratio': float(put_call_ratio),
                'unusual_activity': volume > 20000 or implied_volatility > 0.4
            })
        
        # Sort by volume (descending)
        option_activity.sort(key=lambda x: x['volume'], reverse=True)
        
        # Calculate market-wide implied volatility
        market_iv = np.mean([item['implied_volatility'] for item in option_activity])
        
        # Calculate market-wide put/call ratio
        market_pc_ratio = np.mean([item['put_call_ratio'] for item in option_activity])
        
        return {
            'option_activity': option_activity,
            'market_implied_volatility': float(market_iv),
            'market_put_call_ratio': float(market_pc_ratio),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating options analysis: {e}")
        traceback.print_exc()
        return {'option_activity': [], 'market_implied_volatility': 0, 'market_put_call_ratio': 0}

def generate_ai_insights():
    """
    Generate AI-powered market insights.
    
    Returns:
        dict: AI insights
    """
    try:
        # In a real implementation, this would use actual ML/AI models
        # For now, we'll generate synthetic insights
        
        # Possible market themes
        market_themes = [
            'Interest Rate Sensitivity',
            'AI and Semiconductor Demand',
            'Consumer Discretionary Weakness',
            'Healthcare Innovation',
            'Energy Transition',
            'Supply Chain Resilience',
            'Financial Sector Stability',
            'Cloud Computing Growth',
            'Electric Vehicle Adoption',
            'Commodity Price Pressure'
        ]
        
        # Select random themes
        selected_themes = np.random.choice(market_themes, 3, replace=False)
        
        # Generate insights for each theme
        insights = []
        for theme in selected_themes:
            # Generate random confidence score
            confidence = np.random.uniform(65, 95)
            
            # Generate random impact score
            impact = np.random.uniform(3, 8)
            
            # Generate timeframe
            timeframe = np.random.choice(['Short-term', 'Medium-term', 'Long-term'])
            
            # Generate affected sectors
            sectors = [
                'Technology', 'Financials', 'Healthcare', 'Consumer Discretionary',
                'Consumer Staples', 'Energy', 'Materials', 'Industrials',
                'Utilities', 'Real Estate', 'Communication Services'
            ]
            affected_sectors = np.random.choice(sectors, np.random.randint(2, 4), replace=False)
            
            # Generate insight description based on theme
            if theme == 'Interest Rate Sensitivity':
                description = "Our AI models indicate heightened sensitivity to interest rate fluctuations across rate-sensitive sectors, with increasing correlation between Fed policy signals and market movements."
            elif theme == 'AI and Semiconductor Demand':
                description = "Data center and AI chip demand continue to show acceleration beyond seasonal patterns, with supply constraints potentially impacting availability in the next quarter."
            elif theme == 'Consumer Discretionary Weakness':
                description = "Consumer spending patterns show early signs of weakness in discretionary categories, with credit card transaction data indicating reduced purchase frequency."
            elif theme == 'Healthcare Innovation':
                description = "Recent FDA approval velocity and clinical trial successes suggest an accelerating innovation cycle in targeted therapeutics and AI-assisted diagnostics."
            elif theme == 'Energy Transition':
                description = "Capital allocation patterns suggest utilities and traditional energy companies are accelerating renewable investments beyond regulatory requirements, potentially pressuring margins short-term."
            elif theme == 'Supply Chain Resilience':
                description = "Alternative data indicates improving inventory positions and reduced shipping delays across manufacturing sectors, potentially lowering input cost pressures."
            elif theme == 'Financial Sector Stability':
                description = "Interbank lending metrics and credit default swap spreads suggest reduced systemic risk perceptions within the financial sector despite recent volatility."
            elif theme == 'Cloud Computing Growth':
                description = "Enterprise cloud migration continues to accelerate with AI workloads driving higher-than-forecast computing demand across major providers."
            elif theme == 'Electric Vehicle Adoption':
                description = "Registration data and charging network utilization suggest EV adoption is reaching inflection points in major urban markets ahead of consensus expectations."
            elif theme == 'Commodity Price Pressure':
                description = "Satellite imagery of key mining operations and shipping data indicate potential supply constraints that could drive commodity price volatility in coming months."
            else:
                description = f"Our AI models have identified {theme} as a significant market driver with potential to impact asset pricing models in the coming quarter."
            
            insights.append({
                'theme': theme,
                'description': description,
                'confidence': float(confidence),
                'impact': float(impact),
                'timeframe': timeframe,
                'affected_sectors': list(affected_sectors)
            })
        
        # Generate trading signals
        potential_signals = [
            {'signal': 'Relative Strength Momentum', 'direction': 'Bullish', 'lookback': '30 days'},
            {'signal': 'Mean Reversion', 'direction': 'Bearish', 'lookback': '14 days'},
            {'signal': 'Volume Pattern Recognition', 'direction': 'Bullish', 'lookback': '21 days'},
            {'signal': 'Volatility Expansion', 'direction': 'Neutral', 'lookback': '10 days'},
            {'signal': 'Sentiment Analysis', 'direction': 'Bullish', 'lookback': '7 days'},
            {'signal': 'Technical Pattern Detection', 'direction': 'Bearish', 'lookback': '90 days'},
            {'signal': 'Options Flow Analysis', 'direction': 'Bullish', 'lookback': '5 days'},
            {'signal': 'Sector Rotation', 'direction': 'Neutral', 'lookback': '60 days'}
        ]
        
        # Select random signals
        selected_signals = np.random.choice(
            potential_signals,
            np.random.randint(2, 5),
            replace=False
        )
        signals = [dict(s) for s in selected_signals]
        
        return {
            'insights': insights,
            'signals': signals,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        traceback.print_exc()
        return {'insights': [], 'signals': []}

def generate_sentiment_analysis():
    """
    Generate sentiment analysis of market news and social media.
    
    Returns:
        dict: Sentiment analysis results
    """
    try:
        # In a real implementation, this would analyze actual news and social data
        # For now, we'll generate synthetic data
        
        # List of major tickers
        tickers = ['SPY', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA']
        
        # Generate sentiment data for each ticker
        sentiment_data = []
        for ticker in tickers:
            # Generate random sentiment scores
            news_sentiment = np.random.normal(0, 0.5)  # Normal distribution around 0
            news_sentiment = max(min(news_sentiment, 1), -1)  # Clamp to [-1, 1]
            
            social_sentiment = news_sentiment + np.random.normal(0, 0.3)  # Correlated with news but with noise
            social_sentiment = max(min(social_sentiment, 1), -1)  # Clamp to [-1, 1]
            
            # Generate random volume
            news_volume = int(np.random.uniform(5, 100))
            social_volume = int(np.random.uniform(50, 5000))
            
            # Generate sentiment change
            sentiment_change = np.random.normal(0, 0.2)
            
            # Add to sentiment data
            sentiment_data.append({
                'ticker': ticker,
                'news_sentiment': float(news_sentiment),
                'social_sentiment': float(social_sentiment),
                'combined_sentiment': float((news_sentiment + social_sentiment) / 2),
                'news_volume': news_volume,
                'social_volume': social_volume,
                'sentiment_change_24h': float(sentiment_change),
                'noteworthy': abs(sentiment_change) > 0.3 or abs(news_sentiment) > 0.7
            })
        
        # Sort by absolute combined sentiment (most extreme first)
        sentiment_data.sort(key=lambda x: abs(x['combined_sentiment']), reverse=True)
        
        # Generate trending topics (keywords from news/social)
        trending_topics = []
        potential_topics = [
            'Earnings', 'Fed', 'Inflation', 'Interest Rates', 'GDP',
            'Unemployment', 'AI', 'Layoffs', 'Acquisitions', 'Regulations',
            'Dividends', 'Stock Splits', 'IPOs', 'Crypto', 'Options',
            'Housing', 'Manufacturing', 'Consumer Spending', 'Trade', 'Commodities'
        ]
        
        selected_topics = np.random.choice(potential_topics, 5, replace=False)
        for topic in selected_topics:
            # Generate random volume and sentiment
            volume = int(np.random.uniform(1000, 50000))
            sentiment = np.random.normal(0, 0.5)
            sentiment = max(min(sentiment, 1), -1)  # Clamp to [-1, 1]
            
            trending_topics.append({
                'topic': topic,
                'volume': volume,
                'sentiment': float(sentiment),
                'trending_score': int(np.random.uniform(60, 100))
            })
        
        # Sort by volume
        trending_topics.sort(key=lambda x: x['volume'], reverse=True)
        
        return {
            'sentiment_data': sentiment_data,
            'trending_topics': trending_topics,
            'market_sentiment': float(np.mean([item['combined_sentiment'] for item in sentiment_data])),
            'sentiment_breadth': float(np.std([item['combined_sentiment'] for item in sentiment_data])),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating sentiment analysis: {e}")
        traceback.print_exc()
        return {'sentiment_data': [], 'trending_topics': [], 'market_sentiment': 0}

def generate_crypto_dashboard():
    """
    Generate cryptocurrency market dashboard.
    
    Returns:
        dict: Crypto dashboard data
    """
    try:
        # In a real implementation, this would use actual crypto market data
        # For now, we'll generate synthetic data
        
        # List of cryptocurrencies
        cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'MATIC', 'LINK']
        
        # Base prices (roughly realistic as of late 2024)
        base_prices = {
            'BTC': 60000 + np.random.uniform(-5000, 5000),
            'ETH': 3000 + np.random.uniform(-300, 300),
            'SOL': 150 + np.random.uniform(-20, 20),
            'XRP': 0.7 + np.random.uniform(-0.1, 0.1),
            'ADA': 0.5 + np.random.uniform(-0.05, 0.05),
            'DOGE': 0.1 + np.random.uniform(-0.02, 0.02),
            'MATIC': 0.8 + np.random.uniform(-0.1, 0.1),
            'LINK': 14 + np.random.uniform(-2, 2)
        }
        
        # Generate crypto data
        crypto_data = []
        for crypto in cryptos:
            # Get base price
            price = base_prices.get(crypto, 100)
            
            # Generate 24h percent change
            percent_change = np.random.normal(0, 5)  # Normal distribution around 0 with 5% std dev
            
            # Generate volume
            volume = price * np.random.uniform(10000, 1000000)
            
            # Generate market cap
            circulating_supply = {
                'BTC': 19.5e6, 'ETH': 120e6, 'SOL': 430e6, 'XRP': 50e9,
                'ADA': 35e9, 'DOGE': 140e9, 'MATIC': 9e9, 'LINK': 550e6
            }
            supply = circulating_supply.get(crypto, 1e9)
            market_cap = price * supply
            
            # Generate dominance
            dominance = 0  # Will calculate after all entries are created
            
            # Generate fear/greed index (0-100)
            fear_greed = np.random.uniform(20, 80)
            
            # Add to crypto data
            crypto_data.append({
                'symbol': crypto,
                'price': float(price),
                'percent_change_24h': float(percent_change),
                'volume_24h': float(volume),
                'market_cap': float(market_cap),
                'dominance': dominance,
                'fear_greed_index': int(fear_greed)
            })
        
        # Calculate total market cap
        total_market_cap = sum(c['market_cap'] for c in crypto_data)
        
        # Calculate dominance for each crypto
        for crypto in crypto_data:
            crypto['dominance'] = float(crypto['market_cap'] / total_market_cap * 100)
        
        # Sort by market cap (descending)
        crypto_data.sort(key=lambda x: x['market_cap'], reverse=True)
        
        # Calculate market-wide fear/greed index (weighted by market cap)
        market_fear_greed = sum(c['fear_greed_index'] * c['market_cap'] for c in crypto_data) / total_market_cap
        
        return {
            'crypto_data': crypto_data,
            'total_market_cap': float(total_market_cap),
            'btc_dominance': float(next(c['dominance'] for c in crypto_data if c['symbol'] == 'BTC')),
            'market_fear_greed': int(market_fear_greed),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating crypto dashboard: {e}")
        traceback.print_exc()
        return {'crypto_data': [], 'total_market_cap': 0, 'btc_dominance': 0, 'market_fear_greed': 50}

def generate_correlation_chart(subscriber_email=None):
    """
    Generate correlation matrix chart.
    
    Args:
        subscriber_email: Subscriber email for watermarking
        
    Returns:
        bytes: PNG image bytes
    """
    try:
        # Get correlation data
        correlation_data = generate_correlation_matrix()
        
        # Extract assets and create correlation matrix
        assets = correlation_data['assets']
        matrix_data = correlation_data['matrix_data']
        
        # Create matrix
        n = len(assets)
        corr_matrix = np.zeros((n, n))
        
        for item in matrix_data:
            i = assets.index(item['asset1'])
            j = assets.index(item['asset2'])
            corr_matrix[i, j] = item['correlation']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create heatmap
        cmap = plt.cm.RdBu_r  # Red-White-Blue colormap, reversed
        im = ax.imshow(corr_matrix, cmap=cmap, vmin=-1, vmax=1)
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Correlation", rotation=-90, va="bottom")
        
        # Set ticks and labels
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(assets)
        ax.set_yticklabels(assets)
        
        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add correlation values to cells
        for i in range(n):
            for j in range(n):
                text = ax.text(j, i, f"{corr_matrix[i, j]:.2f}",
                               ha="center", va="center", color="white" if abs(corr_matrix[i, j]) > 0.5 else "black")
        
        # Set title and style
        ax.set_title("Asset Correlation Matrix")
        fig.tight_layout()
        
        # Add watermark if email provided
        if subscriber_email:
            # Hash email for privacy
            email_hash = hashlib.md5(subscriber_email.encode()).hexdigest()[:8]
            watermark_text = f"DailyStonks-{email_hash}"
            
            # Add watermark with low opacity
            fig.text(0.5, 0.5, watermark_text,
                     fontsize=20, color='white',
                     ha='center', va='center', alpha=0.1,
                     rotation=45, transform=fig.transFigure)
        
        # Convert to PNG bytes
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, facecolor='#1b1b1b')
        buf.seek(0)
        
        # Close figure to free memory
        plt.close(fig)
        
        return buf.read()
        
    except Exception as e:
        logger.error(f"Error generating correlation chart: {e}")
        traceback.print_exc()
        
        # Create error chart
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Error generating correlation chart",
                ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        
        # Convert to PNG bytes
        buf = io.BytesIO()
        fig.savefig(buf, format='png', facecolor='#1a1a1a')
        buf.seek(0)
        
        # Close figure to free memory
        plt.close(fig)
        
        return buf.read()
        
    except Exception as e:
        logger.error(f"Error generating correlation chart: {e}")
        traceback.print_exc()
        return None

def generate_volume_profile_chart(subscriber_email=None):
    """
    Generate volume profile chart.
    
    Args:
        subscriber_email: Subscriber email for watermarking
        
    Returns:
        bytes: PNG image bytes
    """
    try:
        # Get volume profile data
        profile_data = generate_volume_profile()
        
        # Extract price levels and volumes
        prices = [item['price'] for item in profile_data['profile_data']]
        volumes = [item['volume'] for item in profile_data['profile_data']]
        
        # Get key levels
        value_area_high = profile_data['value_area_high']
        value_area_low = profile_data['value_area_low']
        point_of_control = profile_data['point_of_control']
        
        # Create figure with dark background
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#1b1b1b')
        ax.set_facecolor('#1b1b1b')
        
        # Plot horizontal volume bars
        ax.barh(prices, volumes, height=prices[1]-prices[0], color='#66ccff', alpha=0.7)
        
        # Add key levels
        ax.axhline(y=value_area_high, color='#4dfd5d', linestyle='-', linewidth=1.5, 
                   label=f'Value Area High: {value_area_high:.2f}')
        ax.axhline(y=value_area_low, color='#fd4d4d', linestyle='-', linewidth=1.5,
                   label=f'Value Area Low: {value_area_low:.2f}')
        ax.axhline(y=point_of_control, color='#ffaa00', linestyle='-', linewidth=2,
                   label=f'Point of Control: {point_of_control:.2f}')
        
        # Add labels and title
        ax.set_title('Volume Profile Analysis', fontsize=16, color='white')
        ax.set_xlabel('Volume', fontsize=12, color='white')
        ax.set_ylabel('Price', fontsize=12, color='white')
        
        # Add legend
        ax.legend(loc='upper right', facecolor='#333333')
        
        # Add grid
        ax.grid(True, linestyle=':', color='#444444', alpha=0.5)
        
        # Add watermark if email provided
        if subscriber_email:
            # Hash email for privacy
            email_hash = hashlib.md5(subscriber_email.encode()).hexdigest()[:8]
            watermark_text = f"DailyStonks-{email_hash}"
            
            # Add watermark with low opacity
            fig.text(0.5, 0.5, watermark_text,
                     fontsize=20, color='white',
                     ha='center', va='center', alpha=0.1,
                     rotation=45, transform=fig.transFigure)
        
        # Convert to PNG bytes
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        
        # Close figure to free memory
        plt.close(fig)
        
        return buf.read()
        
    except Exception as e:
        logger.error(f"Error generating volume profile chart: {e}")
        traceback.print_exc()
        return None

def generate_options_chart(subscriber_email=None):
    """
    Generate options analysis chart.
    
    Args:
        subscriber_email: Subscriber email for watermarking
        
    Returns:
        bytes: PNG image bytes
    """
    try:
        # Get options data
        options_data = generate_options_analysis()
        
        # Extract option activity
        option_activity = options_data['option_activity']
        
        # Create figure with two subplots (IV and volume)
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1]})
        fig.patch.set_facecolor('#1b1b1b')
        
        # Prepare data for plots
        tickers = [item['ticker'] for item in option_activity]
        iv_values = [item['implied_volatility'] for item in option_activity]
        volumes = [item['volume'] for item in option_activity]
        colors = ['#4dfd5d' if item['option_type'] == 'Call' else '#fd4d4d' for item in option_activity]
        
        # Plot implied volatility
        ax1.bar(tickers, iv_values, color=colors, alpha=0.7)
        ax1.set_title('Implied Volatility by Ticker', fontsize=14, color='white')
        ax1.set_ylabel('Implied Volatility', fontsize=12, color='white')
        ax1.grid(True, linestyle=':', color='#444444', alpha=0.5)
        ax1.set_facecolor('#1b1b1b')
        
        # Plot volume
        ax2.bar(tickers, volumes, color=colors, alpha=0.7)
        ax2.set_title('Option Volume by Ticker', fontsize=14, color='white')
        ax2.set_ylabel('Volume', fontsize=12, color='white')
        ax2.grid(True, linestyle=':', color='#444444', alpha=0.5)
        ax2.set_facecolor('#1b1b1b')
        
        # Format y-axis for volume (K for thousands, M for millions)
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{x/1000:.0f}K" if x < 1000000 else f"{x/1000000:.1f}M"))
        
        # Add market-wide metrics as text
        market_iv = options_data['market_implied_volatility']
        market_pc_ratio = options_data['market_put_call_ratio']
        
        text = f"Market Implied Volatility: {market_iv:.2f}\nMarket Put/Call Ratio: {market_pc_ratio:.2f}"
        fig.text(0.02, 0.02, text, fontsize=12, color='white')
        
        # Create color legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#4dfd5d', edgecolor='white', alpha=0.7, label='Calls'),
            Patch(facecolor='#fd4d4d', edgecolor='white', alpha=0.7, label='Puts')
        ]
        fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.99, 0.99), facecolor='#333333')
        
        # Add watermark if email provided
        if subscriber_email:
            # Hash email for privacy
            email_hash = hashlib.md5(subscriber_email.encode()).hexdigest()[:8]
            watermark_text = f"DailyStonks-{email_hash}"
            
            # Add watermark with low opacity
            fig.text(0.5, 0.5, watermark_text,
                     fontsize=20, color='white',
                     ha='center', va='center', alpha=0.1,
                     rotation=45, transform=fig.transFigure)
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to PNG bytes
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        
        # Close figure to free memory
        plt.close(fig)
        
        return buf.read()
        
    except Exception as e:
        logger.error(f"Error generating options chart: {e}")
        traceback.print_exc()
        return None

def generate_sentiment_chart(subscriber_email=None):
    """
    Generate sentiment analysis chart.
    
    Args:
        subscriber_email: Subscriber email for watermarking
        
    Returns:
        bytes: PNG image bytes
    """
    try:
        # Get sentiment data
        sentiment_data = generate_sentiment_analysis()
        
        # Extract ticker sentiment data
        ticker_data = sentiment_data['sentiment_data']
        
        # Create figure with two subplots
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [2, 1]})
        fig.patch.set_facecolor('#1b1b1b')
        
        # Prepare data for sentiment plot
        tickers = [item['ticker'] for item in ticker_data]
        news_sentiment = [item['news_sentiment'] for item in ticker_data]
        social_sentiment = [item['social_sentiment'] for item in ticker_data]
        
        # Set bar width
        width = 0.35
        x = np.arange(len(tickers))
        
        # Plot sentiment comparison
        ax1.bar(x - width/2, news_sentiment, width, label='News Sentiment', color='#66ccff', alpha=0.7)
        ax1.bar(x + width/2, social_sentiment, width, label='Social Sentiment', color='#ff66cc', alpha=0.7)
        
        # Add horizontal line at zero
        ax1.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
        
        # Configure sentiment plot
        ax1.set_title('News vs Social Media Sentiment', fontsize=14, color='white')
        ax1.set_ylabel('Sentiment (-1 to +1)', fontsize=12, color='white')
        ax1.set_xticks(x)
        ax1.set_xticklabels(tickers)
        ax1.legend(facecolor='#333333')
        ax1.grid(True, linestyle=':', color='#444444', alpha=0.5)
        ax1.set_facecolor('#1b1b1b')
        
        # Plot trending topics
        trending_topics = sentiment_data['trending_topics']
        topics = [item['topic'] for item in trending_topics]
        sentiment_scores = [item['sentiment'] for item in trending_topics]
        trending_scores = [item['trending_score'] for item in trending_topics]
        
        # Create color map based on sentiment
        colors = ['#fd4d4d' if s < -0.3 else '#ffaa00' if s < 0.3 else '#4dfd5d' for s in sentiment_scores]
        
        # Plot trending topics as horizontal bars
        y_pos = np.arange(len(topics))
        ax2.barh(y_pos, trending_scores, color=colors, alpha=0.7)
        
        # Configure trending topics plot
        ax2.set_title('Trending Topics by Sentiment', fontsize=14, color='white')
        ax2.set_xlabel('Trending Score', fontsize=12, color='white')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(topics)
        ax2.grid(True, linestyle=':', color='#444444', alpha=0.5)
        ax2.set_facecolor('#1b1b1b')
        
        # Add market sentiment as text
        market_sentiment = sentiment_data['market_sentiment']
        sentiment_text = "Bearish" if market_sentiment < -0.3 else "Neutral" if market_sentiment < 0.3 else "Bullish"
        sentiment_color = "#fd4d4d" if market_sentiment < -0.3 else "#ffaa00" if market_sentiment < 0.3 else "#4dfd5d"
        
        text = f"Overall Market Sentiment: {sentiment_text} ({market_sentiment:.2f})"
        fig.text(0.5, 0.02, text, fontsize=14, color=sentiment_color, ha='center')
        
        # Add watermark if email provided
        if subscriber_email:
            # Hash email for privacy
            email_hash = hashlib.md5(subscriber_email.encode()).hexdigest()[:8]
            watermark_text = f"DailyStonks-{email_hash}"
            
            # Add watermark with low opacity
            fig.text(0.5, 0.5, watermark_text,
                     fontsize=20, color='white',
                     ha='center', va='center', alpha=0.1,
                     rotation=45, transform=fig.transFigure)
        
        # Adjust layout
        fig.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Convert to PNG bytes
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        
        # Close figure to free memory
        plt.close(fig)
        
        return buf.read()
        
    except Exception as e:
        logger.error(f"Error generating sentiment chart: {e}")
        traceback.print_exc()
        return None

def generate_crypto_chart(subscriber_email=None):
    """
    Generate cryptocurrency market chart.
    
    Args:
        subscriber_email: Subscriber email for watermarking
        
    Returns:
        bytes: PNG image bytes
    """
    try:
        # Get crypto data
        crypto_data = generate_crypto_dashboard()
        
        # Extract crypto market data
        market_data = crypto_data['crypto_data']
        
        # Create figure with two subplots
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1, 1]})
        fig.patch.set_facecolor('#1b1b1b')
        
        # Prepare data for price change plot
        symbols = [item['symbol'] for item in market_data]
        changes = [item['percent_change_24h'] for item in market_data]
        
        # Set colors based on change direction
        colors = ['#4dfd5d' if c >= 0 else '#fd4d4d' for c in changes]
        
        # Plot price changes
        ax1.bar(symbols, changes, color=colors, alpha=0.7)
        
        # Add horizontal line at zero
        ax1.axhline(y=0, color='white', linestyle='-', linewidth=0.5)
        
        # Configure price change plot
        ax1.set_title('24-Hour Price Change (%)', fontsize=14, color='white')
        ax1.set_ylabel('Percent Change', fontsize=12, color='white')
        ax1.grid(True, linestyle=':', color='#444444', alpha=0.5)
        ax1.set_facecolor('#1b1b1b')
        
        # Prepare data for market cap plot (pie chart)
        market_caps = [item['market_cap'] for item in market_data]
        dominance = [item['dominance'] for item in market_data]
        
        # Plot market cap distribution
        wedges, texts, autotexts = ax2.pie(
            market_caps, 
            labels=symbols, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=plt.cm.viridis(np.linspace(0, 1, len(symbols))),
            wedgeprops={'alpha': 0.7}
        )
        
        # Configure market cap plot
        ax2.set_title('Market Cap Distribution', fontsize=14, color='white')
        ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Format autotext (percentage labels)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
        
        # Add fear/greed index as text
        fear_greed = crypto_data['market_fear_greed']
        fear_greed_text = "Extreme Fear" if fear_greed < 25 else "Fear" if fear_greed < 40 else \
                           "Neutral" if fear_greed < 60 else "Greed" if fear_greed < 75 else "Extreme Greed"
        fear_greed_color = "#fd4d4d" if fear_greed < 40 else "#ffaa00" if fear_greed < 60 else "#4dfd5d"
        
        text = f"Crypto Fear & Greed Index: {fear_greed} ({fear_greed_text})"
        fig.text(0.5, 0.02, text, fontsize=14, color=fear_greed_color, ha='center')
        
        # Add watermark if email provided
        if subscriber_email:
            # Hash email for privacy
            email_hash = hashlib.md5(subscriber_email.encode()).hexdigest()[:8]
            watermark_text = f"DailyStonks-{email_hash}"
            
            # Add watermark with low opacity
            fig.text(0.5, 0.5, watermark_text,
                     fontsize=20, color='white',
                     ha='center', va='center', alpha=0.1,
                     rotation=45, transform=fig.transFigure)
        
        # Adjust layout
        fig.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        # Convert to PNG bytes
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        
        # Close figure to free memory
        plt.close(fig)
        
        return buf.read()
        
    except Exception as e:
        logger.error(f"Error generating crypto chart: {e}")
        traceback.print_exc()
        return None

# For testing
if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("charts", exist_ok=True)
    
    # Test the Pro features generation
    sample_report_data = {
        'images': {}
    }
    
    enhanced_data = generate_pro_features(sample_report_data, "test@example.com")
    
    # Save charts to disk for inspection
    for chart_name, chart_bytes in enhanced_data['images'].items():
        if chart_bytes:
            with open(f"charts/{chart_name}.png", "wb") as f:
                f.write(chart_bytes)
            print(f"Saved {chart_name}.png")
    
    print("Pro features generation completed")