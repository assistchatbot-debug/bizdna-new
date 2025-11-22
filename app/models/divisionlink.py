from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DivisionLink(Base):
    __tablename__ = 'division_links'
    
    id = Column(Integer, primary_key=True, index=True)
    from_division_id = Column(Integer, ForeignKey('divisions.id'))
    to_division_id = Column(Integer, ForeignKey('divisions.id'))
    sequence_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

