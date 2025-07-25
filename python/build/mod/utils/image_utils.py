"""
Utilities for image handling, primarily for converting matplotlib figures to various formats.
"""
import base64
import io
import matplotlib.pyplot as plt
import traceback
import hashlib
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/image_utils.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fig_to_png_bytes(fig):
    """
    Convert a matplotlib figure to raw PNG bytes (not base64).
    
    Args:
        fig: Matplotlib figure
        
    Returns:
        bytes: Raw PNG image data
    """
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.error(f"Error converting figure to PNG: {e}")
        traceback.print_exc()
        return None

def fig_to_base64(fig):
    """
    Convert a matplotlib figure to base64 for embedding in HTML.
    
    Args:
        fig: Matplotlib figure
        
    Returns:
        str: Base64-encoded PNG data
    """
    try:
        png_bytes = fig_to_png_bytes(fig)
        if png_bytes:
            return base64.b64encode(png_bytes).decode('utf-8')
        return None
    except Exception as e:
        logger.error(f"Error converting figure to base64: {e}")
        traceback.print_exc()
        return None

def create_placeholder_image(width=600, height=400, text="Image Placeholder"):
    """
    Create a placeholder image with specified text.
    
    Args:
        width: Image width
        height: Image height
        text: Text to display in the placeholder
        
    Returns:
        matplotlib.figure.Figure: Placeholder figure
    """
    try:
        fig, ax = plt.subplots(figsize=(width/100, height/100))
        ax.text(0.5, 0.5, text, ha='center', va='center', fontsize=14)
        ax.set_axis_off()
        fig.patch.set_facecolor('#1a1a1a')  # Dark background
        fig.tight_layout()
        return fig
    except Exception as e:
        logger.error(f"Error creating placeholder image: {e}")
        traceback.print_exc()
        return None

def add_watermark_to_image(fig, identifier, opacity=0.1):
    """
    Add a subtle watermark to a matplotlib figure.
    
    Args:
        fig: Matplotlib figure
        identifier: String identifier (email, name, etc.) for watermark
        opacity: Opacity of the watermark (0-1)
        
    Returns:
        matplotlib.figure.Figure: Figure with watermark
    """
    try:
        # Hash the identifier for privacy
        identifier_hash = hashlib.md5(identifier.encode()).hexdigest()[:8]
        watermark_text = f"DailyStonks-{identifier_hash}"
        
        # Add watermark text
        fig.text(
            0.5, 0.5,                           # Center position
            watermark_text,                     # Watermark text
            fontsize=20,                        # Font size
            color=f'rgba(255,255,255,{opacity})', # Color with opacity
            ha='center',                        # Horizontal alignment
            va='center',                        # Vertical alignment
            alpha=opacity,                      # Transparency
            rotation=45,                        # Rotation
            transform=fig.transFigure,          # Use figure coordinates
            zorder=-1                           # Behind all other elements
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        traceback.print_exc()
        return fig  # Return original figure if watermarking fails

def optimize_figure_for_email(fig, dpi=150):
    """
    Optimize figure settings for email display.
    
    Args:
        fig: Matplotlib figure
        dpi: Resolution (dots per inch)
        
    Returns:
        matplotlib.figure.Figure: Optimized figure
    """
    try:
        # Set figure DPI for good quality without excessive file size
        fig.dpi = dpi
        
        # Ensure figure has a dark background (for dark mode emails)
        fig.patch.set_facecolor('#1a1a1a')
        
        # Make sure all axes have white text
        for ax in fig.get_axes():
            ax.tick_params(colors='white')
            
            # Update labels
            ax.xaxis.label.set_color('white')

# Update title if present
            if ax.get_title():
                ax.set_title(ax.get_title(), color='white')
                
            # Handle axis scales and grids
            ax.grid(True, linestyle=':', color='#444444', alpha=0.5)
            
            # Ensure legend is readable if present
            if ax.get_legend():
                legend = ax.get_legend()
                frame = legend.get_frame()
                frame.set_facecolor('#333333')
                frame.set_edgecolor('#444444')
                for text in legend.get_texts():
                    text.set_color('white')
        
        # Adjust layout for better display
        fig.tight_layout()
        
        return fig
    except Exception as e:
        logger.error(f"Error optimizing figure for email: {e}")
        traceback.print_exc()
        return fig  # Return original figure if optimization fails

def compress_image_bytes(image_bytes, quality=85):
    """
    Compress image bytes to reduce file size (using PIL).
    
    Args:
        image_bytes: Raw image bytes
        quality: JPEG quality (0-100)
        
    Returns:
        bytes: Compressed image bytes
    """
    try:
        from PIL import Image
        
        # Open the image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Create output buffer
        output = io.BytesIO()
        
        # Save as optimized JPEG
        img.convert('RGB').save(
            output, 
            format='JPEG', 
            quality=quality, 
            optimize=True
        )
        
        # Return the compressed bytes
        output.seek(0)
        return output.read()
    except ImportError:
        logger.warning("PIL not installed, returning original image")
        return image_bytes
    except Exception as e:
        logger.error(f"Error compressing image: {e}")
        traceback.print_exc()
        return image_bytes  # Return original if compression fails

def generate_chart_filename(chart_type, identifier=None):
    """
    Generate a unique filename for chart images.
    
    Args:
        chart_type: Type of chart (e.g., 'candlestick', 'heatmap')
        identifier: Optional identifier for the chart
        
    Returns:
        str: Unique filename
    """
    import time
    import uuid
    
    # Generate timestamp
    timestamp = int(time.time())
    
    # Generate unique ID
    unique_id = str(uuid.uuid4())[:8]
    
    # Create filename components
    parts = ['dailystonks', chart_type]
    
    # Add identifier if provided
    if identifier:
        # Clean identifier (remove special chars)
        clean_id = ''.join(c for c in identifier if c.isalnum() or c in '_-')
        parts.append(clean_id)
    
    # Add timestamp and unique ID
    parts.extend([str(timestamp), unique_id])
    
    # Join with underscores and add extension
    return f"{'_'.join(parts)}.png"

def save_chart_to_disk(fig, chart_type, output_dir='charts', identifier=None):
    """
    Save a matplotlib figure to disk.
    
    Args:
        fig: Matplotlib figure
        chart_type: Type of chart (e.g., 'candlestick', 'heatmap')
        output_dir: Directory to save the chart in
        identifier: Optional identifier for the chart
        
    Returns:
        str: Path to saved file
    """
    import os
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        filename = generate_chart_filename(chart_type, identifier)
        filepath = os.path.join(output_dir, filename)
        
        # Save figure
        fig.savefig(filepath, format='png', bbox_inches='tight', dpi=150)
        
        logger.info(f"Chart saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving chart to disk: {e}")
        traceback.print_exc()
        return None

def add_copyright_notice(fig, year=None):
    """
    Add a copyright notice to a matplotlib figure.
    
    Args:
        fig: Matplotlib figure
        year: Year for copyright, defaults to current year
        
    Returns:
        matplotlib.figure.Figure: Figure with copyright
    """
    import datetime
    
    try:
        # Get current year if not provided
        if year is None:
            year = datetime.datetime.now().year
        
        # Add copyright text
        fig.text(
            0.99, 0.01,                       # Bottom right
            f"© {year} DailyStonks",          # Copyright text
            fontsize=8,                       # Small font
            color='rgba(255,255,255,0.5)',    # Semi-transparent white
            ha='right',                       # Right-aligned
            va='bottom',                      # Bottom-aligned
            alpha=0.5                         # Transparency
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error adding copyright notice: {e}")
        traceback.print_exc()
        return fig  # Return original figure if adding notice fails

# Testing functions
if __name__ == "__main__":
    # Create necessary directories
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Create a test figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot([0, 1, 2, 3, 4], [0, 3, 1, 4, 2])
    ax.set_title("Test Chart")
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    
    # Optimize for email
    fig = optimize_figure_for_email(fig)
    
    # Add watermark
    fig = add_watermark_to_image(fig, "test@example.com")
    
    # Add copyright
    fig = add_copyright_notice(fig)
    
    # Save to disk
    save_chart_to_disk(fig, "test", "test_charts")
    
    # Convert to PNG bytes
    png_bytes = fig_to_png_bytes(fig)
    
    # Convert to base64
    base64_data = fig_to_base64(fig)
    
    print(f"PNG size: {len(png_bytes) if png_bytes else 'Failed'} bytes")
    print(f"Base64 length: {len(base64_data) if base64_data else 'Failed'} chars")
    
    plt.show()