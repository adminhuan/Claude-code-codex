#!/bin/bash
# Smart Search MCP - 全局自动配置脚本

echo "🌟 Smart Search MCP - 全局自动配置"
echo "=================================="

# 检查 claude 命令
if ! command -v claude &> /dev/null; then
  echo "⚠️ 未找到 claude 命令，请先安装 Claude CLI 或使用 npm 全局安装 smart-search-mcp"
  echo "👉 示例：npm install -g smart-search-mcp"
  exit 1
fi

# 添加到用户级别配置（所有项目都可用）
echo "📝 添加用户级别MCP配置..."
claude mcp add smart-search-mcp --scope user npx smart-search-mcp

# 验证配置
echo "✅ 验证配置..."
claude mcp list

echo ""
echo "🎉 全局配置完成！"
echo ""
echo "🔎 现在所有项目都可以使用 Smart Search MCP 的14个搜索工具："
echo "   • 国际平台：网络、GitHub、StackOverflow、NPM、技术文档、API参考"
echo "   • 国内平台：微信文档、CSDN、掘金、SegmentFault、博客园、开源中国、阿里云、腾讯云"
echo ""
echo "🚀 使用方法："
echo "   1. 在任意项目目录运行 Claude Code"
echo "   2. 说：'帮我搜索 React Hooks 最佳实践'"
echo "   3. 或者：'搜索微信小程序登录接口文档'"
echo ""
echo "📚 更多信息：https://github.com/adminhuan/smart-search-mcp"
