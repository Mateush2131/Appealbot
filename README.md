Описание проекта
Полнофункциональная система для приема и обработки обращений учащихся и родителей в образовательных организациях. Система предоставляет удобный интерфейс через Telegram-бота и мощный бэкенд на FastAPI для управления обращениями.

Проект разработан в рамках производственной практики для ИП «Александров А.В.» (разработка веб-сервисов для образовательных организаций).

Основные возможности
Для пользователей
Создание обращений через Telegram-бота

Три типа обращений: вопросы, жалобы, предложения

Система приоритетов: низкий, средний, высокий

Отслеживание статуса обращений

История всех отправленных обращений

Для администраторов
Админ-панель в Telegram для управления обращениями

Изменение статусов обращений

Добавление комментариев к обращениям

Статистика и аналитика

Экспорт данных в CSV формате

Поиск и фильтрация обращений

Технологический стек
Backend: Python 3.11, FastAPI, SQLAlchemy, Pydantic

База данных: PostgreSQL (продакшн), SQLite (разработка)

Интерфейс: Telegram Bot (aiogram 3.x)

Контейнеризация: Docker, Docker Compose

Документация: Swagger/OpenAPI автоматическая генерация

Быстрый старт
Предварительные требования
Python 3.11 или выше

PostgreSQL (или SQLite для разработки)

Токен Telegram-бота (получить у @BotFather)

Установка
Клонирование репозитория

bash
git clone https://github.com/ваш-логин/support-education-bot.git
cd support-education-bot
Создание виртуального окружения

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
Установка зависимостей

bash
pip install -r requirements.txt
Настройка переменных окружения

bash
cp .env.example .env
# Отредактируйте .env файл
Запуск системы

bash
# Запуск бэкенда
cd backend
uvicorn app.main:app --reload

# В отдельном терминале запуск бота
cd telegram_bot
python bot.py
Docker развертывание
bash
# Запуск всех сервисов
docker-compose up -d

# Остановка
docker-compose down
Конфигурация
Основные настройки (.env)
env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321

# Database
DATABASE_URL=sqlite:///./support.db
# или для PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/support_db

# Application
ENVIRONMENT=development
DEBUG=true
API документация
После запуска бэкенда доступны:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Основные эндпоинты
Метод	Endpoint	Описание
POST	/tickets/	Создание обращения
GET	/tickets/	Получение списка обращений
GET	/tickets/{id}	Получение обращения по ID
PATCH	/tickets/{id}	Обновление обращения
DELETE	/tickets/{id}	Удаление обращения
GET	/tickets/stats	Статистика по обращениям
Пример запроса
bash
curl -X POST "http://localhost:8000/tickets/" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иванов Иван Иванович",
    "contact": "ivanov@school.ru",
    "type": "QUESTION",
    "text": "Как подключиться к электронному дневнику?",
    "priority": "MEDIUM"
  }'
Структура проекта
text
support-education-bot/
├── backend/                    # FastAPI приложение
│   ├── app/
│   │   ├── main.py            # Точка входа
│   │   ├── database.py        # Конфигурация БД
│   │   ├── api/              # API эндпоинты
│   │   ├── models/           # SQLAlchemy модели
│   │   ├── schemas/          # Pydantic схемы
│   │   └── crud/             # Бизнес-логика
│   └── requirements.txt       # Зависимости
├── telegram_bot/              # Telegram бот
│   ├── bot.py                # Основной файл
│   ├── config.py             # Конфигурация
│   ├── handlers/             # Обработчики команд
│   ├── keyboards/            # Клавиатуры
│   ├── services/             # Сервисы
│   └── requirements.txt      # Зависимости
├── requirements.txt          # Общие зависимости
├── docker-compose.yml        # Docker конфигурация
├── .env.example             # Шаблон переменных
└── README.md                # Документация
Разработка
Установка для разработки
bash
# Установка дополнительных зависимостей
pip install -r requirements-dev.txt

# Настройка pre-commit
pre-commit install

# Запуск тестов
pytest

# Проверка стиля кода
black --check .
flake8 .
Тестирование
Проект включает несколько уровней тестирования:

Unit-тесты: Тестирование отдельных функций

Интеграционные тесты: Тестирование взаимодействия компонентов

API тесты: Тестирование REST эндпоинтов

Запуск тестов:

bash
pytest backend/tests/
pytest telegram_bot/tests/
Деплой
Вариант 1: Docker (рекомендуется)
bash
# Сборка и запуск
docker-compose up --build -d

# Просмотр логов
docker-compose logs -f
Вариант 2: Вручную
Настройка веб-сервера (nginx/apache)

Настройка PostgreSQL базы данных

Настройка systemd сервисов для бэкенда и бота

Настройка SSL сертификатов

Безопасность
Все входные данные проходят валидацию через Pydantic

SQL-инъекции защищены использованием ORM (SQLAlchemy)

Разделение прав пользователей и администраторов

Rate limiting для предотвращения атак

Хранение чувствительных данных в переменных окружения

Лицензия
Этот проект распространяется под лицензией MIT. Подробнее см. файл LICENSE.

Контакты
Разработчик: [Ваше ФИО]

Заказчик: ИП «Александров А.В.»

GitHub: https://github.com/ваш-логин/support-education-bot

Email: [ваш email]

Вклад в проект
Форкните репозиторий

Создайте ветку для новой функциональности

Внесите изменения

Напишите тесты

Отправьте pull request

Поддержка
При возникновении проблем:

Проверьте Issues на наличие похожих проблем

Создайте новый Issue с подробным описанием

Приложите логи и конфигурацию
