import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.types import BotCommand, BotCommandScopeDefault, Message, CallbackQuery
from redis.asyncio import Redis

from config import config
from database import init_db, close_db  # Измененный импорт!
from middleware import LoggingMiddleware, DependenciesMiddleware
from handlers.user import register_user_handlers
from handlers.admin import register_admin_handlers
from handlers.payment import register_payment_handlers
from handlers.start import router as start_router
from keyboards.main import get_main_menu
from services.notifications import NotificationService
from services.analytics import AnalyticsService
from services.api_client import APIClient
from utils.logger import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

async def set_bot_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="🚀 Начать работу"),
        BotCommand(command="new", description="📝 Создать обращение"),
        BotCommand(command="tickets", description="📋 Мои обращения"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="stats", description="📊 Статистика"),
    ]
    
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())

async def on_startup(bot: Bot, dp: Dispatcher):
    """Действия при запуске"""
    logger.info("Starting up...")
    
    # Инициализация сервисов
    analytics_service = AnalyticsService()
    api_client = APIClient()
    notification_service = NotificationService(bot=bot)
    
    # Добавляем сервисы в workflow_data диспетчера для доступа в middleware
    dp.workflow_data["analytics_service"] = analytics_service
    dp.workflow_data["api_client"] = api_client
    dp.workflow_data["notification_service"] = notification_service
    
    # Инициализация базы данных
    init_db()  # Теперь это не асинхронная функция!
    
    # Установка команд бота
    await set_bot_commands(bot)
    
    # Запуск службы уведомлений
    await notification_service.start()
    
    # Отправка уведомления админам
    for admin_id in config.bot.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                "🤖 Бот запущен и готов к работе!\n"
                f"Режим: {'🟢 PRODUCTION' if config.environment == 'production' else '🟡 DEVELOPMENT'}"
            )
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")
    
    logger.info("Bot started successfully")

async def on_shutdown(bot: Bot, dp: Dispatcher):
    """Действия при выключении"""
    logger.info("Бот выключается...")
    
    # Закрываем сервисы
    if hasattr(dp, 'workflow_data'):
        if "notification_service" in dp.workflow_data:
            await dp.workflow_data["notification_service"].shutdown()
        
        if "analytics_service" in dp.workflow_data:
            await dp.workflow_data["analytics_service"].shutdown()
    
    # Закрываем соединение с БД
    close_db()  # Используем правильную функцию
    
    await bot.session.close()

async def main():
    """Основная функция запуска бота"""
    
    # Инициализация Redis
    redis = Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        password=config.redis.password,
        decode_responses=True
    )
    
    # Настройка хранилища FSM
    storage = RedisStorage(
        redis=redis,
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True)
    )
    
    # Создание бота
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
            protect_content=False
        )
    )
    
    # Создание диспетчера
    dp = Dispatcher(storage=storage)
    
    # Регистрация middleware
    dp.update.outer_middleware(DependenciesMiddleware())
    dp.update.outer_middleware(LoggingMiddleware())
    
    # Регистрация обработчиков
    dp.include_router(start_router)
    register_user_handlers(dp)
    register_admin_handlers(dp)
    
    if config.bot.enable_payments:
        register_payment_handlers(dp)
    
    # Запуск и завершение
    try:
        await on_startup(bot, dp)
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.exception(f"Error in main: {e}")
    finally:
        await on_shutdown(bot, dp)
        await redis.aclose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение завершено")
    except Exception as e:
        logger.exception(f"Фатальная ошибка: {e}")