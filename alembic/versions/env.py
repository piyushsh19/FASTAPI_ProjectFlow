from app.core.config import settings
from app.db.base import Base

config.set_main_option(
    "sqlalchemy.url",
    settings.database_url.replace("%", "%%")
)

target_metadata = Base.metadata