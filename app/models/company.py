from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True)
    settings = Column(JSON)
    tg_token = Column(String(255), unique=True)  # ВАЖНО: для привязки бота к компании
    default_language = Column(String(10), default='ru')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    bots = relationship("CompanyBot", back_populates="company")
    prompts = relationship("CompanyPrompt", back_populates="company")

