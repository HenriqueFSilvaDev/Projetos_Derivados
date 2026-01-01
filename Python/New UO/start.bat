@echo off
echo ========================================
echo    Color Validator
echo ========================================
echo.
echo Verificando dependencias...

python -c "import tkinter, PIL, win32gui, keyboard, winsound, numpy, psutil" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Instalando dependencias necessarias...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo Erro na instalacao! Verifique os requisitos.
        pause
        exit /b 1
    )
    echo.
    echo Dependencias instaladas!
    echo.
)

echo.
echo Iniciando Color Validator...
echo.
python color_validator.py

if %errorlevel% neq 0 (
    echo.
    echo Erro ao executar aplicacao!
    echo Verifique se todas as dependencias estao instaladas.
)

pause
