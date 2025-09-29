#!/bin/bash
# AI规则遵守MCP工具 - 全局自动配置脚本

echo "🌟 AI规则遵守MCP工具 - 全局自动配置"
echo "=================================="

# 添加到用户级别配置（所有项目都可用）
echo "📝 添加用户级别MCP配置..."
claude mcp add ai-rule-mcp-server --scope user npx ai-rule-mcp-server@latest

# 验证配置
echo "✅ 验证配置..."
claude mcp list

echo ""
echo "🎉 全局配置完成！"
echo ""
echo "📝 现在所有项目都可以使用AI规则工具了："
echo "   • 智能规则提醒"
echo "   • 多模式工作流 (Plan/PR/FR)"
echo "   • 代码合规检查"
echo "   • 38个专业工具"
echo ""
echo "🚀 使用方法："
echo "   1. 在任意项目目录运行 Claude Code"
echo "   2. 说：'请提醒我关于编码规范'"
echo "   3. 说：'切换到Plan模式'"
echo ""
echo "📚 更多信息：https://github.com/adminhuan/Claude-code-codex"