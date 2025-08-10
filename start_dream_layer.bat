@echo off
setlocal enabledelayedexpansion

:: Dream Layer Windows Startup Script
:: This script starts all the necessary services for the Dream Layer application on Windows

:: Colors for output (basic)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "NC=[0m"

echo.
echo %CYAN%================================================%NC%
echo %CYAN%       DREAM LAYER - WINDOWS STARTUP%NC%
echo %CYAN%================================================%NC%
echo.

:: Check if we're in the correct directory
if not exist "dream_layer_backend" (
    echo %RED%[ERROR]%NC% This script must be run from the Dream Layer project root directory!
    echo %RED%[ERROR]%NC% Please navigate to the 'DreamLayer' folder and run this script again.
    echo %YELLOW%[INFO]%NC% Current directory: %CD%
    echo %YELLOW%[INFO]%NC% Expected files: dream_layer_backend, dream_layer_frontend, ComfyUI
    echo.
    pause
    exit /b 1
)

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

echo %BLUE%[INFO]%NC% Starting Dream Layer services...
echo %YELLOW%[INFO]%NC% Logs will be saved in the 'logs' directory
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Python is not installed or not in PATH!
    echo %YELLOW%[INFO]%NC% Please run install_windows_dependencies.bat first
    pause
    exit /b 1
)

:: Check Node.js installation  
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[ERROR]%NC% Node.js is not installed or not in PATH!
    echo %YELLOW%[INFO]%NC% Please run install_windows_dependencies.bat first
    pause
    exit /b 1
)

:: Check if PyTorch is installed
python -c "import torch" >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% PyTorch not found. Installing...
    nvidia-smi >nul 2>&1
    if %errorlevel% equ 0 (
        echo %GREEN%[INFO]%NC% NVIDIA GPU detected - installing PyTorch with CUDA...
        python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    ) else (
        echo %YELLOW%[INFO]%NC% No NVIDIA GPU detected - installing CPU-only PyTorch...
        python -m pip install torch torchvision torchaudio
    )
)

:: Check GPU availability and set CPU mode if needed
echo %BLUE%[INFO]%NC% Checking GPU availability...
:: FORCING CPU MODE FOR COMFYUI
set "DREAMLAYER_COMFYUI_CPU_MODE=true"
set "DEVICE_MODE=CPU"
:: Original logic commented out:
:: nvidia-smi >nul 2>&1
:: if %errorlevel% neq 0 (
::     echo %YELLOW%[INFO]%NC% No NVIDIA GPU detected - ComfyUI will run in CPU mode
::     set "COMFYUI_CPU_MODE=--cpu"
::     set "DEVICE_MODE=CPU"
:: ) else (
::     echo %GREEN%[INFO]%NC% NVIDIA GPU detected - ComfyUI will use GPU acceleration
::     set "COMFYUI_CPU_MODE="
::     set "DEVICE_MODE=GPU"
:: )

:: Check if backend dependencies are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% Backend dependencies not found. Installing...
    cd dream_layer_backend
    python -m pip install -r requirements.txt
    cd ..
)

:: Check if ComfyUI dependencies are installed
python -c "import sys; sys.path.append('ComfyUI'); import torch" >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% ComfyUI dependencies not found. Installing...
    cd ComfyUI
    python -m pip install -r requirements.txt
    cd ..
)

:: Check if frontend dependencies are installed
if not exist "dream_layer_frontend\node_modules" (
    echo %YELLOW%[WARNING]%NC% Frontend dependencies not found. Installing...
    cd dream_layer_frontend
    npm install
    cd ..
)

echo.
echo %GREEN%[SUCCESS]%NC% All dependencies are ready!
echo %BLUE%[INFO]%NC% Device mode: %DEVICE_MODE%
echo.

:: Start services
echo %CYAN%================================================%NC%
echo %CYAN%           STARTING SERVICES%NC%
echo %CYAN%================================================%NC%
echo.

:: Start Dream Layer backend (which also starts ComfyUI internally)
echo %BLUE%[STEP 1/4]%NC% Starting Dream Layer backend...
start "Dream Layer Backend" /D "%CD%" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && python dream_layer_backend\dream_layer.py > logs\dream_layer.log 2>&1"

:: Wait for backend to start
echo %YELLOW%[INFO]%NC% Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Start txt2img_server.py
echo %BLUE%[STEP 2/4]%NC% Starting txt2img_server.py...
start "Txt2Img Server" /D "%CD%\dream_layer_backend" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && python txt2img_server.py > ..\logs\txt2img_server.log 2>&1"

:: Start img2img_server.py
echo %BLUE%[STEP 3/4]%NC% Starting img2img_server.py...
start "Img2Img Server" /D "%CD%\dream_layer_backend" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && python img2img_server.py > ..\logs\img2img_server.log 2>&1"

:: Start extras.py
echo %BLUE%[STEP 4/4]%NC% Starting extras.py...
start "Extras Server" /D "%CD%\dream_layer_backend" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && python extras.py > ..\logs\extras.log 2>&1"

:: Wait for all backend services to start
echo %YELLOW%[INFO]%NC% Waiting for all backend services to initialize...
timeout /t 10 /nobreak >nul

:: Start frontend development server
echo %BLUE%[STEP 5/5]%NC% Starting frontend development server...
start "Dream Layer Frontend" /D "%CD%\dream_layer_frontend" cmd /c "npm run dev > ..\logs\frontend.log 2>&1"

:: Wait for frontend to start
echo %YELLOW%[INFO]%NC% Waiting for frontend to initialize...
timeout /t 15 /nobreak >nul

echo.
echo %GREEN%[SUCCESS]%NC% All services started!
echo.
echo %CYAN%================================================%NC%
echo %CYAN%           ACCESS INFORMATION%NC%
echo %CYAN%================================================%NC%
echo.
echo %GREEN%Frontend (Main UI):%NC%     http://localhost:8080
echo %GREEN%ComfyUI Interface:%NC%      http://localhost:8188
echo %GREEN%Backend API:%NC%            http://localhost:5002
echo.
echo %BLUE%[INFO]%NC% Device Mode: %DEVICE_MODE%
echo %BLUE%[INFO]%NC% Check logs in the 'logs' directory if you encounter issues
echo.

:: Test service connectivity
echo %BLUE%[INFO]%NC% Testing service connectivity...
echo.

:: Test ComfyUI
timeout /t 5 /nobreak >nul
python -c "import requests; print('ComfyUI Status:', 'OK' if requests.get('http://localhost:8188', timeout=10).status_code == 200 else 'ERROR')" 2>nul
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% ComfyUI may still be starting up - please wait a moment
)

:: Test Backend
python -c "import requests; print('Backend Status:', 'OK' if requests.get('http://localhost:5002', timeout=10).status_code == 200 else 'ERROR')" 2>nul
if %errorlevel% neq 0 (
    echo %YELLOW%[WARNING]%NC% Backend may still be starting up - please wait a moment
)

echo.
echo %GREEN%Dream Layer is now running! %NC%
echo %CYAN%Open your browser and navigate to: http://localhost:8080%NC%
echo.
echo %YELLOW%[INFO]%NC% To stop all services, close this window or press Ctrl+C
echo %YELLOW%[INFO]%NC% Log files are available in the 'logs' directory
echo.

:: Keep the window open
echo Press any key to stop all services...
pause >nul

:: Cleanup - kill all related processes
echo.
echo %BLUE%[INFO]%NC% Stopping all services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im cmd.exe >nul 2>&1

echo %GREEN%[SUCCESS]%NC% All services stopped.
pause 