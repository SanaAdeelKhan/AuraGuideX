# agents/answer_agent.py
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/answer", methods=["POST"])
def answer():
    data = request.json
    question = data.get("question", "")
    return jsonify({
        "answer": f"🧠 Dummy answer for: {question}"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "agent": "answer"})

if __name__ == "__main__":
    print("🧠 Dummy Answer Agent running on port 5002...")
    app.run(port=5002)
