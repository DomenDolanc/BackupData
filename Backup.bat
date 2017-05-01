@echo off
if not "%minimized%"=="" goto :minimized
set minimized=true
start /min cmd /C "%~dpnx0"
goto :EOF
:minimized
cd "C:\Users\domen_000\Documents\Projects\Python projects\Backup data"
py "main.py" %*