# database.py - простая версия для SQLite
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с локальной SQLite базой данных бота"""
    
    def __init__(self, db_path: str = "telegram_bot.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def _init_db(self) -> None:
        """Инициализация базы данных"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            logger.info(f"✅ Локальная БД инициализирована: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            raise
    
    def _create_tables(self) -> None:
        """Создание таблиц"""
        cursor = self.conn.cursor()
        
        # Таблица для обращений пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                ticket_id INTEGER,
                full_name TEXT NOT NULL,
                contact TEXT NOT NULL,
                type TEXT NOT NULL,
                text TEXT NOT NULL,
                priority TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'NEW',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица для пользователей бота
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Индексы для быстрого поиска
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_tickets_telegram_id ON user_tickets(telegram_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_tickets_created_at ON user_tickets(created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_bot_users_telegram_id ON bot_users(telegram_id)")
        
        self.conn.commit()
    
    def save_user_ticket(self, telegram_id: int, ticket_data: dict) -> bool:
        """Сохранение обращения пользователя"""
        try:
            cursor = self.conn.cursor()
            
            # Получаем текущее время
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO user_tickets 
                (telegram_id, ticket_id, full_name, contact, type, text, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                telegram_id,
                ticket_data.get('id'),
                ticket_data.get('full_name', ''),
                ticket_data.get('contact', ''),
                ticket_data.get('type', ''),
                ticket_data.get('text', ''),
                ticket_data.get('priority', 'MEDIUM'),
                ticket_data.get('status', 'NEW'),
                created_at
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving user ticket: {e}")
            return False
    
    def get_user_tickets(self, telegram_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получение обращений пользователя"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT 
                    ticket_id, 
                    full_name, 
                    contact, 
                    type, 
                    text, 
                    priority, 
                    status, 
                    datetime(created_at) as created_at
                FROM user_tickets 
                WHERE telegram_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (telegram_id, limit))
            
            tickets = cursor.fetchall()
            return [dict(ticket) for ticket in tickets]
            
        except Exception as e:
            logger.error(f"Error getting user tickets: {e}")
            return []
    
    def update_user(self, telegram_id: int, username: str = None, 
                   first_name: str = None, last_name: str = None) -> bool:
        """Обновление информации о пользователе"""
        try:
            cursor = self.conn.cursor()
            
            # Проверяем, есть ли пользователь
            cursor.execute("SELECT id FROM bot_users WHERE telegram_id = ?", (telegram_id,))
            user_exists = cursor.fetchone()
            
            if user_exists:
                # Обновляем существующего
                cursor.execute("""
                    UPDATE bot_users 
                    SET username = ?, first_name = ?, last_name = ?, last_activity = CURRENT_TIMESTAMP
                    WHERE telegram_id = ?
                """, (username, first_name, last_name, telegram_id))
            else:
                # Добавляем нового
                cursor.execute("""
                    INSERT INTO bot_users (telegram_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                """, (telegram_id, username, first_name, last_name))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False
    
    def close(self) -> None:
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("✅ Соединение с БД закрыто")

# Создаем глобальный экземпляр
db_instance = Database()

# Функции для удобного доступа
def save_user_ticket(telegram_id: int, ticket_data: dict) -> bool:
    return db_instance.save_user_ticket(telegram_id, ticket_data)

def get_user_tickets(telegram_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    return db_instance.get_user_tickets(telegram_id, limit)

def update_user(telegram_id: int, username: str = None, 
               first_name: str = None, last_name: str = None) -> bool:
    return db_instance.update_user(telegram_id, username, first_name, last_name)

def close_db() -> None:
    """Функция для закрытия БД"""
    db_instance.close()

def init_db() -> Database:
    """Функция для инициализации БД (для совместимости)"""
    return db_instance