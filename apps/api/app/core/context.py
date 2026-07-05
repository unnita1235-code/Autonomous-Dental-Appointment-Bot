from contextvars import ContextVar
from uuid import uuid4

request_id_var: ContextVar[str] = ContextVar("request_id", default="")
task_id_var: ContextVar[str] = ContextVar("task_id", default="")


def get_request_id() -> str:
    return request_id_var.get()


def get_task_id() -> str:
    return task_id_var.get()


def generate_request_id() -> str:
    return uuid4().hex


__all__ = ["get_request_id", "get_task_id", "generate_request_id", "request_id_var", "task_id_var"]
