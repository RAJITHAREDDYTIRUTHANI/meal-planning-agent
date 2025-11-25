"""
Simple launcher for the Streamlit UI
Works on Windows, Mac, and Linux
"""

import subprocess
import sys
import os
import webbrowser
import time

def main():
    """Launch the Streamlit app"""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✓ Streamlit is installed")
    except ImportError:
        print("Streamlit is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Run streamlit
    app_path = os.path.join(script_dir, "app.py")
    print("\n" + "="*60)
    print("Starting Meal Planning & Shopping Assistant UI...")
    print("="*60)
    print("\nThe app will open in your browser automatically.")
    print("If it doesn't, go to: http://localhost:8501")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Give a moment for the server to start, then open browser
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8501")
    
    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Run streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)

