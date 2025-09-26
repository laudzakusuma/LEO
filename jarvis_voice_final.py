# jarvis_voice_final.py - Fixed event loop issue
import os
import sys
import signal
import asyncio
import websockets
import json
import threading
import webbrowser
import queue
from datetime import datetime
from dotenv import load_dotenv
from http.server import HTTPServer, SimpleHTTPRequestHandler

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
║         J.A.R.V.I.S - AI Assistant Interface               ║
║              Developed by LEO Technologies              ║
╚══════════════════════════════════════════════════════════════╗
""")

# Check API keys
agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")

print("\n🔑 Checking credentials...")
print(f"  AGENT_ID: {'✅ Found' if agent_id else '❌ Not found'}")
print(f"  API_KEY: {'✅ Found' if api_key else '❌ Not found'}")

# Message queue for thread-safe communication
message_queue = queue.Queue()

# Global variables
VOICE_ENABLED = False
conversation = None
clients = set()
main_loop = None  # Store main event loop

# Try to initialize voice
if agent_id and api_key:
    try:
        from elevenlabs.client import ElevenLabs
        from elevenlabs.conversational_ai.conversation import Conversation
        from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
        
        # Import tools
        try:
            from tools import client_tools
        except:
            from elevenlabs.conversational_ai.conversation import ClientTools
            client_tools = ClientTools()
        
        elevenlabs_client = ElevenLabs(api_key=api_key)
        VOICE_ENABLED = True
        print("✅ Voice system ready")
        
    except Exception as e:
        print(f"❌ Voice init error: {e}")

async def broadcast(data):
    """Broadcast to all connected clients"""
    if clients:
        disconnected = []
        for client in clients:
            try:
                await client.send(json.dumps(data))
            except:
                disconnected.append(client)
        for client in disconnected:
            clients.discard(client)

async def process_message_queue():
    """Process messages from queue (runs in main event loop)"""
    while True:
        try:
            # Check for messages in queue
            while not message_queue.empty():
                msg = message_queue.get_nowait()
                await broadcast(msg)
        except:
            pass
        await asyncio.sleep(0.1)  # Small delay to prevent CPU spinning

def queue_message(msg_type, text, **kwargs):
    """Queue a message to be sent (thread-safe)"""
    message = {
        'type': msg_type,
        'text': text,
        'timestamp': datetime.now().isoformat()
    }
    message.update(kwargs)
    message_queue.put(message)

def start_voice_session():
    """Start ElevenLabs voice conversation with fixed callbacks"""
    global conversation
    
    if not VOICE_ENABLED:
        return False
    
    try:
        print("🎤 Starting voice session...")
        
        # Create conversation with thread-safe callbacks
        conversation = Conversation(
            elevenlabs_client,
            agent_id,
            client_tools=client_tools,
            requires_auth=True,
            audio_interface=DefaultAudioInterface(),
            
            # Thread-safe callbacks using queue
            callback_agent_response=lambda response: queue_message('response', response),
            callback_user_transcript=lambda transcript: queue_message('transcript', transcript),
            callback_agent_response_correction=lambda original, corrected: queue_message(
                'correction', corrected, original=original
            ),
        )
        
        # Start session in separate thread
        conversation_thread = threading.Thread(target=conversation.start_session)
        conversation_thread.daemon = True
        conversation_thread.start()
        
        print("✅ Voice session active - Speak now!")
        return True
        
    except Exception as e:
        print(f"❌ Voice session error: {e}")
        import traceback
        traceback.print_exc()
        return False

def stop_voice_session():
    """Stop voice conversation"""
    global conversation
    
    if conversation:
        try:
            conversation.end_session()
            print("✅ Voice session ended")
        except Exception as e:
            print(f"Error ending session: {e}")
        finally:
            conversation = None

async def handle_websocket(websocket):
    """WebSocket handler"""
    clients.add(websocket)
    print(f"👤 Client connected. Total: {len(clients)}")
    
    # Send initial status
    await websocket.send(json.dumps({
        'type': 'connection',
        'status': 'connected',
        'message': f'JARVIS {"Voice Ready" if VOICE_ENABLED else "Demo Mode"}',
        'voice_enabled': VOICE_ENABLED
    }))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'start_listening':
                if VOICE_ENABLED:
                    if start_voice_session():
                        await websocket.send(json.dumps({
                            'type': 'status',
                            'message': '🎤 Voice Active - Speak Now!'
                        }))
                    else:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': 'Voice session failed'
                        }))
                else:
                    # Demo mode
                    await websocket.send(json.dumps({
                        'type': 'status',
                        'message': 'Demo Mode'
                    }))
                    
                    await asyncio.sleep(1)
                    await broadcast({
                        'type': 'transcript',
                        'text': 'Hello JARVIS!',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    await asyncio.sleep(1)
                    await broadcast({
                        'type': 'response',
                        'text': 'Voice requires API configuration.',
                        'timestamp': datetime.now().isoformat()
                    })
            
            elif action == 'stop_listening':
                if VOICE_ENABLED:
                    stop_voice_session()
                
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'Stopped'
                }))
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.discard(websocket)

def start_http_server():
    """Start HTTP server"""
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/templates/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        def log_message(self, *args):
            pass
    
    httpd = HTTPServer(('localhost', 5000), Handler)
    print("🌐 UI at http://localhost:5000")
    httpd.serve_forever()

async def main():
    """Main function with proper event loop"""
    global main_loop
    main_loop = asyncio.get_event_loop()
    
    # Check HTML
    if not os.path.exists('templates/index.html'):
        print("❌ templates/index.html not found!")
        return
    
    # Start HTTP server
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    
    # Open browser
    threading.Timer(2, lambda: webbrowser.open('http://localhost:5000')).start()
    
    # Start message queue processor
    asyncio.create_task(process_message_queue())
    
    print("🔌 WebSocket at ws://localhost:8765")
    print("\n📊 Status:")
    print(f"  • Voice: {'✅ ENABLED' if VOICE_ENABLED else '❌ DISABLED'}")
    print(f"  • UI: http://localhost:5000")
    print(f"\nPress Ctrl+C to stop\n")
    
    # WebSocket server
    async def ws_wrapper(ws, *args):
        await handle_websocket(ws)
    
    async with websockets.serve(ws_wrapper, "localhost", 8765):
        await asyncio.Future()

def signal_handler(sig, frame):
    """Handle shutdown"""
    print("\n👋 Shutting down...")
    if conversation:
        stop_voice_session()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        signal_handler(None, None)