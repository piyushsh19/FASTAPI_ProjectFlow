from contextvars import ContextVar
import logging


request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)


class RequestIdFilter(logging.Filter):
    """Attach the current request ID to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_context.get()
        return True