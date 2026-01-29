# add_user_id_column.py
import sqlite3
from pathlib import Path

# Путь к базе данных
db_path = Path("C:/Users/Admin/OneDrive/Рабочий стол/производственная практика/backend/support.db")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Проверяем, есть ли уже колонка user_id
        cursor.execute("PRAGMA table_info(tickets)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("Добавляем колонку user_id...")
            
            # Добавляем колонку user_id
            cursor.execute("ALTER TABLE tickets ADD COLUMN user_id VARCHAR(255)")
            
            # Добавляем значение по умолчанию для существующих записей
            cursor.execute("UPDATE tickets SET user_id = 'unknown' WHERE user_id IS NULL")
            
            conn.commit()
            print("✅ Колонка user_id успешно добавлена!")
        else:
            print("✅ Колонка user_id уже существует")
            
        # Проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(tickets)")
        print("\nОбновленная структура таблицы tickets:")
        for col in cursor.fetchall():
            print(f"  {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULLABLE'}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()
else:
    print(f"❌ База данных не найдена: {db_path}")