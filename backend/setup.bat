@echo off
chcp 65001 > nul
echo ============================================
echo УСТАНОВКА ПРОЕКТА НА PYTHON 3.12
echo ============================================
echo.

echo 1. ПРОВЕРКА PYTHON 3.12...
if exist "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" (
    echo [OK] Python 3.12 найден!
    set PYTHON_PATH=C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe
) else (
    echo [ERROR] Python 3.12 не найден!
    echo Проверьте путь: C:\Users\Admin\AppData\Local\Programs\Python\Python312\
    pause
    exit /b 1
)

echo.
echo 2. ПЕРЕХОД В ПАПКУ ПРОЕКТА...
cd /d "C:\Users\Admin\OneDrive\Рабочий стол\производственная практика\backend"

echo.
echo 3. УДАЛЕНИЕ СТАРОЙ ВИРТУАЛЬНОЙ СРЕДЫ...
if exist venv (
    echo Удаление папки venv...
    rmdir /s /q venv
)

echo.
echo 4. СОЗДАНИЕ ВИРТУАЛЬНОЙ СРЕДЫ С PYTHON 3.12...
"%PYTHON_PATH%" -m venv venv

if errorlevel 1 (
    echo [ERROR] Ошибка создания виртуальной среды
    echo Попробуйте вручную:
    echo   "C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe" -m venv venv
    pause
    exit /b 1
)

echo.
echo 5. АКТИВАЦИЯ ВИРТУАЛЬНОЙ СРЕДЫ...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERROR] Ошибка активации виртуальной среды
    echo Проверьте существование файла: venv\Scripts\activate.bat
    pause
    exit /b 1
)

echo.
echo 6. ПРОВЕРКА ВЕРСИИ PYTHON В ВИРТУАЛЬНОЙ СРЕДЕ...
python --version

echo.
echo 7. ОБНОВЛЕНИЕ PIP...
python -m pip install --upgrade pip setuptools wheel

echo.
echo 8. УСТАНОВКА ЗАВИСИМОСТЕЙ...
echo.

echo 8.1. Установка FastAPI и зависимостей...
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 sqlalchemy==2.0.23 pydantic==2.5.0 python-dotenv==1.0.0

echo.
echo 8.2. Установка aiogram...
pip install aiogram==3.10.0 aiohttp==3.9.3 httpx==0.25.2

echo.
echo 8.3. Установка базы данных...
pip install aiosqlite==0.20.0

echo.
echo 9. ПРОВЕРКА УСТАНОВКИ...
echo.

python -c "import sys
print('Python version:', sys.version)
print()
packages = ['fastapi', 'sqlalchemy', 'pydantic', 'aiogram', 'aiohttp', 'httpx', 'aiosqlite']
for pkg in packages:
    try:
        module = __import__(pkg)
        version = getattr(module, '__version__', 'OK')
        print(f'[OK] {pkg}: {version}')
    except ImportError as e:
        print(f'[ERROR] {pkg}: НЕ УСТАНОВЛЕН')
"

echo.
echo 10. СОЗДАНИЕ .ENV ФАЙЛА...
if not exist .env (
    echo TELEGRAM_BOT_TOKEN=ваш_токен_бота_здесь > .env
    echo ADMIN_IDS=123456789 >> .env
    echo API_URL=http://localhost:8000 >> .env
    echo DEBUG=True >> .env
    echo.
    echo [INFO] ФАЙЛ .ENV СОЗДАН! ЗАМЕНИТЕ 'ваш_токен_бота_здесь' НА РЕАЛЬНЫЙ ТОКЕН
)

echo.
echo ============================================
echo [OK] УСТАНОВКА ЗАВЕРШЕНА!
echo.
echo Дальнейшие шаги:
echo 1. Получите токен бота у @BotFather
echo 2. Откройте файл .env и замените токен
echo 3. Запустите бэкенд: uvicorn app.main:app --reload
echo 4. Запустите бота: python telegram_bot/bot.py
echo ============================================
echo.
pause