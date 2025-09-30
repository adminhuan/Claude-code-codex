# 更新日志 (Changelog)

所有重要的项目更改都将记录在此文件中。

## [0.6.9] - 2025-09-30

### 🐛 重要修复
- **删除所有项目中的旧配置**: Claude Code按项目存储配置，现在会遍历所有项目删除旧配置
- **彻底清理**: 不仅删除全局配置，还删除每个项目目录中的旧配置
- **真正解决问题**: 修复了旧配置"删除后又出现"的问题

### 📈 功能改进
- 脚本会显示删除了哪些项目的配置
- 统计并显示总共删除的配置数量
- 更准确的清理结果提示

### 💡 问题说明
Claude Code的配置文件结构：
```json
{
  "projects": {
    "/path/to/project1": {
      "mcpServers": { ... }
    },
    "/path/to/project2": {
      "mcpServers": { ... }
    }
  }
}
```
每个项目都有独立的MCP配置，需要逐个清理。

---

## [0.6.8] - 2025-09-30

### 🎉 重大改进
- **真正自动化迁移**: 使用Python/Node.js自动删除JSON配置中的旧条目
- **无需手动操作**: 不再要求用户手动编辑配置文件
- **智能回退**: 如果没有Python/Node.js，才提示手动操作

### 🐛 修复
- 移除询问用户是否删除旧配置的步骤，直接自动删除
- 使用JSON解析器安全删除旧配置，避免破坏JSON格式
- 自动备份配置文件到 `.claude.json.backup`

### 📈 功能改进
- 优先使用 Python3 解析JSON
- 降级使用 Node.js 解析JSON
- 最后才提示手动操作

---

## [0.6.7] - 2025-09-30

### 🐛 修复
- **迁移脚本智能检测**: 检测到 smart-search-mcp 已存在时，询问是否重新配置
- **避免重复配置**: 防止多次运行脚本导致配置冲突
- **优雅处理已存在**: 提供删除旧配置并重新添加的选项

### 📈 功能改进
- 使用 `claude mcp list` 检查配置是否存在
- 提供跳过或重新配置的选择
- 更友好的用户提示

---

## [0.6.6] - 2025-09-30

### 🔄 重大变更
- **仓库更名**: GitHub仓库从 `Claude-code-codex` 更名为 `smart-search-mcp`
- **统一品牌**: 与NPM包名保持一致

### 📚 文档更新
- 更新所有文档中的GitHub链接
- 更新package.json仓库地址
- 更新所有shell脚本中的链接
- 修正README、CHANGELOG中的仓库引用

### 🔗 新链接
- GitHub: https://github.com/adminhuan/smart-search-mcp
- NPM: https://www.npmjs.com/package/smart-search-mcp

---

## [0.6.5] - 2025-09-30

### 🐛 修复
- **优化迁移脚本**: 移除用户选择环节，自动检测并安装
- **智能安装方式**: 自动检测 `claude` 命令，优先使用 Claude MCP 安装
- **配置备份**: 在删除旧配置前自动备份

### 📈 功能改进
- 简化迁移流程，减少用户操作步骤
- 更友好的提示信息
- 自动降级到npm全局安装（如果claude命令不可用）

---

## [0.6.4] - 2025-09-30

### 🎉 新增功能
- **一键迁移脚本**: 添加 `migrate.sh` 自动从旧版本升级
- **自动清理旧版本**: 迁移脚本会检测并卸载 `ai-rule-mcp-server`
- **智能配置检查**: 自动检测并提示清理旧配置

### 📚 文档更新
- 添加"从旧版本升级"专门章节
- 提供一键迁移脚本和手动迁移说明
- 在package.json中包含迁移脚本

---

## [0.6.3] - 2025-09-30

### 🎉 新增功能
- **一键迁移脚本**: 添加 `migrate.sh` 自动从旧版本升级
- **自动清理旧版本**: 迁移脚本会检测并卸载 `ai-rule-mcp-server`
- **智能配置检查**: 自动检测并提示清理旧配置

### 🐛 修复
- **修正Claude MCP命令格式**: 正确命令为 `claude mcp add smart-search-mcp npx smart-search-mcp`
- **验证命令可用性**: 经过实际测试确认命令正确工作

### 📚 文档更新
- 添加"从旧版本升级"专门章节
- 提供一键迁移脚本说明
- 更新README中的Claude MCP命令示例
- 添加手动迁移步骤说明

---

## [0.6.2] - 2025-09-30

### 📈 功能改进
- **添加Claude MCP命令支持**: 用户可直接使用 `claude mcp add smart-search-mcp npx smart-search-mcp` 安装
- **恢复一键安装脚本**: 更新 install.sh 支持新包名和Node.js环境
- **优化安装方式**: 提供5种安装方式，满足不同用户需求

### 📚 文档更新
- 更新README添加Claude MCP命令安装说明（修正命令格式）
- 重新组织安装方式优先级
- 完善一键脚本使用说明

### 🐛 修复
- 修正Claude MCP命令格式，去掉错误的 `--npm` 参数

---

## [0.6.1] - 2025-09-30

### 🔄 重大变更
- **包名变更**: `ai-rule-mcp-server` → `smart-search-mcp`
- **定位调整**: 突出智能搜索和调试功能作为核心特色
- **描述优化**: 更简洁明确的功能说明

### 📈 功能改进
- 重新组织工具优先级：搜索工具(14个) > 调试工具(5个) > 编码规范(38个) > 监督指导(7个)
- 简化安装流程，统一使用NPM包管理
- 优化README文档结构

### 📚 文档更新
- 更新所有文档中的包名引用
- 简化安装和配置说明
- 优化功能描述顺序

---

## [0.6.0] - 2025-09-30

### 🎉 新增功能

#### 🇨🇳 国内开发者平台搜索工具（8个全新工具）
- **`ai_search_wechat_docs`** - 微信开发者文档搜索
  - 支持小程序、公众号、开放平台、微信支付
  - 提供常用文档入口和开发工具链接
  - 包含HBuilderX跨平台开发建议

- **`ai_search_csdn`** - CSDN搜索
  - 支持博客和问答分类搜索
  - 提供搜索技巧和注意事项
  - 推荐高质量内容筛选方法

- **`ai_search_juejin`** - 掘金搜索
  - 支持热门、最新、点赞排序
  - 推荐小册、专栏等优质内容
  - 前端和全栈技术内容丰富

- **`ai_search_segmentfault`** - SegmentFault搜索
  - 专业技术问答社区
  - 支持标签筛选
  - 高质量技术讨论

- **`ai_search_cnblogs`** - 博客园搜索
  - 深度技术文章和系列教程
  - .NET和C#技术内容丰富
  - 长期维护的优质内容

- **`ai_search_oschina`** - 开源中国搜索
  - 支持资讯、博客、问答、项目搜索
  - Gitee代码托管平台
  - 开源项目和技术翻译

- **`ai_search_aliyun_docs`** - 阿里云文档搜索
  - 搜索阿里云产品和API文档
  - 支持产品范围筛选
  - 提供SDK、最佳实践等资源

- **`ai_search_tencent_docs`** - 腾讯云文档搜索
  - 搜索腾讯云产品和API文档
  - 支持产品范围筛选
  - 完整的开发者资源

### 📈 功能改进
- 工具总数从56个增加到64个
- 搜索工具从6个扩展到14个
- 全面覆盖国内主流开发者平台
- 特别优化微信生态开发支持
- 提供国内镜像站点和加速方案

### 📚 文档更新
- 更新README添加所有国内平台搜索说明
- 添加14个搜索工具的详细使用示例
- 完善国内平台使用技巧和注意事项

---

## [0.5.0] - 2025-09-30

### 🎉 新增功能

#### 🐛 控制台调试工具（5个全新工具）
- **`ai_console_error_monitor`** - 浏览器控制台错误监控
  - 支持多种错误类型分析：JavaScript、Network、CORS、Syntax、Reference、Type、Range
  - 提供针对性解决方案和调试步骤
  - 自动识别错误堆栈信息
  - 包含MDN和StackOverflow参考链接

- **`ai_console_warning_check`** - 控制台警告检查
  - 识别React、Vue、浏览器API等框架警告
  - 区分Deprecation、Performance、Security等警告类型
  - 提供修复建议和最佳实践

- **`ai_network_error_diagnosis`** - 网络请求错误诊断
  - 详细分析HTTP状态码（400、401、403、404、500、502、503等）
  - 区分客户端错误(4xx)和服务器错误(5xx)
  - 提供具体的排查步骤和解决方案
  - 推荐API测试工具（Postman、Insomnia等）

- **`ai_console_log_analyzer`** - 控制台日志智能分析
  - 自动统计错误、警告、网络请求数量
  - 识别性能问题模式
  - 提供日志优化建议
  - 推荐日志管理工具（Sentry、LogRocket等）

- **`ai_debug_suggestion`** - 系统化调试建议生成
  - 提供6步系统化调试流程
  - 包含常用调试命令和代码示例
  - 支持多种运行环境（Chrome、Firefox、Node.js等）
  - 提供预防措施建议（TypeScript、ESLint等）

### 📈 功能改进
- 工具总数从51个增加到56个
- 完善的错误诊断和解决方案系统
- 支持中文友好的错误提示

### 📚 文档更新
- 更新README添加控制台调试工具使用说明
- 添加详细的使用示例
- 创建CHANGELOG.md记录版本历史

---

## [0.4.0] - 2025-09-29

### 🎉 新增功能

#### 🔎 智能搜索工具（6个全新工具）
- **`ai_search_web`** - 多引擎网络搜索
  - 支持Google、Bing、百度、搜狗
  - 默认使用百度（国内网络优化）
  - 提供高级搜索技巧

- **`ai_search_github`** - GitHub搜索
  - 搜索仓库、代码、Issues、用户
  - 支持语言筛选和排序
  - 推荐国内镜像站（Gitee、GitCode）

- **`ai_search_stackoverflow`** - StackOverflow搜索
  - 搜索技术问答
  - 支持标签筛选
  - 推荐国内替代站（SegmentFault、掘金、CSDN）

- **`ai_search_npm`** - NPM包搜索
  - 搜索和评估NPM包
  - 提供包质量评估标准
  - 推荐淘宝NPM镜像

- **`ai_search_docs`** - 技术文档搜索
  - 支持React、Vue、Angular、Node.js、Python、Java等
  - 提供中英文文档链接
  - 推荐国内优质文档站

- **`ai_search_api_reference`** - API参考搜索
  - 快速查找API文档
  - 常用库直达链接
  - 推荐API测试工具

### 📈 功能改进
- 工具总数从45个增加到51个
- 国内网络访问优化
- 提供国内镜像站点推荐

---

## [0.3.0] - 2025-09-29

### 🎉 新增功能

#### 🔍 智能监督指导工具（7个全新工具）
- **`ai_guide_project_rules`** - 项目规则书生成指导
- **`ai_guide_development_plan`** - 开发计划生成指导
- **`ai_guide_pr_review`** - PR审查清单生成指导
- **`ai_guide_feature_request`** - 功能请求文档生成指导
- **`ai_validate_content`** - 内容质量检查
- **`ai_suggest_improvements`** - 改进建议生成
- **`ai_project_health_check`** - 项目健康检查

### 📈 功能改进
- 工具总数从38个增加到45个
- 增强AI监督能力，确保生成内容的专业性

---

## [0.2.0] - 2025-09-29

### 🔄 重大变更
- 使用官方MCP SDK重写服务器
- 从Python实现迁移到Node.js实现
- 移除Python依赖，简化安装流程

### 📈 功能改进
- 更好的性能和稳定性
- 简化的配置流程
- 纯Node.js实现，无需Python环境

---

## [0.1.0] - 2025-09-29

### 🎉 首次发布

#### 核心功能
- 38个基础AI规则遵守工具
- 4种工作模式（Normal/Plan/PR/FR）
- 智能规则提醒和代码检查
- 开发计划和PR管理
- 功能请求系统
- AI协作通信（可选）

#### 基础工具列表
- 规则提醒和管理
- 代码合规检查
- 工作模式切换
- 开发计划创建
- PR审查管理
- 功能请求提交

---

## 版本说明

本项目遵循[语义化版本控制](https://semver.org/zh-CN/)规范：

- **主版本号**：不兼容的API变更
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 链接

- [GitHub仓库](https://github.com/adminhuan/smart-search-mcp)
- [NPM包](https://www.npmjs.com/package/smart-search-mcp)
- [问题反馈](https://github.com/adminhuan/smart-search-mcp/issues)