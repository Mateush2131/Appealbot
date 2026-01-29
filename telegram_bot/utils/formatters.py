from datetime import datetime
from typing import Dict, Any, List
import json

class Formatters:
    """Класс форматирования"""
    
    @staticmethod
    def format_ticket(ticket: Dict[str, Any]) -> str:
        """Форматирование тикета для отображения"""
        status_emojis = {
            "NEW": "🆕",
            "IN_PROGRESS": "⚙️",
            "RESOLVED": "✅",
            "CLOSED": "🔒"
        }
        
        priority_emojis = {
            "LOW": "🟢",
            "MEDIUM": "🟡", 
            "HIGH": "🔴"
        }
        
        type_emojis = {
            "QUESTION": "❓",
            "COMPLAINT": "⚠️",
            "SUGGESTION": "💡"
        }
        
        # Парсим дату
        created_at = datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(ticket['updated_at'].replace('Z', '+00:00'))
        
        text = (
            f"{type_emojis.get(ticket['type'], '📋')} "
            f"<b>Тикет #{ticket['id']}</b>\n\n"
            
            f"📝 <b>Тип:</b> {ticket['type']}\n"
            f"📊 <b>Статус:</b> {status_emojis.get(ticket['status'], '')} {ticket['status']}\n"
            f"🚨 <b>Приоритет:</b> {priority_emojis.get(ticket['priority'], '')} {ticket['priority']}\n\n"
            
            f"👤 <b>Автор:</b> {ticket['full_name']}\n"
            f"📞 <b>Контакт:</b> {ticket['contact']}\n\n"
            
            f"📅 <b>Создан:</b> {created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"🔄 <b>Обновлен:</b> {updated_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        )
        
        if ticket.get('assigned_to'):
            text += f"👨‍💻 <b>Назначен:</b> {ticket['assigned_to']}\n\n"
        
        if ticket.get('admin_comment'):
            text += f"💬 <b>Комментарий:</b>\n{ticket['admin_comment']}\n\n"
        
        text += f"📋 <b>Текст обращения:</b>\n{ticket['text']}"
        
        return text
    
    @staticmethod
    def format_stats(stats: Dict[str, Any]) -> str:
        """Форматирование статистики"""
        status_emojis = {
            "NEW": "🆕",
            "IN_PROGRESS": "⚙️",
            "RESOLVED": "✅",
            "CLOSED": "🔒"
        }
        
        text = "📊 <b>Статистика системы</b>\n\n"
        text += f"📈 <b>Всего обращений:</b> {stats.get('total', 0)}\n\n"
        
        for status, count in stats.get('statuses', {}).items():
            emoji = status_emojis.get(status, '')
            text += f"{emoji} <b>{status}:</b> {count}\n"
        
        # Добавляем время генерации
        text += f"\n⏱️ <i>Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>"
        
        return text
    
    @staticmethod
    def format_list(tickets: List[Dict[str, Any]]) -> str:
        """Форматирование списка тикетов"""
        if not tickets:
            return "📭 Список пуст"
        
        text = "📋 <b>Список обращений</b>\n\n"
        
        for i, ticket in enumerate(tickets, 1):
            status_emoji = {
                "NEW": "🆕",
                "IN_PROGRESS": "⚙️",
                "RESOLVED": "✅",
                "CLOSED": "🔒"
            }.get(ticket['status'], '📋')
            
            priority_emoji = {
                "LOW": "🟢",
                "MEDIUM": "🟡",
                "HIGH": "🔴"
            }.get(ticket['priority'], '⚪')
            
            text += (
                f"{status_emoji} <b>#{ticket['id']}</b> - "
                f"{priority_emoji} {ticket['priority']}\n"
                f"👤 {ticket['full_name']} | "
                f"📝 {ticket['text'][:50]}...\n"
                f"📅 {ticket['created_at'][:10]}\n\n"
            )
        
        return text
    
    @staticmethod
    def format_json(data: Any) -> str:
        """Форматирование JSON"""
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def format_bytes(size: int) -> str:
        """Форматирование размера в байтах"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Форматирование длительности"""
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes} мин"
        elif seconds < 86400:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} ч {minutes} мин"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days} д {hours} ч"