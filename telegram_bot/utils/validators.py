import re
from typing import Optional, Tuple
from datetime import datetime

class Validators:
    """Класс валидаторов"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Валидация email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация телефона"""
        # Убираем все нецифровые символы
        digits = re.sub(r'\D', '', phone)
        
        # Проверяем российские номера
        if len(digits) == 11 and digits.startswith(('7', '8')):
            return True
        
        # Проверяем международные форматы
        if len(digits) >= 10 and len(digits) <= 15:
            return True
        
        return False
    
    @staticmethod
    def validate_full_name(name: str) -> Tuple[bool, Optional[str]]:
        """Валидация ФИО"""
        # Проверяем длину
        if len(name) < 2:
            return False, "Имя слишком короткое"
        
        if len(name) > 100:
            return False, "Имя слишком длинное"
        
        # Проверяем наличие только букв, пробелов и дефисов
        if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$', name):
            return False, "Имя содержит недопустимые символы"
        
        # Проверяем количество слов
        words = name.split()
        if len(words) < 2:
            return False, "Введите имя и фамилию"
        
        return True, None
    
    @staticmethod
    def validate_ticket_text(text: str) -> Tuple[bool, Optional[str]]:
        """Валидация текста обращения"""
        # Проверяем длину
        if len(text) < 10:
            return False, "Текст слишком короткий (минимум 10 символов)"
        
        if len(text) > 5000:
            return False, "Текст слишком длинный (максимум 5000 символов)"
        
        # Проверяем наличие запрещенных слов
        banned_words = ['спам', 'реклама', 'вирус', 'хакер']
        for word in banned_words:
            if word in text.lower():
                return False, f"Текст содержит запрещенное слово: {word}"
        
        return True, None
    
    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """Валидация даты"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Очистка ввода от опасных символов"""
        # Удаляем HTML теги
        clean = re.sub(r'<[^>]*>', '', text)
        
        # Экранируем специальные символы
        clean = clean.replace('&', '&amp;')
        clean = clean.replace('<', '&lt;')
        clean = clean.replace('>', '&gt;')
        clean = clean.replace('"', '&quot;')
        clean = clean.replace("'", '&#39;')
        
        return clean
    
    @staticmethod
    def is_admin(user_id: int, admin_ids: list) -> bool:
        """Проверка является ли пользователь админом"""
        return user_id in admin_ids
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> Tuple[bool, Optional[str]]:
        """Валидация размера файла"""
        if file_size > max_size:
            size_mb = max_size / (1024 * 1024)
            return False, f"Файл слишком большой. Максимальный размер: {size_mb}MB"
        
        return True, None
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: list) -> Tuple[bool, Optional[str]]:
        """Валидация типа файла"""
        extension = filename.split('.')[-1].lower()
        
        if extension not in allowed_types:
            allowed = ', '.join(allowed_types)
            return False, f"Недопустимый тип файла. Разрешены: {allowed}"
        
        return True, None