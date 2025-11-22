import asyncio
import logging
import time
from typing import Callable, Any, Optional

logger = logging.getLogger("api_retry")

async def call_with_retry(
    func: Callable,
    *args,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    description: str = "API call",
    **kwargs
) -> Optional[Any]:
    """
    Выполнить функцию с экспоненциальным ретраем
    
    Args:
        func: Синхронная функция для выполнения
        max_attempts: Максимальное количество попыток (по умолчанию: 3)
        initial_delay: Начальная задержка в секундах (по умолчанию: 1.0)
        backoff_factor: Множитель задержки (по умолчанию: 2.0)
        max_delay: Максимальная задержка в секундах (по умолчанию: 60.0)
        description: Описание для логов
    """
    attempt = 1
    delay = initial_delay
    
    while attempt <= max_attempts:
        try:
            if attempt > 1:
                logger.warning(f"🔄 Попытка #{attempt} {description} (задержка: {delay:.1f}s)")
            
            # Выполняем функцию в отдельном потоке
            result = await asyncio.to_thread(func, *args, **kwargs)
            
            if attempt > 1:
                logger.info(f"✅ Успешно на попытке #{attempt} {description}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка на попытке #{attempt} {description}: {str(e)}")
            
            if attempt == max_attempts:
                logger.error(f"💔 Все попытки исчерпаны {description}")
                return None
            
            # Экспоненциальная задержка с ограничением
            actual_delay = min(delay, max_delay)
            logger.info(f"⏳ Ожидание {actual_delay:.1f}s перед следующей попыткой...")
            await asyncio.sleep(actual_delay)
            
            # Увеличиваем задержку для следующей попытки
            delay *= backoff_factor
            attempt += 1
    
    return None
