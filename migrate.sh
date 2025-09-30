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
OLD_CONFIG_FOUND=false

if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✅ 发现配置文件: $CLAUDE_CONFIG"

    if grep -q "ai-rule-mcp-server" "$CLAUDE_CONFIG"; then
        echo "⚠️  发现旧配置 ai-rule-mcp-server"
        OLD_CONFIG_FOUND=true

        echo ""
        read -p "是否自动删除旧配置？(y/n): " remove_config
        if [ "$remove_config" = "y" ] || [ "$remove_config" = "Y" ]; then
            # 备份配置文件
            cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup"
            echo "✅ 已备份配置文件到: $CLAUDE_CONFIG.backup"

            # 使用sed删除旧配置（简单方式，可能不完美）
            echo "⚠️  请手动编辑配置文件删除旧配置："
            echo "  $CLAUDE_CONFIG"
            echo ""
            read -p "删除完成后，按回车键继续..."
        else
            echo ""
            echo "⚠️  请手动编辑配置文件删除旧配置："
            echo "  $CLAUDE_CONFIG"
            echo ""
            read -p "删除完成后，按回车键继续..."
        fi
    else
        echo "✅ 配置文件中未发现旧配置"
    fi
else
    echo "ℹ️  配置文件不存在"
fi

# 3. 安装新版本
echo ""
echo "📦 安装新版本 smart-search-mcp..."
echo ""

# 自动尝试使用Claude MCP命令
if command -v claude &> /dev/null; then
    echo "✅ 检测到 claude 命令，使用 Claude MCP 安装"

    # 检查是否已经存在
    if claude mcp list 2>/dev/null | grep -q "smart-search-mcp"; then
        echo "ℹ️  检测到 smart-search-mcp 已存在"
        read -p "是否重新配置？(y/n): " reconfig
        if [ "$reconfig" = "y" ] || [ "$reconfig" = "Y" ]; then
            echo "🔄 删除旧配置..."
            claude mcp remove smart-search-mcp 2>/dev/null || true
            echo "📦 添加新配置..."
            claude mcp add smart-search-mcp npx smart-search-mcp
        else
            echo "⏭️  跳过配置"
        fi
    else
        claude mcp add smart-search-mcp npx smart-search-mcp
    fi

    echo ""
    echo "✅ MCP服务器配置完成！"
else
    echo "ℹ️  未找到 claude 命令，使用全局安装"
    npm install -g smart-search-mcp
    echo ""
    echo "✅ 全局安装完成！"
    echo ""
    echo "📝 请运行以下命令配置："
    echo "claude mcp add smart-search-mcp npx smart-search-mcp"
fi

echo ""
echo "🎉 迁移完成！"
echo ""
echo "📚 下一步："
echo "1. 重启 Claude Code"
echo "2. 试试说: '搜索React Hooks最佳实践'"
echo "3. 或者说: '搜索微信小程序一键登录'"
echo ""
echo "📖 更多信息: https://github.com/adminhuan/smart-search-mcp"