
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.schemas.notification import NotificationCreate
from app.services.notification_service import create_notification
from app.services.notification_publisher import publish_notification


def dispatch_notification(
    db: Session,
    background_tasks: BackgroundTasks,
    *,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    data: dict | None = None,
) -> None:

    # Step 1: Persist notification in PostgreSQL.
    notification = create_notification(
        db=db,
        notification_data=NotificationCreate(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data,
        ),
    )

    # Step 2: Publish only after persistence succeeds.
    event = {
        "type": "notification.created",
        "notification": notification.model_dump(mode="json"),
    }

    background_tasks.add_task(
        publish_notification,
        user_id,
        event,
    )
