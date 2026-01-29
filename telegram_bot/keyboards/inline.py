from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_inline_menu() -> InlineKeyboardMarkup:
    """Инлайн меню"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📋 Мои тикеты", callback_data="inline:my_tickets"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="inline:stats")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔔 Настройки", callback_data="inline:settings"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="inline:help")
    )
    
    builder.row(
        InlineKeyboardButton(text="🌐 Сайт поддержки", url="https://example.com"),
        InlineKeyboardButton(text="📞 Контакты", callback_data="inline:contacts")
    )
    
    return builder.as_markup()

def get_ticket_filters_keyboard() -> InlineKeyboardMarkup:
    """Фильтры для тикетов"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🆕 Новые", callback_data="filter:status:NEW"),
        InlineKeyboardButton(text="⚙️ В работе", callback_data="filter:status:IN_PROGRESS"),
        InlineKeyboardButton(text="✅ Решено", callback_data="filter:status:RESOLVED")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔴 Высокий приоритет", callback_data="filter:priority:HIGH"),
        InlineKeyboardButton(text="🟡 Средний", callback_data="filter:priority:MEDIUM"),
        InlineKeyboardButton(text="🟢 Низкий", callback_data="filter:priority:LOW")
    )
    
    builder.row(
        InlineKeyboardButton(text="❓ Вопросы", callback_data="filter:type:QUESTION"),
        InlineKeyboardButton(text="⚠️ Жалобы", callback_data="filter:type:COMPLAINT"),
        InlineKeyboardButton(text="💡 Предложения", callback_data="filter:type:SUGGESTION")
    )
    
    builder.row(
        InlineKeyboardButton(text="🧹 Сбросить фильтры", callback_data="filter:reset"),
        InlineKeyboardButton(text="🔍 Расширенный поиск", callback_data="filter:advanced")
    )
    
    builder.adjust(3, 3, 3, 2)
    return builder.as_markup()

def get_admin_actions_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    """Действия администратора"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👤 Назначить себе", callback_data=f"admin:assign_self:{ticket_id}"),
        InlineKeyboardButton(text="👥 Назначить другому", callback_data=f"admin:assign_other:{ticket_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="📝 Добавить комментарий", callback_data=f"admin:comment:{ticket_id}"),
        InlineKeyboardButton(text="📎 Прикрепить файл", callback_data=f"admin:attach:{ticket_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="📊 Изменить статус", callback_data=f"admin:change_status:{ticket_id}"),
        InlineKeyboardButton(text="🚨 Изменить приоритет", callback_data=f"admin:change_priority:{ticket_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="📋 Детали пользователя", callback_data=f"admin:user_details:{ticket_id}"),
        InlineKeyboardButton(text="⏱️ История изменений", callback_data=f"admin:history:{ticket_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="🗑️ Удалить тикет", callback_data=f"admin:delete:{ticket_id}"),
        InlineKeyboardButton(text="📤 Экспорт", callback_data=f"admin:export:{ticket_id}")
    )
    
    builder.adjust(2, 2, 2, 2, 2)
    return builder.as_markup()

def get_status_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    """Выбор статуса"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🆕 Новый", callback_data=f"status:NEW:{ticket_id}"),
        InlineKeyboardButton(text="⚙️ В работе", callback_data=f"status:IN_PROGRESS:{ticket_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="✅ Решено", callback_data=f"status:RESOLVED:{ticket_id}"),
        InlineKeyboardButton(text="🔒 Закрыт", callback_data=f"status:CLOSED:{ticket_id}")
    )
    
    builder.row(
        InlineKeyboardButton(text="⏸️ На паузе", callback_data=f"status:PAUSED:{ticket_id}"),
        InlineKeyboardButton(text="🔄 Возвращен", callback_data=f"status:REOPENED:{ticket_id}")
    )
    
    builder.adjust(2, 2, 2)
    return builder.as_markup()

def get_yes_no_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура да/нет"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да, подтверждаю", callback_data=f"confirm:{action}:{item_id}:yes"),
        InlineKeyboardButton(text="❌ Нет, отменить", callback_data=f"confirm:{action}:{item_id}:no")
    )
    
    return builder.as_markup()

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Настройки"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings:notifications"),
        InlineKeyboardButton(text="🌍 Язык", callback_data="settings:language")
    )
    
    builder.row(
        InlineKeyboardButton(text="📱 Тема", callback_data="settings:theme"),
        InlineKeyboardButton(text="⏰ Часовой пояс", callback_data="settings:timezone")
    )
    
    builder.row(
        InlineKeyboardButton(text="🔒 Конфиденциальность", callback_data="settings:privacy"),
        InlineKeyboardButton(text="📊 Аналитика", callback_data="settings:analytics")
    )
    
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="settings:back")
    )
    
    builder.adjust(2, 2, 2, 1)
    return builder.as_markup()