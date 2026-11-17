
import jwt
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.dependencies import get_db
from app.models.user import User
from app.services.notification_websocket_manager import (
    notification_manager,
)


router = APIRouter(tags=["Notification WebSockets"])


@router.websocket("/ws/notifications")
async def notification_websocket(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db),
):
    try:
        user_id = decode_access_token(token)
    except jwt.InvalidTokenError:
        await websocket.close(
            code=4401,
            reason="Invalid authentication token",
        )
        return

    user = db.get(User, user_id)

    if user is None:
        await websocket.close(
            code=4403,
            reason="User not found",
        )
        return

    await notification_manager.connect(websocket, user_id)

    try:
        while True:
            message = await websocket.receive_text()

            # Notification WebSocket is read-only.
            if message == "ping":
                await websocket.send_json({
                    "type": "pong",
                })

    except WebSocketDisconnect:
        pass

    finally:
        await notification_manager.disconnect(
            websocket,
            user_id,
        )
