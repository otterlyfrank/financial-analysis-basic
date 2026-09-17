@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "URL=http://127.0.0.1:8501"
set "PY="

if not exist "app.py" goto :missing_files
if not exist "requirements.txt" goto :missing_files

py -3.12 -c "import sys" >nul 2>&1
if not errorlevel 1 (
  set "PY=py -3.12"
  goto :have_py
)
python3.12 -c "import sys" >nul 2>&1
if not errorlevel 1 (
  set "PY=python3.12"
  goto :have_py
)
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
  set "PY=%LocalAppData%\Programs\Python\Python312\python.exe"
  goto :have_py
)
python -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(3,12) else 1)" >nul 2>&1
if not errorlevel 1 (
  set "PY=python"
  goto :have_py
)

powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Install Python 3.12 from python.org (tick Add to PATH) and double-click again.','Cash P&L')"
echo Install Python 3.12 from python.org (tick Add to PATH) and double-click again.
pause
exit /b 1

:missing_files
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Keep Run Cash P&L.bat in the unzipped folder (next to app.py), then double-click again.','Cash P&L')"
echo Keep Run Cash P&L.bat in the unzipped folder (next to app.py), then double-click again.
pause
exit /b 1

:have_py
if not exist ".venv\Scripts\python.exe" (
  echo First run: creating .venv (can take a minute)...
  %PY% -m venv .venv
  if errorlevel 1 (
    powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Could not create .venv. Install Python 3.12 from python.org (tick Add to PATH) and double-click again.','Cash P&L')"
    pause
    exit /b 1
  )
)

echo Installing packages if needed...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show('Could not install Python packages. Read the window, then double-click again.','Cash P&L')"
  pause
  exit /b 1
)

start "" cmd /c "timeout /t 4 /nobreak >nul & start %URL%"
".venv\Scripts\python.exe" -m streamlit run app.py --server.address=127.0.0.1 --server.headless=true --browser.gatherUsageStats=false
if errorlevel 1 (
  echo Cash P&L failed to start.
  pause
  exit /b 1
)
exit /b 0
