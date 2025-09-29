# AI规则遵守MCP工具

一个专为Claude Code和Codex设计的MCP工具集，主要功能是提醒AI遵守编码规范和项目规则，可选的AI协作通信功能。

## 🎯 主要功能

### 📋 规则遵守提醒（主要功能）
- **智能提醒** - 根据上下文自动提醒相关规则
- **代码检查** - 检测常见的代码问题和规范违反
- **规则管理** - 查看和管理各类编码规范
- **自定义规则** - 添加项目特定的规则

### 🤝 AI协作通信（可选功能）
- **协作开关** - 用户可选择开启/关闭协作功能
- **消息通信** - AI之间可以发送协作消息
- **状态同步** - 查看协作伙伴的工作状态

## 🚀 快速开始

### 安装
```bash
pip install -r requirements.txt
pip install -e .
```

### 基本使用
```python
from ai_duet.mcp.tools import ai_rule_reminder, ai_check_compliance

# 获取规则提醒
reminder = await ai_rule_reminder("我要实现用户登录API")

# 检查代码合规性
result = await ai_check_compliance(your_code)
```

### 开启协作功能（可选）
```python
from ai_duet.mcp.tools import ai_enable_collaboration, ai_send_message

# 启用协作
await ai_enable_collaboration(True)

# 发送消息给协作伙伴
await ai_send_message("开始实现认证功能", "claude_code")
```

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

## 📖 使用示例

查看 `example_usage.py` 获取详细的使用示例。

运行测试：
```bash
python test_ai_rules.py
```

## 📁 规则配置

工具会在项目根目录创建 `.ai_rules/` 目录：
- `config.yaml` - 规则配置文件
- `collaboration/` - 协作消息存储（如果启用）

## 🎯 设计理念

- **主要功能**：帮助AI遵守编码规范和项目规则
- **可选协作**：用户可以选择是否启用AI间的协作通信
- **简单可靠**：基于文件的轻量级实现
- **高度可定制**：支持项目特定的自定义规则

## 📄 许可证

MIT License - 详见 LICENSE 文件