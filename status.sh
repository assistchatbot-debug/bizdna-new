#!/bin/bash
echo "=== BizDNAi Status ==="
echo "Bot process:"
ps aux | grep "bot.py" | grep -v grep || echo "Bot not running"
echo ""
echo "API process:"
ps aux | grep "uvicorn" | grep -v grep || echo "API not running"
echo ""
echo "Recent bot logs:"
tail -3 /root/bizdna-new/logs/bot.log
echo ""
echo "Recent API logs:"
tail -3 /root/bizdna-new/logs/app.log 2>/dev/null || echo "No API logs"
