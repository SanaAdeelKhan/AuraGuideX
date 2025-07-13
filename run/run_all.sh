#!/bin/bash
echo "🚀 Starting all HoloMentor agents..."

# Make sure other scripts are executable
chmod +x "$(dirname "$0")"/*.sh

# Start memory agent in background
echo "Starting Memory Agent..."
"$(dirname "$0")/run_memory.sh" &
MEMORY_PID=$!

# Start answer agent in background
echo "Starting Answer Agent..."
"$(dirname "$0")/run_answer.sh" &
ANSWER_PID=$!

# Wait a bit for others to be ready
sleep 3

# Start master agent
echo "Starting Master Agent..."
"$(dirname "$0")/run_master.sh" &
MASTER_PID=$!

echo "✅ All agents started!"
echo "Master PID: $MASTER_PID"
echo "Memory PID: $MEMORY_PID"
echo "Answer PID: $ANSWER_PID"

# Wait for any agent to exit
wait

# If this point is reached, one of the agents stopped
echo "⚠ One of the agents has stopped. Cleaning up..."
kill $MASTER_PID $MEMORY_PID $ANSWER_PID 2>/dev/null
