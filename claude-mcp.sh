#!/bin/bash
# Claude Code MCP服务器启动脚本

# 设置工作目录为脚本所在目录
cd "$(dirname "$0")"

# 确保依赖已安装
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install ai-rule-mcp-server@latest
fi

# 启动MCP服务器
echo "🚀 Starting AI Rule MCP Server..."
npx ai-rule-mcp-server@latest