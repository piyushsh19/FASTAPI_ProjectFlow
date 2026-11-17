
import jwt
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.dependencies import get_db
from app.models import Project, ProjectMember
from app.services.websocket_manager import manager


router = APIRouter(tags=["WebSockets"])


def authenticate_websocket(
    token: str,
    project_id: int,
    db: Session,
) -> int | None:
    try:
        user_id = decode_access_token(token)
    except jwt.InvalidTokenError:
        return None

    project = db.get(Project, project_id)

    if project is None:
        return None

    if project.owner_id == user_id:
        return user_id

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()

    if membership is None:
        return None

    return user_id


@router.websocket("/ws/projects/{project_id}")
async def project_websocket(
    websocket: WebSocket,
    project_id: int,
    db: Session = Depends(get_db),
):
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(
            code=4401,
            reason="Authentication required",
        )
        return

    user_id = authenticate_websocket(
        token=token,
        project_id=project_id,
        db=db,
    )

    if user_id is None:
        await websocket.close(
            code=4403,
            reason="Invalid token or project access denied",
        )
        return

    await manager.connect(websocket, project_id)

    try:
        while True:
            message = await websocket.receive_text()

            # Project WebSocket is read-only.
            if message == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        await manager.disconnect(websocket, project_id)

    except Exception:
        await manager.disconnect(websocket, project_id)
        raise
