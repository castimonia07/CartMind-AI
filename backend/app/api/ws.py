from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_service import websocket_manager
import json

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Client can send simple pings or updates here
            await websocket_manager.send_personal_message(
                {"type": "ack", "message": f"Message text was: {data}"},
                session_id
            )
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
