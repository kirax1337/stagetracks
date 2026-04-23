@echo off
echo Starting StageTracks...

start cmd /k "cd /d %~dp0backend && venv\Scripts\python.exe -m uvicorn server:app --reload --port 8000"
start powershell -NoExit -Command "cd '%~dp0frontend'; npm start"

start cmd /k "cd frontend && npm start"