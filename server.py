#!/usr/bin/env python3
"""
Run script for the Flask DocSmith application
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import and run the Flask app
from flask_app import app

if __name__ == '__main__':
    # Check if API key is set
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("WARNING: ANTHROPIC_API_KEY environment variable is not set!")
        print("Please set it in a .env file or as an environment variable.")
        print("")
    
    # Try different ports if 5000 is in use
    port = 5001
    
    print("🚀 Starting Flask DocSmith...")
    print(f"📍 Server running at: http://localhost:{port}")
    print(f"📚 Documentation Generator: http://localhost:{port}/documentation-generator")
    print(f"🔍 Code Explanation: http://localhost:{port}/code-explanation")
    print("")
    print("Press Ctrl+C to stop the server")
    
    # Run the Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port,
        use_reloader=True
    )