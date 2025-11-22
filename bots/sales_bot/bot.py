#!/usr/bin/env python3
import sys

import os, logging, asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from openai import OpenAI
from app.db.session import get_db
from app.services.company_cache import get_company_id_cached
from common.api_retry import call_with_retry
from common.rate_limiter import RateLimiterMiddleware  # Добавлен импорт
from sqlalchemy.orm import Session
from app.models.all_models import Company, Lead, UserPreference, Interaction, UIText
from app.services.translation_service import t
from datetime import datetime

BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Единственный источник правды для языков
LANGUAGES_CONFIG = [
    {"name": "English",    "code": "en"},
    {"name": "Русский",    "code": "ru"},
    {"name": "Қазақша",    "code": "kk"},
    {"name": "Кыргызча",   "code": "ky"},
    {"name": "O'zbekcha",  "code": "uz"},
    {"name": "Українська", "code": "uk"}
]

LANG_ORDER = [lang["name"] for lang in LANGUAGES_CONFIG]
LANG_MAP = {lang["name"]: lang["code"] for lang in LANGUAGES_CONFIG}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()
gpt = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER)
whisper_client = OpenAI(api_key=OPENAI_API_KEY, base_url="https://api.openai.com/v1")

# === ДОБАВЛЕНО: Подключение Rate Limiter Middleware ===
rate_limiter = RateLimiterMiddleware(max_requests=15, window_seconds=60)
dp.message.middleware(rate_limiter)
# =======================================================

def lang_kb(db: Session):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=l)] for l in LANG_ORDER], resize_keyboard=True)

def main_kb(lang: str, db: Session):
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t("contact", lang, db))],
        [KeyboardButton(text=t("ask", lang, db))],
        [KeyboardButton(text=t("change", lang, db))]
    ], resize_keyboard=True)

async def show_lang_menu(message: Message, db: Session):
    await message.answer("Выберите язык / Select language:", reply_markup=lang_kb(db))

def get_or_create_lead(db: Session, uid: int, username: str, company_id: int):
    lead = db.query(Lead).filter(Lead.telegram_user_id == uid, Lead.company_id == company_id).first()
    if not lead:
        lead = Lead(company_id=company_id, telegram_user_id=uid, contact_info={"username": username}, status="new")
        db.add(lead); db.commit(); db.refresh(lead)
    return lead

def save_interaction(db: Session, lead_id: int, content: str, outcome: str, msg_type: str = "text", company_id: int = None):
    db.add(Interaction(company_id=company_id, lead_id=lead_id, type=msg_type, content=content, outcome=outcome))
    db.commit()

def get_lang(update: Message, db: Session):
    pref = db.query(UserPreference).filter_by(telegram_user_id=update.from_user.id).first()
    return pref.language_code if pref else "ru"

@dp.message(Command("start"))
async def start_cmd(m: Message):
    db = next(get_db())
    try:
        company_id = get_company_id_cached(db, BOT_TOKEN)
        get_or_create_lead(db, m.from_user.id, m.from_user.username or "", company_id)
        await show_lang_menu(m, db)
    finally:
        db.close()

@dp.message(F.text.in_(LANG_ORDER))
async def set_lang(m: Message):
    db = next(get_db())
    try:
        lang_name = m.text
        lang_code = LANG_MAP.get(lang_name, "ru")
        logging.info(f"🌐 Язык изменен: {lang_name} -> {lang_code}")
        pref = db.query(UserPreference).filter_by(telegram_user_id=m.from_user.id).first()
        if not pref:
            pref = UserPreference(telegram_user_id=m.from_user.id, language_code=lang_code)
            db.add(pref)
        else:
            pref.language_code = lang_code
        db.commit()
        await m.answer(t("welcome", lang_code, db), reply_markup=main_kb(lang_code, db))
    finally:
        db.close()

@dp.message(F.text)
async def router(m: Message):
    db = next(get_db())
    try:
        company_id = get_company_id_cached(db, BOT_TOKEN)
        lang = get_lang(m, db)
        text = m.text
        if text == t("contact", lang, db): 
            await m.answer(t("contact_message", lang, db))
        elif text == t("ask", lang, db): 
            await m.answer(t("ask_message", lang, db))
        elif text == t("change", lang, db): 
            await show_lang_menu(m, db)
        elif text in LANG_MAP: 
            await set_lang(m, db)
        else: 
            await text_question(m, db, company_id)
    finally:
        db.close()

async def text_question(m: Message, db: Session, company_id: int):
    lead = get_or_create_lead(db, m.from_user.id, m.from_user.username or "", company_id)
    lang = get_lang(m, db)
    await m.chat.do("typing")
    await m.answer(t("think", lang, db))
    
    system = f"Ты – консультант компании. Отвечай кратко и дружелюбно. Always respond in {lang} language."
    
    def call_gpt():
        return gpt.chat.completions.create(
            model="openai/gpt-oss-120b", 
            messages=[
                {"role": "system", "content": system}, 
                {"role": "user", "content": m.text}
            ], 
            max_tokens=500, 
            temperature=0.7
        )
    
    resp = await call_with_retry(
        call_gpt,
        max_attempts=3,
        description="GPT текстовый запрос"
    )
    
    if not resp:
        logging.error("❌ GPT не вернул ответ после всех попыток")
        await m.answer(t("error", lang, db))
        return
    
    answer = resp.choices[0].message.content.strip()
    
    get_or_create_lead(db, m.from_user.id, m.from_user.username or "", company_id)
    save_interaction(db, lead.id, m.text, answer, "text", company_id)
    await m.answer(answer)

@dp.message(F.voice)
async def voice_question(m: Message):
    db = next(get_db())
    voice_path = f"/tmp/voice_{m.from_user.id}.ogg"
    try:
        company_id = get_company_id_cached(db, BOT_TOKEN)
        pref = db.query(UserPreference).filter_by(telegram_user_id=m.from_user.id).first()
        if not pref:
            await show_lang_menu(m, db)
            return
        lead = get_or_create_lead(db, m.from_user.id, m.from_user.username or "", company_id)
        lang = pref.language_code
        await m.chat.do("typing")
        await m.answer(t("think", lang, db))
        
        file = await bot.get_file(m.voice.file_id)
        await bot.download_file(file.file_path, voice_path)
        
        logging.info(f"📤 OpenAI Whisper запрос: файл={voice_path}, язык={lang}")
        
        def call_whisper():
            with open(voice_path, "rb") as audio_file:
                return whisper_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    language=lang
                )
        
        transcription = await call_with_retry(
            call_whisper,
            max_attempts=3,
            description="Whisper STT"
        )
        
        if not transcription:
            logging.error("❌ Whisper не вернул результат после всех попыток")
            await m.answer(t("retry", lang, db))
            return
        
        text = transcription.text
        
        logging.info(f"📝 Распознанный текст: {text}")
        await m.answer(f"{t('said', lang, db)} {text}")
        await m.chat.do("typing")
        
        system = f"Ты – консультант компании. Отвечай кратко и дружелюбно. Always respond in {lang} language."
        
        def call_gpt():
            return gpt.chat.completions.create(
                model="openai/gpt-oss-120b", 
                messages=[
                    {"role": "system", "content": system}, 
                    {"role": "user", "content": text}
                ], 
                max_tokens=500, 
                temperature=0.7
            )
        
        resp = await call_with_retry(
            call_gpt,
            max_attempts=3,
            description="GPT голосовой запрос"
        )
        
        if not resp:
            logging.error("❌ GPT не вернул ответ после всех попыток")
            await m.answer(t("error", lang, db))
            return
        
        answer = resp.choices[0].message.content.strip()
        
        save_interaction(db, lead.id, text, answer, msg_type="voice", company_id=company_id)
        await m.answer(answer)
        
    except Exception as e:
        logging.error(f"Voice processing failed: {e}")
        lang = pref.language_code if 'pref' in locals() and pref else 'ru'
        await m.answer(t("retry", lang, db))
    finally:
        db.close()
        if os.path.exists(voice_path):
            os.remove(voice_path)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
