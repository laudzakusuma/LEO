# app.py - Flask Backend dengan WebSocket untuk UI
import os
import json
import asyncio
import websockets
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import threading
import queue
from datetime import datetime

# Import existing modules
from tools import client_tools
from enhanced_tools import (
    get_weather, translate_text, get_news, 
    set_reminder, get_system_info, calculate_math,
    get_crypto_price, send_email_notification
)
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

load_dotenv()

app = Flask(__name__)
CORS(app)

# Global variables
conversation = None
message_queue = queue.Queue()
connected_clients = set()

# Initialize ElevenLabs
agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")
elevenlabs = ElevenLabs(api_key=api_key)

class WebSocketAudioInterface(DefaultAudioInterface):
    """Custom audio interface that sends updates to WebSocket clients"""
    
    def __init__(self, websocket_handler):
        super().__init__()
        self.websocket_handler = websocket_handler
    
    def on_audio_start(self):
        self.websocket_handler.send_update({
            'type': 'audio_start',
            'timestamp': datetime.now().isoformat()
        })
    
    def on_audio_stop(self):
        self.websocket_handler.send_update({
            'type': 'audio_stop',
            'timestamp': datetime.now().isoformat()
        })

class WebSocketHandler:
    """Handler for WebSocket communications"""
    
    def __init__(self):
        self.clients = set()
    
    async def register(self, websocket):
        self.clients.add(websocket)
        await websocket.send(json.dumps({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to JARVIS AI Assistant'
        }))
    
    def unregister(self, websocket):
        self.clients.remove(websocket)
    
    def send_update(self, data):
        """Send update to all connected clients"""
        if self.clients:
            message = json.dumps(data)
            for client in self.clients:
                asyncio.create_task(client.send(message))
    
    async def handle_client(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.process_message(data, websocket)
        finally:
            self.unregister(websocket)
    
    async def process_message(self, data, websocket):
        action = data.get('action')
        
        if action == 'start_listening':
            await self.start_conversation(websocket)
        elif action == 'stop_listening':
            await self.stop_conversation(websocket)
        elif action == 'use_tool':
            await self.use_tool(data.get('tool'), websocket)
        elif action == 'send_message':
            await self.send_message(data.get('text'), websocket)
    
    async def start_conversation(self, websocket):
        global conversation
        
        if not conversation:
            conversation = Conversation(
                elevenlabs,
                agent_id,
                client_tools=client_tools,
                requires_auth=bool(api_key),
                audio_interface=WebSocketAudioInterface(self),
                callback_agent_response=lambda response: self.handle_agent_response(response),
                callback_agent_response_correction=lambda original, corrected: self.handle_correction(original, corrected),
                callback_user_transcript=lambda transcript: self.handle_user_transcript(transcript),
            )
            conversation.start_session()
            
        await websocket.send(json.dumps({
            'type': 'status',
            'message': 'Listening started'
        }))
    
    async def stop_conversation(self, websocket):
        global conversation
        
        if conversation:
            conversation.end_session()
            conversation = None
            
        await websocket.send(json.dumps({
            'type': 'status',
            'message': 'Listening stopped'
        }))
    
    async def use_tool(self, tool_name, websocket):
        result = None
        
        try:
            if tool_name == 'weather':
                result = get_weather({'location': 'current'})
            elif tool_name == 'news':
                result = get_news({'category': 'technology'})
            elif tool_name == 'crypto':
                result = get_crypto_price({'symbol': 'BTC'})
            elif tool_name == 'system':
                result = get_system_info({})
            
            await websocket.send(json.dumps({
                'type': 'tool_result',
                'tool': tool_name,
                'result': str(result)
            }))
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Tool error: {str(e)}'
            }))
    
    def handle_agent_response(self, response):
        self.send_update({
            'type': 'response',
            'text': response,
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_correction(self, original, corrected):
        self.send_update({
            'type': 'correction',
            'original': original,
            'corrected': corrected,
            'timestamp': datetime.now().isoformat()
        })
    
    def handle_user_transcript(self, transcript):
        self.send_update({
            'type': 'transcript',
            'text': transcript,
            'timestamp': datetime.now().isoformat()
        })

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'online',
        'conversation_active': conversation is not None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system-info')
def get_system_info_api():
    info = get_system_info({})
    return jsonify(info)

# WebSocket Server
async def websocket_server():
    handler = WebSocketHandler()
    async with websockets.serve(handler.handle_client, "localhost", 8765):
        await asyncio.Future()  # run forever

def run_websocket_server():
    asyncio.new_event_loop().run_until_complete(websocket_server())

# Main execution
if __name__ == '__main__':
    # Start WebSocket server in separate thread
    ws_thread = threading.Thread(target=run_websocket_server, daemon=True)
    ws_thread.start()
    
    # Start Flask server
    app.run(debug=True, port=5000)