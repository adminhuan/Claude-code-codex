# 🔧 自定义API端点使用指南

## 📋 环境变量配置

如果您使用的是自定义的中转API接口，可以通过以下环境变量配置：

### OpenAI中转接口
```bash
# 官方接口（默认）
export OPENAI_API_KEY="your-openai-api-key"

# 自定义中转接口
export OPENAI_API_KEY="your-proxy-api-key"
export OPENAI_BASE_URL="https://your-proxy-domain.com/v1"
```

### Anthropic中转接口
```bash
# 官方接口（默认）
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# 自定义中转接口
export ANTHROPIC_API_KEY="your-proxy-api-key"
export ANTHROPIC_BASE_URL="https://your-claude-proxy.com/v1"
```

## 🚀 使用示例

### 1. 使用官方API（默认）
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

python -m ai_duet "debug user login issue" --dry-run
```

### 2. 使用中转API
```bash
# 设置中转端点
export OPENAI_API_KEY="your-proxy-key"
export OPENAI_BASE_URL="https://api.openai-proxy.com/v1"

export ANTHROPIC_API_KEY="your-claude-proxy-key"
export ANTHROPIC_BASE_URL="https://claude.proxy-service.com/v1"

# 运行AI协作
python -m ai_duet "implement user registration" --type implement --verbose
```

### 3. 只使用一个中转API
```bash
# 只中转OpenAI，Claude使用官方
export OPENAI_API_KEY="proxy-key"
export OPENAI_BASE_URL="https://openai-proxy.com/v1"
export ANTHROPIC_API_KEY="sk-ant-official-key"

python -m ai_duet "code review task"
```

## ⚙️ 支持的中转格式

### OpenAI兼容接口
- 支持标准的 `/v1/chat/completions` 端点
- 兼容OpenAI API格式的响应
- 常见中转服务：OneAPI、FastGPT等

### Anthropic兼容接口
- 支持 `/v1/messages` 端点
- 兼容Claude API格式
- 需要支持Claude的message结构

## 🔧 配置验证

使用 `--print-config` 查看当前配置：

```bash
python -m ai_duet "test" --print-config
```

输出示例：
```
=== AI Duet Config ===
Claude role: executor (model: claude-3-5-sonnet-20240620)
OpenAI role: reviewer (model: gpt-4o-mini)
Task type: implement
Max turns: 10
First speaker: claude
File ops: off
Token budget: 50000
Dry run: off
Base URLs:
  OpenAI: https://api.openai-proxy.com/v1
  Claude: https://claude-proxy.com/v1
==============================
```

## 🛡️ 安全注意事项

1. **API密钥安全**：使用中转服务时，确保您的API密钥安全
2. **数据隐私**：了解中转服务的数据处理政策
3. **服务可靠性**：确保中转服务的稳定性和响应速度
4. **费用控制**：通过 `--budget` 参数控制token使用量

## 🐛 常见问题

### 1. 连接失败
```
Error: Connection failed to custom endpoint
```
**解决**：检查base_url格式，确保包含协议(https://)和正确路径

### 2. 认证错误
```
Error: Invalid API key for custom endpoint
```
**解决**：确认中转服务的API密钥格式要求

### 3. 响应格式错误
```
Error: Invalid response format from proxy
```
**解决**：确保中转服务完全兼容对应的官方API格式

## 📞 技术支持

如遇到中转API相关问题，请检查：
1. 网络连通性
2. API密钥有效性
3. 中转服务状态
4. 请求格式兼容性

---

**提示**：建议先使用 `--dry-run` 模式测试配置，确保设置正确后再进行实际的AI协作。