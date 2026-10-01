"""
ORBIT WebSocket Event Bus & Connection Manager
Broadcasting real-time agent reasoning traces, node health pulses, and live telemetry.
"""
from typing import List, Dict, Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime, timezone


class ConnectionManager:
    """Manages active WebSocket client connections and event dispatch."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send initial handshake
        await websocket.send_json({
            "type": "connection_established",
            "message": "Connected to ORBIT Control Tower Real-Time Telemetry Bus",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcasts a JSON event to all connected clients."""
        if not self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)


ws_manager = ConnectionManager()
