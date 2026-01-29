import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
import httpx
from httpx import AsyncClient, Timeout, HTTPStatusError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import config

logger = logging.getLogger(__name__)
async def get_tickets_by_user_id(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
    """Получение обращений по user_id (работает с любым форматом)"""
    try:
        # Пробуем получить все обращения и отфильтровать
        all_tickets = []
        skip = 0
        limit = 100
        
        while True:
            tickets = await self.get_tickets(skip=skip, limit=limit)
            if not tickets:
                break
            
            # Фильтруем по user_id
            for ticket in tickets:
                ticket_user_id = ticket.get('user_id')
                
                # Проверяем все возможные форматы
                if isinstance(ticket_user_id, str):
                    # Если user_id в формате "user_12345"
                    if ticket_user_id == f"user_{user_id}":
                        all_tickets.append(ticket)
                    # Если user_id это просто число в виде строки
                    elif ticket_user_id == str(user_id):
                        all_tickets.append(ticket)
                elif isinstance(ticket_user_id, int):
                    # Если user_id это число
                    if ticket_user_id == int(user_id):
                        all_tickets.append(ticket)
            
            # Если получили меньше лимита, значит это последняя страница
            if len(tickets) < limit:
                break
            
            skip += limit
        
        return all_tickets
        
    except Exception as e:
        logger.error(f"Error getting tickets by user_id {user_id}: {e}")
        return []
class APIClient:
    """Умный клиент для работы с API"""
    
    def __init__(self):
        self.base_url = config.api.base_url
        self.timeout = Timeout(config.api.timeout)
        self.headers = {
            "User-Agent": "Telegram-Support-Bot/1.0",
            "Content-Type": "application/json",
        }
        
        if config.api.api_key:
            self.headers["Authorization"] = f"Bearer {config.api.api_key}"
    
    def _create_client(self) -> AsyncClient:
        """Создание клиента с настройками"""
        return AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    @retry(
        stop=stop_after_attempt(config.api.max_retries),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
    )
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Выполнение запроса с повторными попытками"""
        async with self._create_client() as client:
            try:
                response = await client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                return response.json() if response.content else None
            except HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                if e.response.status_code == 401:
                    raise
                return None
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создание обращения"""
        return await self._make_request("POST", "/tickets/", json=ticket_data)
    
    async def get_tickets(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Получение списка обращений"""
        # Ограничиваем лимит 100, как требует API
        if limit > 100:
            limit = 100
            
        params = {"skip": skip, "limit": limit}
        if filters:
            params.update(filters)
        
        result = await self._make_request("GET", "/tickets/", params=params)
        return result if result else []
    
    async def get_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Получение обращения по ID"""
        return await self._make_request("GET", f"/tickets/{ticket_id}")
    
    async def update_ticket(
        self, 
        ticket_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновление обращения"""
        return await self._make_request("PATCH", f"/tickets/{ticket_id}", json=update_data)
    
    async def add_comment(self, ticket_id: int, comment: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Добавление комментария к обращению"""
        update_data = {
            "admin_comment": comment,
            "assigned_to": f"telegram_{user_id}"
        }
        return await self.update_ticket(ticket_id, update_data)
    
    async def change_status(
        self, 
        ticket_id: int, 
        status: str, 
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Изменение статуса обращения"""
        update_data = {
            "status": status,
            "assigned_to": f"telegram_{user_id}"
        }
        return await self.update_ticket(ticket_id, update_data)
    
    async def get_stats(self) -> Optional[Dict[str, Any]]:
        """Получение статистики"""
        return await self._make_request("GET", "/tickets/stats")
    
    async def search_tickets(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Поиск обращений по любому полю"""
        return await self._make_request("GET", "/tickets/", params={"search": query})
    
    # ВАЖНО: Обновленный метод для поиска обращений пользователя
    async def get_user_tickets(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """Получение обращений конкретного пользователя"""
        # Сначала пробуем поиск по user_id в формате "user_12345"
        user_tickets = []
        
        try:
            # Пробуем разные форматы поиска
            search_formats = [
                f"user_{user_id}",  # формат "user_12345"
                str(user_id),        # просто число
            ]
            
            for search_query in search_formats:
                try:
                    result = await self.search_tickets(search_query)
                    if result:
                        # Фильтруем только обращения этого пользователя
                        for ticket in result:
                            ticket_user_id = ticket.get('user_id')
                            if isinstance(ticket_user_id, str) and ticket_user_id == f"user_{user_id}":
                                user_tickets.append(ticket)
                            elif isinstance(ticket_user_id, int) and ticket_user_id == user_id:
                                user_tickets.append(ticket)
                            elif str(ticket_user_id) == str(user_id):
                                user_tickets.append(ticket)
                        
                        # Если нашли обращения, выходим
                        if user_tickets:
                            break
                except Exception as e:
                    logger.error(f"Error searching with query {search_query}: {e}")
                    continue
            
            # Если не нашли через поиск, получаем все обращения и фильтруем
            if not user_tickets:
                all_tickets = await self.get_tickets(limit=500)  # Получаем все доступные
                if all_tickets:
                    for ticket in all_tickets:
                        ticket_user_id = ticket.get('user_id')
                        if isinstance(ticket_user_id, str) and ticket_user_id == f"user_{user_id}":
                            user_tickets.append(ticket)
                        elif isinstance(ticket_user_id, int) and ticket_user_id == user_id:
                            user_tickets.append(ticket)
                        elif str(ticket_user_id) == str(user_id):
                            user_tickets.append(ticket)
            
            return user_tickets if user_tickets else []
            
        except Exception as e:
            logger.error(f"Error getting user tickets: {e}")
            return []
    
    async def upload_attachment(
        self, 
        ticket_id: int, 
        file_data: bytes, 
        filename: str, 
        content_type: str
    ) -> Optional[Dict[str, Any]]:
        """Загрузка вложения"""
        # Здесь нужно будет реализовать загрузку файлов
        # Для начала можно сохранять как комментарий
        comment = f"📎 Прикреплен файл: {filename}"
        return await self.add_comment(ticket_id, comment, 0)

class CachedAPIClient(APIClient):
    """Клиент с кэшированием"""
    
    def __init__(self, redis_client):
        super().__init__()
        self.redis = redis_client
    
    async def get_tickets_cached(
        self, 
        skip: int = 0, 
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        ttl: int = 60  # 1 минута
    ) -> Optional[List[Dict[str, Any]]]:
        """Получение с кэшированием"""
        cache_key = f"tickets:{skip}:{limit}:{json.dumps(filters or {})}"
        
        # Пытаемся получить из кэша
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Получаем из API
        result = await self.get_tickets(skip, limit, filters)
        
        if result:
            # Сохраняем в кэш
            await self.redis.setex(cache_key, ttl, json.dumps(result))
        
        return result
    
    async def get_stats_cached(self, ttl: int = 300) -> Optional[Dict[str, Any]]:
        """Статистика с кэшированием"""
        cache_key = "stats:global"
        
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        result = await self.get_stats()
        
        if result:
            await self.redis.setex(cache_key, ttl, json.dumps(result))
        
        return result