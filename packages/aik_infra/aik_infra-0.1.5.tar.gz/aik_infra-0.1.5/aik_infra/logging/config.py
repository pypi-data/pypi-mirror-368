import os
import sys
import uuid
import logging
from contextvars import ContextVar
from typing import Any, Dict

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars

# Context variables для хранения контекста запроса
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")
instance_id_var: ContextVar[str] = ContextVar("instance_id", default="")

# Генерируем уникальный ID для экземпляра сервиса
INSTANCE_ID = str(uuid.uuid4())[:8]


def get_trace_id() -> str:
    """Получить текущий trace_id из контекста"""
    return trace_id_var.get()


def get_user_id() -> str:
    """Получить текущий user_id из контекста"""
    return user_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """Установить trace_id в контекст"""
    trace_id_var.set(trace_id)


def set_user_id(user_id: str) -> None:
    """Установить user_id в контекст"""
    user_id_var.set(user_id)


def clear_context() -> None:
    """Очистить весь контекст"""
    clear_contextvars()


def configure_logging(log_level: int = logging.INFO) -> None:
    """Настроить структурированное логирование"""
    
    # Настройка базового логирования
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        stream=sys.stdout
    )
    
    # Настройка процессоров structlog
    processors = [
        # Добавляем контекстные переменные
        structlog.contextvars.merge_contextvars,
        
        # Добавляем временную метку
        structlog.processors.TimeStamper(fmt="iso"),
        
        # Добавляем уровень логирования
        structlog.stdlib.add_log_level,
        
        # Добавляем информацию о стеке
        structlog.processors.StackInfoRenderer(),
        
        # Добавляем информацию об исключениях
        structlog.processors.format_exc_info,
        
        # Добавляем service и instance_id
        _add_service_info,
        
        # Рендерим в JSON
        structlog.processors.JSONRenderer()
    ]
    
    # Конфигурируем structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def _add_service_info(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Добавить информацию о сервисе в каждый лог"""
    # Определяем имя сервиса из переменной окружения или по умолчанию
    service_name = os.getenv("SERVICE_NAME", "unknown_service")
    event_dict["service"] = service_name
    event_dict["instance_id"] = INSTANCE_ID
    
    # Добавляем trace_id и user_id если они есть в контексте
    trace_id = get_trace_id()
    if trace_id:
        event_dict["trace_id"] = trace_id
    
    user_id = get_user_id()
    if user_id:
        event_dict["user_id"] = user_id
    
    return event_dict


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """Получить структурированный логгер"""
    if name is None:
        name = __name__
    return structlog.get_logger(name) 