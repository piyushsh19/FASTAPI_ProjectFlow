
"""add composite database indexes

Revision ID: d66d3f7df0cc
Revises: aa25493e1613
"""

from typing import Sequence, Union

from alembic import op

revision: str = "d66d3f7df0cc"
down_revision: Union[str, Sequence[str], None] = "aa25493e1613"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Projects: owner filtering and created_at sorting.
    op.create_index(
        "ix_projects_owner_created_at",
        "projects",
        ["owner_id", "created_at"],
    )

    # Tasks: project filtering and common task filters.
    op.create_index(
        "ix_tasks_project_created_at",
        "tasks",
        ["project_id", "created_at"],
    )
    op.create_index(
        "ix_tasks_project_status",
        "tasks",
        ["project_id", "status"],
    )
    op.create_index(
        "ix_tasks_project_priority",
        "tasks",
        ["project_id", "priority"],
    )
    op.create_index(
        "ix_tasks_project_assigned_to",
        "tasks",
        ["project_id", "assigned_to"],
    )

    # Foreign-key lookup when a user is deleted.
    op.create_index(
        "ix_tasks_assigned_to",
        "tasks",
        ["assigned_to"],
    )
    op.create_index(
        "ix_project_members_user_id",
        "project_members",
        ["user_id"],
    )

    # Notifications: listing and unread notification queries.
    op.create_index(
        "ix_notifications_user_created_at",
        "notifications",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_notifications_user_is_read",
        "notifications",
        ["user_id", "is_read"],
    )

    # Remove standalone indexes covered by composite indexes.
    op.drop_index(
        "ix_tasks_project_id",
        table_name="tasks",
    )
    op.drop_index(
        "ix_notifications_user_id",
        table_name="notifications",
    )


def downgrade() -> None:
    # Restore original standalone indexes.
    op.create_index(
        "ix_tasks_project_id",
        "tasks",
        ["project_id"],
    )
    op.create_index(
        "ix_notifications_user_id",
        "notifications",
        ["user_id"],
    )

    # Remove newly introduced indexes.
    op.drop_index(
        "ix_notifications_user_is_read",
        table_name="notifications",
    )
    op.drop_index(
        "ix_notifications_user_created_at",
        table_name="notifications",
    )
    op.drop_index(
        "ix_project_members_user_id",
        table_name="project_members",
    )
    op.drop_index(
        "ix_tasks_assigned_to",
        table_name="tasks",
    )
    op.drop_index(
        "ix_tasks_project_assigned_to",
        table_name="tasks",
    )
    op.drop_index(
        "ix_tasks_project_priority",
        table_name="tasks",
    )
    op.drop_index(
        "ix_tasks_project_status",
        table_name="tasks",
    )
    op.drop_index(
        "ix_tasks_project_created_at",
        table_name="tasks",
    )
    op.drop_index(
        "ix_projects_owner_created_at",
        table_name="projects",
    )
