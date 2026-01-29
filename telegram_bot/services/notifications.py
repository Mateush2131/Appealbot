# services/notifications.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup

from config import config
from services.api_client import APIClient

logger = logging.getLogger(__name__)

@dataclass
class Notification:
    """Модель уведомления"""
    user_id: int
    message: str
    keyboard: Optional[InlineKeyboardMarkup] = None
    priority: str = "normal"  # low, normal, high
    scheduled_at: Optional[datetime] = None

class NotificationService:
    """Сервис умных уведомлений"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.api_client = APIClient()
        self.queue = asyncio.Queue()
        self.is_running = False
    
    async def notify_new_ticket(self, ticket: Dict[str, Any]):
        """Уведомление о новом тикете"""
        try:
            message = (
                f"🚨 <b>НОВОЕ ОБРАЩЕНИЕ</b>\n\n"
                f"🆔 <b>ID:</b> #{ticket['id']}\n"
                f"👤 <b>Автор:</b> {ticket['full_name']}\n"
                f"📞 <b>Контакт:</b> {ticket['contact']}\n"
                f"📋 <b>Тип:</b> {ticket['type']}\n"
                f"🚨 <b>Приоритет:</b> {ticket['priority']}\n\n"
                f"📝 <b>Текст:</b>\n{ticket['text'][:200]}...\n\n"
                f"⏰ <b>Создано:</b> {ticket['created_at']}"
            )
            
            for admin_id in config.bot.admin_ids:
                try:
                    await self.bot.send_message(admin_id, message, parse_mode="HTML")
                except Exception as e:
                    logger.error(f"Failed to send notification to admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in notify_new_ticket: {e}")
    
    async def notify_status_change(self, ticket_id: int, old_status: str, new_status: str, user_id: int):
        """Уведомление об изменении статуса"""
        try:
            message = (
                f"🔄 <b>Статус обращения изменен</b>\n\n"
                f"🆔 <b>Обращение:</b> #{ticket_id}\n"
                f"📊 <b>Статус:</b> {old_status} → {new_status}\n"
                f"👤 <b>Изменено:</b> пользователем {user_id}"
            )
            
            # Здесь можно добавить логику уведомления пользователя
            # если у него есть telegram_id в системе
            
        except Exception as e:
            logger.error(f"Error in notify_status_change: {e}")
    
    async def send_immediate(self, user_id: int, message: str, keyboard=None):
        """Немедленная отправка уведомления"""
        try:
            await self.bot.send_message(user_id, message, parse_mode="HTML", reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Failed to send immediate notification to {user_id}: {e}")
    
    async def schedule_notification(self, notification: Notification):
        """Планирование уведомления"""
        await self.queue.put(notification)
    
    async def start(self):
        """Запуск обработчика очереди"""
        self.is_running = True
        asyncio.create_task(self._process_queue())
    
    async def _process_queue(self):
        """Обработка очереди уведомлений"""
        while self.is_running:
            try:
                notification = await self.queue.get()
                
                if notification.scheduled_at:
                    # Если уведомление запланировано на будущее
                    wait_time = (notification.scheduled_at - datetime.now()).total_seconds()
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                
                await self.send_immediate(
                    notification.user_id,
                    notification.message,
                    notification.keyboard
                )
                
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing notification queue: {e}")
                await asyncio.sleep(1)
    
    async def send_daily_report(self):
        """Ежедневный отчет"""
        try:
            stats = await self.api_client.get_stats()
            
            if not stats:
                return
            
            report = (
                f"📊 <b>ЕЖЕДНЕВНЫЙ ОТЧЕТ</b>\n\n"
                f"📈 <b>Всего обращений:</b> {stats.get('total', 0)}\n"
                f"🆕 <b>Новых:</b> {stats.get('statuses', {}).get('NEW', 0)}\n"
                f"⚙️ <b>В работе:</b> {stats.get('statuses', {}).get('IN_PROGRESS', 0)}\n"
                f"✅ <b>Решено:</b> {stats.get('statuses', {}).get('RESOLVED', 0)}\n"
                f"🔒 <b>Закрыто:</b> {stats.get('statuses', {}).get('CLOSED', 0)}\n\n"
                f"📅 {datetime.now().strftime('%d.%m.%Y')}"
            )
            
            for admin_id in config.bot.admin_ids:
                await self.send_immediate(admin_id, report)
                
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
    
    async def shutdown(self):
        """Завершение работы"""
        self.is_running = False
        logger.info("Notification service shutdown")