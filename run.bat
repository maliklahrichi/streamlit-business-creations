@echo off
REM Windows launcher: double-click this file.
cd /d "%~dp0"
set PY=python
where python >nul 2>nul
if errorlevel 1 set PY=py -3
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.11 or newer from https://www.python.org/downloads/
  echo ^(tick "Add Python to PATH" during installation^), then run this file again.
  pause
  exit /b 1
)
%PY% -c "import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)"
if errorlevel 1 (
  echo Python 3.11 or newer is required. Install a recent version from https://www.python.org/downloads/
  pause
  exit /b 1
)
if not exist .venv (
  echo Creating the environment ^(first run only^)...
  %PY% -m venv .venv
)
call .venv\Scripts\activate.bat
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
  mkdir "%USERPROFILE%\.streamlit" 2>nul
  echo [general]> "%USERPROFILE%\.streamlit\credentials.toml"
  echo email = "">> "%USERPROFILE%\.streamlit\credentials.toml"
)
echo Installing packages ^(fast if already done^)...
python -m pip install -q -r requirements.txt
echo.
echo Starting the app... Close this window to stop it.
python -m streamlit run app.py
pause
