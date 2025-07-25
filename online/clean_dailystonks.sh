#!/bin/bash

echo "[*] Removing redundant files..."

cd /home/wofl/whispr.dev/DailyStonks || { echo "Project folder not found."; exit 1; }

# Remove known dev clutter
rm -rf __pycache__ junk/ build/cache/ build/__pycache__

# Remove Python backup files
find . -type f \( -name "*.pyc" -o -name "*.pyo" -o -name "*.bak" -o -name "*.swp" -o -name "*.tmp" \) -exec rm -v {} \;

echo "[✓] Cleanup complete."
