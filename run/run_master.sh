#!/bin/bash
echo "🎓 Starting Master Agent..."
cd "$(dirname "$0")/../agents"
python master_agent.py
