
"""add database check constraints

Revision ID: 4786cb879bc7
Revises: d66d3f7df0cc
Create Date: 2026-11-15 20:07:12.311390

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4786cb879bc7"
down_revision: Union[str, Sequence[str], None] = "d66d3f7df0cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add database check constraints."""

    op.create_check_constraint(
        "ck_projects_status",
        "projects",
        "status IN ('active', 'completed', 'archived')",
    )

    op.create_check_constraint(
        "ck_tasks_status",
        "tasks",
        "status IN ('todo', 'in_progress', 'done')",
    )

    op.create_check_constraint(
        "ck_tasks_priority",
        "tasks",
        "priority IN ('low', 'medium', 'high', 'urgent')",
    )

    op.create_check_constraint(
        "ck_project_members_role",
        "project_members",
        "role IN ('admin', 'member', 'viewer')",
    )


def downgrade() -> None:
    """Remove database check constraints."""

    op.drop_constraint(
        "ck_project_members_role",
        "project_members",
        type_="check",
    )

    op.drop_constraint(
        "ck_tasks_priority",
        "tasks",
        type_="check",
    )

    op.drop_constraint(
        "ck_tasks_status",
        "tasks",
        type_="check",
    )

    op.drop_constraint(
        "ck_projects_status",
        "projects",
        type_="check",
    )
