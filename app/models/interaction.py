from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Interaction(Base):
    __tablename__ = 'interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    employee_id = Column(Integer, ForeignKey('employees.id'))
    type = Column(String(50))
    content = Column(Text)
    outcome = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

