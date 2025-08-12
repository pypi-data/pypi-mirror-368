# Requests-Keeper

一个功能强大的HTTP会话持久化工具，支持会话保存、自动重试、请求拦截器等功能。

## 特性

- 🔄 **会话持久化** - 自动保存和恢复HTTP会话，包括cookies、headers等
- ⚡ **自动重试** - 内置智能重试机制，处理网络波动和服务器错误
- 🎯 **拦截器系统** - 支持请求和响应拦截器，方便添加认证、日志等功能
- 📝 **便捷的JSON API** - 提供get_json、post_json等便捷方法
- 🛡️ **错误处理** - 完善的错误处理和日志记录
- ⏱️ **频率限制** - 内置请求频率控制
- 🔧 **高度可配置** - 支持自定义超时、重试策略等

## 安装

```bash
pip install reqkeeper
```

## 快速开始

### 基本使用

```python
from reqkeeper import PersistentSession

# 创建持久化会话
with PersistentSession() as session:
    # GET请求
    response = session.get('https://httpbin.org/get')
    print(response.json())
    
    # POST请求
    data = session.post_json('https://httpbin.org/post', json={'key': 'value'})
    print(data)
    
    # 会话会自动保存cookies等信息
```

### 添加拦截器

```python
from reqkeeper import PersistentSession, auth_interceptor, logging_request_interceptor

with PersistentSession() as session:
    # 添加认证拦截器
    session.add_request_interceptor(auth_interceptor("your_token_here"))
    
    # 添加日志拦截器
    session.add_request_interceptor(logging_request_interceptor)
    
    # 现在所有请求都会自动添加认证头和日志
    response = session.get('https://api.example.com/protected')
```

### 自定义配置

```python
from reqkeeper import PersistentSession

session = PersistentSession(
    session_file='./my_session.pkl',  # 自定义会话文件位置
    retries=5,                        # 重试次数
    timeout=60,                       # 请求超时
    auto_save=True                    # 自动保存会话
)
```

## 内置拦截器

### 认证拦截器
```python
from reqkeeper import auth_interceptor

# Bearer token
auth = auth_interceptor("your_token_here")
session.add_request_interceptor(auth)

# API Key
api_auth = auth_interceptor("your_api_key", auth_type="ApiKey")
session.add_request_interceptor(api_auth)
```

### 日志拦截器
```python
from reqkeeper import logging_request_interceptor, logging_response_interceptor

session.add_request_interceptor(logging_request_interceptor)
session.add_response_interceptor(logging_response_interceptor)
```

### 频率限制拦截器
```python
from reqkeeper import rate_limit_interceptor

# 每秒最多2个请求
rate_limiter = rate_limit_interceptor(2.0)
session.add_request_interceptor(rate_limiter)
```

### 错误处理拦截器
```python
from reqkeeper import error_handling_interceptor

session.add_response_interceptor(error_handling_interceptor)
```

## 完整示例

```python
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
logging.basicConfig(level=logging.INFO)

def main():
    with PersistentSession(
        session_file='./api_session.pkl',
        retries=3,
        timeout=30,
        auto_save=True
    ) as session:
        
        # 添加各种拦截器
        session.add_request_interceptor(logging_request_interceptor)
        session.add_request_interceptor(rate_limit_interceptor(2.0))  # 每秒2个请求
        
        session.add_response_interceptor(logging_response_interceptor)
        session.add_response_interceptor(error_handling_interceptor)
        
        # 如果需要认证
        # session.add_request_interceptor(auth_interceptor("your_token"))
        
        try:
            # API调用
            user_data = session.get_json('https://api.example.com/user/profile')
            print(f"用户数据: {user_data}")
            
            # 提交数据
            result = session.post_json(
                'https://api.example.com/data',
                json={'message': 'Hello from persistent-requests!'}
            )
            print(f"提交结果: {result}")
            
            print(f"会话保存在: {session.get_session_file_path()}")
            
        except Exception as e:
            print(f"请求失败: {e}")

if __name__ == "__main__":
    main()
```

## API参考

### Reqkeeper

主要的会话类，提供持久化HTTP请求功能。

#### 构造函数

```python
reqkeeper(
    session_file: Optional[str] = None,
    retries: int = 3,
    backoff_factor: float = 0.3,
    timeout: int = 30,
    auto_save: bool = True
)
```

- `session_file`: 会话保存文件路径，默认为系统临时目录
- `retries`: 失败重试次数
- `backoff_factor`: 重试延迟倍数
- `timeout`: 请求超时时间（秒）
- `auto_save`: 是否在每次请求后自动保存会话

#### 请求方法

- `get(url, params=None, **kwargs)` - GET请求
- `post(url, data=None, json=None, **kwargs)` - POST请求
- `put(url, data=None, json=None, **kwargs)` - PUT请求
- `patch(url, data=None, json=None, **kwargs)` - PATCH请求
- `delete(url, **kwargs)` - DELETE请求
- `head(url, **kwargs)` - HEAD请求
- `options(url, **kwargs)` - OPTIONS请求
- `request(method, url, **kwargs)` - 通用请求方法

#### JSON便捷方法

- `get_json(url, params=None, **kwargs)` - GET请求并返回JSON
- `post_json(url, data=None, json=None, **kwargs)` - POST请求并返回JSON
- `request_json(method, url, **kwargs)` - 通用请求并返回JSON

#### 拦截器管理

- `add_request_interceptor(interceptor)` - 添加请求拦截器
- `add_response_interceptor(interceptor)` - 添加响应拦截器
- `remove_request_interceptor(interceptor)` - 移除请求拦截器
- `remove_response_interceptor(interceptor)` - 移除响应拦截器
- `clear_interceptors()` - 清除所有拦截器

#### 会话管理

- `save_session()` - 手动保存会话
- `get_session_file_path()` - 获取会话文件路径
- `close()` - 关闭会话

## 许可证

MIT License

## 更新日志

### v1.0.0

- 初始版本发布
- 支持会话持久化
- 内置重试机制
- 拦截器系统
- JSON便捷方法
- 完善的错误处理

## 贡献

欢迎提交Issue和Pull Request！

## 作者

Flikify - reqkeeper@92coco.cn

项目链接: https://github.com/Flikify/reqkeeper