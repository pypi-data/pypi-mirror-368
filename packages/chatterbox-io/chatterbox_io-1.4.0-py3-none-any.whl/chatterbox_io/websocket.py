import asyncio
import socketio
from typing import Callable, Dict, Optional
from .models import WebSocketEvent


class WebSocketClient:
    """WebSocket client for handling real-time ChatterBox events."""

    def __init__(self, session_id: str, authorization_token: str, base_url: str = "wss://ws.chatter-box.io"):
        self.session_id = session_id
        self.authorization_token = authorization_token
        self.base_url = base_url
        self._handlers: Dict[str, list[Callable]] = {
            "meeting_started": [],
            "meeting_finished": [],
            "transcript_received": [],
        }
        self._sio: Optional[socketio.AsyncClient] = None
        self._running = False
        self._connected = asyncio.Event()
        self._last_error = None

    async def __aenter__(self) -> 'WebSocketClient':
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()

    def on_meeting_started(self, handler: Callable):
        """Register a handler for meeting started events."""
        self._handlers["meeting_started"].append(handler)

    def on_meeting_finished(self, handler: Callable):
        """Register a handler for meeting finished events."""
        self._handlers["meeting_finished"].append(handler)

    def on_transcript_received(self, handler: Callable):
        """Register a handler for transcript events."""
        self._handlers["transcript_received"].append(handler)

    async def connect(self) -> None:
        """Connect to the Socket.IO server."""
        if self._sio is not None:
            return

        self._sio = socketio.AsyncClient(
            logger=False,
            engineio_logger=False,
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5
        )
        
        @self._sio.event
        async def connect():
            self._running = True
            self._connected.set()
            self._last_error = None

        @self._sio.event
        async def connect_error(error):
            self._last_error = error
            self._connected.set()

        @self._sio.event
        async def disconnect():
            self._running = False
            self._connected.clear()

        @self._sio.event
        async def error(error):
            print(f"Socket.IO error: {error}")
            self._last_error = error

        @self._sio.on('started')
        async def handle_meeting_started(data):
            for handler in self._handlers["meeting_started"]:
                await handler(data)

        @self._sio.on('finished')
        async def handle_meeting_finished(data):
            for handler in self._handlers["meeting_finished"]:
                await handler(data)

        @self._sio.on('transcript')
        async def handle_transcript(data):
            for handler in self._handlers["transcript_received"]:
                await handler(data)

        try:
            url = f"{self.base_url}?sessionId={self.session_id}"
            await self._sio.connect(
                url,
                auth={'token': self.authorization_token},
                wait_timeout=10,
                transports=['websocket'],
                headers={'Authorization': f'Bearer {self.authorization_token}'}
            )
            await self._connected.wait()
            
            if self._last_error:
                raise Exception(f"Connection failed: {self._last_error}")
                
        except Exception as e:
            print(f"Failed to connect to Socket.IO server: {str(e)}")
            if self._sio:
                await self._sio.disconnect()
            self._sio = None
            raise

    async def disconnect(self) -> None:
        """Disconnect from the Socket.IO server."""
        if self._sio is not None:
            await self._sio.disconnect()
            self._sio = None
        self._running = False

    async def wait_closed(self) -> None:
        """Wait for the Socket.IO connection to close."""
        if self._sio is not None:
            try:
                while self._running:
                    await asyncio.sleep(1)
                    if self._last_error:
                        print(f"Connection error detected: {self._last_error}")
                        break
            except asyncio.CancelledError:
                pass 