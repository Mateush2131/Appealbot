<img src="https://img.shields.io/badge/status-production-green?style=for-the-badge">
<img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi">
<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql">
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker">

# 📬 AppealBot — CRM-система приёма заявок в Telegram

**Готовое решение для школ, онлайн-курсов и сервисных компаний.**  
Бот + Админ-панель + Аналитика + API-документация.

👇 **Смотреть демо (видео 2 минуты)**  
[![Смотреть демо](https://img.shields.io/badge/▶️-Смотреть_демо-FF0000?style=for-the-badge)](ССЫЛКА_НА_ВИДЕО_ИЛИ_ГИФКУ)

---

## 🎯 Зачем это бизнесу?

| Проблема | Решение |
|----------|---------|
| Клиенты пишут в личку, заявки теряются | Единый бот для всех обращений |
| Менеджер тратит часы на «Где мой заказ?» | Автоматические статусы + история |
| Нет статистики | Готовая аналитика по заявкам |
| Сложно контролировать сотрудников | Прозрачная админ-панель |

---

## 📸 Как это выглядит

| Пользователь | Админ | API-документация |
|--------------|-------|------------------|
| ![Скрин1](ССЫЛКА) | ![Скрин2](ССЫЛКА) | ![Скрин3](ССЫЛКА) |

*— бот, форма создания заявки*  
*— список заявок, кнопки статусов*  
*— автогенерация Swagger*

---

## ⚙️ Из чего состоит

✅ **Telegram-бот** (aiogram 3.x) — приём заявок, уведомления, клавиатуры  
✅ **Backend на FastAPI** — бизнес-логика, база данных, авторизация  
✅ **База данных** — PostgreSQL / SQLite  
✅ **Админ-панель** — управление прямо в Telegram  
✅ **Документация API** — Swagger, ReDoc  
✅ **Docker** — запуск одной командой  

---

## 🧠 Что умеет система

**Для клиента:**
- Создать обращение (вопрос / жалоба / предложение)
- Выбрать приоритет (низкий / средний / высокий)
- Отслеживать статус заявки
- Смотреть историю своих обращений

**Для администратора:**
- Видеть все заявки в одном месте
- Менять статусы: «В работе», «Выполнено», «Отклонено»
- Оставлять комментарии
- Искать и фильтровать
- Выгружать статистику в CSV


Необходимое программное обеспечение
Python 3.11 или выше (рекомендуется Python 3.11)

Git (для клонирования репозитория)

Telegram аккаунт для использования бота




Зависимости Python
Проект требует установки следующих пакетов:

FastAPI - веб-фреймворк для API

Uvicorn - ASGI сервер для запуска FastAPI

SQLAlchemy - ORM для работы с базой данных

Pydantic - валидация данных

Aiogram - фреймворк для Telegram ботов

Aiohttp - HTTP клиент для асинхронных запросов

Python-dotenv - работа с переменными окружения
---

## 🚀 Быстрый старт (для разработчиков)

Если вы разработчик и хотите развернуть проект:

```
Шаг 1: Клонирование репозитория
cmd
git clone https://github.com/Mateush2131/Appealbot.git
cd Appealbot
Шаг 2: Создание виртуального окружения (рекомендуется)
cmd
python -m venv venv
venv\Scripts\activate  # Для Windows
source venv/bin/activate  # Для Linux/Mac
Шаг 3: Установка зависимостей
cmd
pip install -r requirements.txt
Если файла requirements.txt нет, установите вручную:

cmd
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 sqlalchemy==2.0.23 pydantic==2.5.0 python-dotenv==1.0.0 aiosqlite==0.20.0 aiogram==3.10.0 aiohttp==3.9.3
Шаг 4: Настройка переменных окружения
Создайте файл .env в папке telegram_bot:

cmd
cd telegram_bot
echo TELEGRAM_BOT_TOKEN=8557994918:AAGrgdXsdBBsNMAa1aGlqmXtFzo1xmrlh2A > .env
echo ADMIN_IDS=6033527749 >> .env
cd ..
Шаг 5: Запуск бэкенда (FastAPI + Uvicorn)
Способ 1: Из папки backend
cmd
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Способ 2: Из корня проекта
cmd
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
После запуска бэкенда откройте в браузере:

http://localhost:8000 - главная страница API

http://localhost:8000/docs - документация Swagger

http://localhost:8000/health - проверка здоровья

Шаг 6: Запуск Telegram бота
Откройте новое окно терминала и выполните:

cmd
cd telegram_bot
python bot.py
Запуск через единый скрипт
Создайте файл run_project.bat (для Windows):

batch
@echo off
echo Запуск проекта...

start "Backend" cmd /c "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
start "Telegram Bot" cmd /c "cd telegram_bot && python bot.py"

echo Проект запущен!
echo Backend: http://localhost:8000
echo Документация: http://localhost:8000/docs
pause
Запуск через Python скрипт
Создайте файл run.py в корне проекта:

python
import subprocess
import sys
import os
import time
import threading

def run_backend():
    os.chdir('backend')
    subprocess.run([sys.executable, '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'])

def run_bot():
    time.sleep(3)
    os.chdir('telegram_bot')
    subprocess.run([sys.executable, 'bot.py'])

if __name__ == '__main__':
    print("🚀 Запуск проекта...")
    
    backend_thread = threading.Thread(target=run_backend)
    backend_thread.daemon = True
    backend_thread.start()
    
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    print("✅ Проект запущен!")
    print("📡 Backend: http://localhost:8000")
    print("📚 Документация: http://localhost:8000/docs")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Остановка проекта...")
        sys.exit(0)
Запуск:

cmd
python run.py
Проверка работоспособности
Проверка бэкенда
Откройте http://localhost:8000/docs

Должна открыться документация Swagger

Проверьте эндпоинт GET /health

Проверка бота
Откройте Telegram

Найдите бота @ваш_бот

Отправьте команду /start

Должно появиться приветственное сообщение

Возможные проблемы и их решения
Проблема: ModuleNotFoundError: No module named 'app'
Решение: Запускайте из папки backend:

cmd
cd backend
python -m uvicorn app.main:app --reload
Проблема: Ошибка при установке pydantic
Решение: Используйте старую версию:

cmd
pip install pydantic==1.10.14
Проблема: Порт 8000 уже занят
Решение: Используйте другой порт:

cmd
python -m uvicorn app.main:app --reload --port 8001
Проблема: Бот не отвечает
Решение: Проверьте токен в .env файле
```
