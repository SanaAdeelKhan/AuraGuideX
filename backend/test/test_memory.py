# test/test_memory.py
import requests

# 1. Save an interaction
requests.post("http://localhost:5001/save_interaction", json={
    "user_id": "ali123",
    "question": "What's the weather?",
    "answer": "It's sunny today."
})

# 2. Get memory
res = requests.get("http://localhost:5001/get_memory/ali123")
print(res.json())
