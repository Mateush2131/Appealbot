from aiogram.fsm.state import State, StatesGroup

class TicketCreation(StatesGroup):
    """Состояния создания тикета"""
    full_name = State()
    contact = State()
    type = State()
    text = State()
    priority = State()
    attachments = State()
    confirmation = State()

class TicketEdit(StatesGroup):
    """Состояния редактирования тикета"""
    select_ticket = State()
    choose_action = State()
    edit_text = State()
    add_comment = State()
    change_status = State()
    change_priority = State()

class UserSettings(StatesGroup):
    """Состояния настроек пользователя"""
    main = State()
    notifications = State()
    language = State()
    theme = State()
    timezone = State()

class SearchTickets(StatesGroup):
    """Состояния поиска тикетов"""
    enter_query = State()
    choose_filter = State()
    view_results = State()

class FileUpload(StatesGroup):
    """Состояния загрузки файла"""
    waiting_file = State()
    processing = State()
    add_description = State()
    confirm = State()