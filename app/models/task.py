
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="todo",
        nullable=False,
    )

    priority: Mapped[str] = mapped_column(
        String(30),
        default="medium",
        nullable=False,
    )

    project_id: Mapped[int] = mapped_column(
    ForeignKey("projects.id", ondelete="CASCADE"),
    nullable=False,
)
    assigned_to: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    project: Mapped["Project"] = relationship(
        back_populates="tasks",
    )

    assignee: Mapped["User | None"] = relationship()
    __table_args__ = (
    Index("ix_tasks_project_created_at", "project_id", "created_at"),
    Index("ix_tasks_project_status", "project_id", "status"),
    Index("ix_tasks_project_priority", "project_id", "priority"),
    Index("ix_tasks_project_assigned_to", "project_id", "assigned_to"),
    Index("ix_tasks_assigned_to", "assigned_to"),
)
