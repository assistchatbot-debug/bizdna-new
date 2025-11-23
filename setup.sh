#!/bin/bash
set -e

echo "=== BizDNAi Final Setup Script ==="

# 1. Check environment
echo "1. Checking environment variables..."
test -f /root/bizdna-new/.env || { echo "❌ .env not found"; exit 1; }
source /root/bizdna-new/.env
test -n "$DATABASE_URL" || { echo "❌ DATABASE_URL missing"; exit 1; }
echo "✅ Environment OK"

# 2. Setup Alembic
echo "2. Setting up Alembic..."
cd /root/bizdna-new
if [ ! -d "/root/bizdna-new/alembic" ]; then
    /root/bizdna-new/venv/bin/pip install alembic
    PYTHONPATH=/root/bizdna-new /root/bizdna-new/venv/bin/alembic init alembic
    # Configure alembic.ini
    sed -i "s|sqlalchemy.url =.*|sqlalchemy.url = $DATABASE_URL|g" /root/bizdna-new/alembic/alembic.ini
    # Configure env.py
    sed -i 's|target_metadata = None|import sys; sys.path.append("/root/bizdna-new"); from app.models.all_models import Base; target_metadata = Base.metadata|g' /root/bizdna-new/alembic/env.py
fi
echo "✅ Alembic ready"

# 3. Create Docker files
echo "3. Creating Docker files..."

# Dockerfile.api
cat > /root/bizdna-new/Dockerfile.api << 'DOCKER_EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements-api.txt ./
RUN pip install -r requirements-api.txt
COPY app/ ./app/
COPY common/ ./common/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKER_EOF

# Dockerfile.bot
cat > /root/bizdna-new/Dockerfile.bot << 'DOCKER_EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt requirements-bot.txt ./
RUN pip install -r requirements-bot.txt
COPY bots/ ./bots/
COPY common/ ./common/
COPY app/ ./app/
COPY .env ./
CMD ["python", "bots/sales_bot/bot.py"]
DOCKER_EOF

# docker-compose.yml
cat > /root/bizdna-new/docker-compose.yml << 'DOCKER_EOF'
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: doadmin
      POSTGRES_PASSWORD: your_password
      POSTGRES_DB: defaultdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    env_file: .env
    depends_on:
      - db

  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    environment:
      - PYTHONPATH=/app
    env_file: .env
    depends_on:
      - db

volumes:
  postgres_data:
DOCKER_EOF

echo "✅ Docker files created"

# 4. Setup tests
echo "4. Setting up tests..."
mkdir -p /root/bizdna-new/tests/{unit,integration}
cat > /root/bizdna-new/tests/__init__.py << 'EOF'
# Test suite for BizDNAi
