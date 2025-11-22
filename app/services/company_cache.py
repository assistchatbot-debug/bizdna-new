from sqlalchemy.orm import Session
from app.models.all_models import Company
import logging

_company_cache = {}

def get_company_id_cached(db: Session, token: str) -> int:
    if token in _company_cache:
        return _company_cache[token]
    company = db.query(Company).filter(Company.tg_token == token).first()
    if not company:
        raise ValueError(f"Токен не найден в БД: {token}")
    company_id = company.id
    _company_cache[token] = company_id
    logging.info(f"🏢 Company ID загружен в кэш: {company_id}")
    return company_id
