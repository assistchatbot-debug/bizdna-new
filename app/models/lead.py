from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    telegram_user_id = Column(BigInteger, nullable=False)  # Убрано unique=True (критично для мультитенантности)
    contact_info = Column(JSON, nullable=False)
    status = Column(String(50), default='new')
    source = Column(String(100))
    assigned_employee_id = Column(Integer, ForeignKey('employees.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Мультитенантность: один telegram_user может быть лидом в разных компаниях
    __table_args__ = (UniqueConstraint('company_id', 'telegram_user_id', name='_company_user_uc'),)

