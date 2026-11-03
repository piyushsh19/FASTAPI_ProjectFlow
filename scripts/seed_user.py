from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import User


def seed_user():
    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where(
                User.email == "admin@projectflow.local"
            )
        )

        if existing_user:
            print("Development user already exists.")
            return

        user = User(
            name="ProjectFlow Admin",
            email="admin@projectflow.local",
            password_hash="TEMPORARY-NOT-A-REAL-PASSWORD-HASH",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Development user created. ID: {user.id}")


if __name__ == "__main__":
    seed_user()