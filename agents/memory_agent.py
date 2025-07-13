#!/usr/bin/env python3
"""
🧠 Memory Agent - Remembers users and past conversations
Stores user interactions and provides context for better responses
"""

import os
import json
import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class MemoryAgent:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing user interactions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_interactions INTEGER DEFAULT 0
                )
            ''')
            
            # Create interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing database: {str(e)}")
    
    def save_interaction(self, user_id, question, answer, timestamp=None):
        """Save a new interaction to the database"""
        try:
            if not timestamp:
                timestamp = datetime.now().isoformat()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert or update user
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, first_seen, last_seen, total_interactions)
                VALUES (?, 
                        COALESCE((SELECT first_seen FROM users WHERE user_id = ?), ?),
                        ?,
                        COALESCE((SELECT total_interactions FROM users WHERE user_id = ?), 0) + 1)
            ''', (user_id, user_id, timestamp, timestamp, user_id))
            
            # Insert interaction
            cursor.execute('''
                INSERT INTO interactions (user_id, question, answer, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (user_id, question, answer, timestamp))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Saved interaction for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving interaction: {str(e)}")
            return False
    
    def get_user_memory(self, user_id, limit=10):
        """Get user's interaction history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user info
            cursor.execute('''
                SELECT user_id, first_seen, last_seen, total_interactions
                FROM users WHERE user_id = ?
            ''', (user_id,))
            
            user_info = cursor.fetchone()
            
            # Get recent interactions
            cursor.execute('''
                SELECT question, answer, timestamp
                FROM interactions 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            interactions = cursor.fetchall()
            conn.close()
            
            # Format response
            if user_info:
                memory = {
                    "user_id": user_info[0],
                    "first_seen": user_info[1],
                    "last_seen": user_info[2],
                    "total_interactions": user_info[3],
                    "recent_interactions": [
                        {
                            "question": interaction[0],
                            "answer": interaction[1],
                            "timestamp": interaction[2]
                        }
                        for interaction in interactions
                    ]
                }
            else:
                memory = {
                    "user_id": user_id,
                    "first_seen": None,
                    "last_seen": None,
                    "total_interactions": 0,
                    "recent_interactions": []
                }
            
            logger.info(f"✅ Retrieved memory for user {user_id}")
            return memory
            
        except Exception as e:
            logger.error(f"❌ Error getting user memory: {str(e)}")
            return {
                "user_id": user_id,
                "error": str(e),
                "recent_interactions": []
            }
    
    def get_all_users(self):
        """Get list of all users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, first_seen, last_seen, total_interactions
                FROM users
                ORDER BY last_seen DESC
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "user_id": user[0],
                    "first_seen": user[1],
                    "last_seen": user[2],
                    "total_interactions": user[3]
                }
                for user in users
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting all users: {str(e)}")
            return []
    
    def search_interactions(self, query, limit=20):
        """Search through interactions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, question, answer, timestamp
                FROM interactions 
                WHERE question LIKE ? OR answer LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "user_id": result[0],
                    "question": result[1],
                    "answer": result[2],
                    "timestamp": result[3]
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"❌ Error searching interactions: {str(e)}")
            return []

# Initialize memory agent
memory_agent = MemoryAgent()

@app.route('/save_interaction', methods=['POST'])
def save_interaction():
    """Save a new interaction"""
    try:
        data = request.json
        user_id = data.get('user_id')
        question = data.get('question')
        answer = data.get('answer')
        timestamp = data.get('timestamp')
        
        if not all([user_id, question, answer]):
            return jsonify({"error": "Missing required fields"}), 400
        
        success = memory_agent.save_interaction(user_id, question, answer, timestamp)
        
        if success:
            return jsonify({"status": "success", "message": "Interaction saved"})
        else:
            return jsonify({"error": "Failed to save interaction"}), 500
            
    except Exception as e:
        logger.error(f"Error in /save_interaction: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_memory/<user_id>', methods=['GET'])
def get_memory(user_id):
    """Get user's memory context"""
    try:
        limit = request.args.get('limit', 10, type=int)
        memory = memory_agent.get_user_memory(user_id, limit)
        return jsonify(memory)
        
    except Exception as e:
        logger.error(f"Error in /get_memory: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    try:
        users = memory_agent.get_all_users()
        return jsonify({"users": users})
        
    except Exception as e:
        logger.error(f"Error in /users: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_interactions():
    """Search through interactions"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400
        
        results = memory_agent.search_interactions(query, limit)
        return jsonify({"results": results})
        
    except Exception as e:
        logger.error(f"Error in /search: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": "memory",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🧠 Starting Memory Agent on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True) 