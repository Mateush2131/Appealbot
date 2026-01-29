import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
import io

from config import config

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Сервис аналитики"""
    
    def __init__(self):
        self.events = []
        self.metrics = defaultdict(list)
    
    async def track_event(
        self, 
        user_id: int, 
        event_type: str, 
        data: Optional[Dict[str, Any]] = None
    ):
        """Отслеживание события"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "data": data or {}
        }
        
        self.events.append(event)
        
        # Ограничиваем размер истории
        if len(self.events) > 10000:
            self.events = self.events[-10000:]
        
        logger.info(f"Event tracked: {event_type} from user {user_id}")
    
    async def track_metric(self, metric_name: str, value: float):
        """Отслеживание метрики"""
        self.metrics[metric_name].append({
            "timestamp": datetime.now().isoformat(),
            "value": value
        })
    
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Статистика пользователя"""
        user_events = [e for e in self.events if e["user_id"] == user_id]
        
        # Группировка по типам событий
        event_counts = defaultdict(int)
        for event in user_events:
            event_counts[event["event_type"]] += 1
        
        # Время первого и последнего события
        if user_events:
            first_event = min(user_events, key=lambda x: x["timestamp"])
            last_event = max(user_events, key=lambda x: x["timestamp"])
        else:
            first_event = last_event = None
        
        return {
            "total_events": len(user_events),
            "event_types": dict(event_counts),
            "first_seen": first_event["timestamp"] if first_event else None,
            "last_seen": last_event["timestamp"] if last_event else None,
        }
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Системная статистика"""
        # Группировка событий по часам
        hourly_counts = defaultdict(int)
        for event in self.events[-1000:]:  # Последние 1000 событий
            hour = datetime.fromisoformat(event["timestamp"]).hour
            hourly_counts[hour] += 1
        
        # Активные пользователи (события за последние 24 часа)
        day_ago = datetime.now() - timedelta(days=1)
        active_users = {
            event["user_id"]
            for event in self.events
            if datetime.fromisoformat(event["timestamp"]) > day_ago
        }
        
        return {
            "total_events": len(self.events),
            "active_users_24h": len(active_users),
            "events_by_hour": dict(hourly_counts),
            "metrics": {k: len(v) for k, v in self.metrics.items()},
        }
    
    async def generate_chart(
        self, 
        chart_type: str = "events_by_hour"
    ) -> Optional[bytes]:
        """Генерация графика"""
        try:
            if chart_type == "events_by_hour":
                stats = await self.get_system_stats()
                hours = list(range(24))
                counts = [stats["events_by_hour"].get(h, 0) for h in hours]
                
                plt.figure(figsize=(10, 6))
                plt.bar(hours, counts, color='skyblue')
                plt.title('Активность по часам')
                plt.xlabel('Час')
                plt.ylabel('Количество событий')
                plt.xticks(hours)
                plt.grid(axis='y', alpha=0.3)
                
            elif chart_type == "user_activity":
                # Здесь можно реализовать другие графики
                pass
            
            # Сохранение в bytes
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
            buf.seek(0)
            plt.close()
            
            return buf.read()
            
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return None
    
    async def export_data(self, format: str = "json") -> Optional[str]:
        """Экспорт данных"""
        try:
            data = {
                "events": self.events[-1000:],  # Экспортируем последние 1000 событий
                "metrics": self.metrics,
                "timestamp": datetime.now().isoformat(),
            }
            
            if format == "json":
                return json.dumps(data, ensure_ascii=False, indent=2)
            elif format == "csv":
                # Здесь можно реализовать CSV экспорт
                pass
                
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return None
    
    async def shutdown(self):
        """Завершение работы"""
        # Можно сохранить данные в файл
        try:
            with open("analytics_backup.json", "w") as f:
                json.dump({
                    "events": self.events,
                    "metrics": self.metrics,
                    "exported_at": datetime.now().isoformat()
                }, f)
        except Exception as e:
            logger.error(f"Error saving analytics backup: {e}")