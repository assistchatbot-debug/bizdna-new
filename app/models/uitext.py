from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class UIText(Base):
    __tablename__ = 'ui_texts'
    key = Column(String(50), primary_key=True)
    language = Column(String(10), primary_key=True)
    text = Column(String(500), nullable=False)

# === ДОБАВЛЕНО: Таблица поддерживаемых языков ===


# === ДОБАВЛЕНО: Таблица поддерживаемых языков ===
