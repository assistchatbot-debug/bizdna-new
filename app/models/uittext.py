from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UIText(Base):
    __tablename__ = 'ui_texts'
    key = Column(String(50), primary_key=True)
    language = Column(String(10), primary_key=True)
    text = Column(String(500), nullable=False)
