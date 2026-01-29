from aiogram.fsm.state import State, StatesGroup

class AdminPanel(StatesGroup):
    """Состояния админ-панели"""
    main = State()
    view_tickets = State()
    manage_users = State()
    broadcast = State()
    export_data = State()
    system_settings = State()

class BroadcastMessage(StatesGroup):
    """Состояния рассылки"""
    select_type = State()
    enter_text = State()
    add_media = State()
    preview = State()
    confirm = State()
    sending = State()

class UserManagement(StatesGroup):
    """Состояния управления пользователями"""
    select_user = State()
    view_profile = State()
    edit_permissions = State()
    view_statistics = State()
    send_message = State()

class ExportData(StatesGroup):
    """Состояния экспорта данных"""
    select_format = State()
    select_period = State()
    choose_fields = State()
    processing = State()
    download = State()

class SystemSettings(StatesGroup):
    """Состояния системных настроек"""
    general = State()
    security = State()
    notifications = State()
    backup = State()
    api_settings = State()