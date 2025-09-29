#!/bin/bash
# AI规则遵守MCP工具 - 项目安装脚本

echo "🎯 AI规则遵守MCP工具项目安装器"
echo "=================================="

# 检查是否提供了项目路径
if [ "$1" != "" ]; then
    PROJECT_DIR="$1"
else
    PROJECT_DIR="$(pwd)"
fi

echo "📁 项目目录: $PROJECT_DIR"

# 检查目录是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 目录不存在: $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR"

# 创建.mcp.json配置文件
echo "⚙️ 创建MCP配置文件..."
cat > .mcp.json << 'EOF'
{
  "servers": {
    "ai-rule-mcp": {
      "command": "npx",
      "args": ["ai-rule-mcp-server@latest"],
      "description": "AI规则遵守MCP工具 - 38个智能规则提醒、多模式工作流、AI协作功能"
    }
  }
}
EOF

echo "✅ 已创建 .mcp.json 配置文件"

# 检查Claude settings
CLAUDE_SETTINGS="$HOME/.claude/settings.json"
if [ ! -f "$CLAUDE_SETTINGS" ]; then
    echo "⚠️ 未找到Claude settings文件，需要手动配置"
    echo "📝 请在 $CLAUDE_SETTINGS 中添加:"
    echo '   "enableAllProjectMcpServers": true'
else
    echo "✅ Claude settings文件存在"
fi

echo ""
echo "🎉 安装完成!"
echo ""
echo "📝 使用说明:"
echo "1. 重启Claude Code"
echo "2. 在当前项目目录中运行Claude Code"
echo "3. 试试说: '请提醒我Python编码规范'"
echo "4. 或者说: '切换到Plan模式'"
echo ""
echo "🛠️ 可用工具包括:"
echo "   • ai_rule_reminder - 智能规则提醒"
echo "   • ai_switch_mode - 模式切换"
echo "   • ai_create_plan - 创建开发计划"
echo "   • ai_create_pr - 创建PR审查"
echo "   • ai_check_compliance - 代码合规检查"
echo "   • 还有33个其他工具..."
echo ""
echo "📚 更多信息: https://github.com/adminhuan/Claude-code-codex"