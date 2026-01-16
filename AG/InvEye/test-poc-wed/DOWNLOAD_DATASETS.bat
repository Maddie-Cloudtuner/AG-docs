@echo off
:: ============================================================================
:: 🔥 👊 👤 Dataset Downloader - Windows Batch Script
:: ============================================================================
:: Easy one-click dataset download for Fire, Fight, and Face Detection
:: 
:: Usage: Double-click this file or run from command prompt
:: ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║   🔥 👊 👤 AUTOMATED DATASET DOWNLOADER FOR AI TRAINING 👤 👊 🔥   ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Navigate to script directory
cd /d "%~dp0"

:: Install dependencies
echo.
echo 📦 Installing required packages...
pip install roboflow kaggle requests tqdm gdown --quiet

:: Check for Roboflow API Key
if "%ROBOFLOW_API_KEY%"=="" (
    echo.
    echo ⚠️  ROBOFLOW_API_KEY not set!
    echo    Get your FREE API key from: https://app.roboflow.com/account/api
    echo.
    set /p ROBOFLOW_API_KEY="Enter your Roboflow API key (or press Enter to skip): "
)

:: Show menu
:menu
echo.
echo ═══════════════════════════════════════════════════════════════════
echo                         SELECT DOWNLOAD OPTION
echo ═══════════════════════════════════════════════════════════════════
echo.
echo   [1] Download ALL datasets (Fire + Fight + Face)
echo   [2] Download FIRE/SMOKE datasets only
echo   [3] Download FIGHT/VIOLENCE datasets only
echo   [4] Download FACE DETECTION datasets only
echo   [5] List available datasets (no download)
echo   [6] Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto download_all
if "%choice%"=="2" goto download_fire
if "%choice%"=="3" goto download_fight
if "%choice%"=="4" goto download_face
if "%choice%"=="5" goto list_datasets
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
goto menu

:download_all
echo.
echo 📥 Downloading ALL datasets...
if not "%ROBOFLOW_API_KEY%"=="" (
    python download_datasets.py --all --roboflow-key %ROBOFLOW_API_KEY%
) else (
    python download_datasets.py --all --skip-roboflow
)
goto complete

:download_fire
echo.
echo 🔥 Downloading FIRE/SMOKE datasets...
if not "%ROBOFLOW_API_KEY%"=="" (
    python download_datasets.py --fire --roboflow-key %ROBOFLOW_API_KEY%
) else (
    python download_datasets.py --fire --skip-roboflow
)
goto complete

:download_fight
echo.
echo 👊 Downloading FIGHT/VIOLENCE datasets...
if not "%ROBOFLOW_API_KEY%"=="" (
    python download_datasets.py --fight --roboflow-key %ROBOFLOW_API_KEY%
) else (
    python download_datasets.py --fight --skip-roboflow
)
goto complete

:download_face
echo.
echo 👤 Downloading FACE DETECTION datasets...
if not "%ROBOFLOW_API_KEY%"=="" (
    python download_datasets.py --face --roboflow-key %ROBOFLOW_API_KEY%
) else (
    python download_datasets.py --face --skip-roboflow
)
goto complete

:list_datasets
echo.
python download_datasets.py --list
echo.
pause
goto menu

:complete
echo.
echo ════════════════════════════════════════════════════════════════════
echo ✅ DOWNLOAD COMPLETE!
echo ════════════════════════════════════════════════════════════════════
echo.
echo 📁 Datasets saved to: %cd%\datasets
echo 📄 Config file: %cd%\datasets\combined_dataset.yaml
echo.
echo Next steps:
echo   1. Review downloaded datasets
echo   2. Train your model with: yolo train data=datasets/combined_dataset.yaml
echo.
pause
goto menu

:end
echo.
echo 👋 Goodbye!
exit /b 0
