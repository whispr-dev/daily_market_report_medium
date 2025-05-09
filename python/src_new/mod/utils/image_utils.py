"""
Utilities for image handling, primarily for converting matplotlib figures to base64.
"""
import base64
import io
import matplotlib.pyplot as plt
import traceback

import io

def fig_to_png_bytes(fig):
    """
    Convert a matplotlib figure to raw PNG bytes (not base64).
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf.read()