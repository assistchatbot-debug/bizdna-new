from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    category = Column(String(100))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    attributes = Column(JSON)
    pricing = Column(JSON)
    inventory = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

