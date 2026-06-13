@echo off
setlocal
cd /d "%~dp0"
echo [NOM] Checking MediaPipe compatibility...
python -c "import mediapipe as mp, sys; sys.exit(0 if (getattr(mp,'__version__','')=='0.10.14' and hasattr(mp,'solutions')) else 1)" >nul 2>nul
if errorlevel 1 (
  echo [NOM] Fixing MediaPipe to stable version 0.10.14...
  python -m pip install --user --upgrade --force-reinstall --no-cache-dir mediapipe==0.10.14 -q
)
echo [NOM] Installing dependencies (pip)...
python -m pip install --user -r "%~dp0requirements.txt" -q
if errorlevel 1 (
  echo [NOM] pip install failed. Check Python is on PATH.
  pause
  exit /b 1
)
echo [NOM] Starting app...
python "%~dp0main.py"
if errorlevel 1 pause
endlocal
