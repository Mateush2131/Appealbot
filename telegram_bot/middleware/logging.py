# middleware/logging.py
import logging
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging"""
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        # Log incoming event
        user = None
        
        # Пытаемся получить пользователя из разных типов событий
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        elif event.inline_query:
            user = event.inline_query.from_user
        elif event.chosen_inline_result:
            user = event.chosen_inline_result.from_user
        
        if user:
            logger.info(f"User {user.id} ({user.username if user.username else 'no username'}): Event type: {event.event_type}")
        
        try:
            # Execute handler
            result = await handler(event, data)
            return result
        except Exception as e:
            logger.error(f"Handler error: {e}", exc_info=True)
            raise