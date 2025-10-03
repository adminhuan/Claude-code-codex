#!/bin/bash
# Smart Search MCP - 项目安装脚本

echo "🎯 Smart Search MCP 项目安装器"
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

if [ -f .mcp.json ]; then
    BACKUP=".mcp.json.backup.$(date +%Y%m%d%H%M%S)"
    cp .mcp.json "$BACKUP"
    echo "🗂️ 已备份现有 .mcp.json 至 $BACKUP"
fi

cat > .mcp.json << 'EOF'
{
  "servers": {
    "smart-search-mcp": {
      "command": "npx",
      "args": ["smart-search-mcp@latest"],
      "description": "Smart Search MCP - 14个增强型国内外搜索工具"
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
echo "3. 试试说: '搜索 React Hooks 最佳实践'"
echo "4. 或者说: '帮我找微信支付退款文档'"
echo ""
echo "🔎 可用搜索工具示例:"
echo "   • ai_search_web - 多引擎网络搜索"
echo "   • ai_search_github - GitHub 仓库/代码检索"
echo "   • ai_search_stackoverflow - 技术问答搜索"
echo "   • ai_search_npm - NPM 包与API搜索"
echo "   • ai_search_docs - React/Vue/Node等官方文档"
echo "   • ai_search_wechat_docs - 微信开发者文档"
echo "   • ai_search_aliyun_docs / ai_search_tencent_docs - 云厂商文档"
echo ""
echo "📚 更多信息: https://github.com/adminhuan/smart-search-mcp"
