
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.repositories import notification_repository as repository
from app.schemas.notification import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    NotificationReadResponse,
)


def create_notification(
    db: Session,
    notification_data: NotificationCreate,
) -> NotificationResponse:
    notification = repository.create_notification(
        db=db,
        user_id=notification_data.user_id,
        type=notification_data.type,
        title=notification_data.title,
        message=notification_data.message,
        data=notification_data.data,
    )

    return NotificationResponse.model_validate(notification)


def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
) -> NotificationListResponse:
    notifications = repository.get_user_notifications(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )

    total = repository.count_user_notifications(
        db=db,
        user_id=user_id,
    )

    unread_count = repository.count_unread_notifications(
        db=db,
        user_id=user_id,
    )

    return NotificationListResponse(
        notifications=[
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ],
        total=total,
        unread_count=unread_count,
    )


def get_unread_count(
    db: Session,
    user_id: int,
) -> int:
    return repository.count_unread_notifications(
        db=db,
        user_id=user_id,
    )


def mark_as_read(
    db: Session,
    notification_id: int,
    user_id: int,
) -> NotificationReadResponse | None:
    notification = repository.mark_notification_as_read(
        db=db,
        notification_id=notification_id,
        user_id=user_id,
    )

    if notification is None:
        return None

    return NotificationReadResponse(
        id=notification.id,
        is_read=notification.is_read,
    )


def mark_all_as_read(
    db: Session,
    user_id: int,
) -> int:
    return repository.mark_all_notifications_as_read(
        db=db,
        user_id=user_id,
    )


def delete_notification(
    db: Session,
    notification_id: int,
    user_id: int,
) -> bool:
    return repository.delete_notification(
        db=db,
        notification_id=notification_id,
        user_id=user_id,
    )
