import sqlite3
import os
from pathlib import Path

# Находим базу данных
db_path = Path("C:\Users\Admin\OneDrive\Рабочий стол\производственная практика")
print(f"Путь к БД: {db_path.absolute()}")
print(f"БД существует: {db_path.exists()}")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Проверяем структуру таблицы
    cursor.execute("PRAGMA table_info(tickets)")
    columns = cursor.fetchall()
    print("\nСтруктура таблицы tickets:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Проверяем примеры user_id
    cursor.execute("SELECT id, user_id, full_name FROM tickets LIMIT 5")
    tickets = cursor.fetchall()
    
    print("\nПервые 5 записей:")
    for ticket in tickets:
        print(f"  ID: {ticket[0]}, User ID: {ticket[1]} (тип: {type(ticket[1])}), Имя: {ticket[2]}")
    
    # Проверяем все форматы user_id
    cursor.execute("SELECT DISTINCT user_id FROM tickets")
    user_ids = cursor.fetchall()
    
    print("\nУникальные user_id:")
    for user_id in user_ids:
        actual_id = user_id[0]
        print(f"  '{actual_id}' (тип: {type(actual_id)})")
    
    conn.close()
else:
    print("База данных не найдена!")