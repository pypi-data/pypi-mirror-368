import os
import pickle
import tempfile
import time
import logging
from pathlib import Path
from typing import Callable, List, Optional, Dict, Any, Tuple, Union

import requests
from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# 使用标准logging
logger = logging.getLogger(__name__)


class InterceptorManager:
    """拦截器管理器，负责管理和执行请求/响应拦截器"""

    def __init__(self):
        self.request_interceptors: List[Callable] = []
        self.response_interceptors: List[Callable] = []

    def add_request_interceptor(self, interceptor: Callable[[str, str, Dict], Tuple[str, str, Dict]]) -> None:
        """添加请求拦截器

        Args:
            interceptor: 拦截器函数，签名为 (method, url, kwargs) -> (method, url, kwargs)
        """
        if interceptor not in self.request_interceptors:
            self.request_interceptors.append(interceptor)

    def add_response_interceptor(self, interceptor: Callable[[Response], Response]) -> None:
        """添加响应拦截器

        Args:
            interceptor: 拦截器函数，签名为 (response) -> response
        """
        if interceptor not in self.response_interceptors:
            self.response_interceptors.append(interceptor)

    def remove_request_interceptor(self, interceptor: Callable) -> bool:
        """移除请求拦截器

        Returns:
            bool: 是否成功移除
        """
        try:
            self.request_interceptors.remove(interceptor)
            return True
        except ValueError:
            return False

    def remove_response_interceptor(self, interceptor: Callable) -> bool:
        """移除响应拦截器

        Returns:
            bool: 是否成功移除
        """
        try:
            self.response_interceptors.remove(interceptor)
            return True
        except ValueError:
            return False

    def clear_request_interceptors(self) -> None:
        """清除所有请求拦截器"""
        self.request_interceptors.clear()

    def clear_response_interceptors(self) -> None:
        """清除所有响应拦截器"""
        self.response_interceptors.clear()

    def apply_request_interceptors(self, method: str, url: str, **kwargs) -> Tuple[str, str, Dict]:
        """应用所有请求拦截器"""
        for interceptor in self.request_interceptors:
            try:
                method, url, kwargs = interceptor(method, url, kwargs)
            except Exception as e:
                logger.error(f"请求拦截器 {interceptor.__name__} 执行失败: {e}")
                raise
        return method, url, kwargs

    def apply_response_interceptors(self, response: Response) -> Response:
        """应用所有响应拦截器"""
        for interceptor in self.response_interceptors:
            try:
                response = interceptor(response)
            except Exception as e:
                logger.error(f"响应拦截器 {interceptor.__name__} 执行失败: {e}")
                raise
        return response


class SessionManager:
    """会话管理器，负责会话的持久化存储和加载"""

    def __init__(self, session_file: Optional[str] = None):
        if session_file is None:
            # 默认存储在系统临时目录
            temp_dir = Path(tempfile.gettempdir())
            session_file = temp_dir / "persistent_session.pkl"

        self.session_file = Path(session_file)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

    def load_session(self) -> Session:
        """加载会话，如果文件不存在或加载失败则创建新会话"""
        if self.session_file.exists():
            try:
                with open(self.session_file, "rb") as f:
                    session = pickle.load(f)
                    logger.info(f"已加载保存的会话: {self.session_file}")
                    return session
            except Exception as e:
                logger.warning(f"加载会话失败，创建新会话: {e}")

        logger.info("创建新会话")
        return requests.Session()

    def save_session(self, session: Session) -> bool:
        """保存会话到文件

        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.session_file, "wb") as f:
                pickle.dump(session, f)
                logger.debug(f"会话已保存到: {self.session_file}")
                return True
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
            return False


class PersistentSession:
    """持久化HTTP会话工具类

    提供HTTP会话的持久化存储、自动重试、拦截器等功能。

    Examples:
        >>> with PersistentSession() as session:
        ...     response = session.get('https://httpbin.org/get')
        ...     json_data = session.get_json('https://httpbin.org/json')
    """

    def __init__(
            self,
            session_file: Optional[str] = None,
            retries: int = 3,
            backoff_factor: float = 0.3,
            timeout: int = 30,
            auto_save: bool = True
    ):
        """初始化持久化会话

        Args:
            session_file: 会话文件路径，默认存储在系统临时目录
            retries: 重试次数
            backoff_factor: 重试间隔因子
            timeout: 请求超时时间
            auto_save: 是否自动保存会话
        """
        self.session_manager = SessionManager(session_file)
        self.interceptor_manager = InterceptorManager()
        self.auto_save = auto_save
        self.timeout = timeout

        # 加载或创建会话
        self.session = self.session_manager.load_session()

        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'persistent-requests/1.0.0 (https://github.com/your-username/persistent-requests)'
        })

        # 配置重试机制
        self._setup_retry_strategy(retries, backoff_factor)

    def _setup_retry_strategy(self, retries: int, backoff_factor: float) -> None:
        """设置重试策略"""
        retry_strategy = Retry(
            total=retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "PATCH"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _make_request(self, method: str, url: str, **kwargs) -> Response:
        """内部请求方法"""
        # 设置默认超时
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        # 应用请求拦截器
        method, url, kwargs = self.interceptor_manager.apply_request_interceptors(method, url, **kwargs)

        logger.debug(f"发起请求: {method.upper()} {url}")

        # 发起请求
        response = self.session.request(method, url, **kwargs)

        # 应用响应拦截器
        response = self.interceptor_manager.apply_response_interceptors(response)

        # 自动保存会话
        if self.auto_save:
            self.save_session()

        return response

    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> Response:
        """发起GET请求"""
        return self._make_request('GET', url, params=params, **kwargs)

    def post(self, url: str, data: Optional[Union[Dict, str]] = None,
             json: Optional[Dict] = None, **kwargs) -> Response:
        """发起POST请求"""
        return self._make_request('POST', url, data=data, json=json, **kwargs)

    def put(self, url: str, data: Optional[Union[Dict, str]] = None,
            json: Optional[Dict] = None, **kwargs) -> Response:
        """发起PUT请求"""
        return self._make_request('PUT', url, data=data, json=json, **kwargs)

    def patch(self, url: str, data: Optional[Union[Dict, str]] = None,
              json: Optional[Dict] = None, **kwargs) -> Response:
        """发起PATCH请求"""
        return self._make_request('PATCH', url, data=data, json=json, **kwargs)

    def delete(self, url: str, **kwargs) -> Response:
        """发起DELETE请求"""
        return self._make_request('DELETE', url, **kwargs)

    def head(self, url: str, **kwargs) -> Response:
        """发起HEAD请求"""
        return self._make_request('HEAD', url, **kwargs)

    def options(self, url: str, **kwargs) -> Response:
        """发起OPTIONS请求"""
        return self._make_request('OPTIONS', url, **kwargs)

    def request(self, method: str, url: str, **kwargs) -> Response:
        """通用请求方法"""
        return self._make_request(method, url, **kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type((requests.RequestException,))
    )
    def get_json(self, url: str, params: Optional[Dict] = None, **kwargs) -> Optional[Dict]:
        """发起GET请求并返回JSON数据"""
        response = self.get(url, params=params, **kwargs)
        return self._extract_json(response)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type((requests.RequestException,))
    )
    def post_json(self, url: str, data: Optional[Union[Dict, str]] = None,
                  json: Optional[Dict] = None, **kwargs) -> Optional[Dict]:
        """发起POST请求并返回JSON数据"""
        response = self.post(url, data=data, json=json, **kwargs)
        return self._extract_json(response)

    def request_json(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """通用请求方法，返回JSON数据"""
        response = self._make_request(method, url, **kwargs)
        return self._extract_json(response)

    def _extract_json(self, response: Response) -> Optional[Dict]:
        """从响应中提取JSON数据"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP错误: {e}")
            return None
        except ValueError as e:
            logger.error(f"响应不是有效的JSON格式: {e}")
            return None

    # 拦截器管理方法
    def add_request_interceptor(self, interceptor: Callable[[str, str, Dict], Tuple[str, str, Dict]]) -> None:
        """添加请求拦截器"""
        self.interceptor_manager.add_request_interceptor(interceptor)

    def add_response_interceptor(self, interceptor: Callable[[Response], Response]) -> None:
        """添加响应拦截器"""
        self.interceptor_manager.add_response_interceptor(interceptor)

    def remove_request_interceptor(self, interceptor: Callable) -> bool:
        """移除请求拦截器"""
        return self.interceptor_manager.remove_request_interceptor(interceptor)

    def remove_response_interceptor(self, interceptor: Callable) -> bool:
        """移除响应拦截器"""
        return self.interceptor_manager.remove_response_interceptor(interceptor)

    def clear_interceptors(self) -> None:
        """清除所有拦截器"""
        self.interceptor_manager.clear_request_interceptors()
        self.interceptor_manager.clear_response_interceptors()

    # 会话管理方法
    def save_session(self) -> bool:
        """手动保存会话"""
        return self.session_manager.save_session(self.session)

    def get_session_file_path(self) -> Path:
        """获取会话文件路径"""
        return self.session_manager.session_file

    def close(self) -> None:
        """关闭会话并保存"""
        self.save_session()
        self.session.close()
        logger.info("会话已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()