from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Statistic(Base):
    __tablename__ = 'statistics'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    division_id = Column(Integer, ForeignKey('divisions.id'))
    metric_name = Column(String(100), nullable=False)
    value = Column(DECIMAL(15,2))
    period = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

