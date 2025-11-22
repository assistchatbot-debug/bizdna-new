from sqlalchemy.orm import Session
from app.models import UIText
import logging

# Настройка логирования для кэша
cache_logger = logging.getLogger("translation_cache")

# Кэш для переводов: ключ (key, lang) -> текст
_translation_cache = {}
_cache_hits = 0
_cache_misses = 0

def t(key: str, lang: str, db: Session) -> str:
    """Получение перевода с кэшированием"""
    global _translation_cache, _cache_hits, _cache_misses
    
    cache_key = (key, lang)
    
    # Проверяем кэш
    if cache_key in _translation_cache:
        _cache_hits += 1
        if _cache_hits % 50 == 0:  # Логируем каждые 50 попаданий
            cache_logger.info(f"📊 Кэш переводов: hits={_cache_hits}, misses={_cache_misses}, эффективность={(_cache_hits/(_cache_hits+_cache_misses)*100):.1f}%")
        return _translation_cache[cache_key]
    
    _cache_misses += 1
    
    # Запрос в БД
    row = db.query(UIText).filter(UIText.key == key, UIText.language == lang).first()
    
    if not row:
        cache_logger.warning(f"❌ Ключ '{key}' не найден для языка '{lang}'")
        result = f"[{key}] (not found)"
    else:
        result = row.text
    
    # Сохраняем в кэш, ограничиваем размер до 256 записей (FIFO)
    if len(_translation_cache) >= 256:
        # Удаляем самый старый элемент
        _translation_cache.pop(next(iter(_translation_cache)))
        cache_logger.debug("🗑️ Кэш переводов: достигнут лимит, удалена старая запись")
    
    _translation_cache[cache_key] = result
    cache_logger.info(f"💾 Кэш переводов: добавлено '{key}' ({lang}), размер кэша: {len(_translation_cache)}")
    
    return result

def get_cache_stats() -> str:
    """Получить статистику кэша для логирования"""
    global _cache_hits, _cache_misses
    total = _cache_hits + _cache_misses
    if total == 0:
        return "Кэш переводов: еще не использовался"
    hit_rate = (_cache_hits / total) * 100
    return f"Кэш переводов: hits={_cache_hits}, misses={_cache_misses}, эффективность={hit_rate:.1f}%"

# Автоматическое логирование статистики каждый час
import threading, time

def _log_cache_stats_periodically():
    while True:
        time.sleep(3600)  # Каждый час
        cache_logger.info(get_cache_stats())

# Запускаем фоновый поток (не влияет на asyncio)
stats_thread = threading.Thread(target=_log_cache_stats_periodically, daemon=True)
stats_thread.start()
