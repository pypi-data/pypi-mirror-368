"""
基本使用示例
"""

import logging
from reqkeeper import (
    PersistentSession,
    auth_interceptor,
    logging_request_interceptor,
    logging_response_interceptor,
    error_handling_interceptor,
    rate_limit_interceptor
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def basic_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")

    with PersistentSession() as session:
        # GET请求
        response = session.get('https://httpbin.org/get', params={'key': 'value'})
        print(f"GET状态码: {response.status_code}")

        # JSON GET请求
        json_data = session.get_json('https://httpbin.org/get', params={'test': 'json'})
        print(f"JSON数据: {json_data}")

        # POST请求
        post_result = session.post_json(
            'https://httpbin.org/post',
            json={'message': 'Hello from persistent-requests!'}
        )
        print(f"POST结果: {post_result}")


def interceptors_example():
    """拦截器示例"""
    print("\n=== 拦截器示例 ===")

    with PersistentSession() as session:
        # 添加日志拦截器
        session.add_request_interceptor(logging_request_interceptor)
        session.add_response_interceptor(logging_response_interceptor)
        session.add_response_interceptor(error_handling_interceptor)

        # 添加频率限制（每秒1个请求）
        session.add_request_interceptor(rate_limit_interceptor(1.0))

        # 测试请求
        for i in range(3):
            json_data = session.get_json(f'https://httpbin.org/get?test={i}')
            print(f"请求 {i + 1} 完成")


def auth_example():
    """认证示例"""
    print("\n=== 认证示例 ===")

    with PersistentSession() as session:
        # 添加认证拦截器（模拟token）
        session.add_request_interceptor(auth_interceptor("fake_token_12345"))
        session.add_request_interceptor(logging_request_interceptor)

        # 带认证的请求
        json_data = session.get_json('https://httpbin.org/bearer')
        print(f"认证请求结果: {json_data}")


def persistent_session_example():
    """会话持久化示例"""
    print("\n=== 会话持久化示例 ===")

    # 创建会话并设置cookie
    with PersistentSession(session_file='./demo_session.pkl') as session:
        # 设置cookie
        session.get('https://httpbin.org/cookies/set/demo_cookie/persistent_value')
        print(f"会话文件保存在: {session.get_session_file_path()}")

    print("重新加载会话...")

    # 重新加载会话，验证cookie是否持久化
    with PersistentSession(session_file='./demo_session.pkl') as session:
        cookie_data = session.get_json('https://httpbin.org/cookies')
        print(f"持久化的Cookie: {cookie_data}")


def error_handling_example():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")

    with PersistentSession() as session:
        session.add_response_interceptor(error_handling_interceptor)

        # 测试404错误
        try:
            response = session.get('https://httpbin.org/status/404')
            print(f"404请求状态码: {response.status_code}")
        except Exception as e:
            print(f"请求异常: {e}")

        # 测试500错误
        try:
            response = session.get('https://httpbin.org/status/500')
            print(f"500请求状态码: {response.status_code}")
        except Exception as e:
            print(f"请求异常: {e}")


if __name__ == "__main__":
    basic_example()
    interceptors_example()
    auth_example()
    persistent_session_example()
    error_handling_example()
