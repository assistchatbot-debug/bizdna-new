#!/bin/bash
set -e
echo "=== BizDNAi Deployment ==="
pkill -f "uvicorn" || true
pkill -f "bot.py" || true
source /root/bizdna-new/venv/bin/activate
cd /root/bizdna-new
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &
cd /root/bizdna-new/bots/sales_bot
nohup python bot.py > ../../../logs/bot.log 2>&1 &
echo "✅ Запущено"
