#!/bin/bash
cd /data/data/com.termux/files/home/indodax-bot

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the bot
python main.py

# Keep terminal open
echo "Press Enter to exit..."
read