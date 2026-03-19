@echo off
echo ========================================
echo Helldiver Voice Assistant - Build Script
echo ========================================
echo.

REM Set conda environment path
set CONDA_ENV_PATH=D:\conda_envs\helldiver
set PYTHON_EXE=%CONDA_ENV_PATH%\python.exe

echo Using Python: %PYTHON_EXE%
echo.

REM Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at: %PYTHON_EXE%
    echo Please check your conda environment path
    pause
    exit /b 1
)

echo Checking Python version...
"%PYTHON_EXE%" --version
"%PYTHON_EXE%" -c "import sys; print('Python path:', sys.executable)"
echo.

pause
echo.

echo [1/4] Checking PyInstaller...
"%PYTHON_EXE%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not installed, installing...
    "%PYTHON_EXE%" -m pip install pyinstaller
) else (
    echo PyInstaller installed
)
echo.

echo [2/4] Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist modules\__pycache__ rmdir /s /q modules\__pycache__
if exist gui\__pycache__ rmdir /s /q gui\__pycache__
echo Cleanup complete
echo.

echo [3/4] Starting build...
echo This may take a few minutes, please wait...
"%PYTHON_EXE%" -m PyInstaller build.spec
echo.

if errorlevel 1 (
    echo [ERROR] Build failed!
    echo Please check error messages and try again
    pause
    exit /b 1
)

echo [4/4] Copying config files...
if exist "dist\Helldiver Voice Assistant" (
    copy stratagems.json "dist\Helldiver Voice Assistant\" >nul
    echo Config files copied
) else (
    echo [WARNING] Output directory not found
)
echo.

echo ========================================
echo Build complete!
echo Output directory: dist\Helldiver Voice Assistant
echo Executable: Helldiver Voice Assistant.exe
echo ========================================
echo.
echo Tips:
echo 1. First run requires Aliyun credentials configuration
echo 2. You can compress the entire folder for distribution
echo 3. Users do not need to install Python to run
echo.
pause