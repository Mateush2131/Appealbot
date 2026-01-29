# middleware/dependencies.py
import logging
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)

class DependenciesMiddleware(BaseMiddleware):
    """Middleware для внедрения зависимостей в хендлеры"""
    
    def __init__(self):
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Получаем диспетчер из data
        dispatcher = data.get('dispatcher')
        
        if dispatcher and hasattr(dispatcher, 'workflow_data'):
            # Добавляем сервисы из workflow_data диспетчера
            for key in ['analytics_service', 'api_client', 'notification_service']:
                if key in dispatcher.workflow_data:
                    data[key] = dispatcher.workflow_data[key]
        
        # Вызываем следующий middleware или хендлер
        return await handler(event, data)