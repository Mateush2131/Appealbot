# handlers/admin.py (исправленная версия)
from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton  # Добавь этот импорт!
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import sqlite3
import csv
from pathlib import Path
from io import BytesIO
from datetime import datetime, timedelta

from config import config
from keyboards.main import (
    get_admin_panel, 
    get_ticket_actions_keyboard,
    get_status_change_keyboard,
    get_pagination_keyboard
)
from services.api_client import APIClient

router = Router()
logger = logging.getLogger(__name__)

class IsAdminFilter(BaseFilter):
    """Фильтр для проверки прав администратора"""
    
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config.bot.admin_ids

router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())

class TicketManagement(StatesGroup):
    """Состояния для управления обращением"""
    select_ticket = State()
    choose_action = State()
    change_status = State()
    add_comment = State()

def get_all_tickets_from_db(limit: int = 100, status_filter: str = None):
    """Получить все обращения напрямую из базы данных"""
    try:
        db_path = Path("C:/Users/Admin/OneDrive/Рабочий стол/производственная практика/backend/support.db")
        
        if not db_path.exists():
            logger.error(f"БД не найдена по пути: {db_path}")
            return []
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT id, full_name, contact, type, text, priority, status, created_at, admin_comment, updated_at
            FROM tickets 
        """
        
        params = []
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        tickets = cursor.fetchall()
        conn.close()
        
        return [dict(ticket) for ticket in tickets]
        
    except Exception as e:
        logger.error(f"Ошибка при чтении из БД: {e}")
        return []

def update_ticket_status(ticket_id: int, status: str, comment: str = None):
    """Обновить статус обращения в базе данных"""
    try:
        db_path = Path("C:/Users/Admin/OneDrive/Рабочий стол/производственная практика/backend/support.db")
        
        if not db_path.exists():
            logger.error(f"БД не найдена по пути: {db_path}")
            return False
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        update_data = {
            'status': status,
            'updated_at': current_time
        }
        
        # Если есть комментарий, добавляем его
        if comment:
            # Проверяем, есть ли уже комментарий
            cursor.execute("SELECT admin_comment FROM tickets WHERE id = ?", (ticket_id,))
            existing_comment = cursor.fetchone()
            
            if existing_comment and existing_comment[0]:
                # Добавляем к существующему комментарию с новой строкой
                new_comment = f"{existing_comment[0]}\n[{current_time[:16]}] {comment}"
            else:
                new_comment = f"[{current_time[:16]}] {comment}"
            
            update_data['admin_comment'] = new_comment
            logger.info(f"Добавлен комментарий к обращению #{ticket_id}: {comment}")
        
        # Формируем SQL запрос
        set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(ticket_id)
        
        cursor.execute(f"UPDATE tickets SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()
        
        logger.info(f"Статус обращения #{ticket_id} обновлен на '{status}'")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса обращения #{ticket_id}: {e}")
        return False

@router.message(Command("admin"))
@router.message(F.text == "👑 Админ-панель")
async def cmd_admin(message: Message):
    """Админ-панель"""
    await message.answer(
        "👑 <b>Панель администратора</b>\n\n"
        "Выберите действие:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_panel()
    )

@router.callback_query(F.data == "page:1")
async def admin_all_tickets(callback: CallbackQuery):
    """Показать все обращения (первая страница)"""
    try:
        tickets = get_all_tickets_from_db(limit=10)
        
        if not tickets:
            await callback.message.answer("📭 Обращений нет.")
            await callback.answer()
            return
        
        # Форматируем список
        tickets_text = "<b>📋 Последние обращения:</b>\n\n"
        
        for i, ticket in enumerate(tickets, 1):
            status_emoji = {"NEW": "🆕", "IN_PROGRESS": "⚙️", "RESOLVED": "✅", "CLOSED": "🔒"}.get(ticket.get('status', ''), '')
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(ticket.get('priority', ''), '')
            
            tickets_text += (
                f"{i}. 🆔 <b>#{ticket.get('id', 'N/A')}</b> - {ticket.get('type', 'N/A')}\n"
                f"   👤 {ticket.get('full_name', 'N/A')}\n"
                f"   📞 {ticket.get('contact', 'N/A')}\n"
                f"   📊 {status_emoji} {ticket.get('status', 'N/A')}\n"
                f"   🚨 {priority_emoji} {ticket.get('priority', 'N/A')}\n"
                f"   📅 {ticket.get('created_at', 'N/A')[:10]}\n\n"
            )
        
        # Добавляем кнопку управления
        keyboard = get_ticket_actions_keyboard()
        
        await callback.message.edit_text(
            tickets_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        await callback.answer("❌ Ошибка при получении обращений")

@router.callback_query(F.data == "admin:new_tickets")
async def admin_new_tickets(callback: CallbackQuery):
    """Показать новые обращения (созданные за последние 2 дня)"""
    try:
        tickets = get_all_tickets_from_db(limit=100)
        
        if not tickets:
            await callback.message.edit_text("📭 Обращений нет.")
            await callback.answer()
            return
        
        # Фильтруем только новые (статус NEW) И созданные за последние 2 дня
        new_tickets = []
        two_days_ago = datetime.now() - timedelta(days=2)
        
        for ticket in tickets:
            if ticket.get('status') == 'NEW':
                # Пробуем распарсить дату создания
                try:
                    created_at_str = ticket.get('created_at', '')
                    # Убираем 'Z' и пробуем разные форматы
                    if 'Z' in created_at_str:
                        created_at_str = created_at_str.replace('Z', '+00:00')
                    created_at = datetime.fromisoformat(created_at_str)
                    if created_at > two_days_ago:
                        new_tickets.append(ticket)
                except Exception as parse_error:
                    # Если не удалось распарсить, просто добавляем все новые
                    logger.warning(f"Ошибка парсинга даты: {parse_error}")
                    new_tickets.append(ticket)
        
        if not new_tickets:
            await callback.message.edit_text("🆕 Новых обращений за последние 2 дня нет.")
            await callback.answer()
            return
        
        tickets_text = "<b>🆕 Новые обращения (последние 2 дня):</b>\n\n"
        
        for i, ticket in enumerate(new_tickets[:10], 1):
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(ticket.get('priority', ''), '')
            
            tickets_text += (
                f"{i}. 🆔 <b>#{ticket.get('id', 'N/A')}</b> - {ticket.get('type', 'N/A')}\n"
                f"   👤 {ticket.get('full_name', 'N/A')}\n"
                f"   📞 {ticket.get('contact', 'N/A')}\n"
                f"   🚨 {priority_emoji} {ticket.get('priority', 'N/A')}\n"
                f"   📅 Создано: {ticket.get('created_at', 'N/A')[:19]}\n\n"
            )
        
        await callback.message.edit_text(
            tickets_text,
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error getting new tickets: {e}")
        await callback.message.edit_text("❌ Ошибка при получении обращений")
        await callback.answer()

@router.callback_query(F.data == "admin:manage_tickets")
async def admin_manage_tickets(callback: CallbackQuery):
    """Управление обращениями - выбор обращения"""
    try:
        tickets = get_all_tickets_from_db(limit=20)
        
        if not tickets:
            await callback.message.edit_text("📭 Обращений нет.")
            await callback.answer()
            return
        
        # Формируем список для выбора
        tickets_text = "<b>🛠️ Управление обращениями</b>\n\n"
        tickets_text += "Выберите обращение для управления:\n\n"
        
        keyboard_buttons = []
        
        for ticket in tickets[:10]:  # Ограничим 10 для удобства
            status_emoji = {"NEW": "🆕", "IN_PROGRESS": "⚙️", "RESOLVED": "✅", "CLOSED": "🔒"}.get(ticket.get('status', ''), '')
            
            tickets_text += (
                f"{status_emoji} <b>#{ticket.get('id', 'N/A')}</b> - {ticket.get('full_name', 'N/A')}\n"
                f"   📝 {ticket.get('text', '')[:50]}...\n"
                f"   📅 {ticket.get('created_at', 'N/A')[:10]}\n\n"
            )
            
            # Добавляем кнопку для каждого обращения
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"#{ticket.get('id')} - {ticket.get('full_name')[:15]}...",
                    callback_data=f"manage:{ticket.get('id')}"
                )
            ])
        
        # Добавляем кнопку "Назад"
        keyboard_buttons.append([
            InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:back")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            tickets_text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error managing tickets: {e}")
        await callback.message.edit_text("❌ Ошибка при получении обращений")
        await callback.answer()

@router.callback_query(F.data.startswith("manage:"))
async def manage_single_ticket(callback: CallbackQuery):
    """Управление конкретным обращением"""
    try:
        ticket_id = int(callback.data.split(":")[1])
        
        # Получаем информацию о обращении
        tickets = get_all_tickets_from_db(limit=100)
        ticket = next((t for t in tickets if t.get('id') == ticket_id), None)
        
        if not ticket:
            await callback.answer("❌ Обращение не найдено")
            return
        
        # Форматируем информацию
        status_emoji = {"NEW": "🆕", "IN_PROGRESS": "⚙️", "RESOLVED": "✅", "CLOSED": "🔒"}.get(ticket.get('status', ''), '')
        priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(ticket.get('priority', ''), '')
        
        # Форматируем даты
        created_at = ticket.get('created_at', 'N/A')
        updated_at = ticket.get('updated_at', 'N/A')
        
        if created_at != 'N/A' and len(created_at) > 10:
            created_at = created_at[:19]
        if updated_at != 'N/A' and len(updated_at) > 10:
            updated_at = updated_at[:19]
        
        ticket_info = (
            f"🛠️ <b>Управление обращением</b>\n\n"
            f"🆔 <b>#{ticket.get('id', 'N/A')}</b>\n"
            f"👤 <b>ФИО:</b> {ticket.get('full_name', 'N/A')}\n"
            f"📞 <b>Контакт:</b> {ticket.get('contact', 'N/A')}\n"
            f"📋 <b>Тип:</b> {ticket.get('type', 'N/A')}\n"
            f"📊 <b>Статус:</b> {status_emoji} {ticket.get('status', 'N/A')}\n"
            f"🚨 <b>Приоритет:</b> {priority_emoji} {ticket.get('priority', 'N/A')}\n"
            f"📅 <b>Создано:</b> {created_at}\n"
            f"🔄 <b>Обновлено:</b> {updated_at}\n\n"
            f"📝 <b>Текст обращения:</b>\n{ticket.get('text', 'N/A')[:300]}...\n\n"
        )
        
        if ticket.get('admin_comment'):
            ticket_info += f"💬 <b>Комментарий:</b>\n{ticket.get('admin_comment')}\n\n"
        
        # Клавиатура для управления статусом
        keyboard = get_status_change_keyboard(ticket_id, ticket.get('status'))
        
        await callback.message.edit_text(
            ticket_info,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error managing ticket: {e}")
        await callback.answer("❌ Ошибка при управлении обращением")

@router.callback_query(F.data.startswith("status:"))
async def change_ticket_status(callback: CallbackQuery):
    """Изменить статус обращения"""
    try:
        data_parts = callback.data.split(":")
        if len(data_parts) != 3:
            await callback.answer("❌ Неверный формат команды")
            return
        
        ticket_id = int(data_parts[1])
        new_status = data_parts[2].upper()
        
        # Обновляем статус в базе
        success = update_ticket_status(ticket_id, new_status, f"Статус изменен на {new_status}")
        
        if success:
            # Обновляем локальную БД бота (если такое обращение есть)
            try:
                # Импортируем здесь, чтобы избежать циклического импорта
                from database import db_instance
                # Обновляем статус в локальной БД бота
                cursor = db_instance.conn.cursor()
                cursor.execute(
                    "UPDATE user_tickets SET status = ? WHERE ticket_id = ?",
                    (new_status, ticket_id)
                )
                db_instance.conn.commit()
            except Exception as e:
                logger.error(f"Error updating local DB: {e}")
            
            status_names = {
                "NEW": "Новый",
                "IN_PROGRESS": "В работе",
                "RESOLVED": "Решено",
                "CLOSED": "Закрыт"
            }
            
            await callback.answer(f"✅ Статус обращения #{ticket_id} изменен на '{status_names.get(new_status, new_status)}'")
            
            # Показываем обновленную информацию
            await manage_single_ticket(callback)
        else:
            await callback.answer("❌ Не удалось изменить статус")
            
    except Exception as e:
        logger.error(f"Error changing ticket status: {e}")
        await callback.answer("❌ Ошибка при изменении статуса")

@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery):
    """Показать пользователей"""
    try:
        tickets = get_all_tickets_from_db(limit=200)
        
        if not tickets:
            await callback.message.edit_text("👥 Пользователей пока нет.")
            await callback.answer()
            return
        
        # Собираем уникальных пользователей по ФИО
        users = {}
        for ticket in tickets:
            user_key = f"{ticket.get('full_name', '')}_{ticket.get('contact', '')}"
            
            if user_key not in users:
                users[user_key] = {
                    'full_name': ticket.get('full_name', ''),
                    'contact': ticket.get('contact', ''),
                    'count': 0,
                    'last_ticket': ticket,
                }
            users[user_key]['count'] += 1
        
        if not users:
            await callback.message.edit_text("👥 Пользователей пока нет.")
            await callback.answer()
            return
        
        # Сортируем по количеству обращений
        sorted_users = sorted(users.items(), key=lambda x: x[1]['count'], reverse=True)
        
        users_text = "<b>👥 Пользователи (топ-10):</b>\n\n"
        
        for i, (user_key, data) in enumerate(sorted_users[:10], 1):
            users_text += (
                f"{i}. 👤 <b>{data['full_name']}</b>\n"
                f"   📞 Контакт: {data['contact']}\n"
                f"   📊 Обращений: {data['count']}\n"
                f"   📅 Последнее: {data['last_ticket'].get('created_at', 'N/A')[:10]}\n\n"
            )
        
        users_text += f"<b>📈 Статистика:</b>\n"
        users_text += f"Всего уникальных пользователей: {len(users)}\n"
        users_text += f"Всего обращений: {len(tickets)}"
        
        await callback.message.edit_text(
            users_text,
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        await callback.message.edit_text("❌ Ошибка при получении данных о пользователях")
        await callback.answer()

@router.callback_query(F.data == "admin:export")
async def admin_export(callback: CallbackQuery, bot: Bot):
    """Экспорт данных"""
    try:
        # Получаем все обращения
        tickets = get_all_tickets_from_db(limit=500)
        
        if not tickets:
            await callback.message.edit_text("📁 Нет данных для экспорта.")
            await callback.answer()
            return
        
        # Создаем CSV файл
        output = BytesIO()
        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # Заголовок
        writer.writerow(['ID', 'Тип', 'Статус', 'Приоритет', 'ФИО', 'Контакт', 'Текст', 'Дата создания', 'Дата обновления', 'Комментарий'])
        
        # Данные
        for ticket in tickets:
            writer.writerow([
                ticket.get('id', ''),
                ticket.get('type', ''),
                ticket.get('status', ''),
                ticket.get('priority', ''),
                ticket.get('full_name', ''),
                ticket.get('contact', ''),
                (ticket.get('text', '')[:500]).replace('\n', ' '),
                ticket.get('created_at', ''),
                ticket.get('updated_at', ''),
                (ticket.get('admin_comment', '')[:200]).replace('\n', ' ') if ticket.get('admin_comment') else ''
            ])
        
        file_data = output.getvalue()
        file = BufferedInputFile(file_data, filename="tickets_export.csv")
        
        # Отправляем файл
        await bot.send_document(
            chat_id=callback.from_user.id,
            document=file,
            caption=f"📁 Экспорт обращений (CSV)\nВсего записей: {len(tickets)}"
        )
        
        await callback.message.delete()
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error exporting: {e}")
        await callback.message.edit_text("❌ Ошибка при экспорте данных")
        await callback.answer()

@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery, api_client: APIClient):
    """Показать статистику"""
    try:
        # Получаем статистику из базы напрямую
        tickets = get_all_tickets_from_db(limit=1000)
        
        if not tickets:
            await callback.message.edit_text("📊 Нет данных для статистики.")
            await callback.answer()
            return
        
        # Считаем статистику
        stats = {
            'total': len(tickets),
            'statuses': {
                'NEW': 0,
                'IN_PROGRESS': 0,
                'RESOLVED': 0,
                'CLOSED': 0
            },
            'priorities': {
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0
            },
            'types': {}
        }
        
        for ticket in tickets:
            status = ticket.get('status', 'NEW')
            priority = ticket.get('priority', 'MEDIUM')
            type_ = ticket.get('type', 'UNKNOWN')
            
            if status in stats['statuses']:
                stats['statuses'][status] += 1
            
            if priority in stats['priorities']:
                stats['priorities'][priority] += 1
            
            stats['types'][type_] = stats['types'].get(type_, 0) + 1
        
        # Формируем отчет
        report = (
            "📊 <b>РАСШИРЕННАЯ СТАТИСТИКА</b>\n\n"
            
            "<b>Обращения:</b>\n"
            f"📈 Всего: {stats['total']}\n"
            f"🆕 Новые: {stats['statuses']['NEW']}\n"
            f"⚙️ В работе: {stats['statuses']['IN_PROGRESS']}\n"
            f"✅ Решено: {stats['statuses']['RESOLVED']}\n"
            f"🔒 Закрыто: {stats['statuses']['CLOSED']}\n\n"
            
            "<b>Приоритеты:</b>\n"
            f"🔴 Высокий: {stats['priorities']['HIGH']}\n"
            f"🟡 Средний: {stats['priorities']['MEDIUM']}\n"
            f"🟢 Низкий: {stats['priorities']['LOW']}\n\n"
            
            "<b>Типы обращений:</b>\n"
        )
        
        for type_name, count in stats['types'].items():
            report += f"📋 {type_name}: {count}\n"
        
        await callback.message.edit_text(
            report,
            parse_mode=ParseMode.HTML
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await callback.answer("❌ Ошибка при получении статистики")

@router.callback_query(F.data == "admin:back")
async def admin_back(callback: CallbackQuery):
    """Вернуться в админ-панель"""
    await cmd_admin(callback.message)

def register_admin_handlers(dp):
    """Регистрация обработчиков администратора"""
    dp.include_router(router)