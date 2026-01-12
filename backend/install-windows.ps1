# Script de instalación para Windows
# Ejecutar con: .\install-windows.ps1

Write-Host "=== Instalación de Despensa Backend (Windows) ===" -ForegroundColor Green
Write-Host ""

# Verificar si estamos en el entorno virtual
if (-not $env:VIRTUAL_ENV) {
    Write-Host "ERROR: El entorno virtual no está activado" -ForegroundColor Red
    Write-Host "Por favor ejecuta primero: venv\Scripts\activate" -ForegroundColor Yellow
    exit 1
}

Write-Host "1. Actualizando pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel

Write-Host ""
Write-Host "2. Instalando PyTorch (CPU version)..." -ForegroundColor Cyan
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

Write-Host ""
Write-Host "3. Instalando dependencias del backend..." -ForegroundColor Cyan
pip install -r requirements-windows.txt

Write-Host ""
Write-Host "4. Poblando base de datos con recetas de ejemplo..." -ForegroundColor Cyan
python seed_data.py

Write-Host ""
Write-Host "=== Instalación completada! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Para ejecutar el servidor:" -ForegroundColor Yellow
Write-Host "  uvicorn main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
