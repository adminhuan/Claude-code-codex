# Smart Search MCP - 快速开始指南

## ⚡ 5分钟快速上手

### 1. 安装（选择一种方式）

```bash
# 方式1: Claude MCP命令（推荐）
claude mcp add smart-search-mcp npx smart-search-mcp

# 方式2: NPX直接运行
npx smart-search-mcp@latest

# 方式3: 全局安装
npm install -g smart-search-mcp
```

### 2. 配置 Claude Code

在 Claude Code 的 MCP 配置文件中添加：

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

### 3. 重启 Claude Code

重启后即可使用全部14个搜索工具！

---

## 🎯 常用场景速查

### 场景1：学习 React Hooks

```
你：我想学习React Hooks
Claude Code: [自动调用] ai_search_docs({ query: "hooks", framework: "react" })
→ 返回React官方文档链接 + 常用Hooks列表 + 使用指南
```

### 场景2：查找NPM包

```
你：帮我找一个日期处理的npm包
Claude Code: [自动调用] ai_search_npm({ query: "date", size: 10 })
→ 返回top10包 + 包详情链接 + 相关推荐
```

### 场景3：解决技术问题

```
你：React useEffect依赖数组警告怎么解决
Claude Code: [自动调用] ai_search_stackoverflow({
  query: "useEffect dependency warning",
  tags: "react,hooks"
})
→ 返回StackOverflow高票回答 + 解决方案
```

### 场景4：搜索开源项目

```
你：GitHub上有哪些好的Vue3管理后台项目
Claude Code: [自动调用] ai_search_github({
  query: "vue3 admin",
  type: "repositories",
  language: "vue",
  sort: "stars"
})
→ 返回按Star排序的仓库列表
```

### 场景5：查微信小程序API

```
你：微信小程序怎么发起网络请求
Claude Code: [自动调用] ai_search_wechat_docs({
  query: "wx.request",
  platform: "miniprogram"
})
→ 返回小程序API文档 + 使用示例
```

---

## 📚 14个工具快速参考

### 国际平台（6个）

| 工具 | 用途 | 示例关键词 |
|------|------|-----------|
| `ai_search_web` | 通用网络搜索 | "React最佳实践" |
| `ai_search_github` | 查找开源项目 | "vue admin" |
| `ai_search_stackoverflow` | 技术问答 | "async await error" |
| `ai_search_npm` | 查找npm包 | "http client" |
| `ai_search_docs` | 官方文档 | "useState" |
| `ai_search_api_reference` | API参考 | "axios.get" |

### 国内平台（8个）

| 工具 | 平台 | 特点 |
|------|------|------|
| `ai_search_wechat_docs` | 微信文档 | 小程序/公众号开发 |
| `ai_search_csdn` | CSDN | 中文博客/问答 |
| `ai_search_juejin` | 掘金 | 前端技术文章 |
| `ai_search_segmentfault` | 思否 | 技术问答社区 |
| `ai_search_cnblogs` | 博客园 | .NET/后端博客 |
| `ai_search_oschina` | 开源中国 | 开源项目/资讯 |
| `ai_search_aliyun_docs` | 阿里云 | 云服务文档 |
| `ai_search_tencent_docs` | 腾讯云 | 云产品文档 |

---

## 💡 高级搜索技巧

### 网络搜索技巧

```
精确匹配：      "React Hooks"
排除关键词：    React -class
限定站点：      React site:github.com
文件类型：      React filetype:pdf
时间范围：      React after:2023
```

### GitHub搜索技巧

```
Star筛选：      vue3 stars:>1000
最近更新：      react pushed:>2024-01-01
特定语言：      admin language:typescript
主题标签：      ui topic:react
组织仓库：      react org:facebook
```

### StackOverflow技巧

```
标签搜索：      [javascript] async
多标签：        [react] [hooks] state
已回答：        React is:answer
已接受：        useEffect isaccepted:yes
高分问题：      async score:10..
```

---

## 🔥 实战案例

### 案例1：从0到1学习新框架

**目标**：学习 Next.js

**搜索策略**：
1. `ai_search_docs` - 查看Next.js官方文档
2. `ai_search_github` - 找优秀的Next.js项目参考
3. `ai_search_juejin` - 阅读中文入门教程
4. `ai_search_npm` - 了解Next.js相关插件

### 案例2：解决复杂Bug

**问题**：React应用内存泄漏

**搜索策略**：
1. `ai_search_stackoverflow` - 搜索 "react memory leak"
2. `ai_search_github` - 查看Issues中的解决方案
3. `ai_search_web` - 搜索最新的博客文章
4. `ai_search_docs` - 查看React官方性能优化文档

### 案例3：技术选型

**需求**：选择HTTP客户端库

**搜索策略**：
1. `ai_search_npm` - 搜索 "http client"，查看下载量
2. `ai_search_github` - 对比axios、fetch、got等库的Star数
3. `ai_search_docs` - 查看各库的API文档
4. `ai_search_stackoverflow` - 了解各库的优缺点

### 案例4：云服务部署

**目标**：在阿里云部署Node.js应用

**搜索策略**：
1. `ai_search_aliyun_docs` - 查看ECS产品文档
2. `ai_search_csdn` - 阅读部署教程
3. `ai_search_oschina` - 寻找开源部署脚本
4. `ai_search_web` - 搜索最佳实践

---

## ❓ 常见问题

### Q1: 搜索结果是真实的吗？
✅ 是的！所有搜索工具返回真实的搜索URL，Claude Code会使用WebFetch工具获取真实结果。

### Q2: 可以同时搜索多个平台吗？
✅ 可以！Claude Code会根据你的问题自动选择最合适的搜索工具，也可以组合使用。

### Q3: 国内平台访问速度如何？
✅ 所有国内平台都是直连访问，速度快且稳定。

### Q4: 支持哪些搜索引擎？
✅ 网络搜索支持：Google、Bing、百度（默认）、搜狗。

### Q5: 可以自定义搜索参数吗？
✅ 可以！每个工具都支持多个参数，如结果数量、排序方式、语言筛选等。

### Q6: 如何更新到最新版本？
```bash
npm update -g smart-search-mcp
# 或
npx smart-search-mcp@latest
```

---

## 🎓 学习资源

- 📘 [完整文档](./README.md)
- 📋 [功能详解](./FEATURES.md)
- 📝 [更新日志](./CHANGELOG.md)
- 🐛 [问题反馈](https://github.com/adminhuan/smart-search-mcp/issues)

---

## 🚀 下一步

1. 尝试每个搜索工具，熟悉它们的特点
2. 学习高级搜索技巧，提高搜索效率
3. 根据实际需求组合使用多个工具
4. 分享你的使用经验，帮助社区成长

**享受智能搜索的乐趣吧！** 🎉
