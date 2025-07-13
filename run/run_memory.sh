#!/bin/bash
echo "🧠 Starting Memory Agent..."
cd "$(dirname "$0")/../agents"
python memory_agent.py
