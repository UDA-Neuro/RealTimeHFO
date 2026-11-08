@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m realtimehfo %*
) else (
  py -3.12 -m realtimehfo %*
)
