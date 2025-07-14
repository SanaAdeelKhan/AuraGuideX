#!/bin/bash
echo "💬 Starting Answer Agent..."
cd "$(dirname "$0")/../agents"
python answer_agent.py
