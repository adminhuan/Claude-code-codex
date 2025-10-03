# Smart Search MCP - 强大的智能搜索工具集

> 🎉 **v2.0.0 重大更新** - 极致精简，功能强大！专注于14个高质量搜索工具。

**Smart Search MCP** 提供**14个增强型智能搜索工具**：

### 🌍 国际平台搜索（6个）
- ✅ **网络搜索** - 支持4大搜索引擎，智能搜索技巧，相关搜索建议
- ✅ **GitHub搜索** - 多维度筛选，高级搜索语法，热门仓库推荐
- ✅ **StackOverflow** - 技术问答，标签筛选，投票排序
- ✅ **NPM包搜索** - 双重搜索方式，包详情直达，分类推荐
- ✅ **技术文档** - 7大框架文档，中文优先，快速导航
- ✅ **API参考** - 多源搜索，常用库快速访问，代码示例

### 🇨🇳 国内平台搜索（8个）
- ✅ **微信文档** - 小程序/公众号/支付，常用API速查
- ✅ **CSDN** - IT社区，博客/问答/资源
- ✅ **掘金** - 技术分享，前后端全栈
- ✅ **SegmentFault** - 技术问答，活跃社区
- ✅ **博客园** - 开发者家园，技术博客
- ✅ **开源中国** - 开源项目，技术资讯
- ✅ **阿里云** - 云服务文档，产品指南
- ✅ **腾讯云** - 云产品文档，API手册

## 🎯 核心特性

### ⚡ 增强功能
每个搜索工具都经过精心优化，提供：

1. **智能URL生成** - 根据不同平台特性生成最优搜索URL
2. **输入验证** - 自动检查并验证搜索关键词
3. **高级搜索技巧** - 为每个平台提供专业的搜索语法提示
4. **相关搜索建议** - 智能推荐相关搜索词
5. **多源搜索** - 部分工具支持多个搜索源（如NPM、API参考）
6. **平台介绍** - 详细的平台说明和热门主题推荐
7. **快速导航** - 直达官方文档和常用资源
8. **格式化输出** - 清晰的Markdown格式，易读易用
9. **🆕 自动文件保存** - 搜索详情自动保存到 `.search-results/` 文件夹，界面只显示简洁摘要

### 🔍 搜索工作流程

```mermaid
用户输入搜索关键词
    ↓
Smart Search MCP 处理请求
    ↓
生成优化的搜索URL + 详细信息保存到文件
    ↓
返回简洁摘要（关键词、链接、文件路径）
    ↓
Claude Code 使用 WebFetch 获取实时结果
    ↓
用户查看搜索结果 + 可查阅保存的详细信息
```

## 📊 版本对比

| 版本 | 总工具数 | 功能 |
|------|---------|------|
| v0.8.0 | 37个 | 混杂了各种功能 |
| v1.0.0 | 15个 | 1个编码规范 + 14个搜索 |
| **v2.0.0** | **14个** | **纯搜索工具** |

**v2.0.0 删除的功能**：
- ❌ 编码规范提醒工具（用户只需要搜索功能）

## 🚀 快速开始

### ⚠️ 从旧版本升级？

如果你之前安装过 `ai-rule-mcp-server`，使用一键迁移脚本：

```bash
# 🔄 一键迁移（自动卸载旧版本并安装新版本）
curl -sSL https://raw.githubusercontent.com/adminhuan/smart-search-mcp/main/migrate.sh | bash

# 或手动迁移：
# 1. 卸载旧版本
npm uninstall -g ai-rule-mcp-server

# 2. 删除旧的MCP配置
# 编辑 ~/.claude.json 删除 "ai-rule-mcp-server" 配置

# 3. 安装新版本（见下方）
```

### ⚡ 一键安装 (推荐)
```bash
# 🎯 Claude MCP命令 (最简单)
claude mcp add smart-search-mcp npx smart-search-mcp

# 📜 或一键脚本安装
curl -sSL https://raw.githubusercontent.com/adminhuan/smart-search-mcp/main/install.sh | bash

# 📦 或NPM直接运行
npx smart-search-mcp@latest

# 🔧 或全局安装
npm install -g smart-search-mcp

# 📥 或从GitHub源码安装
git clone https://github.com/adminhuan/smart-search-mcp.git
cd smart-search-mcp
npm install
npm start
```

### 🔧 配置Claude Code
在Claude Code的MCP配置中添加：
```json
{
  "mcpServers": {
    "smart-search-mcp": {
      "command": "npx",
      "args": ["smart-search-mcp@latest"]
    }
  }
}
```

### 🎉 开始使用
安装完成后，重启Claude Code即可使用14个搜索工具：

**🌍 国际平台搜索**（6个）：
- **网络搜索**: `ai_search_web()` - 多引擎网络搜索（百度/Google/Bing/搜狗）
- **GitHub搜索**: `ai_search_github()` - 搜索GitHub仓库、代码、Issues
- **StackOverflow搜索**: `ai_search_stackoverflow()` - 搜索技术问答
- **NPM包搜索**: `ai_search_npm()` - 搜索NPM包和文档
- **技术文档搜索**: `ai_search_docs()` - 搜索框架官方文档
- **API参考搜索**: `ai_search_api_reference()` - 查找API使用文档

**🇨🇳 国内平台搜索**（8个）：
- **微信开发者文档**: `ai_search_wechat_docs()` - 搜索小程序/公众号文档
- **CSDN搜索**: `ai_search_csdn()` - 搜索CSDN博客和问答
- **掘金搜索**: `ai_search_juejin()` - 搜索掘金技术文章
- **SegmentFault搜索**: `ai_search_segmentfault()` - 搜索技术问答
- **博客园搜索**: `ai_search_cnblogs()` - 搜索博客园文章
- **开源中国搜索**: `ai_search_oschina()` - 搜索开源项目和资讯
- **阿里云文档**: `ai_search_aliyun_docs()` - 搜索阿里云文档
- **腾讯云文档**: `ai_search_tencent_docs()` - 搜索腾讯云文档

## 🛠️ 可用工具

| 工具函数 | 功能说明 | 平台 |
|---------|---------|------|
| `ai_search_web()` | 网络搜索（Google/Bing/百度/搜狗） | 国际 |
| `ai_search_github()` | GitHub搜索 | 国际 |
| `ai_search_stackoverflow()` | StackOverflow搜索 | 国际 |
| `ai_search_npm()` | NPM包搜索 | 国际 |
| `ai_search_docs()` | 技术文档搜索 | 国际 |
| `ai_search_api_reference()` | API参考搜索 | 国际 |
| `ai_search_wechat_docs()` | 微信开发者文档 | 国内 |
| `ai_search_csdn()` | CSDN搜索 | 国内 |
| `ai_search_juejin()` | 掘金搜索 | 国内 |
| `ai_search_segmentfault()` | SegmentFault搜索 | 国内 |
| `ai_search_cnblogs()` | 博客园搜索 | 国内 |
| `ai_search_oschina()` | 开源中国搜索 | 国内 |
| `ai_search_aliyun_docs()` | 阿里云文档搜索 | 国内 |
| `ai_search_tencent_docs()` | 腾讯云文档搜索 | 国内 |

## 📖 使用方式

配置完成后，在Claude Code中可以直接使用搜索功能：

### 🔎 智能搜索使用
**国际平台**：
1. **网络搜索**: "搜索React Hooks最佳实践"（默认使用百度）
2. **GitHub搜索**: "在GitHub上搜索Vue3相关的仓库"
3. **技术问答**: "在StackOverflow上搜索如何解决CORS错误"
4. **包管理**: "搜索NPM上的日期处理库"
5. **文档查询**: "搜索React官方文档中关于useEffect的说明"
6. **API参考**: "查找axios的请求配置API文档"

**国内平台**：
7. **微信文档**: "搜索微信小程序一键登录功能"
8. **CSDN**: "在CSDN上搜索HBuilder开发教程"
9. **掘金**: "在掘金上搜索Vue3组合式API最佳实践"
10. **SegmentFault**: "在SegmentFault上搜索React性能优化"
11. **博客园**: "在博客园搜索.NET Core教程"
12. **开源中国**: "搜索开源中国的前端开源项目"
13. **阿里云**: "搜索阿里云OSS对象存储文档"
14. **腾讯云**: "搜索腾讯云COS使用指南"

Claude Code会自动使用相应的MCP搜索工具，并通过WebFetch获取真实的搜索结果。

## 🛠️ 管理命令
```bash
# 查看版本
npm list -g smart-search-mcp

# 更新到最新版本
npm update -g smart-search-mcp

# 卸载
npm uninstall -g smart-search-mcp
```

## 🎯 设计特点

- **🔎 专注搜索** - 14个精心打造的搜索工具，专注做好一件事
- **⚡ 智能增强** - 每个工具都配备高级搜索技巧和智能建议
- **🌏 国内优化** - 8个国内主流技术平台，默认百度搜索，访问速度快
- **🌍 国际全面** - 6个国际顶级平台，覆盖GitHub、StackOverflow、NPM等
- **✅ 真实结果** - 配合WebFetch工具获取真实搜索结果，非模拟数据
- **📚 多源搜索** - NPM、API参考等支持多个搜索源，提高查找成功率
- **🎨 格式优美** - Markdown格式输出，信息层次分明，易于阅读
- **🚀 开箱即用** - 无需数据库，无复杂配置，一键安装即可使用

## 🌟 使用示例

### 搜索React Hooks最佳实践

**输入**：
```javascript
ai_search_web({ query: "React Hooks 最佳实践", engine: "baidu" })
```

**输出**：
- 优化的搜索URL
- 4种搜索引擎选项
- 高级搜索技巧（精确匹配、排除关键词、限定站点等）
- 相关搜索建议
- WebFetch使用示例

### 查找GitHub上的Vue3项目

**输入**：
```javascript
ai_search_github({ query: "vue3", type: "repositories", language: "javascript", sort: "stars" })
```

**输出**：
- GitHub搜索链接
- 7种高级搜索技巧
- 相关搜索建议
- 其他搜索类型选项
- WebFetch使用示例

### 搜索微信小程序API

**输入**：
```javascript
ai_search_wechat_docs({ query: "wx.request", platform: "miniprogram" })
```

**输出**：
- 百度站内搜索链接
- 微信小程序文档直达
- 常用API快速参考
- 其他微信平台入口
- 开发者社区链接

## 📄 许可证

MIT License - 详见 LICENSE 文件