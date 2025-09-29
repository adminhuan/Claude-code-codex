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

### 1. 克隆项目
```bash
git clone https://github.com/adminhuan/Claude-code-codex.git
cd Claude-code-codex
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置Claude Code MCP
在Claude Code中配置MCP服务器：

1. 打开Claude Code设置
2. 找到MCP服务器配置选项
3. 添加以下配置（将路径替换为实际路径）：

```json
{
  "mcpServers": {
    "ai-rule-mcp": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/Claude-code-codex",
      "env": {}
    }
  }
}
```

> **注意**: 请将 `/path/to/Claude-code-codex` 替换为项目的实际绝对路径

### 4. 在Claude Code中使用
配置完成后，Claude Code会自动加载所有38个MCP工具：

- **规则提醒**: `ai_rule_reminder()` - 智能规则提醒
- **模式切换**: `ai_switch_mode()` - 切换工作模式
- **计划管理**: `ai_create_plan()` - 创建开发计划
- **代码审查**: `ai_create_pr()` - 创建PR审查
- **功能请求**: `ai_submit_feature_request()` - 提交改进建议
- 还有33个其他工具...

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

配置完成后，在Claude Code中你可以：

1. **直接请求规则提醒**: "请提醒我关于Python编码规范"
2. **切换工作模式**: "切换到Plan模式"，"切换到PR模式"
3. **创建开发计划**: "创建一个用户认证功能的开发计划"
4. **管理代码审查**: "创建一个PR来审查这个功能"
5. **提交功能请求**: "我建议增加代码格式化规则"

Claude Code会自动使用相应的MCP工具来响应你的请求。

## 🧪 测试工具
```bash
# 测试MCP工具功能
python test_ai_rules.py

# 查看使用示例
python example_usage.py
python example_mode_usage.py
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