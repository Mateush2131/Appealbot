# keyboards/main.py
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Главное меню с кнопками"""
    builder = ReplyKeyboardBuilder()
    
    # Основные кнопки
    builder.add(KeyboardButton(text="📝 Создать обращение"))
    builder.add(KeyboardButton(text="📋 Мои обращения"))
    builder.add(KeyboardButton(text="📊 Статистика"))
    builder.add(KeyboardButton(text="❓ Помощь"))
    
    if is_admin:
        builder.add(KeyboardButton(text="👑 Админ-панель"))
    
    # Распределение по строкам
    builder.adjust(2, 2, 1 if is_admin else 0, 1)
    
    return builder.as_markup(resize_keyboard=True)

def get_ticket_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа обращения"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="❓ Вопрос", callback_data="ticket_type:question"),
        InlineKeyboardButton(text="⚠️ Жалоба", callback_data="ticket_type:complaint"),
        InlineKeyboardButton(text="💡 Предложение", callback_data="ticket_type:suggestion"),
    )
    
    builder.adjust(3)
    return builder.as_markup()

def get_priority_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора приоритета"""
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="🔴 Высокий", callback_data="priority:high"),
        InlineKeyboardButton(text="🟡 Средний", callback_data="priority:medium"),
        InlineKeyboardButton(text="🟢 Низкий", callback_data="priority:low"),
    )
    
    builder.adjust(3)
    return builder.as_markup()

def get_admin_panel() -> InlineKeyboardMarkup:
    """Панель администратора (расширенная)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Все обращения", callback_data="page:1"),
                InlineKeyboardButton(text="🆕 Новые", callback_data="admin:new_tickets"),
            ],
            [
                InlineKeyboardButton(text="🛠️ Управление", callback_data="admin:manage_tickets"),
                InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users"),
            ],
            [
                InlineKeyboardButton(text="📊 Статистика", callback_data="admin:stats"),
                InlineKeyboardButton(text="📁 Экспорт", callback_data="admin:export"),
            ]
        ]
    )

def get_ticket_actions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура действий с обращениями"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🛠️ Управление обращениями", callback_data="admin:manage_tickets"),
            ],
            [
                InlineKeyboardButton(text="⬅️ Назад", callback_data="admin:back"),
            ]
        ]
    )

def get_status_change_keyboard(ticket_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Клавиатура для изменения статуса обращения"""
    buttons = []
    
    # Кнопки статусов (кроме текущего)
    status_options = [
        ("🆕 Новый", "NEW"),
        ("⚙️ В работе", "IN_PROGRESS"),
        ("✅ Решено", "RESOLVED"),
        ("🔒 Закрыт", "CLOSED")
    ]
    
    for emoji_text, status in status_options:
        if status != current_status:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{emoji_text} ({status})",
                    callback_data=f"status:{ticket_id}:{status}"
                )
            ])
    
    # Кнопки навигации
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="admin:manage_tickets"),
        InlineKeyboardButton(text="🏠 В админ-панель", callback_data="admin:back")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
    """Клавиатура пагинации"""
    builder = InlineKeyboardBuilder()
    
    if current_page > 1:
        builder.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{prefix}:{current_page - 1}"))
    
    builder.add(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop"))
    
    if current_page < total_pages:
        builder.add(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"{prefix}:{current_page + 1}"))
    
    builder.adjust(3)
    return builder.as_markup()