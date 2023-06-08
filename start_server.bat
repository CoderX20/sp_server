@echo off
set VIRTUAL_ENV_PATH=.\venv

call %VIRTUAL_ENV_PATH%\Scripts\activate.bat

echo "Starting Flask application..."
python app.py
