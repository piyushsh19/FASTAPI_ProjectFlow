import logging
import logging.config

from app.core.request_context import RequestIdFilter


def setup_logging(
    debug: bool = False,
    log_level: str | None = None,
) -> None:
    level = (log_level or ("DEBUG" if debug else "INFO")).upper()

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {
                "()": RequestIdFilter,
            },
        },
        "formatters": {
            "standard": {
                "format": (
                    "%(asctime)s | %(levelname)s | "
                    "%(name)s | request_id=%(request_id)s | "
                    "%(message)s"
                ),
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "filters": ["request_id"],
                "level": level,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    })