"""
ORBIT WebSocket Router
Handles real-time client connection upgrades and stream event subscriptions.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..websocket_manager import ws_manager

router = APIRouter(tags=["WebSocket Events"])


@router.websocket("/ws/events")
async def websocket_events_endpoint(websocket: WebSocket):
    """
    Real-time streaming bus:
    Emits agent reasoning steps, node pulse red/emerald events, and telemetry ticks.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open and receive client pings/messages
            data = await websocket.receive_text()
            # Echo heartbeat ping
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
