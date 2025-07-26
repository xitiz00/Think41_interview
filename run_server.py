"""
Development server runner for conversation backend.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_development_server():
    """Run the Django development server."""
    print("🚀 Starting Conversation Backend Server...")
    
    # Change to backend directory
    backend_dir = Path(__file__).resolve().parent.parent
    os.chdir(backend_dir)
    
    # Check if database exists and is migrated
    if not Path('conversation_db.sqlite3').exists():
        print("📊 Database not found. Setting up...")
        subprocess.run([sys.executable, 'scripts/setup_database.py'])
    
    # Start the development server
    print("🌐 Starting server at http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/")
    print("🔧 Admin Interface: http://localhost:8000/admin/")
    print("\n⚡ Server is running... Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")


if __name__ == '__main__':
    run_development_server()
