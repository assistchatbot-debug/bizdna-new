from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    department_id = Column(Integer, ForeignKey('departments.id'))
    division_id = Column(Integer, ForeignKey('divisions.id'))
    position = Column(String(100))
    permissions = Column(JSON)
    access_level = Column(Integer)
    personal_info = Column(JSON)
    employment_info = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

