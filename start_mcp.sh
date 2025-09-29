#!/bin/bash
# AI规则遵守MCP服务器启动脚本

# 激活虚拟环境
source ./venv/bin/activate

# 安装依赖（如果需要）
pip install -r requirements.txt 2>/dev/null || true

# 启动MCP服务器
python mcp_server.py