#!/bin/bash
set -e

echo "Starting FreqTrade SaaS Backend..."
echo "=================================="

echo "Running database migrations..."
python migrate_bot_table.py << EOF
y
EOF

echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload