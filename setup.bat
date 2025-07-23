@echo off
echo 🏛️ Auto-Museum Generator Setup Script
echo ======================================

REM Create virtual environment
echo Creating virtual environment...
python -m venv automuseum

REM Activate virtual environment
echo Activating virtual environment...
call automuseum\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
D:\Aries\Auto-Museum\auto-museum-generator\automuseum\Scripts\python.exe -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Create uploads directory
echo Creating uploads directory...
if not exist uploads mkdir uploads

REM Copy environment template
if not exist .env (
    echo Creating .env file from template...
    copy .env.template .env
    echo Please edit .env file with your API keys!
) else (
    echo .env file already exists.
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit the .env file with your Google API key
echo 2. Install and start Ollama: https://ollama.ai
echo 3. Pull the llama3 model: ollama pull llama3
echo 4. Run the application: python app.py
echo.
echo The application will be available at http://localhost:5000

pause