import sys
import os

# Добавляем путь к бэкенду
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from app.main import app
    print("✅ Backend импортирован успешно")
    
    if __name__ == "__main__":
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        print(f"🚀 Запуск FastAPI на порту {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Создаю тестовое приложение...")
    
    # Создаем минимальное приложение для теста
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"message": "Education Support API", "status": "working"}
    
    @app.get("/health")
    def health():
        return {"status": "healthy"}
    
    if __name__ == "__main__":
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(app, host="0.0.0.0", port=port)