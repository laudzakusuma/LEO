# quick_fix_install.py - Script untuk install dependencies dengan cepat
import subprocess
import sys
import os

def install_package(package):
    """Install package dengan pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--no-deps"])
        print(f"✅ {package} installed")
        return True
    except:
        print(f"❌ Failed: {package}")
        return False

def main():
    print("=" * 60)
    print("🚀 JARVIS Quick Fix Installer")
    print("=" * 60)
    
    # STEP 1: Update pip first
    print("\n📦 Updating pip...")
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # STEP 2: Install minimal dependencies untuk UI
    print("\n🔧 Installing minimal UI dependencies...")
    
    minimal_packages = [
        "flask==3.1.0",
        "flask-cors",
        "websockets",
        "python-dotenv",
        "psutil",
        "rich",
        "colorama"
    ]
    
    for package in minimal_packages:
        install_package(package)
    
    # STEP 3: Create directories
    print("\n📁 Creating required directories...")
    dirs = ["templates", "generated_images", "notes", "sounds"]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"✅ Created: {d}/")
    
    # STEP 4: Create simple launcher
    print("\n📝 Creating simple launcher...")
    
    launcher_code = '''# run_jarvis.py - Simple launcher
import os
import sys
import webbrowser
import threading
import json
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import asyncio
import websockets

class JarvisServer:
    def __init__(self):
        self.port = 5000
        self.ws_port = 8765
        
    def start_http(self):
        """Start HTTP server"""
        class Handler(SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.path = '/templates/index.html'
                return SimpleHTTPRequestHandler.do_GET(self)
            def log_message(self, format, *args):
                pass
        
        httpd = HTTPServer(('localhost', self.port), Handler)
        print(f"✅ Server: http://localhost:{self.port}")
        httpd.serve_forever()
    
    async def handle_ws(self, websocket, path):
        """Handle WebSocket"""
        await websocket.send(json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'JARVIS Connected'
        }))
        
        async for message in websocket:
            data = json.loads(message)
            if data.get('action') == 'start_listening':
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'Listening...'
                }))
    
    async def start_websocket(self):
        """Start WebSocket server"""
        async with websockets.serve(self.handle_ws, "localhost", self.ws_port):
            print(f"✅ WebSocket: ws://localhost:{self.ws_port}")
            await asyncio.Future()
    
    def run(self):
        """Run server"""
        print("🚀 Starting JARVIS UI...")
        
        # Start HTTP in thread
        http_thread = threading.Thread(target=self.start_http, daemon=True)
        http_thread.start()
        
        # Open browser
        threading.Timer(2, lambda: webbrowser.open(f'http://localhost:{self.port}')).start()
        
        # Run WebSocket
        try:
            asyncio.run(self.start_websocket())
        except KeyboardInterrupt:
            print("\\n👋 Shutting down...")

if __name__ == "__main__":
    if not os.path.exists('templates/index.html'):
        print("⚠️  Please save the HTML UI to templates/index.html first!")
        sys.exit(1)
    
    server = JarvisServer()
    server.run()
'''
    
    with open('run_jarvis.py', 'w') as f:
        f.write(launcher_code)
    print("✅ Created run_jarvis.py")
    
    # STEP 5: Create minimal requirements.txt
    print("\n📝 Creating minimal requirements.txt...")
    
    minimal_req = """# Minimal requirements for JARVIS UI
flask==3.1.0
flask-cors
websockets
python-dotenv
psutil
rich
colorama

# Core (sudah terinstall)
elevenlabs
pyaudio
openai
pillow
langchain_community
"""
    
    with open('requirements_minimal.txt', 'w') as f:
        f.write(minimal_req)
    print("✅ Created requirements_minimal.txt")
    
    print("\n" + "=" * 60)
    print("✅ INSTALLATION COMPLETE!")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("1. Save the HTML from 'Jarvis-style AI Assistant UI' to templates/index.html")
    print("2. Run: python run_jarvis.py")
    print("\n💡 This is a minimal setup for the UI only.")
    print("   Voice features require all API keys configured.")

if __name__ == "__main__":
    main()