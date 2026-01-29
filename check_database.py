import sqlite3
import os
from pathlib import Path

def check_database():
    """Проверить базу данных и структуру таблиц"""
    
    # Определяем путь к БД
    db_paths = [
        # Путь к основной БД бэкенда
        Path("производственная практика/backend/support.db"),
        # Путь к БД бота
        Path("производственная практика/telegram_bot/telegram_bot.db"),
        # Абсолютные пути
        Path("C:/Users/Admin/OneDrive/Рабочий стол/производственная практика/backend/support.db"),
        Path("C:/Users/Admin/OneDrive/Рабочий стол/производственная практика/telegram_bot/telegram_bot.db")
    ]
    
    for db_path in db_paths:
        print(f"\n{'='*60}")
        print(f"Проверяем: {db_path.absolute()}")
        print(f"Файл существует: {db_path.exists()}")
        
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Получаем список всех таблиц
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                print(f"\nТаблицы в базе:")
                for table in tables:
                    table_name = table[0]
                    print(f"  - {table_name}")
                    
                    # Получаем структуру таблицы
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    for col in columns:
                        print(f"    {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULLABLE'}")
                    
                    # Получаем количество записей
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"    Записей: {count}")
                    
                    # Если это таблица tickets, покажем примеры
                    if table_name == 'tickets':
                        cursor.execute(f"SELECT id, user_id, full_name, type, status FROM {table_name} LIMIT 5")
                        tickets = cursor.fetchall()
                        print(f"\n    Примеры записей:")
                        for ticket in tickets:
                            print(f"      ID: {ticket[0]}, User ID: '{ticket[1]}' (тип: {type(ticket[1])}), "
                                  f"Имя: {ticket[2]}, Тип: {ticket[3]}, Статус: {ticket[4]}")
                
                conn.close()
            except Exception as e:
                print(f"  Ошибка при подключении: {e}")

if __name__ == "__main__":
    print("ПРОВЕРКА БАЗЫ ДАННЫХ")
    check_database()