# AI规则遵守MCP工具 v0.1.0 发布说明

## 🎯 项目简介

AI规则遵守MCP工具是专为Claude Code设计的Model Context Protocol (MCP) 工具集，主要功能是智能提醒AI遵守编码规范和项目规则，同时提供可选的AI协作通信功能。

## ✨ 核心功能

### 📋 规则遵守提醒（主要功能）
- ✅ **智能提醒** - 根据代码上下文自动提醒相关编码规范
- ✅ **代码检查** - 检测常见的代码问题和规范违反
- ✅ **规则管理** - 查看和管理各类编码规范
- ✅ **自定义规则** - 添加项目特定的编码规范

### 🔄 多模式工作系统
- ✅ **Normal模式** - 基础规则提醒功能
- ✅ **Plan模式** - 开发计划制定和任务管理
- ✅ **PR模式** - 代码审查流程管理
- ✅ **FR模式** - 功能请求管理和AI投票

### 🤝 AI协作通信（可选功能）
- ✅ **协作开关** - 用户可选择开启/关闭协作功能
- ✅ **消息通信** - AI之间可以发送协作消息
- ✅ **状态同步** - 查看协作伙伴的工作状态

### 💡 功能请求管理
- ✅ **FR提交** - AI可以提出功能改进建议
- ✅ **投票系统** - AI之间可以对功能请求投票
- ✅ **智能建议** - 基于代码问题自动建议规则改进

## 🚀 快速开始

### 1. 安装依赖
```bash
cd cescc+codex
pip install -r requirements.txt
pip install -e .
```

### 2. 配置MCP服务器
将 `mcp_config.json` 添加到Claude Code的MCP配置中：

```json
{
  "mcpServers": {
    "ai-rule-mcp": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/cescc+codex",
      "env": {}
    }
  }
}
```

### 3. 启动MCP服务器
```bash
python3 mcp_server.py
```

### 4. 在Claude Code中使用

现在Claude Code可以直接使用所有MCP工具：

```python
# 获取规则提醒
await ai_rule_reminder("我要实现用户登录API")

# 切换到Plan模式
await ai_switch_mode("plan")

# 创建开发计划
await ai_create_plan("用户认证功能", "实现完整的用户登录注册系统", "claude_code")
```

## 📦 包含的文件

### 核心模块
- `ai_duet/mcp/tools.py` - 主要MCP工具函数接口
- `ai_duet/mcp/rule_checker.py` - 规则检查核心逻辑
- `ai_duet/mcp/mode_manager.py` - 模式管理系统
- `ai_duet/mcp/feature_requests.py` - 功能请求管理

### 服务器配置
- `mcp_server.py` - MCP服务器主程序
- `mcp_config.json` - MCP服务器配置示例

### 示例和测试
- `example_usage.py` - 基本功能使用示例
- `example_mode_usage.py` - 模式系统演示
- `example_fr_usage.py` - 功能请求系统演示
- `test_ai_rules.py` - 功能测试脚本

## 🛠️ 可用的MCP工具

### 主要功能
| 工具名称 | 功能描述 |
|---------|----------|
| `ai_rule_reminder` | 智能规则提醒 |
| `ai_check_compliance` | 代码合规检查 |
| `ai_get_rules` | 获取规则清单 |
| `ai_add_custom_rule` | 添加自定义规则 |

### 模式管理
| 工具名称 | 功能描述 |
|---------|----------|
| `ai_switch_mode` | 切换工作模式 |
| `ai_get_current_mode` | 获取当前模式 |
| `ai_list_modes` | 列出可用模式 |
| `ai_get_mode_statistics` | 获取模式统计 |

### Plan模式工具
| 工具名称 | 功能描述 |
|---------|----------|
| `ai_create_plan` | 创建开发计划 |
| `ai_add_task_to_plan` | 添加计划任务 |
| `ai_update_task_status` | 更新任务状态 |
| `ai_list_plans` | 列出所有计划 |

### PR模式工具
| 工具名称 | 功能描述 |
|---------|----------|
| `ai_create_pr` | 创建代码审查PR |
| `ai_add_review_comment` | 添加审查评论 |
| `ai_update_pr_status` | 更新PR状态 |
| `ai_list_prs` | 列出所有PR |

### FR功能工具
| 工具名称 | 功能描述 |
|---------|----------|
| `ai_submit_feature_request` | 提交功能请求 |
| `ai_vote_feature_request` | 对功能请求投票 |
| `ai_list_feature_requests` | 列出功能请求 |
| `ai_suggest_rule_improvements` | 智能规则建议 |

### 协作功能（可选）
| 工具名称 | 功能描述 |
|---------|----------|
| `ai_enable_collaboration` | 启用协作功能 |
| `ai_send_message` | 发送协作消息 |
| `ai_collaboration_status` | 查看协作状态 |

## 📁 数据存储

工具会在项目根目录创建 `.ai_rules/` 目录：
- `config.yaml` - 规则配置文件
- `mode_config.json` - 模式配置
- `plans.json` - 开发计划数据
- `pull_requests.json` - PR数据
- `feature_requests/requests.json` - 功能请求数据
- `collaboration/` - 协作消息存储（如果启用）

## 🎯 设计特点

- **🎯 主要功能突出**: 规则遵守提醒是核心功能
- **🔄 可选协作**: 用户可以选择是否启用AI间协作
- **📁 文件化存储**: 基于文件的轻量级实现，无需数据库
- **🎛️ 模式化工作**: 支持不同场景的专门工作模式
- **🔧 高度可定制**: 支持项目特定的自定义规则
- **🤖 智能化**: AI可以主动发现问题并提出改进建议

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 📞 支持

如果遇到问题，请：
1. 查看示例文件了解正确用法
2. 运行测试脚本检查环境配置
3. 提交Issue描述具体问题

---

🎉 **这个MCP工具现在已经可以发布使用了！**