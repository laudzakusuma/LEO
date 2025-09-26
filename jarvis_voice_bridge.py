# jarvis_voice_bridge.py - Bridge antara ElevenLabs Voice dan JARVIS UI
import os
import sys
import signal
import asyncio
import websockets
import json
import threading
import queue
from datetime import datetime
from dotenv import load_dotenv

# Import existing modules
from tools import client_tools
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Load environment
load_dotenv()

print("""
╔══════════════════════════════════════════════════════════════╗
║     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗               ║
║     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝               ║
║     ██║███████║██████╔╝██║   ██║██║███████╗               ║
║██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║               ║
║╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║               ║
║ ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝               ║
║                                                             ║
║        VOICE AI BRIDGE - Connecting ElevenLabs to UI       ║
╚══════════════════════════════════════════════════════════════╗
""")

# Global variables
conversation = None
message_queue = queue.Queue()
websocket_clients = set()
is_listening = False

# Get API credentials
agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

# Check credentials
if not agent_id or not api_key:
    print("⚠️  WARNING: ElevenLabs API credentials not found!")
    print("   Add to .env file:")
    print("   ELEVENLABS_API_KEY=your_key")
    print("   AGENT_ID=your_agent_id")
    print("\n   Running in DEMO mode (no real voice)")
    DEMO_MODE = True
else:
    print("✅ API credentials found")
    DEMO_MODE = False
    elevenlabs = ElevenLabs(api_key=api_key)

class VoiceBridge:
    """Bridge between Voice AI and WebSocket UI"""
    
    def __init__(self):
        self.conversation = None
        self.is_active = False
        self.clients = set()
        
    async def register_client(self, websocket):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        await self.send_to_client(websocket, {
            'type': 'connection',
            'status': 'connected',
            'message': 'Voice AI Bridge Connected',
            'demo_mode': DEMO_MODE
        })
        print(f"✅ Client connected. Total clients: {len(self.clients)}")
    
    def unregister_client(self, websocket):
        """Remove WebSocket client"""
        self.clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def send_to_client(self, websocket, data):
        """Send message to specific client"""
        try:
            await websocket.send(json.dumps(data))
        except:
            self.unregister_client(websocket)
    
    async def broadcast(self, data):
        """Broadcast message to all clients"""
        if self.clients:
            await asyncio.gather(
                *[self.send_to_client(client, data) for client in self.clients]
            )
    
    def start_voice_conversation(self):
        """Start ElevenLabs conversation"""
        global conversation
        
        if DEMO_MODE:
            print("🎤 Demo mode - simulating voice")
            return True
        
        try:
            if not conversation:
                conversation = Conversation(
                    elevenlabs,
                    agent_id,
                    client_tools=client_tools,
                    requires_auth=bool(api_key),
                    audio_interface=DefaultAudioInterface(),
                    
                    # Callbacks that send to UI
                    callback_agent_response=lambda response: asyncio.run(
                        self.broadcast({
                            'type': 'response',
                            'text': response,
                            'timestamp': datetime.now().isoformat()
                        })
                    ),
                    callback_agent_response_correction=lambda original, corrected: asyncio.run(
                        self.broadcast({
                            'type': 'correction',
                            'original': original,
                            'corrected': corrected,
                            'timestamp': datetime.now().isoformat()
                        })
                    ),
                    callback_user_transcript=lambda transcript: asyncio.run(
                        self.broadcast({
                            'type': 'transcript',
                            'text': transcript,
                            'timestamp': datetime.now().isoformat()
                        })
                    ),
                )
                conversation.start_session()
                self.conversation = conversation
                print("✅ Voice conversation started")
                return True
        except Exception as e:
            print(f"❌ Error starting voice: {e}")
            return False
    
    def stop_voice_conversation(self):
        """Stop ElevenLabs conversation"""
        global conversation
        
        if conversation:
            try:
                conversation.end_session()
                conversation = None
                self.conversation = None
                print("✅ Voice conversation stopped")
            except:
                pass
    
    async def handle_client_message(self, websocket, data):
        """Handle messages from UI client"""
        action = data.get('action')
        
        if action == 'start_listening':
            if DEMO_MODE:
                # Demo mode simulation
                await self.send_to_client(websocket, {
                    'type': 'status',
                    'message': 'Listening... (Demo Mode)'
                })
                
                # Simulate conversation
                await asyncio.sleep(1)
                await self.broadcast({
                    'type': 'transcript',
                    'text': 'Hello JARVIS, what can you do?',
                    'timestamp': datetime.now().isoformat()
                })
                
                await asyncio.sleep(1.5)
                await self.broadcast({
                    'type': 'response',
                    'text': 'I am JARVIS, your AI assistant. I can search the web, generate images, save data, create HTML files, and much more. How may I assist you today?',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                # Real voice mode
                if self.start_voice_conversation():
                    await self.send_to_client(websocket, {
                        'type': 'status',
                        'message': 'Voice AI Active - Speak Now'
                    })
                else:
                    await self.send_to_client(websocket, {
                        'type': 'error',
                        'message': 'Failed to start voice'
                    })
        
        elif action == 'stop_listening':
            self.stop_voice_conversation()
            await self.send_to_client(websocket, {
                'type': 'status',
                'message': 'Voice stopped'
            })
        
        elif action == 'use_tool':
            tool_name = data.get('tool')
            await self.handle_tool_use(tool_name, websocket)
    
    async def handle_tool_use(self, tool_name, websocket):
        """Handle tool activation from UI"""
        tool_responses = {
            'search': 'Searching the web...',
            'image': 'Preparing to generate image...',
            'save': 'Ready to save data...',
            'html': 'HTML generator ready...',
            'weather': 'Fetching weather information...',
            'translate': 'Translation service ready...'
        }
        
        response = tool_responses.get(tool_name, f'{tool_name} tool activated')
        
        await self.broadcast({
            'type': 'tool_activation',
            'tool': tool_name,
            'message': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # If voice is active, trigger the tool
        if self.conversation and not DEMO_MODE:
            # This would trigger the actual tool in real implementation
            pass
    
    async def handle_websocket(self, websocket, path):
        """Main WebSocket handler"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_client_message(websocket, data)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.unregister_client(websocket)

# HTTP Server for UI
def start_http_server():
    """Start HTTP server for UI"""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/templates/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        
        def log_message(self, format, *args):
            pass  # Suppress logs
    
    port = 5000
    httpd = HTTPServer(('localhost', port), Handler)
    print(f"✅ UI Server running at http://localhost:{port}")
    httpd.serve_forever()

# Main execution
async def main():
    """Main async function"""
    bridge = VoiceBridge()
    
    # Start HTTP server in thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Open browser
    import webbrowser
    threading.Timer(2, lambda: webbrowser.open('http://localhost:5000')).start()
    
    # Start WebSocket server
    print(f"✅ WebSocket running at ws://localhost:8765")
    print("\n📋 Status:")
    print(f"  • Demo Mode: {DEMO_MODE}")
    print(f"  • Voice AI: {'Not configured' if DEMO_MODE else 'Ready'}")
    print(f"  • UI: http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    
    async with websockets.serve(bridge.handle_websocket, "localhost", 8765):
        await asyncio.Future()  # Run forever

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    print("\n👋 Shutting down JARVIS Voice Bridge...")
    if conversation:
        conversation.end_session()
    sys.exit(0)

if __name__ == "__main__":
    # Check requirements
    if not os.path.exists('templates/index.html'):
        print("❌ templates/index.html not found!")
        print("Run: python save_html.py")
        sys.exit(1)
    
    # Set signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        signal_handler(None, None)