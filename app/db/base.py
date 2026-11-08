from app.db.base_class import Base

# Import all models so Alembic can discover them.
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.notification import Notification