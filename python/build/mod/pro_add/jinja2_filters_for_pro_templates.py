"""
Custom Jinja2 filters for email templates.
"""
import locale
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/template_filters.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set locale for number formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except:
        logger.warning("Could not set locale to en_US. Using default locale.")

def format_number(value):
    """
    Format a number with thousands separators.
    
    Args:
        value: Number to format
        
    Returns:
        str: Formatted number string
    """
    try:
        if value is None:
            return "N/A"
        
        # Convert to float or int
        value = float(value)
        
        # Handle large numbers with K, M, B suffixes
        if value >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"
        elif value >= 1_000:
            return f"{value / 1_000:.1f}K"
        else:
            return locale.format_string("%.0f", value, grouping=True)
    except Exception as e:
        logger.error(f"Error formatting number: {e}")
        return str(value)

def format_price(value):
    """
    Format a price value with appropriate decimal places.
    
    Args:
        value: Price to format
        
    Returns:
        str: Formatted price string
    """
    try:
        if value is None:
            return "N/A"
        
        # Convert to float
        value = float(value)
        
        # Format based on magnitude
        if value >= 1000:
            # Large prices: $1,234.56
            return locale.format_string("%.2f", value, grouping=True)
        elif value >= 1:
            # Medium prices: $1.2345
            return locale.format_string("%.4f", value, grouping=True)
        else:
            # Small prices: $0.00001234
            # Count significant digits after initial zeros
            str_value = str(value)
            decimal_part = str_value.split('.')[-1] if '.' in str_value else ''
            
            # Count leading zeros in decimal part
            leading_zeros = 0
            for char in decimal_part:
                if char == '0':
                    leading_zeros += 1
                else:
                    break
            
            # Determine precision (leading zeros + 4 significant digits)
            precision = leading_zeros + 4
            format_str = f"%.{precision}f"
            
            return locale.format_string(format_str, value, grouping=True)
    except Exception as e:
        logger.error(f"Error formatting price: {e}")
        return str(value)

def format_date(value, format_str="%b %d, %Y"):
    """
    Format a date object or string.
    
    Args:
        value: Date to format (datetime or string)
        format_str: Format string
        
    Returns:
        str: Formatted date string
    """
    try:
        if value is None:
            return "N/A"
        
        # If value is already a string, try to parse it
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except:
                try:
                    value = datetime.strptime(value, "%Y-%m-%d")
                except:
                    return value  # Return as is if parsing fails
        
        # Format the datetime
        return value.strftime(format_str)
    except Exception as e:
        logger.error(f"Error formatting date: {e}")
        return str(value)

def format_percent(value, decimals=2):
    """
    Format a number as a percentage.
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    try:
        if value is None:
            return "N/A"
        
        # Convert to float
        value = float(value)
        
        # Format as percentage
        return f"{value:.{decimals}f}%"
    except Exception as e:
        logger.error(f"Error formatting percentage: {e}")
        return str(value)

def register_filters(env):
    """
    Register custom filters with Jinja2 environment.
    
    Args:
        env: Jinja2 Environment
    """
    env.filters['format_number'] = format_number
    env.filters['format_price'] = format_price
    env.filters['format_date'] = format_date
    env.filters['format_percent'] = format_percent
    logger.info("Registered custom Jinja2 filters")