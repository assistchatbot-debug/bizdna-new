from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, DECIMAL, Date, Boolean, BigInteger, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True)
    settings = Column(JSON)
    tg_token = Column(String(255), unique=True)  # ВАЖНО: для привязки бота к компании
    default_language = Column(String(10), default='ru')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    bots = relationship("CompanyBot", back_populates="company")
    prompts = relationship("CompanyPrompt", back_populates="company")

class CompanyBot(Base):
    __tablename__ = 'company_bots'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    telegram_bot_token = Column(String(255), unique=True, nullable=False)
    webhook_secret = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="bots")

class CompanyPrompt(Base):
    __tablename__ = 'company_prompts'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    prompt_type = Column(String(50))
    content = Column(Text)
    documents = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", back_populates="prompts")

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True, index=True)
    department_number = Column(Integer, unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    purpose = Column(Text)
    ideal_scene = Column(Text)
    statistics = Column(Text)
    ckp = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    lead_id = Column(Integer, ForeignKey('leads.id'))
    employee_id = Column(Integer, ForeignKey('employees.id'))
    type = Column(String(50))
    file_path = Column(String(500))
    content = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class DivisionLink(Base):
    __tablename__ = 'division_links'
    
    id = Column(Integer, primary_key=True, index=True)
    from_division_id = Column(Integer, ForeignKey('divisions.id'))
    to_division_id = Column(Integer, ForeignKey('divisions.id'))
    sequence_order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False)
    language_code = Column(String(10), default='ru')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

class DialogState(Base):
    __tablename__ = 'dialog_states'
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    user_id = Column(BigInteger)
    state = Column(String(50), default='start')
    context = Column(JSON)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (UniqueConstraint('company_id', 'user_id', name='unique_company_user'),)

class UIText(Base):
    __tablename__ = 'ui_texts'
    key = Column(String(50), primary_key=True)
    language = Column(String(10), primary_key=True)
    text = Column(String(500), nullable=False)

# === ДОБАВЛЕНО: Таблица поддерживаемых языков ===


# === ДОБАВЛЕНО: Таблица поддерживаемых языков ===
class SupportedLanguage(Base):
    __tablename__ = "supported_languages"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    lang_code = Column(String(10), nullable=False)  # ru, en, kk, etc
    lang_name = Column(String(50), nullable=False)  # Русский, English, etc
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'lang_code', name='uix_company_lang'),
        Index('idx_company_active', 'company_id', 'is_active'),
    )
