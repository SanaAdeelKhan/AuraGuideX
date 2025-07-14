#!/usr/bin/env python3
"""
💬 Answer Agent - Provides intelligent answers to user questions
Uses Groq API and context from memory to generate responses
"""

import os

import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import logging
from dotenv import load_dotenv
load_dotenv()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class AnswerAgent:
    def __init__(self):
        # Set Groq API key directly
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama3-8b-8192"

        if not self.groq_api_key:
            logger.warning("⚠️ GROQ API key not found. Using fallback responses.")
        else:
            logger.info("✅ Groq API key loaded successfully")

    def generate_answer(self, question, user_id, memory_context=None):
        try:
            context = self.build_context(user_id, memory_context)
            prompt = self.create_prompt(question, user_id, context)

            if self.groq_api_key:
                return self.get_groq_response(prompt)
            else:
                return self.get_fallback_response(question, user_id, context)
        except Exception as e:
            logger.error(f"❌ Error generating answer: {str(e)}")
            return "Sorry, I'm having trouble answering right now."

    def build_context(self, user_id, memory_context):
        if not memory_context or not memory_context.get('recent_interactions'):
            return f"This is a new conversation with {user_id}."

        context_parts = []

        total_interactions = memory_context.get('total_interactions', 0)
        if total_interactions > 0:
            context_parts.append(f"I've spoken with {user_id} {total_interactions} times before.")

        recent = memory_context.get('recent_interactions', [])[:3]
        for interaction in recent:
            context_parts.append(f"Q: {interaction['question']}")
            context_parts.append(f"A: {interaction['answer']}")

        return "\n".join(context_parts)

    def create_prompt(self, question, user_id, context):
        return f"""You are HoloMentor, an intelligent AI assistant. You provide helpful, accurate, and engaging responses.

User ID: {user_id}
Current Question: {question}

Context from previous conversations:
{context}

Instructions:
- Greet the user
- Use past memory context
- Respond clearly and informatively
- Be friendly and conversational

Please respond:"""

    def get_groq_response(self, prompt):
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are HoloMentor, a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        try:
            res = requests.post(self.api_url, headers=headers, json=payload)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            return "I'm having trouble connecting to my knowledge base. Please try again later."

    def get_fallback_response(self, question, user_id, context):
        return f"(Fallback mode) Hi {user_id}, I see your question: '{question}'. Memory: {context[:100]}..."

# Initialize agent
answer_agent = AnswerAgent()

@app.route('/answer', methods=['POST'])
def generate_answer():
    try:
        data = request.json
        question = data.get('question')
        user_id = data.get('user_id')
        memory_context = data.get('memory_context', {})

        if not question or not user_id:
            return jsonify({"error": "Missing question or user_id"}), 400

        answer = answer_agent.generate_answer(question, user_id, memory_context)

        return jsonify({
            "question": question,
            "answer": answer,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Error in /answer endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "agent": "answer",
        "groq_configured": bool(answer_agent.groq_api_key),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        "message": "Answer Agent is working!",
        "agent": "answer",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("💬 Starting Answer Agent on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)
