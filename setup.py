"""
AI规则遵守MCP工具安装脚本
支持全局安装和一键配置
"""
from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "AI规则遵守MCP工具服务器"

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-rule-mcp-server",
    version="0.1.0",
    author="AI Community",
    description="AI规则遵守MCP工具服务器 - 38个AI工具函数",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adminhuan/Claude-code-codex",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-rule-mcp=ai_duet.cli:main",
            "ai-rule-mcp-server=ai_duet.cli:server",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_duet": ["mcp_server.py", "mcp_config.json"],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    }
)