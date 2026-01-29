import logging
import sys
from pathlib import Path

def setup_logging():
    """Настройка логирования для бота"""
    
    # Создаем логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Формат сообщений
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Консольный обработчик
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый обработчик (лог в файл)
    try:
        log_file = Path("bot.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logging.info(f"Логирование в файл: {log_file.absolute()}")
    except Exception as e:
        logging.warning(f"Не удалось настроить файловое логирование: {e}")
    
    logging.info("Логирование настроено успешно")