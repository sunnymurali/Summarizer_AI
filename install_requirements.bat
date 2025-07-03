@echo off
REM AI Document Analysis - Windows Installation Script
REM This script installs all required dependencies for the application

echo 🚀 AI Document Analysis - Installing Dependencies
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo ✅ Python is available

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing Python packages...

python -m pip install fastapi==0.104.1
python -m pip install uvicorn==0.24.0
python -m pip install python-multipart==0.0.6
python -m pip install PyPDF2==3.0.1
python -m pip install python-docx==1.1.0
python -m pip install tiktoken==0.5.1
python -m pip install faiss-cpu==1.7.4
python -m pip install numpy==1.24.3
python -m pip install openai==1.3.3
python -m pip install pydantic==2.5.0
python -m pip install streamlit==1.28.1
python -m pip install requests==2.31.0
python -m pip install python-dotenv==1.0.0

echo ✅ All packages installed successfully!
echo.
echo 🔧 Next steps:
echo 1. Configure your Azure OpenAI credentials in .env file
echo 2. Run the application with: python start_services.py
echo 3. Open http://localhost:5000 in your browser
echo.
echo 📋 For detailed setup instructions, see README.md
pause