
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import jwt
from jwt import InvalidTokenError

from app.core.config import settings
from app.db.dependencies import get_db
from app.models import Project, ProjectMember
from app.services.websocket_manager import manager


router = APIRouter(tags=["WebSockets"])


def authenticate_websocket(
    token: str,
    project_id: int,
    db: Session,
):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )

        user_id = int(payload["sub"])

    except (InvalidTokenError, KeyError, TypeError, ValueError):
        return None

    project = db.get(Project, project_id)

    if not project:
        return None

    if project.owner_id == user_id:
        return user_id

    membership = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    ).first()

    if not membership:
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

            if message == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)

    except Exception:
        manager.disconnect(websocket, project_id)
        raise
