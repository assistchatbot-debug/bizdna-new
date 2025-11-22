from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Dialog(Base):
    __tablename__ = 'dialogs'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    message_type = Column(String(20))
    user_message = Column(Text)
    ai_response = Column(Text)
    language = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

