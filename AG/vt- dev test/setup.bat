@echo off
REM Setup script for ML Inference Project
REM Run this script to set up the complete environment

echo ================================================================================
echo   ML INFERENCE SETUP - Schema-Validated Virtual Tagging
echo ================================================================================
echo.

REM Step 1: Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
python --version
echo.

REM Step 2: Create virtual environment
echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)
echo.

REM Step 3: Activate virtual environment and install dependencies
echo [3/6] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo.

REM Step 4: Create .env file from template
echo [4/6] Setting up configuration...
if not exist ".env" (
    copy .env.example .env
    echo Created .env file. Please edit it with your database credentials.
    echo.
    echo IMPORTANT: Edit .env file and set DB_PASSWORD before continuing.
    pause
) else (
    echo .env file already exists.
)
echo.

REM Step 5: Convert Excel to SQL
echo [5/6] Converting Excel file to SQL...
set /p convert_excel="Convert cloud_resource_tags_complete 1.xlsx to SQL? (y/n) [y]: "
if /i "%convert_excel%"=="" set convert_excel=y
if /i "%convert_excel%"=="y" (
    cd ..
    python excel_to_sql_converter.py
    cd "vt- dev test"
    echo.
)

REM Step 6: Database setup
echo [6/6] Database setup...
echo.
echo To complete setup:
echo   1. Ensure PostgreSQL is running
echo   2. Create database: psql -U postgres -c "CREATE DATABASE cloudtuner_db;"
echo   3. Load schema: psql -U postgres -d cloudtuner_db -f ../cloud_resource_tags_from_excel.sql
echo   4. Load ML functions: psql -U postgres -d cloudtuner_db -f ml_inference_config.sql
echo.

set /p run_db_setup="Run database setup now? (y/n) [n]: "
if /i "%run_db_setup%"=="y" (
    echo.
    echo Creating database...
    psql -U postgres -c "CREATE DATABASE cloudtuner_db;" 2>nul
    
    echo Loading cloud_resource_tags table...
    psql -U postgres -d cloudtuner_db -f "../cloud_resource_tags_from_excel.sql"
    
    echo Loading ML inference functions...
    psql -U postgres -d cloudtuner_db -f "ml_inference_config.sql"
    
    echo.
    echo Database setup complete!
)

echo.
echo ================================================================================
echo   SETUP COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo   1. Run tests: python python\test_ml_inference.py
echo   2. Try examples: python python\example_predictions.py
echo   3. Review documentation: README_ML_INFERENCE.md
echo.
echo To activate virtual environment: venv\Scripts\activate.bat
echo.
pause
