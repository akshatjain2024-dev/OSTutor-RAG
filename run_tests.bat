@echo off
title OSTutor - Tests
cd /d "%~dp0"
set "PY=python"
if exist "%~dp0venv\Scripts\python.exe" set "PY=%~dp0venv\Scripts\python.exe"
if not exist logs mkdir logs

echo [1/3] Search accuracy test (also rebuilds the index)...
"%PY%" tests\smoke_test.py > logs\smoke_test.log 2>&1
echo [2/3] Evaluation on 71 held-out questions...
"%PY%" dataset\eval_rag.py > logs\evaluation.log 2>&1
echo [3/3] Dataset checks...
"%PY%" dataset\validate.py > logs\dataset_check.log 2>&1

findstr /C:"accuracy" /C:"hit rate" /C:"hit@" /C:"F1" /C:"passed" /C:"Error" logs\smoke_test.log logs\evaluation.log logs\dataset_check.log
echo.
echo Full results are in the logs folder.
pause
