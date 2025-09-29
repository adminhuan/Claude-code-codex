#!/bin/bash
# AI规则遵守MCP工具一键安装脚本

set -e

echo "🚀 AI规则遵守MCP工具一键安装脚本"
echo "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "=" "="

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3检查通过"

# 检查pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip未安装，请先安装pip"
    exit 1
fi

echo "✅ pip检查通过"

# 安装方式选择
echo ""
echo "请选择安装方式:"
echo "1. 从PyPI安装 (推荐)"
echo "2. 从GitHub源码安装"
echo "3. 本地开发安装"
read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "📦 从PyPI安装..."
        pip install ai-rule-mcp-server
        ;;
    2)
        echo "📥 从GitHub克隆..."
        if [ -d "Claude-code-codex" ]; then
            rm -rf Claude-code-codex
        fi
        git clone https://github.com/adminhuan/Claude-code-codex.git
        cd Claude-code-codex
        pip install -e .
        ;;
    3)
        echo "🔧 本地开发安装..."
        pip install -e .
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo "✅ 包安装完成"

# 运行配置
echo ""
echo "🔧 配置MCP服务器..."
ai-rule-mcp install

echo ""
echo "🎉 安装完成!"
echo ""
echo "📝 使用说明:"
echo "1. 重启Claude Code"
echo "2. 试试说: '请提醒我Python编码规范'"
echo "3. 或者说: '切换到Plan模式'"
echo ""
echo "🛠️ 管理命令:"
echo "• ai-rule-mcp status    - 查看状态"
echo "• ai-rule-mcp start     - 启动服务器"
echo "• ai-rule-mcp uninstall - 卸载"
echo ""
echo "📚 更多信息: https://github.com/adminhuan/Claude-code-codex"