@echo off
echo Starting Daily Stonk Market Report generation...
cd /d "%~dp0"
echo Current directory: %CD%

REM Create a timestamp for the log
set TIMESTAMP=%date:~-4,4%-%date:~-7,2%-%date:~-10,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
REM Remove spaces in timestamp (in case of hours < 10)
set TIMESTAMP=%TIMESTAMP: =0%

REM Run the script and log both output and errors
echo Running Python script...
python main.py >> "logs\stonks_log_%TIMESTAMP%.log" 2>&1

if %ERRORLEVEL% EQU 0 (
  echo Script completed successfully.
) else (
  echo Script failed with error level %ERRORLEVEL%. Check the log for details.
)

echo Done!
pause