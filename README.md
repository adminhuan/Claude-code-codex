# 🤖 AI Duet

**Claude Code 与 OpenAI 智能协作系统**

AI Duet 是一个先进的AI协作框架，让Claude Code和OpenAI GPT-4能够以不同角色（执行者、审核者、协调者）协同工作，完成复杂的编程任务。

## ✨ 特性

- 🎭 **多角色协作**：执行者、审核者、协调者角色自由分配
- 🔄 **确定性状态机**：分析→提案→实现→审核→完成的可预测流程
- 🛡️ **统一安全沙箱**：安全的文件操作和命令执行
- 📊 **严格JSON协议**：强制结构化通信，避免格式错误
- 🔧 **工具执行能力**：支持文件读写、命令执行、测试运行
- 🌐 **自定义API端点**：支持中转API，突破地域限制
- 📝 **完整日志记录**：对话记录、性能统计、错误追踪
- 🎨 **彩色终端输出**：直观的进度显示和状态追踪

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone <your-repo-url>
cd cescc+codex

# 自动安装（推荐）
./install.sh

# 或手动安装
pip install -r requirements.txt
pip install -e .
```

### 2. 配置API密钥

```bash
# 官方API
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# 或使用中转API
export OPENAI_BASE_URL="https://your-proxy.com/v1"
export ANTHROPIC_BASE_URL="https://your-claude-proxy.com/v1"
export OPENAI_API_KEY="your-proxy-openai-key"
export ANTHROPIC_API_KEY="your-proxy-claude-key"
```

### 3. 运行第一个协作任务

```bash
# 基础用法
python -m ai_duet "实现一个用户登录验证函数"

# 指定角色分工
python -m ai_duet "优化这个排序算法" --claude-role executor --openai-role reviewer

# 启用文件操作
python -m ai_duet "修复src/auth.py中的bug" --with-files --project-root ./
```

## 📋 使用示例

### 协作模式示例

```bash
# 调试模式：Claude执行修复，OpenAI审核
python -m ai_duet "调试登录超时问题" \
  --type debug \
  --claude-role executor \
  --openai-role reviewer \
  --with-files

# 设计模式：平等讨论架构方案
python -m ai_duet "设计微服务用户管理系统" \
  --type design \
  --claude-role facilitator \
  --openai-role reviewer \
  --max-turns 15

# 代码审查：OpenAI提出问题，Claude解答
python -m ai_duet "审查支付处理模块安全性" \
  --type review \
  --openai-role executor \
  --claude-role reviewer
```

### 配置参数

```bash
# 模型选择
python -m ai_duet "任务描述" \
  --openai-model gpt-4o \
  --claude-model claude-3-5-sonnet-20240620

# 控制参数
python -m ai_duet "任务描述" \
  --max-turns 20 \
  --temperature 0.7 \
  --budget 30000 \
  --verbose

# 试运行模式
python -m ai_duet "任务描述" --dry-run
```

## 🎭 角色说明

### 执行者 (Executor)
- 负责分析问题并提出解决方案
- 编写和修改代码
- 执行测试验证
- 使用工具完成实际操作

### 审核者 (Reviewer)
- 审查执行者的方案
- 发现潜在问题和风险
- 提供改进建议
- 验证代码质量

### 协调者 (Facilitator)
- 推进讨论进程
- 协调双方观点
- 做出关键决策
- 确保任务聚焦

## 🛠️ 工具能力

当启用 `--with-files` 时，Claude Code 可以使用：

- `fs_read`: 读取文件内容
- `fs_write`: 写入文件（安全限制）
- `fs_list`: 列出目录内容
- `run_command`: 执行安全命令

## 📊 输出格式

协作过程中会显示：

```
🚀 开始AI协作任务
任务: 实现用户登录验证

--- 第 1 轮 ---
🔧 执行者 (claude)
阶段: analysis | 状态: handoff
分析用户登录需求，需要验证用户名密码格式...

🔧 工具调用:
  └── fs_read: {"path": "src/auth.py"}

💬 评审意见:
  • 请审查这个分析是否完整
  • 还需要考虑哪些安全因素？

--- 第 2 轮 ---
👁 审核者 (openai)
阶段: analysis | 状态: handoff
分析合理，建议增加速率限制和密码强度检查...
```

## 🔧 配置选项

### 环境变量
```bash
# API配置
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620

# 协作配置
CLAUDE_ROLE=executor
OPENAI_ROLE=reviewer
TASK_TYPE=implement
MAX_TURNS=10

# 功能开关
ENABLE_FILE_OPS=true
PROJECT_ROOT=/path/to/project
VERBOSE=true
```

### CLI参数优先级
CLI参数 > 环境变量 > 默认值

## 📁 项目结构

```
ai_duet/
├── agents/              # AI代理实现
│   ├── base_agent.py   # 基础代理类
│   ├── claude_agent.py # Claude代理
│   └── openai_agent.py # OpenAI代理
├── protocols/          # 协议定义
│   ├── conversation.py # 对话管理
│   └── roles.py        # 角色定义
├── utils/              # 工具类
│   ├── config.py       # 配置管理
│   ├── logger.py       # 日志输出
│   └── safety.py       # 安全控制
├── examples/           # 示例任务
└── duet.py            # 主协调器
```

## 🎯 示例任务

查看内置示例任务：
```bash
python -m ai_duet.examples.sample_tasks
```

包含以下类型：
- **调试任务**: 找出并修复bug
- **代码审查**: 评估代码质量和安全性
- **系统设计**: 架构方案讨论
- **功能实现**: 编写新功能代码
- **综合任务**: 复杂的多步骤项目

## 🔒 安全考虑

- 文件操作限制在安全路径内
- 命令执行采用白名单机制
- 自动检测和阻止危险操作
- 支持沙箱模式和试运行
- Token使用量监控和限制

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. **JSON解析错误**
   - 模型可能返回非JSON格式
   - 尝试降低temperature参数
   - 检查是否使用了支持JSON模式的模型

3. **文件权限问题**
   ```bash
   # 检查项目根目录权限
   ls -la /path/to/project
   ```

4. **网络连接问题**
   - 检查网络连接
   - 验证API服务状态
   - 考虑使用代理

### 调试模式

```bash
# 详细输出
python -m ai_duet "任务" --verbose

# 试运行（不调用API）
python -m ai_duet "任务" --dry-run

# 查看配置
python -m ai_duet --print-config
```

## 🌐 自定义API端点

支持OpenAI和Claude兼容的中转API服务，详见 [CUSTOM_API_USAGE.md](CUSTOM_API_USAGE.md)

```bash
# OpenAI中转
export OPENAI_BASE_URL="https://your-openai-proxy.com/v1"
export OPENAI_API_KEY="your-proxy-key"

# Claude中转
export ANTHROPIC_BASE_URL="https://your-claude-proxy.com/v1"
export ANTHROPIC_API_KEY="your-proxy-key"
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 感谢 Anthropic 的 Claude API
- 感谢 OpenAI 的 GPT API
- 灵感来源于协作编程的最佳实践

---

*AI Duet - 让AI协作变得简单而强大* 🎵