#!/usr/bin/env python3
"""
🎓 Master Agent - Main Controller
Handles messages between agents and coordinates the workflow
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Agent endpoints
MEMORY_AGENT_URL = "http://localhost:5001"
ANSWER_AGENT_URL = "http://localhost:5002"

class MasterAgent:
    def __init__(self):
        self.session_data = {}
        
    def process_user_request(self, user_input, user_id=None):
        """
        Main workflow handler
        1. Check if we know this user
        2. Get memory context
        3. Generate answer
        4. Save interaction
        """
        try:
            # Step 1: Extract user info if new user
            if not user_id:
                user_id = self.extract_user_id(user_input)
            
            # Step 2: Get user memory context
            memory_context = self.get_user_memory(user_id)
            
            # Step 3: Generate answer using context
            answer = self.get_answer(user_input, memory_context, user_id)
            
            # Step 4: Save this interaction
            self.save_interaction(user_id, user_input, answer)
            
            # Step 5: Return response
            response = {
                "user_id": user_id,
                "question": user_input,
                "answer": answer,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            logger.info(f"✅ Processed request for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }
    
    def extract_user_id(self, user_input):
        """Extract user ID from input if mentioned"""
        # Simple name extraction - can be improved
        words = user_input.lower().split()
        
        # Look for "I'm [name]" or "my name is [name]"
        if "i'm" in words:
            try:
                idx = words.index("i'm")
                if idx + 1 < len(words):
                    return words[idx + 1].capitalize()
            except:
                pass
        
        if "my name is" in user_input.lower():
            try:
                parts = user_input.lower().split("my name is")
                if len(parts) > 1:
                    name = parts[1].strip().split()[0]
                    return name.capitalize()
            except:
                pass
        
        # Default to anonymous user
        return "anonymous"
    
    def get_user_memory(self, user_id):
        """Get user's memory context from Memory Agent"""
        try:
            response = requests.get(f"{MEMORY_AGENT_URL}/get_memory/{user_id}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Memory agent returned {response.status_code}")
                return {"user_id": user_id, "interactions": []}
        except Exception as e:
            logger.error(f"Error getting memory: {str(e)}")
            return {"user_id": user_id, "interactions": []}
    
    def get_answer(self, question, memory_context, user_id):
        """Get answer from Answer Agent"""
        try:
            payload = {
                "question": question,
                "user_id": user_id,
                "memory_context": memory_context
            }
            
            response = requests.post(f"{ANSWER_AGENT_URL}/answer", json=payload)
            if response.status_code == 200:
                return response.json().get("answer", "I couldn't generate an answer.")
            else:
                logger.error(f"Answer agent returned {response.status_code}")
                return "I'm having trouble generating an answer right now."
        except Exception as e:
            logger.error(f"Error getting answer: {str(e)}")
            return "I'm having trouble connecting to my knowledge base."
    
    def save_interaction(self, user_id, question, answer):
        """Save interaction to Memory Agent"""
        try:
            payload = {
                "user_id": user_id,
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(f"{MEMORY_AGENT_URL}/save_interaction", json=payload)
            if response.status_code == 200:
                logger.info(f"✅ Saved interaction for {user_id}")
            else:
                logger.warning(f"Failed to save interaction: {response.status_code}")
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")

# Initialize master agent
master = MasterAgent()

@app.route('/process', methods=['POST'])
def process_request():
    """Main endpoint for processing user requests"""
    try:
        data = request.json
        user_input = data.get('message', '')
        user_id = data.get('user_id', None)
        
        if not user_input:
            return jsonify({"error": "No message provided"}), 400
        
        response = master.process_user_request(user_input, user_id)
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in /process endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "master",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🎓 Starting Master Agent on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)