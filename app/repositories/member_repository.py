from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import ProjectMember, User


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)


def get_membership(
    db: Session,
    project_id: int,
    user_id: int,
) -> ProjectMember | None:
    statement = (
        select(ProjectMember)
        .options(joinedload(ProjectMember.user))
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    return db.scalar(statement)


def get_project_members(
    db: Session,
    project_id: int,
) -> list[ProjectMember]:
    statement = (
        select(ProjectMember)
        .options(joinedload(ProjectMember.user))
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.created_at.asc())
    )
    return list(db.scalars(statement).unique().all())


def create_member(
    db: Session,
    project_id: int,
    user_id: int,
    role: str,
) -> ProjectMember:
    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )

    db.add(member)
    db.commit()

    return get_membership(db, project_id, user_id)


def update_member_role(
    db: Session,
    member: ProjectMember,
    role: str,
) -> ProjectMember:
    member.role = role

    db.commit()

    return get_membership(db, member.project_id, member.user_id)


def delete_member(
    db: Session,
    member: ProjectMember,
) -> None:
    db.delete(member)
    db.commit()