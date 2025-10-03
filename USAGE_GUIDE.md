# 🔎 Smart Search MCP 使用指南

Smart Search MCP 是一组面向 Claude Code 的智能搜索工具，帮助你在 14 个国内外平台上快速找到真实、可用的资料。下面的指南带你从安装到高效搜索一步到位。

---

## 📦 安装与配置回顾

1. **添加服务器**  
   ```bash
   claude mcp add smart-search-mcp npx smart-search-mcp
   ```

2. **配置 Claude Code**  
   - 在 `~/.claude/settings.json` 中启用 `smart-search-mcp`；或
   - 在项目目录创建 `.mcp.json`：
     ```json
     {
       "servers": {
         "smart-search-mcp": {
           "command": "npx",
           "args": ["smart-search-mcp@latest"]
         }
       }
     }
     ```

3. **重启 Claude Code**，即可在对话中直接请求搜索。

---

## 🚀 快速使用示例

| 需求 | 对话指令 | 调用的工具 |
|------|-----------|-------------|
| 学习 React Hooks | “搜索 React Hooks 最佳实践” | `ai_search_web` + WebFetch |
| 选型 Vue3 后台模板 | “找 star 高的 Vue3 admin 仓库” | `ai_search_github` |
| 排查 useEffect 警告 | “StackOverflow 上有没有 useEffect 依赖问题的解决方案” | `ai_search_stackoverflow` |
| 寻找日期处理包 | “帮我搜 10 个日期处理的 npm 包” | `ai_search_npm` |
| 查询微信支付退款 | “微信支付退款文档在哪” | `ai_search_wechat_docs` |

每个工具都会给出：
- 已校验的搜索 URL；
- WebFetch 调用示例；
- 高级搜索技巧与相关关键词；
- 平台简介或热门主题建议。

---

## 🧭 工具全览

### 国际平台（6 个）

| 工具 | 说明 | 主要用途 |
|------|------|----------|
| `ai_search_web` | Google/Bing/百度/搜狗 多引擎 | 通用问题、教程、案例 |
| `ai_search_github` | 仓库/代码/Issues/用户 | 选型、源码学习、Issue 调研 |
| `ai_search_stackoverflow` | 技术问答检索 | 错误排查、最佳实践 |
| `ai_search_npm` | 网页 + API 双通道 | 包选型、下载量对比 |
| `ai_search_docs` | React/Vue/Angular/Node/Python/Java/MDN | 官方文档速查 |
| `ai_search_api_reference` | Google/DevDocs/GitHub/官方 | API 方法、示例代码 |

### 国内平台（8 个）

| 工具 | 平台 | 推荐场景 |
|------|------|----------|
| `ai_search_wechat_docs` | 微信开发者文档 | 小程序、公众号、支付接口 |
| `ai_search_csdn` | CSDN | 中文教程、踩坑分享 |
| `ai_search_juejin` | 掘金 | 前端/后端热点文章 |
| `ai_search_segmentfault` | SegmentFault | 中文 Q&A、技术讨论 |
| `ai_search_cnblogs` | 博客园 | .NET、后端相关资源 |
| `ai_search_oschina` | 开源中国 | 开源资讯、项目收录 |
| `ai_search_aliyun_docs` | 阿里云文档 | 云产品部署、API 手册 |
| `ai_search_tencent_docs` | 腾讯云文档 | 云服务操作、最佳实践 |

---

## 💡 搜索技巧速查

- **精确匹配**：`"关键词"`
- **排除词**：`关键词 -排除词`
- **限定站点**：`site:域名 关键词`
- **文件类型**：`关键词 filetype:pdf`
- **时间范围**：`关键词 after:2023`

GitHub、StackOverflow、NPM 等工具还会额外提供平台专属语法（如 `stars:>1000`、`isaccepted:yes`、`maintainer:`），直接复制即可使用。

---

## 🧪 WebFetch 配合建议

1. 复制工具返回的 WebFetch 代码片段。  
2. 根据需求调整 `prompt`，例如限定返回条数、关注字段等。  
3. 对于结构化数据（NPM API、云厂商文档 JSON 接口），优先使用 API URL，解析更稳定。

---

## ❓ 常见问题

- **结果真实可靠吗？**  所有工具只生成真实搜索 URL，需通过 WebFetch 抓取实际网页或接口结果。
- **可以组合多个工具吗？**  可以。一个请求可以依次调用 GitHub 和 NPM，以同时了解开源趋势与包下载量。
- **国内是否默认百度？**  网络搜索默认百度，可通过 `engine` 参数切换；微信文档等工具内置百度站内搜索。
- **如何调参与过滤？**  每个工具的输入 schema 在 README 中有详细说明，可传入 `language`、`sort`、`tags` 等字段细化结果。

---

尽情使用 Smart Search MCP，让搜索不再成为瓶颈！
