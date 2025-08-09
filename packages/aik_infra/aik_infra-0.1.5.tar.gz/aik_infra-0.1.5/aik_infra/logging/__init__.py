from .config import configure_logging, get_logger, set_trace_id, set_user_id, clear_context, get_trace_id, get_user_id
from structlog import get_logger as structlog_get_logger

configure_logging()
log = structlog_get_logger()

__all__ = [
    "configure_logging",
    "get_logger", 
    "log",
    "set_trace_id",
    "set_user_id", 
    "clear_context",
    "get_trace_id",
    "get_user_id"
] 