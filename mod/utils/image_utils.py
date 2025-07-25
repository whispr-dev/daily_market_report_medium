"""
Utilities for image handling, primarily for converting matplotlib figures to base64.
"""
import base64
import io
import matplotlib.pyplot as plt
import traceback

def img_to_base64(fig):
    """
    Utility to convert a Matplotlib figure to base64-encoded PNG.
    
    Args:
        fig: Matplotlib figure object
        
    Returns:
        str: Base64-encoded PNG string or None if conversion fails
    """
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)  # Close figure to free memory
        return img_data
    except Exception as e:
        print(f"Error in img_to_base64: {e}")
        traceback.print_exc()
        plt.close(fig)  # Ensure figure is closed even on error
        return None