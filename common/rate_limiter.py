import asyncio
import time
from typing import Dict, List
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.orm import Session
from app.services.translation_service import t
import logging

logger = logging.getLogger("rate_limiter")

class RateLimiterMiddleware(BaseMiddleware):
    """Ограничение 15 запросов в минуту на пользователя"""
    
    def __init__(self, max_requests: int = 15, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[int, List[float]] = {}  # user_id -> [timestamps]
        self.lock = asyncio.Lock()
        super().__init__()
    
    async def __call__(self, handler, event: Message, data: dict):
        # Пропускаем команды и языковые выборы
        if event.text and (event.text.startswith("/") or event.text in ["English", "Русский", "Қазақша", "Кыргызча", "O'zbekcha", "Українська"]):
            return await handler(event, data)
        
        user_id = event.from_user.id
        
        async with self.lock:
            now = time.time()
            
            # Инициализируем список для нового пользователя
            if user_id not in self.requests:
                self.requests[user_id] = []
            
            # Очищаем старые записи (старше window_seconds)
            self.requests[user_id] = [
                ts for ts in self.requests[user_id] 
                if now - ts < self.window_seconds
            ]
            
            # Проверяем лимит
            if len(self.requests[user_id]) >= self.max_requests:
                logger.warning(f"⛔ Rate limit exceeded: user={user_id}, requests={len(self.requests[user_id])}")
                
                # Получаем язык для отправки сообщения
                db = data.get("db")
                if not db:
                    from generated_code.common.db import get_db
                    db = next(get_db())
                
                lang = "ru"  # Фолбэк
                try:
                    pref = db.query(UserPreference).filter_by(telegram_user_id=user_id).first()
                    if pref:
                        lang = pref.language_code
                except:
                    pass
                
                await event.answer(t("rate_limit_error", lang, db))
                return  # Не вызываем handler
        
            # Добавляем текущий запрос
            self.requests[user_id].append(now)
            logger.debug(f"✅ Request allowed: user={user_id}, total={len(self.requests[user_id])}")
        
        return await handler(event, data)
    
    def get_stats(self) -> dict:
        """Получить статистику rate limiter"""
        return {
            "total_users": len(self.requests),
            "users_with_limits": sum(1 for req in self.requests.values() if len(req) >= self.max_requests)
        }
