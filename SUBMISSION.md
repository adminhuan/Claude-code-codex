# Anthropic 官方 MCP 目录提交申请

## 📋 项目信息

### 基本信息
- **项目名称**: Smart Search MCP
- **英文名称**: smart-search-mcp
- **项目类型**: MCP 搜索工具服务器
- **GitHub 仓库**: https://github.com/adminhuan/smart-search-mcp
- **许可证**: MIT License

### 功能描述
Smart Search MCP 为 Claude Code 等支持 MCP 协议的助手提供 14 个增强型搜索工具，覆盖国际与国内主流开发平台。工具会返回经过优化的搜索 URL、WebFetch 示例、搜索技巧及相关建议，帮助用户快速获得真实可用的信息。

### 核心功能
1. **多引擎网络搜索** - 一次调用生成 Google/Bing/百度/搜狗搜索入口和技巧。
2. **开发者生态检索** - GitHub、StackOverflow、NPM、DevDocs 等平台的深度搜索助手。
3. **国内技术社区支持** - 微信文档、CSDN、掘金、SegmentFault、博客园、开源中国等 8 个中文平台。
4. **云厂商文档直达** - 阿里云与腾讯云文档站点快速定位 API 与操作指南。
5. **智能搜索提示** - 自动附带高级语法、相关关键词和平台导航链接，提升检索效率。

### 技术规格
- **编程语言**: Node.js (ESM)
- **MCP 协议版本**: 1.0+
- **工具数量**: 14 个搜索工具
- **依赖**: `@modelcontextprotocol/sdk`
- **运行方式**: `npx smart-search-mcp` 或全局安装后 `smart-search-mcp`

### 安装方式
```bash
claude mcp add smart-search-mcp npx smart-search-mcp
# 或
npx smart-search-mcp@latest
```

### 目标用户
- 使用 Claude Code 等 AI IDE 的开发者
- 需要在多平台快速检索资料的工程师
- 关注国内外技术社区、云厂商文档的团队

### 项目亮点
- ✅ **真实可用**：所有工具均返回真实搜索入口并配合 WebFetch 使用。
- ✅ **一次安装，全平台可搜**：14 个平台覆盖常见开发场景。
- ✅ **增强输出**：附带高级搜索技巧、相关搜索建议、热门主题推荐。
- ✅ **轻量快速**：零额外运行时依赖，启动小于 100ms。
- ✅ **中文友好**：国内平台描述、技巧和提示均为中文，适合本地化使用。

### 使用案例
1. **选型热门开源项目**：使用 `ai_search_github` 查找 star 数前列的 Vue3 后台模板。
2. **排查技术难题**：通过 `ai_search_stackoverflow` 获取高票回答，并附带标签筛选技巧。
3. **寻找高质量教程**：`ai_search_web` 同时提供多引擎入口及精确匹配语法建议。
4. **查询云服务 API**：`ai_search_aliyun_docs`/`ai_search_tencent_docs` 直达官方手册。
5. **查阅微信生态文档**：`ai_search_wechat_docs` 结合百度站内搜索与常用 API 列表。

### 质量保证
- **输入校验**：所有工具均检查关键词，避免空请求。
- **统一错误处理**：MCP 返回明确的中文错误信息。
- **文档完善**：README、FEATURES、QUICK_START、USAGE_GUIDE 提供完整说明。
- **版本透明**：CHANGELOG 与 V2_UPGRADE_SUMMARY 记录重要演进。

### 维护计划
- 🔄 持续跟进社区反馈，扩展更多常用搜索平台。
- 📝 保持文档更新，补充使用场景与最佳实践。
- 🧪 根据平台接口变化及时调整搜索参数与提示内容。

---

## 📝 申请理由

Smart Search MCP 专注于为 AI 助手补全“信息搜索能力”的空白。相比人工在多个站点反复复制粘贴搜索关键词，它能：

1. **集中入口**：一次安装即可访问 14 个平台的优化搜索链接。
2. **高质量提示**：自动提供高级搜索语法与相关关键词，提升命中率。
3. **国内生态覆盖**：针对中文开发者常用网站进行适配，降低信息检索门槛。
4. **真实结果获取**：结合 WebFetch 返回真实网页/接口内容，确保可验证。

凭借这些特性，Smart Search MCP 能显著提升 AI 辅助编程过程中的知识检索效率。

## 🎯 期待结果

希望进入 Anthropic 官方 MCP 目录，便于用户通过以下命令快速启用：

```bash
claude mcp add smart-search-mcp
```

欢迎试用并提供改进建议！
