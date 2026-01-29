# Система поддержки для образовательных организаций

## Описание
Полнофункциональная система для приема и обработки обращений с Telegram-ботом как интерфейсом.

## Архитектура
- **Backend**: FastAPI + SQLite/PostgreSQL
- **Frontend**: Telegram Bot (aiogram 3.x)
- **База данных**: PostgreSQL для бота, SQLite для бэкенда (или одна БД)
- **Кэширование**: Redis
- **Контейнеризация**: Docker

## Установка

### Локальная разработка
1. Клонируйте репозиторий
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows