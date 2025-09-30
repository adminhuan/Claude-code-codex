# Smart Search MCP - 真实可用的智能工具集

> 🎉 **v0.9.0 重大更新** - 100%真实可用！删除所有虚假功能，只保留20个经过验证的真实工具。

**Smart Search MCP** 提供**20个真实可用工具**：
- ✅ **14个智能搜索** - 真正获取搜索结果（通过WebFetch）
- ✅ **1个编码规范提醒** - 真正读取项目文件
- ✅ **5个需求分析** - 真正生成文档文件

## 🎯 核心功能（全部真实可用）

### 🎯 智能需求分析工具（5个）
让AI帮你从需求到开发全流程自动化，生成真实的Markdown文档：

- **`ai_smart_wake`** - 智能唤醒
  - 支持多种唤醒词："小c"、"小C"、"MCP"、"小智"、"AI助手"
  - 用法：`"小c，帮我分析需求"` / `"MCP启动，生成计划"`

- **`ai_analyze_requirement`** - 需求分析
  - 生成详细的需求分析报告
  - 包含：功能分类、技术栈建议、架构设计、时间估算、风险评估
  - 支持3种分析深度：basic/detailed/comprehensive

- **`ai_generate_plan`** - 开发计划生成
  - 真正创建 `plan/` 文件夹
  - 真正写入 `项目名-开发计划.md` 文件
  - 包含：项目概述、功能规划、技术架构、开发时间线（12周）、团队分工、风险评估

- **`ai_breakdown_modules`** - 需求拆解
  - 真正创建 `plan/modules/` 文件夹
  - 生成两份真实文档：
    - `项目名-需求拆解.md` - 5个模块25个任务的详细拆解
    - `项目名-TODO.md` - 按优先级排序的任务清单
  - 支持3种拆解粒度：coarse(3模块)/medium(5模块)/fine(8模块)

- **`ai_confirm_action`** - 用户确认
  - 执行重要操作前征求用户意见

### 📋 编码规范提醒工具（1个）- 真实实现
**`ai_coding_rules_reminder`** - 真正读取项目中的编码规范文档：

- ✅ 自动搜索并读取项目中的规范文件：
  - `CODING_STANDARDS.md`、`STYLE_GUIDE.md`、`CONTRIBUTING.md`
  - `README.md`、`docs/coding-standards.md` 等
- ✅ 读取真实内容（最多2000字符）并提醒Claude Code严格遵守
- ✅ 支持关注领域筛选：all/naming/structure/security/performance/documentation
- ✅ 支持严格模式（更严格的规范检查）
- ✅ 如果没有找到规范文档，会返回通用编码规范提醒

**作用**：监督Claude Code在编写代码时遵守项目规范，不乱改乱写。

### 🔎 智能搜索工具（14个）- 真实搜索
所有搜索工具都会返回明确的WebFetch使用说明，Claude Code会自动获取真实搜索结果：

**国际平台（6个）**：
- `ai_search_web` - 网络搜索（Google/Bing/百度/搜狗）
- `ai_search_github` - GitHub搜索（仓库/代码/Issues/用户）
- `ai_search_stackoverflow` - StackOverflow技术问答
- `ai_search_npm` - NPM包搜索
- `ai_search_docs` - 技术文档搜索（React/Vue/Node.js/Python/Java等）
- `ai_search_api_reference` - API参考搜索

**国内平台（8个）**：
- `ai_search_wechat_docs` - 微信开发者文档（小程序/公众号/开放平台）
- `ai_search_csdn` - CSDN技术博客和问答
- `ai_search_juejin` - 掘金技术社区
- `ai_search_segmentfault` - SegmentFault思否
- `ai_search_cnblogs` - 博客园
- `ai_search_oschina` - 开源中国
- `ai_search_aliyun_docs` - 阿里云文档
- `ai_search_tencent_docs` - 腾讯云文档

**搜索工作原理**：
1. 搜索工具返回搜索URL
2. 提供明确的WebFetch使用示例
3. Claude Code自动使用WebFetch访问URL
4. 获取真实的搜索结果并返回给用户

## 📊 版本对比

| 版本 | 总工具数 | 真实功能 | 假功能 | 诚实度 |
|------|---------|---------|--------|--------|
| v0.8.0 | 37个 | 5个 | 32个 | 13.5% |
| **v0.9.0** | **20个** | **20个** | **0个** | **100%** |

**删除的功能（18个假工具）**：
- ❌ 5个控制台监控工具（无法访问浏览器控制台）
- ❌ 13个假的规则/监督工具（只返回模板文本，不读取项目文件）

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
安装完成后，重启Claude Code即可使用69个AI工具：

**⭐ 智能需求分析工具**（5个 - 新增）：
- **智能唤醒**: `ai_smart_wake()` - 自然语言唤醒AI助手
- **需求分析**: `ai_analyze_requirement()` - 智能需求分析报告
- **计划生成**: `ai_generate_plan()` - 自动生成开发计划文档
- **需求拆解**: `ai_breakdown_modules()` - 拆解为模块和任务
- **用户确认**: `ai_confirm_action()` - 操作前用户确认

**🔧 基础工具**（38个）：
- **规则提醒**: `ai_rule_reminder()` - 智能规则提醒
- **模式切换**: `ai_switch_mode()` - 切换工作模式
- **计划管理**: `ai_create_plan()` - 创建开发计划
- **代码审查**: `ai_create_pr()` - 创建PR审查
- **合规检查**: `ai_check_compliance()` - 代码合规检查
- 还有33个其他基础工具...

**🎯 监督指导工具**（7个）：
- **项目规则指导**: `ai_guide_project_rules()` - 指导生成项目规则书
- **开发计划指导**: `ai_guide_development_plan()` - 指导创建开发计划
- **PR审查指导**: `ai_guide_pr_review()` - 指导创建PR审查
- **功能请求指导**: `ai_guide_feature_request()` - 指导创建功能请求
- **内容质量检查**: `ai_validate_content()` - 验证内容质量
- **改进建议**: `ai_suggest_improvements()` - 提出改进建议
- **项目健康检查**: `ai_project_health_check()` - 全面项目评估

**🔎 智能搜索工具**（14个）：
- **网络搜索**: `ai_search_web()` - 多引擎网络搜索（百度/Google/Bing/搜狗）
- **GitHub搜索**: `ai_search_github()` - 搜索GitHub仓库、代码、Issues
- **StackOverflow搜索**: `ai_search_stackoverflow()` - 搜索技术问答
- **NPM包搜索**: `ai_search_npm()` - 搜索NPM包和文档
- **技术文档搜索**: `ai_search_docs()` - 搜索框架官方文档
- **API参考搜索**: `ai_search_api_reference()` - 查找API使用文档
- **微信开发者文档**: `ai_search_wechat_docs()` - 搜索小程序/公众号文档
- **CSDN搜索**: `ai_search_csdn()` - 搜索CSDN博客和问答
- **掘金搜索**: `ai_search_juejin()` - 搜索掘金技术文章
- **SegmentFault搜索**: `ai_search_segmentfault()` - 搜索技术问答
- **博客园搜索**: `ai_search_cnblogs()` - 搜索博客园文章
- **开源中国搜索**: `ai_search_oschina()` - 搜索开源项目和资讯
- **阿里云文档**: `ai_search_aliyun_docs()` - 搜索阿里云文档
- **腾讯云文档**: `ai_search_tencent_docs()` - 搜索腾讯云文档

**🐛 控制台调试工具**（5个）：
- **错误监控**: `ai_console_error_monitor()` - 分析浏览器控制台错误
- **警告检查**: `ai_console_warning_check()` - 检查控制台警告
- **网络诊断**: `ai_network_error_diagnosis()` - 诊断HTTP请求错误
- **日志分析**: `ai_console_log_analyzer()` - 分析控制台日志
- **调试建议**: `ai_debug_suggestion()` - 生成调试建议

## 🛠️ 可用工具

| 工具函数 | 功能说明 | 类型 |
|---------|---------|------|
| `ai_rule_reminder()` | 智能规则提醒 | 基础功能 |
| `ai_check_compliance()` | 代码合规检查 | 基础功能 |
| `ai_get_rules()` | 获取规则清单 | 基础功能 |
| `ai_add_custom_rule()` | 添加自定义规则 | 基础功能 |
| `ai_guide_project_rules()` | 项目规则书指导 | 监督指导 |
| `ai_guide_development_plan()` | 开发计划指导 | 监督指导 |
| `ai_guide_pr_review()` | PR审查指导 | 监督指导 |
| `ai_guide_feature_request()` | 功能请求指导 | 监督指导 |
| `ai_validate_content()` | 内容质量检查 | 监督指导 |
| `ai_suggest_improvements()` | 改进建议 | 监督指导 |
| `ai_project_health_check()` | 项目健康检查 | 监督指导 |
| `ai_search_web()` | 网络搜索 | 搜索工具 |
| `ai_search_github()` | GitHub搜索 | 搜索工具 |
| `ai_search_stackoverflow()` | StackOverflow搜索 | 搜索工具 |
| `ai_search_npm()` | NPM包搜索 | 搜索工具 |
| `ai_search_docs()` | 技术文档搜索 | 搜索工具 |
| `ai_search_api_reference()` | API参考搜索 | 搜索工具 |
| `ai_enable_collaboration()` | 启用协作功能 | 可选功能 |
| `ai_send_message()` | 发送协作消息 | 可选功能 |
| `ai_read_messages()` | 读取协作消息 | 可选功能 |
| `ai_collaboration_status()` | 查看协作状态 | 可选功能 |

## 📖 使用方式

配置完成后，在支持MCP的AI工具中你可以：

### ⭐ 智能需求分析使用（新功能）
1. **唤醒AI助手**: 支持多种方式
   - "小c，帮我分析需求"
   - "小C，生成开发计划"
   - "MCP启动，拆解需求"
   - "MCP，帮我写计划"
2. **需求分析**: "分析这个需求：开发一个在线商城系统"
3. **生成开发计划**: "为我的项目生成详细的开发计划文档"
4. **需求拆解**: "把需求拆解成具体的模块和任务清单"
5. **确认操作**: 系统会在重要操作前自动询问是否继续

**完整工作流示例：**
```
用户: "小c，帮我分析需求：开发一个在线教育平台"
→ AI: 🎯 小C已唤醒！分析需求，生成分析报告

用户: "MCP，生成开发计划"
→ AI: 🎯 MCP已启动！创建plan文件夹，生成完整的开发计划文档

用户: "小C，拆解需求"
→ AI: 🎯 小C已唤醒！生成模块化的任务清单和TODO列表

用户: "确认"
→ 开始执行开发任务
```

**支持的唤醒词：**
- 小c / 小C （不区分大小写）
- MCP （推荐）
- 小智
- AI助手

### 基础功能使用
1. **规则提醒**: "请提醒我关于Python编码规范"
2. **切换工作模式**: "切换到Plan模式"，"切换到PR模式"
3. **创建开发计划**: "创建一个用户认证功能的开发计划"
4. **管理代码审查**: "创建一个PR来审查这个功能"
5. **提交功能请求**: "我建议增加代码格式化规则"

### 智能搜索使用
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

### 控制台调试使用
1. **错误分析**: "分析这个错误：Uncaught TypeError: Cannot read property 'map' of undefined"
2. **网络错误**: "诊断这个404错误：https://api.example.com/users"
3. **警告检查**: "帮我看看这个React警告怎么解决"
4. **日志分析**: "分析我的控制台日志，找出性能问题"
5. **调试建议**: "我的代码报错了，给我调试建议"

AI工具会自动使用相应的MCP工具来响应你的请求，并提供搜索链接、使用建议和国内镜像站点推荐。

## 🛠️ 管理命令
```bash
# 查看版本
npm list -g smart-search-mcp

# 更新到最新版本
npm update -g smart-search-mcp

# 卸载
npm uninstall -g smart-search-mcp
```

## 📁 数据存储

工具会在工作目录创建以下目录和文件：

### `.ai_rules/` 目录
- `config.yaml` - 规则配置文件
- `mode_config.json` - 模式配置
- `plans.json` - 开发计划数据
- `pull_requests.json` - PR数据
- `feature_requests/` - 功能请求数据
- `collaboration/` - 协作消息存储（如果启用）

### `plan/` 目录（新增⭐）
AI自动生成的项目文档存储目录：
- `项目名-开发计划.md` - 完整的开发计划文档
- `modules/` - 模块拆解文档目录
  - `项目名-需求拆解.md` - 详细的模块和任务拆解
  - `项目名-TODO.md` - 快速任务清单

## 🎯 设计特点

- **🎯 智能需求分析（新）** - 自然语言交互，自动生成开发文档，模块化拆解任务
- **🎯 主功能突出** - 规则遵守提醒是核心功能
- **🔄 模式化工作** - Normal/Plan/PR/FR四种专门模式
- **🔎 智能搜索** - 14种搜索工具，支持国内外主流平台，特别优化国内网络访问
- **🐛 调试助手** - 5个控制台调试工具，快速诊断和解决前端问题
- **📁 文件化存储** - 轻量级实现，无需数据库，自动创建plan目录
- **🔧 高度可定制** - 支持项目特定的自定义规则
- **🤖 智能化** - AI主动发现问题并提出改进建议，支持交互式确认
- **🌏 国内优化** - 默认使用百度搜索，提供国内镜像站推荐
- **📚 全面覆盖** - 从需求分析到开发规范到错误调试，全流程AI辅助

## 📄 许可证

MIT License - 详见 LICENSE 文件