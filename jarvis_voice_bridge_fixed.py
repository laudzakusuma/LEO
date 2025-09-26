# jarvis_voice_bridge_fixed.py - Fixed WebSocket handler
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
try:
    from tools import client_tools
    from elevenlabs.client import ElevenLabs
    from elevenlabs.conversational_ai.conversation import Conversation
    from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
    HAS_ELEVENLABS = True
except ImportError:
    HAS_ELEVENLABS = False
    print("⚠️  ElevenLabs not imported - running in demo mode")

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
║        VOICE AI BRIDGE - Fixed WebSocket Handler           ║
╚══════════════════════════════════════════════════════════════╗
""")

# Global variables
conversation = None
websocket_clients = set()

# Get API credentials
agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

# Check mode
if not agent_id or not api_key or not HAS_ELEVENLABS:
    DEMO_MODE = True
    print("\n⚠️  Running in DEMO mode (voice features disabled)")
    if not agent_id or not api_key:
        print("   Add to .env file:")
        print("   ELEVENLABS_API_KEY=your_key")
        print("   AGENT_ID=your_agent_id")
else:
    DEMO_MODE = False
    elevenlabs = ElevenLabs(api_key=api_key)
    print("✅ Voice AI Ready")

# Global clients set for WebSocket connections
clients = set()

async def register_client(websocket):
    """Register new WebSocket client"""
    clients.add(websocket)
    await websocket.send(json.dumps({
        'type': 'connection',
        'status': 'connected',
        'message': 'JARVIS Voice Bridge Connected',
        'demo_mode': DEMO_MODE
    }))
    print(f"✅ Client connected. Total: {len(clients)}")

def unregister_client(websocket):
    """Remove WebSocket client"""
    clients.discard(websocket)
    print(f"Client disconnected. Total: {len(clients)}")

async def broadcast(data):
    """Broadcast to all connected clients"""
    if clients:
        disconnected = set()
        for client in clients:
            try:
                await client.send(json.dumps(data))
            except:
                disconnected.add(client)
        # Remove disconnected clients
        for client in disconnected:
            unregister_client(client)

def start_voice_conversation():
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
                
                # Callbacks
                callback_agent_response=lambda response: asyncio.create_task(
                    broadcast({
                        'type': 'response',
                        'text': response,
                        'timestamp': datetime.now().isoformat()
                    })
                ),
                callback_user_transcript=lambda transcript: asyncio.create_task(
                    broadcast({
                        'type': 'transcript',
                        'text': transcript,
                        'timestamp': datetime.now().isoformat()
                    })
                ),
            )
            conversation.start_session()
            print("✅ Voice conversation started")
            return True
    except Exception as e:
        print(f"❌ Error starting voice: {e}")
        return False

def stop_voice_conversation():
    """Stop ElevenLabs conversation"""
    global conversation
    
    if conversation:
        try:
            conversation.end_session()
            conversation = None
            print("✅ Voice stopped")
        except:
            pass

async def handle_websocket(websocket, path):
    """WebSocket connection handler - FIXED"""
    await register_client(websocket)
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                action = data.get('action')
                
                if action == 'start_listening':
                    if DEMO_MODE:
                        # Demo mode
                        await websocket.send(json.dumps({
                            'type': 'status',
                            'message': 'Demo Mode Active - No real voice'
                        }))
                        
                        # Simulate conversation
                        await asyncio.sleep(1)
                        await broadcast({
                            'type': 'transcript',
                            'text': 'Hello JARVIS, what can you do?',
                            'timestamp': datetime.now().isoformat()
                        })
                        
                        await asyncio.sleep(1.5)
                        await broadcast({
                            'type': 'response',
                            'text': 'I am JARVIS, your AI assistant. I can search the web, generate images, save data, and more. How may I assist you?',
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        # Real voice mode
                        if start_voice_conversation():
                            await websocket.send(json.dumps({
                                'type': 'status',
                                'message': 'Voice Active - Speak Now'
                            }))
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': 'Failed to start voice'
                            }))
                
                elif action == 'stop_listening':
                    stop_voice_conversation()
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'message': 'Voice stopped'
                    }))
                
                elif action == 'use_tool':
                    tool_name = data.get('tool')
                    await handle_tool_use(tool_name)
                
            except json.JSONDecodeError:
                print(f"Invalid JSON received: {message}")
            except Exception as e:
                print(f"Error handling message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        unregister_client(websocket)

async def handle_tool_use(tool_name):
    """Handle tool activation"""
    responses = {
        'search': '🔍 Web search activated',
        'image': '🎨 Image generator ready',
        'save': '💾 Save function ready',
        'html': '🌐 HTML creator ready',
        'weather': '🌤️ Weather service ready',
        'translate': '🌍 Translation ready'
    }
    
    await broadcast({
        'type': 'tool_activation',
        'tool': tool_name,
        'message': responses.get(tool_name, f'{tool_name} activated'),
        'timestamp': datetime.now().isoformat()
    })

def start_http_server():
    """Start HTTP server for UI"""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/templates/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        
        def log_message(self, format, *args):
            pass
    
    port = 5000
    httpd = HTTPServer(('localhost', port), Handler)
    print(f"✅ UI running at http://localhost:{port}")
    httpd.serve_forever()

async def main():
    """Main function"""
    # Start HTTP server in thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Open browser
    import webbrowser
    threading.Timer(2, lambda: webbrowser.open('http://localhost:5000')).start()
    
    # Start WebSocket server - FIXED: Just pass handle_websocket directly
    print(f"✅ WebSocket at ws://localhost:8765")
    print(f"\n📊 Status:")
    print(f"  • Mode: {'DEMO' if DEMO_MODE else 'VOICE ENABLED'}")
    print(f"  • UI: http://localhost:5000")
    print(f"  • API Keys: {'Not configured' if DEMO_MODE else 'Configured'}")
    print(f"\n💡 Tips:")
    print(f"  • Click 'Start Listening' to test")
    print(f"  • Try tool cards in sidebar")
    print(f"  • Press Ctrl+C to stop")
    
    # Start WebSocket server with correct handler
    async with websockets.serve(handle_websocket, "localhost", 8765):
        await asyncio.Future()  # Run forever

def signal_handler(sig, frame):
    """Handle shutdown"""
    print("\n\n👋 Shutting down JARVIS...")
    if conversation:
        conversation.end_session()
    sys.exit(0)

if __name__ == "__main__":
    # Check for HTML
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