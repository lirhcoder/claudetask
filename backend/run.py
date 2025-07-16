#!/usr/bin/env python
"""
Alternative run script for development
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, socketio

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Flask-SocketIO server on http://0.0.0.0:{port}")
    print(f"Debug mode: {debug}")
    print(f"Async mode: threading")
    
    socketio.run(app, debug=debug, host='0.0.0.0', port=port)