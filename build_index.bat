@echo off
title OSTutor - Build search index
cd /d "%~dp0"
set "PY=python"
if exist "%~dp0venv\Scripts\python.exe" set "PY=%~dp0venv\Scripts\python.exe"
if not exist logs mkdir logs

echo Rebuilding the search index from the data folder...
"%PY%" src\ingest.py > logs\build_index.log 2>&1
type logs\build_index.log
echo.
echo Done. Restart run.bat to use the new index.
pause
