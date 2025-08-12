"""预定义的请求和响应拦截器"""

import time
import logging
from typing import Callable, Dict, Tuple
from requests import Response

logger = logging.getLogger(__name__)


def auth_interceptor(token: str, auth_type: str = "Bearer") -> Callable:
    """认证拦截器工厂函数

    Args:
        token: 认证令牌
        auth_type: 认证类型，默认为Bearer
    """

    def interceptor(method: str, url: str, kwargs: Dict) -> Tuple[str, str, Dict]:
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers']['Authorization'] = f'{auth_type} {token}'
        logger.debug(f"已添加认证头到请求: {method.upper()} {url}")
        return method, url, kwargs

    return interceptor


def logging_request_interceptor(method: str, url: str, kwargs: Dict) -> Tuple[str, str, Dict]:
    """请求日志拦截器"""
    logger.info(f"🚀 发起请求: {method.upper()} {url}")
    if kwargs.get('params'):
        logger.debug(f"📝 请求参数: {kwargs['params']}")
    if kwargs.get('json'):
        logger.debug(f"📋 请求JSON: {kwargs['json']}")
    return method, url, kwargs


def logging_response_interceptor(response: Response) -> Response:
    """响应日志拦截器"""
    status_icon = "✅" if response.status_code < 400 else "❌"
    logger.info(f"{status_icon} 响应状态: {response.status_code} - {response.url}")

    if response.headers.get('Content-Type', '').startswith('application/json'):
        try:
            json_data = response.json()
            logger.debug(f"📤 响应JSON: {json_data}")
        except ValueError:
            pass

    return response


def error_handling_interceptor(response: Response) -> Response:
    """错误处理拦截器"""
    if response.status_code >= 400:
        error_messages = {
            401: "🔐 认证失败，需要重新登录",
            403: "🚫 权限不足",
            404: "🔍 资源未找到",
            429: "⏰ 请求频率过高，请稍后重试",
            500: "💥 服务器内部错误"
        }

        message = error_messages.get(response.status_code, f"请求失败: {response.status_code}")
        logger.error(f"{message} - {response.text[:200]}")

    return response


def rate_limit_interceptor(requests_per_second: float = 1.0) -> Callable:
    """请求频率限制拦截器工厂函数

    Args:
        requests_per_second: 每秒允许的请求数
    """
    last_request_time = {'time': 0}
    min_interval = 1.0 / requests_per_second

    def interceptor(method: str, url: str, kwargs: Dict) -> Tuple[str, str, Dict]:
        current_time = time.time()
        time_since_last = current_time - last_request_time['time']

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"⏳ 频率限制：等待 {sleep_time:.2f} 秒")
            time.sleep(sleep_time)

        last_request_time['time'] = time.time()
        return method, url, kwargs

    return interceptor


def retry_on_failure_interceptor(max_retries: int = 3, delay: float = 1.0) -> Callable:
    """失败重试拦截器工厂函数

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟时间
    """

    def interceptor(response: Response) -> Response:
        if response.status_code >= 500:
            logger.warning(f"⚠️ 服务器错误 {response.status_code}，可能需要重试")
        return response

    return interceptor