#!/usr/bin/env python3
"""
MiniMe WebSocket Server
Provides real-time communication between Python backend and Electron frontend.
"""

import asyncio
import json
import logging
import threading
from typing import List, Optional

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    print("⚠️  websockets not installed. Run: pip install websockets")
    websockets = None
    WebSocketServerProtocol = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global WebSocket server instance
_wss: Optional[asyncio.Server] = None
_clients: List[WebSocketServerProtocol] = []
_server_thread: Optional[threading.Thread] = None
_loop: Optional[asyncio.AbstractEventLoop] = None


async def handle_client(websocket, path=None):
    """Handle a new WebSocket client connection."""
    global _clients
    _clients.append(websocket)
    client_addr = getattr(websocket, 'remote_address', 'unknown')
    logger.info(f"Frontend connected: {client_addr}")
    
    # Send connection confirmation
    try:
        await send_to_client(websocket, {"event": "connected"})
    except Exception as e:
        logger.warning(f"Error sending connection confirmation: {e}")
    
    try:
        # Keep connection alive
        async for message in websocket:
            try:
                data = json.loads(message)
                logger.debug(f"Received from frontend: {data}")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from frontend: {message}")
    except websockets.exceptions.ConnectionClosed:
        logger.info("Frontend disconnected")
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
    finally:
        if websocket in _clients:
            _clients.remove(websocket)


async def send_to_client(websocket: WebSocketServerProtocol, data: dict):
    """Send data to a specific client."""
    try:
        await websocket.send(json.dumps(data))
    except websockets.exceptions.ConnectionClosed:
        logger.warning("Client connection closed")


def send_to_ui(data: dict):
    """
    Broadcast data to all connected frontend clients.
    This is the main function to call from the backend.
    
    Args:
        data (dict): Data to send, e.g. {"event": "wake"} or {"event": "talk", "levels": [0.2, 0.6, 0.8]}
    """
    global _clients, _loop
    
    if not _clients:
        return
    
    if _loop is None or not _loop.is_running():
        logger.warning("WebSocket server not running, cannot send message")
        return
    
    message = json.dumps(data)
    
    # Schedule send on the event loop
    async def broadcast():
        disconnected = []
        for client in _clients:
            try:
                # Check if client is still open (websockets 15.x uses different property)
                is_open = getattr(client, 'open', None)
                if is_open is None:
                    # Try alternative check
                    is_open = not getattr(client, 'closed', True)
                
                if is_open:
                    await client.send(message)
                else:
                    disconnected.append(client)
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client)
            except Exception as e:
                logger.warning(f"Error sending to client: {e}")
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            if client in _clients:
                _clients.remove(client)
    
    # Run in the event loop
    asyncio.run_coroutine_threadsafe(broadcast(), _loop)


async def start_server():
    """Start the WebSocket server."""
    global _wss, _loop
    _loop = asyncio.get_event_loop()
    
    try:
        # Use the correct websockets.serve signature for websockets 15.x
        # The handler will be called with (websocket, path) automatically
        _wss = await websockets.serve(
            handle_client,
            "localhost",
            8081,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=10
        )
        logger.info("🌐 WebSocket server started on ws://localhost:8081")
        await asyncio.Future()  # Run forever
    except Exception as e:
        logger.error(f"Error starting WebSocket server: {e}")
        import traceback
        traceback.print_exc()
        raise


def start_server_thread():
    """Start the WebSocket server in a background thread."""
    global _server_thread
    
    if _server_thread is not None and _server_thread.is_alive():
        logger.warning("WebSocket server already running")
        return
    
    if websockets is None:
        logger.error("websockets library not installed. Run: pip install websockets")
        return
    
    def run_server():
        try:
            asyncio.run(start_server())
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
    
    _server_thread = threading.Thread(target=run_server, daemon=True)
    _server_thread.start()
    logger.info("✅ WebSocket server thread started")


def stop_server():
    """Stop the WebSocket server."""
    global _wss, _server_thread, _clients, _loop
    
    _clients.clear()
    
    if _wss:
        _wss.close()
        _wss = None
    
    if _loop and _loop.is_running():
        _loop.call_soon_threadsafe(_loop.stop)
    
    if _server_thread and _server_thread.is_alive():
        # Thread will exit when loop stops
        pass
    
    logger.info("WebSocket server stopped")


if __name__ == "__main__":
    # Test the server
    start_server_thread()
    import time
    time.sleep(2)
    
    # Test sending messages
    send_to_ui({"event": "test", "message": "Hello from backend!"})
    time.sleep(1)
    send_to_ui({"event": "wake"})
    time.sleep(1)
    send_to_ui({"event": "idle"})
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_server()

