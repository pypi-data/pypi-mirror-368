from setuptools import setup, find_packages

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# 读取版本信息
version = {}
with open("reqkeeper/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="reqkeeper",
    version=version['__version__'],
    author="Flikify",
    author_email="reqkeeper@92coco.cn",
    description="一个功能强大的HTTP会话持久化工具，支持会话保存、自动重试、拦截器等功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Flikify/reqkeeper",
    project_urls={
        "Bug Tracker": "https://github.com/Flikify/reqkeeper/issues",
        "Documentation": "https://github.com/Flikify/reqkeeper#readme",
        "Source Code": "https://github.com/Flikify/reqkeeper",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Session",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.812",
            "pre-commit>=2.15",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "responses>=0.18",
            "requests-mock>=1.9",
        ]
    },
    keywords="http requests session persistent cookies retry interceptor",
    include_package_data=True,
    zip_safe=False,
)