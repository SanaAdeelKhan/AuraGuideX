#!/bin/bash
echo "🛑 Stopping all HoloMentor agents..."

pkill -f "python.*master_agent.py"
pkill -f "python.*memory_agent.py"
pkill -f "python.*answer_agent.py"

echo "✅ All agents stopped!"
