# handlers/start.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from keyboards.main import get_main_menu
from config import config

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    
    # Отправка приветственного сообщения
    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я — умный бот поддержки образовательных организаций.\n"
        "Я помогу вам создать обращение, отследить его статус и получить помощь.\n\n"
        "👇 Используйте кнопки ниже для навигации:",
        reply_markup=get_main_menu(user.id in config.bot.admin_ids),
        parse_mode=ParseMode.HTML
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "📚 <b>Доступные команды:</b>\n\n"
        "/start - Перезапустить бота\n"
        "/new - Создать новое обращение\n"
        "/tickets - Мои обращения\n"
        "/stats - Статистика\n"
        "/help - Эта справка\n\n"
        "👑 <b>Команды администратора:</b>\n"
        "/admin - Панель управления\n"
        "/broadcast - Рассылка сообщений\n"
        "/export - Экспорт данных\n\n"
        "📞 <b>Поддержка:</b>\n"
        "Если у вас возникли проблемы, свяжитесь с администратором."
    )
    
    await message.answer(help_text, parse_mode=ParseMode.HTML)