@echo off
cd /d "C:\path\to\your\project" 
python main.py
python main.py >> daily_stonks.log 2>&1
