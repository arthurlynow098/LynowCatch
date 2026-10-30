@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" py -m venv .venv
if errorlevel 1 (
 pause
 exit /b
)
set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"
for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_*") do for /d %%F in ("%%D\ffmpeg-*") do set "PATH=%%F\bin;%PATH%"
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
 pause
 exit /b
)
start http://localhost:8765
".venv\Scripts\python.exe" server.py
pause
