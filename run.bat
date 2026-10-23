@echo off
title OSTutor
cd /d "%~dp0"
set "PY=python"
if exist "%~dp0venv\Scripts\python.exe" set "PY=%~dp0venv\Scripts\python.exe"

echo ==========================================================
echo    OSTutor - Operating Systems Tutor (RAG)
echo    Akshat Jain (24BCE0380) and Vidit Basant Kumar (24BCE0388)
echo ==========================================================

curl -s http://127.0.0.1:11434/api/tags >nul 2>nul
if errorlevel 1 (
  echo [!] Ollama is not running: answers will be taken straight from the notes.
) else (
  echo [ok] Ollama is running: answers will be written by the local LLM.
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8003 " ^| findstr LISTENING') do taskkill /PID %%P /F >nul 2>nul
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8503 " ^| findstr LISTENING') do taskkill /PID %%P /F >nul 2>nul

echo [1/2] Starting backend on port 8003...
start "OSTutor Backend (port 8003)" cmd /s /k ""%PY%" -m uvicorn app:app --app-dir src --port 8003"
timeout /t 5 /nobreak >nul

echo [2/2] Starting web page on port 8503...
"%PY%" -m streamlit run src\streamlit_app.py --server.port 8503
