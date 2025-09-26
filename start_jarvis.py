# start_jarvis.py - Final launcher untuk JARVIS UI
import os
import sys
import time
import webbrowser
import threading
import json
from datetime import datetime

# Check Python version
print(f"Python Version: {sys.version}")

# ASCII Banner
print("""
╔══════════════════════════════════════════════════════════════╗
║     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗               ║
║     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝               ║
║     ██║███████║██████╔╝██║   ██║██║███████╗               ║
║██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║               ║
║╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║               ║
║ ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝               ║
║                                                             ║
║         J.A.R.V.I.S - AI Assistant Interface               ║
║              Developed by LEO Technologies                 ║
╚══════════════════════════════════════════════════════════════╝
""")

# Check required folders and files
print("\n🔍 Checking system requirements...")

def check_requirements():
    """Check if all requirements are met"""
    issues = []
    
    # Check folders
    folders = ['templates', 'generated_images', 'notes', 'sounds']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"📁 Created folder: {folder}")
        else:
            print(f"✅ Folder exists: {folder}")
    
    # Check HTML file
    if not os.path.exists('templates/index.html'):
        issues.append("❌ templates/index.html not found! Run: python save_html.py")
    else:
        print("✅ HTML UI found")
    
    # Check .env file (optional)
    if os.path.exists('.env'):
        print("✅ .env file found (API keys configured)")
    else:
        print("⚠️  .env file not found (Voice features will be disabled)")
    
    return issues

# Check requirements
issues = check_requirements()
if issues:
    print("\n⚠️  Issues found:")
    for issue in issues:
        print(issue)
    print("\nPlease fix these issues before running JARVIS.")
    sys.exit(1)

print("\n✅ All requirements met!")

# Try to import required libraries
libraries = {
    'flask': False,
    'websockets': False,
    'psutil': False
}

for lib in libraries:
    try:
        __import__(lib)
        libraries[lib] = True
        print(f"✅ {lib} is installed")
    except ImportError:
        print(f"⚠️  {lib} not installed (some features may be limited)")

# Choose server mode based on available libraries
if libraries['flask']:
    print("\n🚀 Starting with Flask server...")
    
    # Flask-based server
    server_code = '''
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import psutil

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/api/status')
def status():
    try:
        cpu = psutil.cpu_percent() if psutil else 42
        memory = psutil.virtual_memory().percent if psutil else 50
    except:
        cpu, memory = 42, 50
    
    return jsonify({
        'cpu': cpu,
        'memory': memory,
        'status': 'online'
    })

if __name__ == '__main__':
    import webbrowser
    webbrowser.open('http://localhost:5000')
    app.run(port=5000, debug=False)
'''
    
    exec(server_code)
    
else:
    print("\n🚀 Starting with simple HTTP server...")
    
    # Simple HTTP server (fallback)
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import asyncio
    
    class JarvisHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/templates/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        
        def log_message(self, format, *args):
            # Suppress logs
            pass
    
    def start_http_server():
        """Start HTTP server"""
        port = 5000
        server = HTTPServer(('localhost', port), JarvisHandler)
        print(f"\n✅ JARVIS UI running at: http://localhost:{port}")
        print("\n📋 Controls:")
        print("  • Click 'Start Listening' to test animations")
        print("  • Try different themes with Theme button")
        print("  • Export conversation history")
        print("  • Press Ctrl+C to stop")
        server.serve_forever()
    
    # WebSocket server (if available)
    if libraries['websockets']:
        import websockets
        
        async def handle_websocket(websocket, path):
            """Handle WebSocket connections"""
            await websocket.send(json.dumps({
                'type': 'connection',
                'status': 'connected',
                'message': 'JARVIS WebSocket Connected'
            }))
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    action = data.get('action')
                    
                    if action == 'start_listening':
                        await websocket.send(json.dumps({
                            'type': 'status',
                            'message': 'Demo Mode Active'
                        }))
                        
                        # Simulate conversation
                        await asyncio.sleep(1)
                        await websocket.send(json.dumps({
                            'type': 'transcript',
                            'text': 'Hello JARVIS!',
                            'timestamp': datetime.now().isoformat()
                        }))
                        
                        await asyncio.sleep(1)
                        await websocket.send(json.dumps({
                            'type': 'response',
                            'text': 'Greetings! JARVIS UI is operational. How may I assist you?',
                            'timestamp': datetime.now().isoformat()
                        }))
            except:
                pass
        
        async def start_websocket():
            """Start WebSocket server"""
            async with websockets.serve(handle_websocket, "localhost", 8765):
                print("✅ WebSocket server running at: ws://localhost:8765")
                await asyncio.Future()
        
        # Start WebSocket in thread
        ws_thread = threading.Thread(
            target=lambda: asyncio.run(start_websocket()),
            daemon=True
        )
        ws_thread.start()
    
    # Open browser after delay
    threading.Timer(2, lambda: webbrowser.open('http://localhost:5000')).start()
    
    # Start HTTP server
    try:
        start_http_server()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down JARVIS...")
        print("Thank you for using JARVIS AI Assistant!")
        sys.exit(0)