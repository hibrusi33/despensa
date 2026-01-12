@echo off
REM Script de instalación para Windows
REM Ejecutar con: install-windows.bat

echo === Instalación de Despensa Backend (Windows) ===
echo.

REM Verificar si el venv está activado
if not defined VIRTUAL_ENV (
    echo ERROR: El entorno virtual no esta activado
    echo Por favor ejecuta primero: venv\Scripts\activate
    pause
    exit /b 1
)

echo 1. Actualizando pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto error

echo.
echo 2. Instalando PyTorch (CPU version)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto error

echo.
echo 3. Instalando dependencias del backend...
pip install -r requirements-windows.txt
if errorlevel 1 goto error

echo.
echo 4. Poblando base de datos con recetas de ejemplo...
python seed_data.py
if errorlevel 1 goto error

echo.
echo === Instalacion completada! ===
echo.
echo Para ejecutar el servidor:
echo   uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
pause
exit /b 0

:error
echo.
echo ERROR: La instalacion fallo
pause
exit /b 1
