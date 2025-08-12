"""
Persistent Requests - HTTP会话持久化工具

一个功能强大的HTTP会话管理库，支持会话持久化、请求重试、拦截器等功能。
"""

from .core import PersistentSession, SessionManager, InterceptorManager
from .interceptors import (
    auth_interceptor,
    logging_request_interceptor,
    logging_response_interceptor,
    error_handling_interceptor,
    rate_limit_interceptor,
    retry_on_failure_interceptor
)
from .version import __version__

__all__ = [
    'PersistentSession',
    'SessionManager', 
    'InterceptorManager',
    'auth_interceptor',
    'logging_request_interceptor',
    'logging_response_interceptor', 
    'error_handling_interceptor',
    'rate_limit_interceptor',
    'retry_on_failure_interceptor',
    '__version__'
]
