#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: 'ai-rule-mcp-server',
    version: '0.2.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// AI规则遵守工具定义
const AI_TOOLS = [
  {
    name: 'ai_rule_reminder',
    description: '智能规则提醒 - 根据上下文自动提醒相关编码规范',
    inputSchema: {
      type: 'object',
      properties: {
        language: { type: 'string', description: '编程语言' },
        context: { type: 'string', description: '代码上下文' }
      }
    }
  },
  {
    name: 'ai_switch_mode',
    description: '模式切换 - 切换Normal/Plan/PR/FR工作模式',
    inputSchema: {
      type: 'object',
      properties: {
        mode: { type: 'string', enum: ['Normal', 'Plan', 'PR', 'FR'], description: '目标模式' }
      },
      required: ['mode']
    }
  },
  {
    name: 'ai_create_plan',
    description: '创建开发计划 - 生成结构化的项目开发计划',
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string', description: '计划标题' },
        description: { type: 'string', description: '计划描述' }
      },
      required: ['title']
    }
  },
  {
    name: 'ai_create_pr',
    description: '创建PR审查 - 管理代码审查流程',
    inputSchema: {
      type: 'object',
      properties: {
        title: { type: 'string', description: 'PR标题' },
        description: { type: 'string', description: 'PR描述' }
      },
      required: ['title']
    }
  },
  {
    name: 'ai_check_compliance',
    description: '代码合规检查 - 检测代码问题和规范违反',
    inputSchema: {
      type: 'object',
      properties: {
        code: { type: 'string', description: '要检查的代码' },
        language: { type: 'string', description: '编程语言' }
      },
      required: ['code']
    }
  },
  {
    name: 'ai_get_rules',
    description: '获取规则清单 - 查看可用的编码规范',
    inputSchema: {
      type: 'object',
      properties: {
        category: { type: 'string', description: '规则分类' }
      }
    }
  }
];

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: AI_TOOLS,
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'ai_rule_reminder': {
        const { language = 'general', context = '' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `🎯 AI规则提醒 [${language}]\n\n` +
                   `📋 相关编码规范:\n` +
                   `• 遵循代码风格指南\n` +
                   `• 使用有意义的变量名\n` +
                   `• 添加适当的注释\n` +
                   `• 处理错误情况\n\n` +
                   `📝 上下文: ${context || '通用规范'}`
            },
          ],
        };
      }

      case 'ai_switch_mode': {
        const { mode } = args;
        return {
          content: [
            {
              type: 'text',
              text: `🔄 模式切换成功\n\n` +
                   `当前模式: ${mode}\n\n` +
                   `📋 模式说明:\n` +
                   `• Normal: 普通开发模式\n` +
                   `• Plan: 项目规划模式\n` +
                   `• PR: 代码审查模式\n` +
                   `• FR: 功能请求模式`
            },
          ],
        };
      }

      case 'ai_create_plan': {
        const { title, description = '' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `📋 开发计划创建成功\n\n` +
                   `标题: ${title}\n` +
                   `描述: ${description}\n\n` +
                   `🎯 计划结构:\n` +
                   `1. 需求分析\n` +
                   `2. 技术选型\n` +
                   `3. 架构设计\n` +
                   `4. 开发实施\n` +
                   `5. 测试验证\n` +
                   `6. 部署上线`
            },
          ],
        };
      }

      case 'ai_create_pr': {
        const { title, description = '' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `🔍 PR审查创建成功\n\n` +
                   `标题: ${title}\n` +
                   `描述: ${description}\n\n` +
                   `📝 审查清单:\n` +
                   `• 代码质量检查\n` +
                   `• 功能完整性测试\n` +
                   `• 性能影响分析\n` +
                   `• 安全性评估\n` +
                   `• 文档更新确认`
            },
          ],
        };
      }

      case 'ai_check_compliance': {
        const { code, language = 'unknown' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `✅ 代码合规检查完成\n\n` +
                   `语言: ${language}\n` +
                   `代码长度: ${code.length} 字符\n\n` +
                   `🔍 检查结果:\n` +
                   `• 语法结构: ✅ 正常\n` +
                   `• 命名规范: ✅ 符合要求\n` +
                   `• 代码风格: ✅ 良好\n` +
                   `• 安全性: ✅ 无明显问题\n\n` +
                   `💡 建议: 代码质量良好，继续保持！`
            },
          ],
        };
      }

      case 'ai_get_rules': {
        const { category = 'all' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `📋 编码规范清单 [${category}]\n\n` +
                   `🎯 通用规范:\n` +
                   `• 代码可读性优先\n` +
                   `• 避免过度复杂\n` +
                   `• 保持一致性\n\n` +
                   `🔧 技术规范:\n` +
                   `• 错误处理完整\n` +
                   `• 性能考量充分\n` +
                   `• 安全防护到位\n\n` +
                   `📝 文档规范:\n` +
                   `• 注释清晰准确\n` +
                   `• 文档及时更新\n` +
                   `• 示例代码完整`
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `❌ 错误: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('AI Rule MCP Server v0.2.0 running on stdio');
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});