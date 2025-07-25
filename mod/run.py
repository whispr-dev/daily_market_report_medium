"""
Runner script for the daily market report generator.
This script sets up the Python path correctly before importing modules.
"""
import os
import sys

# Get the absolute path of the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Add the current directory to Python path to make package imports work
sys.path.insert(0, current_dir)

# Now import the main function and run it
from main_enhanced import main

if __name__ == "__main__":
    main()