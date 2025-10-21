# app.py (final)
import asyncio
import threading
import json
import traceback
import logging
from flask import Flask, send_from_directory
import websockets

# Optional: import elevenlabs conversational ai if present
try:
    import elevenlabs.conversational_ai.conversation as el_conv_mod  # optional
except Exception:
    el_conv_mod = None

logging.basicConfig(level=logging.DEBUG)

# ---------- AudioInterfaceAdapter ----------
class AudioInterfaceAdapter:
    """
    Wrap an audio interface implementation so it always exposes .start(...) and .stop().
    Delegates to common alternative names if necessary, otherwise no-ops.
    """
    def __init__(self, impl):
        self._impl = impl

    def start(self, *args, **kwargs):
        if hasattr(self._impl, "start"):
            return self._impl.start(*args, **kwargs)
        if hasattr(self._impl, "open"):
            return self._impl.open(*args, **kwargs)
        if hasattr(self._impl, "begin"):
            return self._impl.begin(*args, **kwargs)
        if hasattr(self._impl, "record"):
            return self._impl.record(*args, **kwargs)
        if hasattr(self._impl, "play"):
            return self._impl.play(*args, **kwargs)
        logging.debug("AudioInterfaceAdapter: no start-like method found; no-op.")
        return None

    def stop(self, *args, **kwargs):
        if hasattr(self._impl, "stop"):
            return self._impl.stop(*args, **kwargs)
        if hasattr(self._impl, "close"):
            return self._impl.close(*args, **kwargs)
        if hasattr(self._impl, "end"):
            return self._impl.end(*args, **kwargs)
        logging.debug("AudioInterfaceAdapter: no stop-like method found; no-op.")
        return None

    def __getattr__(self, name):
        return getattr(self._impl, name)

def wrap_audio_interface(conversation):
    """
    Ensure conversation.audio_interface has start() and stop() by wrapping it with adapter.
    Call after conversation creation.
    """
    try:
        ai = getattr(conversation, "audio_interface", None)
        if ai is None:
            logging.debug("wrap_audio_interface: conversation has no audio_interface.")
            return
        conversation.audio_interface = AudioInterfaceAdapter(ai)
        logging.debug("wrap_audio_interface: wrapped audio_interface with AudioInterfaceAdapter.")
    except Exception:
        logging.exception("wrap_audio_interface failed")

# ---------- Safe conversation helpers ----------
def safe_start_conversation(conversation, input_callback=None):
    try:
        if conversation is None:
            return
        wrap_audio_interface(conversation)
        audio_if = conversation.audio_interface
        if hasattr(audio_if, "start"):
            if input_callback is not None:
                audio_if.start(input_callback)
            else:
                audio_if.start()
        else:
            logging.debug("safe_start_conversation: no start(); skipped.")
    except Exception:
        logging.exception("safe_start_conversation failed")

def safe_end_conversation(conversation):
    try:
        if conversation is None:
            return
        audio_if = getattr(conversation, "audio_interface", None)
        if audio_if is not None and hasattr(audio_if, "stop"):
            audio_if.stop()
        else:
            logging.debug("safe_end_conversation: no stop(); skipped.")
        if hasattr(conversation, "end_session"):
            try:
                conversation.end_session()
            except Exception:
                logging.exception("safe_end_conversation: conversation.end_session() raised")
    except Exception:
        logging.exception("safe_end_conversation failed")

# ---------- Flask app ----------
app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return "<html><body><h1>JARVIS AI Assistant</h1></body></html>"

@app.route("/favicon.ico")
def favicon():
    try:
        return send_from_directory(app.static_folder, "favicon.ico")
    except Exception:
        return "", 404

# ---------- WebSocket / connection management ----------
connected_clients = set()
clients_lock = threading.Lock()
conversations = {}  # map client_id -> conversation object (if you create them)

# WebSocket handler compatible with both old/new websockets signatures
async def websocket_handler(websocket, path=None):
    if path is None and hasattr(websocket, "path"):
        path = websocket.path

    client_id = id(websocket)
    try:
        with clients_lock:
            connected_clients.add(client_id)
            print(f"✅ Client connected. Total clients: {len(connected_clients)}")

        # Example: create a conversation per client if needed (pseudo)
        # conversation = create_conversation(...)
        # wrap_audio_interface(conversation)
        # conversations[client_id] = conversation

        async for raw in websocket:
            try:
                data = json.loads(raw)
            except Exception:
                # not JSON -> echo
                await websocket.send(json.dumps({"error": "invalid json", "raw": raw}))
                continue

            # Example message handling
            action = data.get("action")
            if action == "stop_conversation":
                await (client_id)
                await websocket.send(json.dumps({"status": "stopped"}))
            elif action == "start_conversation":
                conv = conversations.get(client_id)
                if conv:
                    # Demo: start safely (won't raise if audio missing)
                    safe_start_conversation(conv)
                    await websocket.send(json.dumps({"status": "started"}))
                else:
                    await websocket.send(json.dumps({"error": "no conversation for client"}))
            else:
                # default echo
                await websocket.send(json.dumps({"echo": data}))

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception:
        print("connection handler failed")
        traceback.print_exc()
    finally:
        with clients_lock:
            if client_id in connected_clients:
                connected_clients.remove(client_id)
            print(f"❌ Client disconnected. Total clients: {len(connected_clients)}")

        # cleanup conversation (synchronously on executor)
        conv = conversations.pop(client_id, None)
        if conv:
            loop = asyncio.get_event_loop()
            # in case event loop not running in main thread, run end in executor
            try:
                loop.run_in_executor(None, safe_end_conversation, conv)
            except Exception:
                # fallback: call directly (best-effort)
                try:
                    safe_end_conversation(conv)
                except Exception:
                    logging.exception("cleanup conversation failed")

async def stop_conversation_for_client_async(client_id):
    conv = conversations.get(client_id)
    if conv:
        safe_end_conversation(conv)
        conversations.pop(client_id, None)

async def _noop():  # placeholder if needed
    await asyncio.sleep(0)

async def _ws_server_runner(host="localhost", port=8765):
    # Use async context manager so server is closed cleanly on shutdown.
    async with websockets.serve(websocket_handler, host, port):
        print(f"🚀 WebSocket server running on ws://{host}:{port}")
        await asyncio.Future()  # run forever

def start_websocket_server(host="localhost", port=8765):
    """
    Thread target that runs its own event loop via asyncio.run()
    """
    try:
        asyncio.run(_ws_server_runner(host, port))
    except Exception:
        print("WebSocket server thread crashed:")
        traceback.print_exc()

# ---------- Application bootstrap ----------
def start_flask_app():
    # Flask runs in main thread; disable reloader to avoid duplicate threads
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)

def main():
    # Start websocket server in background thread (uses asyncio.run internally)
    ws_thread = threading.Thread(target=start_websocket_server, args=("localhost", 8765), daemon=True)
    ws_thread.start()

    # Start Flask on main thread
    start_flask_app()

if __name__ == "__main__":
    main()
