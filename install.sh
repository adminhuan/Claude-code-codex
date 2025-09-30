#!/bin/bash
# Smart Search MCP 一键安装脚本

set -e

echo "🚀 Smart Search MCP 一键安装脚本"
echo "=================================================================="

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js (>=18.0.0)"
    echo "📥 访问 https://nodejs.org 下载安装"
    exit 1
fi

echo "✅ Node.js检查通过 ($(node -v))"

# 检查npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装"
    exit 1
fi

echo "✅ npm检查通过 ($(npm -v))"

# 安装方式选择
echo ""
echo "请选择安装方式:"
echo "1. 全局安装 (推荐)"
echo "2. 从GitHub源码安装"
read -p "请输入选择 (1-2): " choice

case $choice in
    1)
        echo "📦 全局安装 smart-search-mcp..."
        npm install -g smart-search-mcp
        echo "✅ 安装完成"
        ;;
    2)
        echo "📥 从GitHub克隆..."
        if [ -d "Claude-code-codex" ]; then
            rm -rf Claude-code-codex
        fi
        git clone https://github.com/adminhuan/Claude-code-codex.git
        cd Claude-code-codex
        npm install
        npm link
        echo "✅ 安装完成"
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 安装完成!"
echo ""
echo "📝 配置Claude Code:"
echo "在 Claude Code 的 MCP 配置中添加:"
echo '{'
echo '  "mcpServers": {'
echo '    "smart-search-mcp": {'
echo '      "command": "npx",'
echo '      "args": ["smart-search-mcp@latest"]'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "📚 使用说明:"
echo "1. 重启 Claude Code"
echo "2. 试试说: '搜索React Hooks最佳实践'"
echo "3. 或者说: '搜索微信小程序一键登录'"
echo ""
echo "🛠️ 管理命令:"
echo "• npm list -g smart-search-mcp  - 查看版本"
echo "• npm update -g smart-search-mcp - 更新"
echo "• npm uninstall -g smart-search-mcp - 卸载"
echo ""
echo "📚 更多信息: https://github.com/adminhuan/Claude-code-codex"