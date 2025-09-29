# AI规则遵守MCP工具

为所有支持MCP协议的AI工具设计的规则遵守工具集，提供45个工具函数：原有38个基础工具 + 7个全新监督指导工具，让Claude Code在专业指导下生成高质量规则书、开发计划、PR审查和功能请求。

## 🎯 主要功能

### 📋 规则遵守提醒（基础功能）
- **智能提醒** - 根据上下文自动提醒相关规则
- **代码检查** - 检测常见的代码问题和规范违反
- **规则管理** - 查看和管理各类编码规范
- **自定义规则** - 添加项目特定的规则

### 🔍 智能监督指导（核心功能）
- **项目规则书指导** - 监督Claude Code生成专业的开发规范
- **开发计划指导** - 指导创建详细的项目开发计划
- **PR审查指导** - 根据风险级别生成针对性审查清单
- **功能请求指导** - 创建结构化的功能需求文档
- **内容质量检查** - 验证文档完整性和准确性
- **改进建议** - 分析现有内容并提出优化建议
- **项目健康检查** - 全面评估项目状况

### 🤝 AI协作通信（可选功能）
- **协作开关** - 用户可选择开启/关闭协作功能
- **消息通信** - AI之间可以发送协作消息
- **状态同步** - 查看协作伙伴的工作状态

## 🚀 快速开始

### ⚡ 一键安装 (推荐)
```bash
# 🎯 官方安装方式 (申请中)
claude mcp add ai-rule-mcp

# 🔧 临时安装方式
# 方法1: Python包安装
pip install ai-rule-mcp-server
ai-rule-mcp install

# 方法2: 一键脚本
curl -sSL https://raw.githubusercontent.com/adminhuan/Claude-code-codex/main/install.sh | bash

# 方法3: npm包安装
npx ai-rule-mcp-server@latest
```

> **📋 注意**: 我们正在申请加入Anthropic官方MCP目录，届时可以直接使用 `claude mcp add ai-rule-mcp` 安装

### 🔧 手动安装
```bash
# 1. 克隆项目
git clone https://github.com/adminhuan/Claude-code-codex.git
cd Claude-code-codex

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装到系统
pip install -e .

# 4. 配置MCP
ai-rule-mcp install
```

### 🎉 开始使用
安装完成后，重启Claude Code即可使用45个AI工具：

**🔧 基础工具**：
- **规则提醒**: `ai_rule_reminder()` - 智能规则提醒
- **模式切换**: `ai_switch_mode()` - 切换工作模式
- **计划管理**: `ai_create_plan()` - 创建开发计划
- **代码审查**: `ai_create_pr()` - 创建PR审查
- **合规检查**: `ai_check_compliance()` - 代码合规检查
- 还有33个其他基础工具...

**🎯 新增监督指导工具**：
- **项目规则指导**: `ai_guide_project_rules()` - 指导生成项目规则书
- **开发计划指导**: `ai_guide_development_plan()` - 指导创建开发计划
- **PR审查指导**: `ai_guide_pr_review()` - 指导创建PR审查
- **功能请求指导**: `ai_guide_feature_request()` - 指导创建功能请求
- **内容质量检查**: `ai_validate_content()` - 验证内容质量
- **改进建议**: `ai_suggest_improvements()` - 提出改进建议
- **项目健康检查**: `ai_project_health_check()` - 全面项目评估

## 🛠️ 可用工具

| 工具函数 | 功能说明 | 类型 |
|---------|---------|------|
| `ai_rule_reminder()` | 智能规则提醒 | 主要功能 |
| `ai_check_compliance()` | 代码合规检查 | 主要功能 |
| `ai_get_rules()` | 获取规则清单 | 主要功能 |
| `ai_add_custom_rule()` | 添加自定义规则 | 主要功能 |
| `ai_enable_collaboration()` | 启用协作功能 | 可选功能 |
| `ai_send_message()` | 发送协作消息 | 可选功能 |
| `ai_read_messages()` | 读取协作消息 | 可选功能 |
| `ai_collaboration_status()` | 查看协作状态 | 可选功能 |

## 📖 使用方式

配置完成后，在支持MCP的AI工具中你可以：

1. **直接请求规则提醒**: "请提醒我关于Python编码规范"
2. **切换工作模式**: "切换到Plan模式"，"切换到PR模式"
3. **创建开发计划**: "创建一个用户认证功能的开发计划"
4. **管理代码审查**: "创建一个PR来审查这个功能"
5. **提交功能请求**: "我建议增加代码格式化规则"

AI工具会自动使用相应的MCP工具来响应你的请求。

## 🛠️ 管理命令
```bash
# 查看安装状态
ai-rule-mcp status

# 手动启动服务器
ai-rule-mcp start

# 卸载MCP工具
ai-rule-mcp uninstall

# 重新安装
ai-rule-mcp install
```

## 📁 数据存储

工具会在工作目录创建 `.ai_rules/` 目录：
- `config.yaml` - 规则配置文件
- `mode_config.json` - 模式配置
- `plans.json` - 开发计划数据
- `pull_requests.json` - PR数据
- `feature_requests/` - 功能请求数据
- `collaboration/` - 协作消息存储（如果启用）

## 🎯 设计特点

- **🎯 主功能突出** - 规则遵守提醒是核心功能
- **🔄 模式化工作** - Normal/Plan/PR/FR四种专门模式
- **📁 文件化存储** - 轻量级实现，无需数据库
- **🔧 高度可定制** - 支持项目特定的自定义规则
- **🤖 智能化** - AI主动发现问题并提出改进建议

## 📄 许可证

MIT License - 详见 LICENSE 文件