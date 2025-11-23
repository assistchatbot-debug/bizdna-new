# 🚀 BizDNAi - Multi-Tenant AI Assistant Platform

**Enterprise-grade platform for deploying AI-powered Telegram assistants across multiple companies with voice and text support.**

---

## 📋 Overview

BizDNAi is a multi-service platform that provides intelligent AI assistants via Telegram for multiple companies (multi-tenancy). Each company gets its own isolated bot instance with customizable prompts, languages, and data.

### Key Capabilities
- 🤖 **Multi-company support** — isolated data and configs per company
- 🎙️ **Voice messages** — Speech-to-Text via OpenAI Whisper
- 💬 **AI-powered responses** — OpenRouter integration (GPT models)
- 🌐 **6 languages** — RU, EN, KK, KY, UZ, UK with caching
- ⚡ **Rate limiting** — 15 requests/minute per user
- 📝 **Interaction logging** — Full audit trail in PostgreSQL
- 🔧 **FastAPI backend** — REST API for bot management

---

## 🏗️ Architecture

```mermaid
graph LR
    User([User]) -->|Voice/Text| TG[Telegram Bot API]
    TG -->|Webhook/Polling| Bot[aiogram Bot]
    Bot -->|STT| Whisper[OpenAI Whisper]
    Bot -->|AI Response| OpenRouter[OpenRouter API]
    Bot -->|Store Data| DB[(PostgreSQL)]
    Bot -->|Cache| Redis[(Memory Cache)]
    
    Admin([Admin]) -->|CRUD| API[FastAPI]
    API -->|Manage| Bot
    API -->|Configure| DB
📁 Project Structure
Copy
/root/bizdna-new/
├── app/                          # FastAPI Application
│   ├── main.py                   # API entry point (FastAPI)
│   ├── api/                      # REST endpoints (webhooks, CRUD)
│   ├── core/                     # Config & security
│   ├── services/                 # Business logic
│   │   ├── company_cache.py      # Company token cache
│   │   └── translation_service.py # Translation cache
│   ├── db/                       # Database layer
│   │   └── session.py            # SQLAlchemy sessions
│   ├── models/                   # Data models
│   │   └── all_models.py         # All SQLAlchemy models
│   └── schemas/                  # Pydantic schemas (pending)
├── bots/                         # Telegram Bots
│   └── sales_bot/
│       ├── bot.py                # Bot handlers & logic
│       └── keyboards.py          # UI keyboards (pending)
├── common/                       # Shared utilities
│   ├── api_retry.py              # Retry logic for APIs
│   └── rate_limiter.py           # Rate limiting middleware
├── tests/                        # Test suite (pending)
├── deployments/                  # Docker/K8s configs (pending)
├── scripts/                      # Automation scripts
│   └── deploy.sh                 # Production deploy script
├── logs/                         # Application logs
├── venv/                         # Python virtual environment
├── .env                          # Environment variables (git-ignored)
├── .env.example                  # Template for .env
├── requirements*.txt             # Python dependencies
└── README.md                     # This file
🛠️ Tech Stack
Table
Copy
Layer	Technology
Bot Framework	aiogram 3.x
API Framework	FastAPI
Database	PostgreSQL + SQLAlchemy 2.0
STT	OpenAI Whisper
AI Models	OpenRouter (GPT-4, Claude, etc.)
Cache	In-memory LRU
Languages	Python 3.10+
Deployment	Bash scripts (Docker pending)
⚙️ Setup & Installation
1. Prerequisites
Python 3.10+
PostgreSQL 14+
Telegram Bot Token (@BotFather)
OpenAI & OpenRouter API keys
2. Clone & Setup
bash
Copy
# Clone repository
git clone https://github.com/assistchatbot-debug/bizdna-new.git /root/bizdna-new
cd /root/bizdna-new

# Create virtual environment
python3.10 -m venv venv

# Install dependencies
./venv/bin/pip install -r requirements.txt -r requirements-api.txt -r requirements-bot.txt
3. Environment Configuration
bash
Copy
# Copy template
cp .env.example .env

# Edit .env with your data
nano .env
Required .env variables:
env
Copy
TELEGRAM_BOT_TOKEN=your_bot_token_here
OPENROUTER_API_KEY=your_openrouter_key
OPENAI_API_KEY=your_openai_key
DATABASE_URL=postgresql://user:pass@host:port/dbname
GITHUB_TOKEN=your_github_token
WEBHOOK_URL=https://your-domain.com/webhook/telegram
🚀 Running the Project
Option A: Development (Polling)
bash
Copy
# Run bot only
PYTHONPATH=/root/bizdna-new ./venv/bin/python bots/sales_bot/bot.py

# Run API only
PYTHONPATH=/root/bizdna-new ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
Option B: Production (Deploy Script)
bash
Copy
# Make executable
chmod +x /root/bizdna-new/scripts/deploy.sh

# Run both services
/root/bizdna-new/scripts/deploy.sh

# Check logs
tail -f /root/bizdna-new/logs/bot.log
tail -f /root/bizdna-new/logs/app.log
Option C: Manual Background
bash
Copy
# Stop all instances
pkill -f "bot.py" ; pkill -f "uvicorn"

# Start bot in background
cd /root/bizdna-new
PYTHONPATH=/root/bizdna-new nohup ./venv/bin/python bots/sales_bot/bot.py > logs/bot.log 2>&1 &

# Start API in background
PYTHONPATH=/root/bizdna-new nohup ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &
📊 Current Features
✅ Implemented
Multi-tenancy: Separate companies with isolated data
Multi-language: 6 languages (RU, EN, KK, KY, UZ, UK)
Voice processing: Whisper STT integration
AI responses: OpenRouter LLM integration
Rate limiting: 15 req/min per user
Translation cache: In-memory LRU cache
Interaction logging: Full audit trail
Company cache: Token-to-ID mapping
API retry: Exponential backoff for AI APIs
⚠️ Known Issues
Models: Split into separate files causes SQLAlchemy circular imports — WORKAROUND: Using all_models.py
STT endpoint: Temporarily stubbed in FastAPI
No migrations: Manual DB schema management
🔄 Roadmap (Next Steps)
[✅] Dockerize: Create Dockerfile & docker-compose.yml
[✅] SENTRY INSTALLER v23.1 - Отслеживание ошибок в коде
[ ] Alembic: Database migration management
[ ] Pydantic schemas: Data validation schemas
[ ] Unit tests: pytest coverage
[ ] CI/CD: GitHub Actions automation
[ ] Monitoring: Prometheus + Grafana
[ ] Kubernetes: Production K8s manifests
[ ] Refactor models: Fix circular imports properly
🌐 API Endpoints
Webhook Management
http
Copy
POST /webhook/telegram           # Telegram webhook handler
POST /api/company-bots/          # Create company bot
POST /api/company-bots/{id}/setup-webhook  # Set webhook URL
CRUD Operations
http
Copy
GET  /companies/                 # List all companies
POST /companies/                 # Create company
GET  /companies/{id}             # Get company details
POST /api/company-prompts/       # Create prompt
GET  /api/company-prompts/{id}   # Get prompts
STT (Stub)
http
Copy
POST /api/stt/transcribe         # Speech-to-text (temporarily stubbed)
🔐 Environment Variables
Table
Copy
Variable	Required	Description
TELEGRAM_BOT_TOKEN	✅	Bot token from @BotFather
OPENROUTER_API_KEY	✅	OpenRouter API key
OPENAI_API_KEY	✅	OpenAI API key (Whisper)
DATABASE_URL	✅	PostgreSQL connection string
GITHUB_TOKEN	❌	For GitHub deployments
WEBHOOK_URL	❌	Public webhook URL (ngrok/domain)
AUTH_TOKEN	❌	Internal API auth token
📦 Dependencies
Core
aiogram==3.22.0 — Telegram Bot Framework
fastapi==0.121.3 — API Framework
sqlalchemy==2.0.44 — ORM
openai==2.8.1 — Whisper & GPT
pydantic==2.11.10 — Data validation
psycopg2-binary==2.9.11 — PostgreSQL driver
httpx==0.28.1 — HTTP client
Optional
prometheus-client — Metrics
alembic — DB migrations
pytest — Testing
🤝 Contributing
Create feature branch: git checkout -b feature-name
Test imports: Always use PYTHONPATH=/root/bizdna-new prefix
No circular imports: Check with python -c "import app.models.all_models"
Add tests: Cover new features with pytest
Update README: Document changes
Submit PR: To main branch
🆘 Troubleshooting
Bot not responding?
bash
Copy
# Check if running
ps aux | grep "bot.py"

# Check logs
tail -f /root/bizdna-new/logs/bot.log

# Check for conflicts (only ONE instance!)
pkill -f "bot.py" && restart
SQLAlchemy errors?
bash
Copy
# Check models import
PYTHONPATH=/root/bizdna-new python -c "from app.models.all_models import *"

# If circular import — revert to all_models.py
Import errors?
bash
Copy
# Always use PYTHONPATH!
PYTHONPATH=/root/bizdna-new python -c "import app.main"
📄 License
Private enterprise project for BizDNAi platform.
