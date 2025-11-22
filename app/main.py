from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.all_models import *
from app.db.session import get_db
from app.core.security import verify_webhook_secret
import httpx, secrets, json, logging, os, tempfile, shutil
from fastapi.encoders import jsonable_encoder
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Pydantic модели для API
class CompanyBotCreate(BaseModel):
    company_id: int
    telegram_bot_token: str

class CompanyPromptCreate(BaseModel):
    company_id: int
    prompt_type: str
    content: str

class UserPreferenceCreate(BaseModel):
    telegram_user_id: int
    language_code: str

class CompanyCreate(BaseModel):
    name: str
    subdomain: str = None

# =============================================================================
# TELEGRAM WEBHOOK ENDPOINT
# =============================================================================

async def process_telegram_update(update_data: dict, company_id: int, bot_token: str, db: Session):
    """Обрабатываем апдейт от Telegram в фоне"""
    try:
        bot_url = f"http://localhost:8000/process-update"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                bot_url,
                json={
                    "update": update_data,
                    "company_id": company_id,
                    "bot_token": bot_token
                },
                timeout=30.0
            )
        logger.info(f"Background processing result: {response.status_code}")
    except Exception as e:
        logger.error(f"Background processing failed: {e}")

@app.post("/webhook/telegram/{bot_token}")
async def telegram_webhook(
    bot_token: str,
    update_data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Ендпоинт для вебхуков Telegram"""
    try:
        # Ищем бота по токену
        company_bot = db.query(models.CompanyBot).filter(
            models.CompanyBot.telegram_bot_token == bot_token,
            models.CompanyBot.is_active == True
        ).first()
        
        if not company_bot:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        # Обрабатываем в фоне
        background_tasks.add_task(
            process_telegram_update, 
            update_data, 
            company_bot.company_id,
            company_bot.telegram_bot_token,
            db
        )
        
        return {"status": "ok", "company_id": company_bot.company_id}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

# =============================================================================
# УПРАВЛЕНИЕ БОТАМИ КОМПАНИЙ
# =============================================================================

@app.post("/api/company-bots/", response_model=dict)
def create_company_bot(bot: CompanyBotCreate, db: Session = Depends(get_db)):
    """Регистрация бота компании"""
    try:
        # Проверяем компанию
        company = db.query(models.Company).filter(models.Company.id == bot.company_id).first()
        if not company:
            raise HTTPException(404, "Company not found")
        
        # Генерируем секретный токен
        secret_token = secrets.token_urlsafe(32)
        
        db_bot = models.CompanyBot(
            company_id=bot.company_id,
            telegram_bot_token=bot.telegram_bot_token,
            webhook_secret=secret_token
        )
        db.add(db_bot)
        db.commit()
        db.refresh(db_bot)
        
        return {
            "status": "success", 
            "bot": jsonable_encoder(db_bot),
            "webhook_url": "http://joel-incretionary-aileen.ngrok-free.dev/webhook/telegram",
            "secret_token": secret_token
        }
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.post("/api/company-bots/{company_id}/setup-webhook")
async def setup_company_webhook(company_id: int, db: Session = Depends(get_db)):
    """Установка вебхука для бота компании"""
    try:
        company_bot = db.query(models.CompanyBot).filter(
            models.CompanyBot.company_id == company_id,
            models.CompanyBot.is_active == True
        ).first()
        
        if not company_bot:
            raise HTTPException(404, "Company bot not found")
        
        webhook_url = "http://joel-incretionary-aileen.ngrok-free.dev/webhook/telegram"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{company_bot.telegram_bot_token}/setWebhook",
                json={
                    "url": webhook_url,
                    "secret_token": company_bot.webhook_secret,
                    "drop_pending_updates": True
                }
            )
        
        result = response.json()
        return {"status": "success", "telegram_response": result}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# =============================================================================
# УПРАВЛЕНИЕ ПРОМПТАМИ КОМПАНИЙ
# =============================================================================

@app.post("/api/company-prompts/", response_model=dict)
def create_company_prompt(prompt: CompanyPromptCreate, db: Session = Depends(get_db)):
    """Создание промпта для компании"""
    try:
        db_prompt = models.CompanyPrompt(**prompt.dict())
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
        return {"status": "success", "prompt": jsonable_encoder(db_prompt)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.get("/api/company-prompts/company/{company_id}", response_model=dict)
def get_company_prompts(company_id: int, db: Session = Depends(get_db)):
    """Получение промптов компании"""
    try:
        prompts = db.query(models.CompanyPrompt).filter(
            models.CompanyPrompt.company_id == company_id,
            models.CompanyPrompt.is_active == True
        ).all()
        
        return {
            "status": "success",
            "count": len(prompts),
            "prompts": jsonable_encoder(prompts)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# =============================================================================
# CRUD ОПЕРАЦИИ
# =============================================================================

@app.post("/companies/", response_model=dict)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    try:
        db_company = models.Company(**company.dict())
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return {"status": "success", "company": jsonable_encoder(db_company)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.get("/companies/", response_model=dict)
def get_companies(db: Session = Depends(get_db)):
    try:
        companies = db.query(models.Company).all()
        return {
            "status": "success",
            "count": len(companies),
            "companies": jsonable_encoder(companies)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/companies/{company_id}", response_model=dict)
def get_company(company_id: int, db: Session = Depends(get_db)):
    try:
        company = db.query(models.Company).filter(models.Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"status": "success", "company": jsonable_encoder(company)}
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/user-preferences/", response_model=dict)
def create_user_preference(preference: UserPreferenceCreate, db: Session = Depends(get_db)):
    try:
        existing = db.query(models.UserPreference).filter(
            models.UserPreference.telegram_user_id == preference.telegram_user_id
        ).first()
        
        if existing:
            existing.language_code = preference.language_code
            existing.updated_at = datetime.utcnow()
            db.commit()
            return {"status": "success", "message": "User preference updated", "user_preference": jsonable_encoder(existing)}
        else:
            db_preference = models.UserPreference(**preference.dict())
            db.add(db_preference)
            db.commit()
            db.refresh(db_preference)
            return {"status": "success", "message": "User preference created", "user_preference": jsonable_encoder(db_preference)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}

@app.get("/user-preferences/{telegram_user_id}", response_model=dict)
def get_user_preference(telegram_user_id: int, db: Session = Depends(get_db)):
    try:
        preference = db.query(models.UserPreference).filter(
            models.UserPreference.telegram_user_id == telegram_user_id
        ).first()
        
        if not preference:
            return {"status": "error", "message": "User preference not found"}
        
        return {"status": "success", "user_preference": jsonable_encoder(preference)}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# =============================================================================
# STT ENDPOINT (ВРЕМЕННО ЗАГЛУШЕН)
# =============================================================================

@app.post("/api/stt/transcribe")
async def stt_post(
    audio_file: UploadFile = File(...),
    language: str = Form("auto"),
):
    """Преобразование речи в текст через OpenAI Whisper"""
    print(f"🎤 STT received: language={language}")
    
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            shutil.copyfileobj(audio_file.file, tmp)
            tmp_path = tmp.name
        
        # ВРЕМЕННАЯ ЗАГЛУШКА - whisper_processor не готов
        # if audio_file.content_type != "audio/wav":
        #     tmp_path = whisper_processor.convert_audio_format(tmp_path, "wav")
        
        # result = whisper_processor.transcribe_audio(tmp_path, language if language != "auto" else None)
        # os.unlink(tmp_path)
        
        # ВРЕМЕННЫЙ РЕЗУЛЬТАТ
        result = {"text": "", "language": "unknown"}
        
        return {"success": True, "text": result["text"], "language": result.get("language", "unknown")}
    
    except Exception as e:
        print(f"❌ STT Error: {e}")
        if tmp_path:
            os.unlink(tmp_path)
        return {"success": False, "error": str(e), "text": "", "language": "unknown"}

# =============================================================================
# ЗАПУСК СЕРВЕРА (ТОЛЬКО ОДИН РАЗ)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
