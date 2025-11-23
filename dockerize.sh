#!/bin/bash
set -e

cd /root/bizdna-new

# Dockerfile API
cat > Dockerfile.api << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt
COPY app/ ./app/
COPY common/ ./common/
COPY .env ./
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Dockerfile Bot
cat > Dockerfile.bot << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements-bot.txt ./
RUN pip install --no-cache-dir -r requirements-bot.txt
COPY bots/ ./bots/
COPY common/ ./common/
COPY app/ ./app/
COPY .env ./
ENV PYTHONPATH=/app
CMD ["python", "bots/sales_bot/bot.py"]
EOF

# docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER:-doadmin}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME:-defaultdb}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    restart: unless-stopped
    env_file: .env
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:
EOF

# .dockerignore
cat > .dockerignore << 'EOF'
.git
.gitignore
*.log
logs/
venv/
.gitkeep
.env.example
docker-compose.yml
Dockerfile.*
dockerize.sh
EOF

echo "✅ Docker files created"
echo "Next: docker-compose up --build"
