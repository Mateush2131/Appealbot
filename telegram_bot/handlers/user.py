# handlers/user.py
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
import logging
from datetime import datetime

from states.user_states import TicketCreation
from keyboards.main import (
    get_main_menu, 
    get_ticket_type_keyboard,
    get_priority_keyboard
)
from services.api_client import APIClient
from services.notifications import NotificationService
from database import save_user_ticket, get_user_tickets, update_user  # Правильный импорт!

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("new"))
@router.message(F.text == "📝 Создать обращение")
async def cmd_new_ticket(message: Message, state: FSMContext):
    """Начало создания обращения"""
    # Сохраняем информацию о пользователе
    update_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    await state.set_state(TicketCreation.full_name)
    await message.answer(
        "👤 Пожалуйста, введите ваше ФИО:",
        reply_markup=None
    )

@router.message(TicketCreation.full_name)
async def process_full_name(message: Message, state: FSMContext):
    """Обработка ФИО"""
    if len(message.text) < 2:
        await message.answer("❌ ФИО должно содержать минимум 2 символа.")
        return
    
    await state.update_data(full_name=message.text)
    await state.set_state(TicketCreation.contact)
    await message.answer("📞 Теперь введите ваш email или телефон:")

@router.message(TicketCreation.contact)
async def process_contact(message: Message, state: FSMContext):
    """Обработка контакта"""
    if len(message.text) < 5:
        await message.answer("❌ Контакт должен содержать минимум 5 символов.")
        return
    
    await state.update_data(contact=message.text)
    await state.set_state(TicketCreation.type)
    await message.answer(
        "📋 Выберите тип обращения:",
        reply_markup=get_ticket_type_keyboard()
    )

@router.callback_query(F.data.startswith("ticket_type:"), TicketCreation.type)
async def process_type(callback: CallbackQuery, state: FSMContext):
    """Обработка типа обращения"""
    ticket_type = callback.data.split(":")[1].upper()
    
    # Проверяем, что тип поддерживается
    supported_types = ["QUESTION", "COMPLAINT", "SUGGESTION"]
    if ticket_type not in supported_types:
        await callback.answer("❌ Этот тип обращения временно недоступен")
        return
    
    await state.update_data(type=ticket_type)
    await state.set_state(TicketCreation.text)
    
    await callback.message.edit_text(
        "📝 Теперь опишите вашу проблему или вопрос подробно:"
    )
    await callback.answer()

@router.message(TicketCreation.text)
async def process_text(message: Message, state: FSMContext):
    """Обработка текста обращения"""
    if len(message.text) < 10:
        await message.answer("❌ Описание должно содержать минимум 10 символов.")
        return
    
    await state.update_data(text=message.text)
    await state.set_state(TicketCreation.priority)
    
    await message.answer(
        "🚨 Выберите приоритет обращения:",
        reply_markup=get_priority_keyboard()
    )

@router.callback_query(F.data.startswith("priority:"), TicketCreation.priority)
async def process_priority(
    callback: CallbackQuery,
    state: FSMContext,
    api_client: APIClient,
    notification_service: NotificationService
):
    """Обработка приоритета"""
    priority = callback.data.split(":")[1].upper()
    
    # Получаем все данные
    data = await state.get_data()
    
    # Формируем запрос к API
    ticket_data = {
        "full_name": data["full_name"],
        "contact": data["contact"],
        "type": data["type"],
        "text": data["text"],
        "priority": priority,
        "user_id": f"user_{callback.from_user.id}"
    }
    
    # Показываем прогресс
    progress_msg = await callback.message.answer("⏳ Создаем обращение...")
    
    try:
        result = None
        ticket_id = None
        
        # Пробуем отправить в API
        if hasattr(api_client, 'create_ticket'):
            try:
                result = await api_client.create_ticket(ticket_data)
                if result:
                    ticket_id = result.get('id')
                    
                    # Уведомляем
                    try:
                        await notification_service.notify_new_ticket(result)
                    except Exception as e:
                        logger.error(f"Error notifying: {e}")
            except Exception as api_error:
                logger.error(f"API error: {api_error}")
        
        # Сохраняем в локальную БД
        local_ticket_data = {
            'id': ticket_id,
            'full_name': data["full_name"],
            'contact': data["contact"],
            'type': data["type"],
            'text': data["text"],
            'priority': priority,
            'status': 'NEW'
        }
        
        saved = save_user_ticket(callback.from_user.id, local_ticket_data)  # Правильный вызов!
        
        if saved:
            status_text = "сохранено локально"
            if result:
                status_text = "сохранено в системе"
            
            await progress_msg.edit_text(
                f"✅ {hbold('Обращение создано!')}\n\n"
                f"📋 <b>Данные обращения:</b>\n"
                f"🆔 Номер: #{ticket_id if ticket_id else 'Локальное'}\n"
                f"👤 ФИО: {data['full_name']}\n"
                f"📞 Контакт: {data['contact']}\n"
                f"📝 Тип: {data['type']}\n"
                f"🚨 Приоритет: {priority}\n"
                f"📊 Статус: НОВЫЙ\n\n"
                f"Мы свяжемся с вами в ближайшее время!\n"
                f"<i>Обращение {status_text}.</i>",
                parse_mode=ParseMode.HTML
            )
        else:
            await progress_msg.edit_text(
                "❌ Произошла ошибка при сохранении обращения. Попробуйте позже."
            )
            
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        
        # Пробуем хотя бы сохранить локально
        try:
            local_ticket_data = {
                'id': None,
                'full_name': data["full_name"],
                'contact': data["contact"],
                'type': data["type"],
                'text': data["text"],
                'priority': priority,
                'status': 'NEW'
            }
            
            saved = save_user_ticket(callback.from_user.id, local_ticket_data)  # Правильный вызов!
            
            if saved:
                await progress_msg.edit_text(
                    f"⚠️ {hbold('Обращение создано локально!')}\n\n"
                    f"📋 <b>Данные обращения:</b>\n"
                    f"👤 ФИО: {data['full_name']}\n"
                    f"📞 Контакт: {data['contact']}\n"
                    f"📝 Тип: {data['type']}\n"
                    f"🚨 Приоритет: {priority}\n"
                    f"📊 Статус: НОВЫЙ\n\n"
                    f"Мы свяжемся с вами в ближайшее время!\n"
                    f"<i>Обращение сохранено локально (API временно недоступен).</i>",
                    parse_mode=ParseMode.HTML
                )
            else:
                await progress_msg.edit_text(
                    f"❌ Ошибка при создании обращения: {str(e)}"
                )
        except Exception as save_error:
            logger.error(f"Error saving locally: {save_error}")
            await progress_msg.edit_text(
                f"❌ Критическая ошибка: {str(e)}"
            )
    
    await state.clear()
    await callback.answer()

@router.message(Command("tickets"))
@router.message(F.text == "📋 Мои обращения")
async def cmd_my_tickets(message: Message):
    """Показать мои обращения из локальной БД"""
    user_id = message.from_user.id
    
    progress_msg = await message.answer("🔍 Ищем ваши обращения...")
    
    try:
        # Получаем обращения из локальной БД
        tickets = get_user_tickets(user_id, limit=10)  # Правильный вызов!
        
        if not tickets:
            await progress_msg.edit_text("📭 У вас пока нет обращений.")
            return
        
        # Показываем обращения
        for i, ticket in enumerate(tickets[:5], 1):
            ticket_id = ticket.get('ticket_id', 'Локальное')
            ticket_type = ticket.get('type', 'N/A')
            ticket_text = ticket.get('text', '')[:100]
            ticket_status = ticket.get('status', 'N/A')
            created_at = ticket.get('created_at', 'N/A')
            
            status_emojis = {
                "NEW": "🆕",
                "IN_PROGRESS": "⚙️",
                "RESOLVED": "✅",
                "CLOSED": "🔒"
            }
            status_emoji = status_emojis.get(ticket_status, "")
            
            ticket_display = (
                f"🆔 {hbold(f'#{ticket_id}')} - {ticket_type}\n"
                f"📝 {ticket_text}...\n"
                f"📊 Статус: {status_emoji} {ticket_status}\n"
                f"📅 Создано: {created_at}\n"
            )
            
            await message.answer(
                ticket_display,
                parse_mode=ParseMode.HTML
            )
        
        await progress_msg.delete()
        
        if len(tickets) > 5:
            await message.answer(
                f"📄 Показано 5 из {len(tickets)} обращений. "
                f"Используйте /all_tickets чтобы увидеть все."
            )
            
    except Exception as e:
        logger.error(f"Error getting user tickets: {e}")
        await progress_msg.edit_text("❌ Ошибка при получении ваших обращений")

@router.message(Command("all_tickets"))
async def cmd_all_tickets(message: Message):
    """Показать все мои обращения"""
    user_id = message.from_user.id
    
    progress_msg = await message.answer("🔍 Ищем все ваши обращения...")
    
    try:
        # Получаем все обращения из локальной БД
        tickets = get_user_tickets(user_id, limit=100)  # Правильный вызов!
        
        if not tickets:
            await progress_msg.edit_text("📭 У вас пока нет обращений.")
            return
        
        # Показываем все обращения
        for i, ticket in enumerate(tickets, 1):
            ticket_id = ticket.get('ticket_id', 'Локальное')
            ticket_type = ticket.get('type', 'N/A')
            ticket_text = ticket.get('text', '')[:100]
            ticket_status = ticket.get('status', 'N/A')
            created_at = ticket.get('created_at', 'N/A')
            
            status_emojis = {
                "NEW": "🆕",
                "IN_PROGRESS": "⚙️",
                "RESOLVED": "✅",
                "CLOSED": "🔒"
            }
            status_emoji = status_emojis.get(ticket_status, "")
            
            ticket_display = (
                f"{hbold(f'{i}. #{ticket_id}')} - {ticket_type}\n"
                f"📝 {ticket_text}...\n"
                f"📊 Статус: {status_emoji} {ticket_status}\n"
                f"📅 Создано: {created_at}\n"
            )
            
            await message.answer(
                ticket_display,
                parse_mode=ParseMode.HTML
            )
        
        await progress_msg.delete()
        await message.answer(f"📋 Всего обращений: {len(tickets)}")
            
    except Exception as e:
        logger.error(f"Error getting all tickets: {e}")
        await progress_msg.edit_text("❌ Ошибка при получении обращений")

# УДАЛЯЕМ неработающие функции:

@router.message(Command("sync_tickets"))
async def cmd_sync_tickets(message: Message):
    """Функция временно не работает"""
    await message.answer(
        "🔄 Функция синхронизации временно недоступна.\n"
        "Все ваши обращения сохраняются локально в боте."
    )

@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def cmd_stats(message: Message, api_client: APIClient):
    """Показать статистику"""
    try:
        stats = await api_client.get_stats()
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await message.answer("📊 Статистика временно недоступна.")
        return
    
    if not stats:
        await message.answer("📊 Статистика временно недоступна.")
        return
    
    # Форматируем статистику
    status_emojis = {
        "NEW": "🆕",
        "IN_PROGRESS": "⚙️",
        "RESOLVED": "✅",
        "CLOSED": "🔒"
    }
    
    stats_text = f"{hbold('📊 Статистика обращений')}\n\n"
    stats_text += f"📈 Всего обращений: {stats.get('total', 0)}\n\n"
    
    # Проверяем формат ответа
    if isinstance(stats, dict):
        # Если есть структура statuses
        if 'statuses' in stats:
            for status, count in stats['statuses'].items():
                emoji = status_emojis.get(status, "")
                stats_text += f"{emoji} {status}: {count}\n"
        else:
            # Иначе ищем поля напрямую
            for status in ['NEW', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']:
                if status in stats:
                    emoji = status_emojis.get(status, "")
                    stats_text += f"{emoji} {status}: {stats[status]}\n"
    
    await message.answer(stats_text, parse_mode=ParseMode.HTML)

# Обработчик для кнопки "Помощь"
@router.message(F.text == "❓ Помощь")
async def cmd_help_main(message: Message):
    """Показать справку"""
    help_text = (
        "📚 <b>Справка по боту поддержки</b>\n\n"
        "Я помогу вам создать обращение в поддержку и отслеживать его статус.\n\n"
        "<b>Основные возможности:</b>\n"
        "• 📝 Создание обращений\n"
        "• 📋 Просмотр своих обращений\n"
        "• 📊 Статистика обращений\n\n"
        "<b>Как создать обращение:</b>\n"
        "1. Нажмите «Создать обращение»\n"
        "2. Введите ФИО\n"
        "3. Введите контактные данные\n"
        "4. Выберите тип обращения\n"
        "5. Опишите проблему\n"
        "6. Выберите приоритет\n\n"
        "<b>Команды:</b>\n"
        "/start - Запустить бота\n"
        "/new - Создать обращение\n"
        "/tickets - Мои обращения\n"
        "/all_tickets - Все мои обращения\n"
        "/stats - Статистика\n"
        "/help - Эта справка\n\n"
        "<b>Для администраторов:</b>\n"
        "/admin - Панель управления"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)

# Обработчик для команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    from keyboards.main import get_main_menu
    from config import config
    
    is_admin = message.from_user.id in config.bot.admin_ids
    
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я — умный бот поддержки образовательных организаций.\n"
        "Я помогу вам создать обращение, отследить его статус и получить помощь.\n\n"
        "👇 Используйте кнопки ниже для навигации:",
        reply_markup=get_main_menu(is_admin),
        parse_mode=ParseMode.HTML
    )

def register_user_handlers(dp):
    """Регистрация обработчиков пользователя"""
    dp.include_router(router)