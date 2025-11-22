from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class CompanyPrompt(Base):
    __tablename__ = 'company_prompts'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    prompt_type = Column(String(50))
    content = Column(Text)
    documents = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="prompts")

