#!/bin/bash
# Smart Search MCP 迁移脚本
# 从 ai-rule-mcp-server 升级到 smart-search-mcp

set -e

echo "🔄 Smart Search MCP 迁移脚本"
echo "=================================================="
echo ""
echo "此脚本将帮助你从旧版本 ai-rule-mcp-server 升级到新版本 smart-search-mcp"
echo ""

# 1. 检查是否安装了旧版本
echo "📋 检查旧版本..."
if npm list -g ai-rule-mcp-server &> /dev/null; then
    echo "✅ 发现旧版本 ai-rule-mcp-server"

    read -p "是否卸载旧版本？(y/n): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo "🗑️  卸载旧版本..."
        npm uninstall -g ai-rule-mcp-server
        echo "✅ 旧版本已卸载"
    fi
else
    echo "ℹ️  未发现全局安装的旧版本"
fi

# 2. 清理旧配置
echo ""
echo "📋 检查配置文件..."

CLAUDE_CONFIG="$HOME/.claude.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✅ 发现配置文件: $CLAUDE_CONFIG"

    if grep -q "ai-rule-mcp-server" "$CLAUDE_CONFIG"; then
        echo "⚠️  发现旧配置 ai-rule-mcp-server"
        echo ""
        echo "请手动编辑配置文件删除旧配置："
        echo "  $CLAUDE_CONFIG"
        echo ""
        read -p "按回车键继续..."
    else
        echo "✅ 配置文件中未发现旧配置"
    fi
else
    echo "ℹ️  配置文件不存在"
fi

# 3. 安装新版本
echo ""
echo "📦 安装新版本 smart-search-mcp..."
read -p "选择安装方式 (1=全局安装, 2=Claude MCP命令): " method

case $method in
    1)
        npm install -g smart-search-mcp
        echo ""
        echo "✅ 全局安装完成！"
        echo ""
        echo "📝 配置方法："
        echo "运行: claude mcp add smart-search-mcp npx smart-search-mcp"
        ;;
    2)
        if command -v claude &> /dev/null; then
            claude mcp add smart-search-mcp npx smart-search-mcp
            echo ""
            echo "✅ MCP服务器已添加！"
        else
            echo "❌ 未找到 claude 命令"
            echo "请确保 Claude Code 已安装并配置PATH"
            echo ""
            echo "或手动安装："
            echo "  npm install -g smart-search-mcp"
            exit 1
        fi
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 迁移完成！"
echo ""
echo "📚 下一步："
echo "1. 重启 Claude Code"
echo "2. 试试说: '搜索React Hooks最佳实践'"
echo "3. 或者说: '搜索微信小程序一键登录'"
echo ""
echo "📖 更多信息: https://github.com/adminhuan/Claude-code-codex"