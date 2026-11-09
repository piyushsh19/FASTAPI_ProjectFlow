
import jwt

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.config import settings
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
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        subject = payload.get("sub")

        if subject is None:
            await websocket.close(code=4401)
            return

        user_id = int(subject)

        user = db.get(User, user_id)

        if user is None:
            await websocket.close(code=4403)
            return

    except (jwt.InvalidTokenError, ValueError, TypeError):
        await websocket.close(code=4401)
        return

    await notification_manager.connect(websocket, user_id)

    try:
        while True:
            message = await websocket.receive_text()

            if message == "ping":
                await websocket.send_json({
                    "type": "pong"
                })

    except WebSocketDisconnect:
        pass

    finally:
        await notification_manager.disconnect(
            websocket,
            user_id,
        )
