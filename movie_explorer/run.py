"""
run.py - Application Entry Point
----------------------------------
This is the file you run to start the Flask server.

HOW TO RUN:
  python run.py

Then open your browser at: http://127.0.0.1:5000
"""

from app import create_app

# Create the Flask application
app = create_app('development')

if __name__ == '__main__':
    print("=" * 50)
    print("  🎬 MovieHub Explorer - Starting...")
    print("  Visit: http://127.0.0.1:5000")
    print("=" * 50)
    
    # debug=True enables auto-reload and better error messages
    # NEVER use debug=True in production!
    app.run(debug=True, port=5000)
