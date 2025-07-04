@echo off
echo ========================================
echo Educational Chatbot Setup Script
echo ========================================
echo.

echo 1. Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)

echo 2. Activating virtual environment...
call venv\Scripts\activate.bat

echo 3. Upgrading pip...
python -m pip install --upgrade pip

echo 4. Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements
    pause
    exit /b 1
)

echo 5. Installing spaCy English model...
python -m spacy download en_core_web_sm
if %errorlevel% neq 0 (
    echo Failed to install spaCy model
    echo You can install it manually later with: python -m spacy download en_core_web_sm
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure XAMPP is running with MySQL
echo 2. Create database using database_setup.sql
echo 3. Run: python run.py
echo.
echo To activate the virtual environment in the future:
echo   venv\Scripts\activate.bat
echo.
pause
