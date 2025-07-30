#!/usr/bin/env python3
"""
Simple backend server for Dream Layer without ComfyUI
"""

import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)

# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

@app.route('/', methods=['GET'])
def is_server_running():
    return jsonify({
        "status": "success",
        "message": "Dream Layer Backend is running!"
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        "status": "success",
        "message": "Backend API is working!"
    })

if __name__ == "__main__":
    print("Starting Dream Layer Backend (Simple Mode)...")
    print("Backend will be available at: http://localhost:5002")
    print("Frontend is available at: http://localhost:8080")
    
    # Use environment variable for debug mode (default to False for production safety)
    debug_mode = os.environ.get('DEBUG', 'false').lower() in ('true', '1', 'yes', 'on')
    app.run(host='0.0.0.0', port=5002, debug=debug_mode, use_reloader=False) 