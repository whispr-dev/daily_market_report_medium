@echo off
echo ===================================================
echo Fixing Python package structure for stock analyzer
echo ===================================================

echo.
echo 1. Creating __init__.py files...
echo # This file makes Python treat the directory as a package > "D:\code\repos\GitHub_Desktop\daily_stonk_market_report\mod\__init__.py"
echo Created: mod\__init__.py

echo # This file makes Python treat the directory as a package > "D:\code\repos\GitHub_Desktop\daily_stonk_market_report\mod\data\__init__.py"
echo Created: mod\data\__init__.py

echo # This file makes Python treat the directory as a package > "D:\code\repos\GitHub_Desktop\daily_stonk_market_report\mod\utils\__init__.py"
echo Created: mod\utils\__init__.py

echo.
echo 2. Fixing imports in fetcher.py...
set "fetcher_file=D:\code\repos\GitHub_Desktop\daily_stonk_market_report\mod\data\fetcher.py"

:: Create a temporary file
type nul > "%fetcher_file%.tmp"

:: Read the original file line by line
for /f "tokens=* delims=" %%a in ('type "%fetcher_file%"') do (
    :: Check if the line contains the relative import we want to fix
    echo %%a | findstr /c:"from ..utils.data_utils import" > nul
    if not errorlevel 1 (
        :: Replace the line with absolute import
        echo from mod.utils.data_utils import clean_yfinance_dataframe, fix_missing_values>> "%fetcher_file%.tmp"
    ) else (
        :: Keep the original line
        echo %%a>> "%fetcher_file%.tmp"
    )
)

:: Replace the original file with the temporary file
move /y "%fetcher_file%.tmp" "%fetcher_file%"
echo Fixed relative import in fetcher.py

echo.
echo ===================================================
echo Setup complete! Now try one of these methods:
echo.
echo OPTION 1: Run as a module (recommended)
echo   cd D:\code\repos\GitHub_Desktop\daily_stonk_market_report
echo   python -m mod.main_enhanced
echo.
echo OPTION 2: Install as a package
echo   cd D:\code\repos\GitHub_Desktop\daily_stonk_market_report
echo   pip install -e .
echo   python -m mod.main_enhanced
echo ===================================================

pause