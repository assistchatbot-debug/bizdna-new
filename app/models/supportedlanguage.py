from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class SupportedLanguage(Base):
    __tablename__ = "supported_languages"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    lang_code = Column(String(10), nullable=False)
    lang_name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'lang_code', name='uix_company_lang'),
        Index('idx_company_active', 'company_id', 'is_active'),
    )
