# test/test_master.py

import requests

payload = {
    "message": "Hello, I'm Junaid. What can you teach me?",
    "user_id": "junaid123"
}

res = requests.post("http://localhost:5000/process", json=payload)
print(res.json())
