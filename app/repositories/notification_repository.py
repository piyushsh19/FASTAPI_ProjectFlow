
from datetime import datetime, timezone

from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    *,
    user_id: int,
    type: str,
    title: str,
    message: str,
    data: dict | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        data=data,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_user_notifications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
) -> list[Notification]:
    statement = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def count_user_notifications(
    db: Session,
    user_id: int,
) -> int:
    statement = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id)
    )

    return db.scalar(statement) or 0


def count_unread_notifications(
    db: Session,
    user_id: int,
) -> int:
    statement = (
        select(func.count())
        .select_from(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
    )

    return db.scalar(statement) or 0


def mark_notification_as_read(
    db: Session,
    notification_id: int,
    user_id: int,
) -> Notification | None:
    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user_id,
    )

    notification = db.scalar(statement)

    if notification is None:
        return None

    notification.is_read = True

    db.commit()
    db.refresh(notification)

    return notification


def mark_all_notifications_as_read(
    db: Session,
    user_id: int,
) -> int:
    statement = (
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True)
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount or 0


def delete_notification(
    db: Session,
    notification_id: int,
    user_id: int,
) -> bool:
    statement = delete(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == user_id,
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount > 0
