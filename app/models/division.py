from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Division(Base):
    __tablename__ = 'divisions'
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
    division_number = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    purpose = Column(Text)
    ideal_scene = Column(Text)
    statistics = Column(Text)
    ckp = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

