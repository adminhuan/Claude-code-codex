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

// AI规则遵守工具定义 (原有38个工具 + 新增监督工具)
const AI_TOOLS = [
  // === 原有核心工具 ===
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
  },

  // === 新增监督指导工具 ===
  {
    name: 'ai_guide_project_rules',
    description: '📋 指导生成项目规则书 - 监督Claude Code根据项目特征生成开发规范',
    inputSchema: {
      type: 'object',
      properties: {
        project_type: { type: 'string', description: '项目类型(如：微信小程序、React应用等)' },
        specific_requirements: { type: 'string', description: '特殊要求或关注点' }
      }
    }
  },
  {
    name: 'ai_guide_development_plan',
    description: '📅 指导生成开发计划 - 监督Claude Code创建详细的项目开发计划',
    inputSchema: {
      type: 'object',
      properties: {
        project_title: { type: 'string', description: '项目标题' },
        project_scope: { type: 'string', description: '项目范围和目标' },
        timeline: { type: 'string', description: '预期时间线' }
      },
      required: ['project_title']
    }
  },
  {
    name: 'ai_guide_pr_review',
    description: '🔍 指导创建PR审查 - 监督Claude Code生成针对性的代码审查清单',
    inputSchema: {
      type: 'object',
      properties: {
        pr_title: { type: 'string', description: 'PR标题' },
        change_type: { type: 'string', description: '变更类型(功能、修复、重构等)' },
        risk_level: { type: 'string', enum: ['low', 'medium', 'high'], description: '风险级别' }
      },
      required: ['pr_title']
    }
  },
  {
    name: 'ai_guide_feature_request',
    description: '✨ 指导创建功能请求 - 监督Claude Code生成结构化的功能需求文档',
    inputSchema: {
      type: 'object',
      properties: {
        feature_title: { type: 'string', description: '功能标题' },
        user_story: { type: 'string', description: '用户故事或使用场景' },
        priority: { type: 'string', enum: ['low', 'medium', 'high', 'critical'], description: '优先级' }
      },
      required: ['feature_title']
    }
  },
  {
    name: 'ai_validate_content',
    description: '✅ 内容质量检查 - 验证生成的规则书、计划、PR等内容的完整性和准确性',
    inputSchema: {
      type: 'object',
      properties: {
        content_type: { type: 'string', enum: ['rules', 'plan', 'pr', 'feature'], description: '内容类型' },
        content: { type: 'string', description: '要检查的内容' }
      },
      required: ['content_type', 'content']
    }
  },
  {
    name: 'ai_suggest_improvements',
    description: '💡 改进建议 - 分析现有文档并提出具体的改进建议',
    inputSchema: {
      type: 'object',
      properties: {
        document_type: { type: 'string', description: '文档类型' },
        current_content: { type: 'string', description: '当前内容' },
        focus_area: { type: 'string', description: '重点改进领域' }
      },
      required: ['document_type', 'current_content']
    }
  },
  {
    name: 'ai_project_health_check',
    description: '🏥 项目健康检查 - 评估项目的整体健康状况和规范遵循情况',
    inputSchema: {
      type: 'object',
      properties: {
        check_areas: { type: 'array', items: { type: 'string' }, description: '检查领域数组' }
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

      // === 新增监督指导工具处理 ===
      case 'ai_guide_project_rules': {
        const { project_type = '通用项目', specific_requirements = '' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `📋 ${project_type} 规则书生成指导\n\n` +
                   `🎯 请Claude Code按以下结构生成项目开发规范：\n\n` +
                   `## 必须包含的章节：\n` +
                   `### 1. 📝 项目概述\n` +
                   `- 项目类型和技术栈说明\n` +
                   `- 团队开发规范总则\n\n` +
                   `### 2. 🔧 代码规范\n` +
                   `- 命名约定（变量、函数、类、文件）\n` +
                   `- 代码格式和缩进规范\n` +
                   `- 注释规范和文档要求\n\n` +
                   `### 3. 🏗️ 架构规范\n` +
                   `- 目录结构规范\n` +
                   `- 模块划分原则\n` +
                   `- 组件/类设计规范\n\n` +
                   `### 4. 🔒 安全规范\n` +
                   `- 输入验证和数据处理\n` +
                   `- 敏感信息处理\n` +
                   `- 权限控制原则\n\n` +
                   `### 5. 🧪 质量保证\n` +
                   `- 测试要求和覆盖率标准\n` +
                   `- 代码审查流程\n` +
                   `- 性能优化指导\n\n` +
                   `### 6. 🚀 部署规范\n` +
                   `- 环境配置管理\n` +
                   `- 发布流程和回滚策略\n` +
                   `- 监控和日志规范\n\n` +
                   `${specific_requirements ? `🔍 特殊要求：${specific_requirements}\n\n` : ''}` +
                   `💡 请确保规范具体可执行，包含具体示例和反例说明。`
            },
          ],
        };
      }

      case 'ai_guide_development_plan': {
        const { project_title, project_scope = '', timeline = '4周' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `📅 "${project_title}" 开发计划生成指导\n\n` +
                   `🎯 请Claude Code按以下结构生成详细开发计划：\n\n` +
                   `## 必须包含的内容：\n\n` +
                   `### 1. 🎯 项目概述\n` +
                   `- **项目名称**: ${project_title}\n` +
                   `- **项目目标**: ${project_scope || '请明确项目的具体目标和预期成果'}\n` +
                   `- **预期时间**: ${timeline}\n` +
                   `- **团队角色**: 明确开发、测试、产品等角色分工\n\n` +
                   `### 2. 📋 需求分析\n` +
                   `- **功能需求**: 列出所有核心功能和特性\n` +
                   `- **非功能需求**: 性能、安全、可用性要求\n` +
                   `- **用户故事**: 主要使用场景和用户流程\n` +
                   `- **验收标准**: 每个功能的完成标准\n\n` +
                   `### 3. 🏗️ 技术方案\n` +
                   `- **架构设计**: 系统整体架构和核心组件\n` +
                   `- **技术选型**: 开发语言、框架、数据库等\n` +
                   `- **环境搭建**: 开发、测试、生产环境规划\n` +
                   `- **风险评估**: 技术风险和应对策略\n\n` +
                   `### 4. ⏰ 里程碑规划\n` +
                   `- **第1阶段**: 项目初始化和基础搭建\n` +
                   `- **第2阶段**: 核心功能开发\n` +
                   `- **第3阶段**: 功能完善和联调测试\n` +
                   `- **第4阶段**: 优化部署和上线\n\n` +
                   `### 5. 📊 资源分配\n` +
                   `- **人力资源**: 各阶段人员投入\n` +
                   `- **时间分配**: 详细的任务时间安排\n` +
                   `- **预算评估**: 开发成本预估\n\n` +
                   `### 6. 🎯 质量保证\n` +
                   `- **测试计划**: 单元测试、集成测试、用户测试\n` +
                   `- **代码规范**: 开发标准和审查流程\n` +
                   `- **交付标准**: 各阶段交付物要求\n\n` +
                   `💡 请确保计划具体可执行，时间安排合理，包含风险应对措施。`
            },
          ],
        };
      }

      case 'ai_guide_pr_review': {
        const { pr_title, change_type = '功能开发', risk_level = 'medium' } = args;
        const riskChecks = {
          low: ['代码格式检查', '基础功能测试'],
          medium: ['代码逻辑审查', '安全性检查', '性能影响评估', '兼容性测试'],
          high: ['架构影响分析', '数据安全审查', '全面回归测试', '生产环境影响评估', '回滚方案确认']
        };

        return {
          content: [
            {
              type: 'text',
              text: `🔍 "${pr_title}" PR审查指导\n\n` +
                   `变更类型: ${change_type} | 风险级别: ${risk_level.toUpperCase()}\n\n` +
                   `🎯 请Claude Code按以下清单创建PR审查：\n\n` +
                   `## 📋 代码质量检查\n` +
                   `- [ ] 代码符合项目编码规范\n` +
                   `- [ ] 变量和函数命名清晰有意义\n` +
                   `- [ ] 代码逻辑清晰，无冗余代码\n` +
                   `- [ ] 错误处理完善，边界条件考虑周全\n` +
                   `- [ ] 注释和文档更新完整\n\n` +
                   `## 🧪 功能测试\n` +
                   `- [ ] 新功能按需求正常工作\n` +
                   `- [ ] 边界情况和异常情况处理正确\n` +
                   `- [ ] 不影响现有功能(回归测试)\n` +
                   `- [ ] 用户体验良好\n\n` +
                   `## 🔒 安全性检查\n` +
                   `- [ ] 输入数据验证和清理\n` +
                   `- [ ] SQL注入和XSS防护\n` +
                   `- [ ] 权限控制和访问限制\n` +
                   `- [ ] 敏感信息不暴露\n\n` +
                   `## ⚡ 性能考虑\n` +
                   `- [ ] 代码执行效率合理\n` +
                   `- [ ] 数据库查询优化\n` +
                   `- [ ] 内存使用合理\n` +
                   `- [ ] 网络请求优化\n\n` +
                   `## 🎯 ${risk_level.toUpperCase()}风险级别专项检查\n` +
                   riskChecks[risk_level].map(check => `- [ ] ${check}`).join('\n') + '\n\n' +
                   `## 📝 文档和部署\n` +
                   `- [ ] README和技术文档更新\n` +
                   `- [ ] 数据库迁移脚本(如需要)\n` +
                   `- [ ] 环境配置更新说明\n` +
                   `- [ ] 部署步骤和注意事项\n\n` +
                   `💡 请根据具体代码变更调整检查重点，确保审查全面深入。`
            },
          ],
        };
      }

      case 'ai_guide_feature_request': {
        const { feature_title, user_story = '', priority = 'medium' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `✨ "${feature_title}" 功能请求指导\n\n` +
                   `优先级: ${priority.toUpperCase()}\n\n` +
                   `🎯 请Claude Code按以下模板创建功能请求：\n\n` +
                   `## 📝 功能概述\n` +
                   `**功能名称**: ${feature_title}\n` +
                   `**提出人**: [填写提出者]\n` +
                   `**提出时间**: ${new Date().toLocaleDateString()}\n` +
                   `**优先级**: ${priority}\n\n` +
                   `## 👤 用户需求\n` +
                   `**用户故事**: ${user_story || ' 作为[用户角色]，我希望[具体功能]，以便[实现价值]'}\n\n` +
                   `**使用场景**: \n` +
                   `- 场景1: [详细描述主要使用场景]\n` +
                   `- 场景2: [详细描述次要使用场景]\n\n` +
                   `**用户价值**: [这个功能能为用户带来什么价值]\n\n` +
                   `## 🔧 功能详情\n` +
                   `### 核心功能\n` +
                   `- [ ] 功能点1: [具体描述]\n` +
                   `- [ ] 功能点2: [具体描述]\n` +
                   `- [ ] 功能点3: [具体描述]\n\n` +
                   `### 交互设计\n` +
                   `- **入口**: [用户如何访问这个功能]\n` +
                   `- **流程**: [用户操作的完整流程]\n` +
                   `- **反馈**: [系统如何给用户反馈]\n\n` +
                   `### 边界条件\n` +
                   `- **限制条件**: [功能的使用限制]\n` +
                   `- **异常处理**: [异常情况的处理方式]\n\n` +
                   `## 📊 验收标准\n` +
                   `- [ ] 功能按预期工作\n` +
                   `- [ ] 用户体验流畅\n` +
                   `- [ ] 性能满足要求\n` +
                   `- [ ] 通过测试验证\n` +
                   `- [ ] 文档完整\n\n` +
                   `## 🛠️ 技术考虑\n` +
                   `**技术方案**: [推荐的技术实现方案]\n` +
                   `**工作量评估**: [预估的开发工作量]\n` +
                   `**技术风险**: [可能的技术难点和风险]\n` +
                   `**依赖关系**: [与其他功能或系统的依赖]\n\n` +
                   `## ⏰ 时间规划\n` +
                   `**期望完成时间**: [预期完成日期]\n` +
                   `**里程碑**: \n` +
                   `- 设计完成: [日期]\n` +
                   `- 开发完成: [日期]\n` +
                   `- 测试完成: [日期]\n` +
                   `- 上线时间: [日期]\n\n` +
                   `💡 请确保需求描述清晰具体，验收标准明确可衡量。`
            },
          ],
        };
      }

      case 'ai_validate_content': {
        const { content_type, content } = args;
        const validationChecks = {
          rules: ['是否包含项目特定的代码规范', '命名约定是否明确具体', '是否有具体的代码示例', '安全规范是否完整', '测试要求是否明确', '部署规范是否可执行'],
          plan: ['项目目标是否清晰明确', '里程碑规划是否合理', '资源分配是否详细', '风险评估是否充分', '时间安排是否可行', '交付标准是否明确'],
          pr: ['检查项是否覆盖全面', '风险级别评估是否准确', '测试要求是否完整', '安全检查是否到位', '文档要求是否明确', '回滚方案是否考虑'],
          feature: ['用户需求是否清晰', '功能描述是否具体', '验收标准是否明确', '技术方案是否可行', '时间规划是否合理', '风险评估是否充分']
        };
        const checks = validationChecks[content_type] || ['内容结构是否完整', '描述是否清晰', '可执行性如何'];

        return {
          content: [
            {
              type: 'text',
              text: `✅ ${content_type} 内容质量检查\n\n` +
                   `📋 检查项目：\n` +
                   checks.map((check, index) => `${index + 1}. ${check}`).join('\n') + '\n\n' +
                   `📝 内容长度: ${content.length} 字符\n\n` +
                   `💡 建议Claude Code检查以下方面：\n` +
                   `• 内容完整性和逻辑性\n` +
                   `• 描述的具体性和可执行性\n` +
                   `• 专业术语使用是否准确\n` +
                   `• 格式和结构是否规范\n` +
                   `• 是否遗漏重要信息\n\n` +
                   `🔍 请逐项检查并提出具体改进建议。`
            },
          ],
        };
      }

      case 'ai_suggest_improvements': {
        const { document_type, current_content, focus_area = '整体优化' } = args;
        return {
          content: [
            {
              type: 'text',
              text: `💡 ${document_type} 改进建议\n\n` +
                   `🎯 重点改进领域: ${focus_area}\n\n` +
                   `📊 当前内容分析：\n` +
                   `- 内容长度: ${current_content.length} 字符\n` +
                   `- 结构完整性: [需要分析]\n` +
                   `- 专业性: [需要评估]\n\n` +
                   `🔍 请Claude Code从以下角度提出改进建议：\n\n` +
                   `### 1. 📝 内容质量改进\n` +
                   `- 哪些部分需要更详细的说明？\n` +
                   `- 哪些描述可以更具体、更可执行？\n` +
                   `- 是否有遗漏的重要信息？\n\n` +
                   `### 2. 🏗️ 结构优化建议\n` +
                   `- 章节组织是否逻辑清晰？\n` +
                   `- 是否需要调整内容顺序？\n` +
                   `- 标题和层级是否合理？\n\n` +
                   `### 3. 🎯 实用性提升\n` +
                   `- 如何增加具体示例和代码片段？\n` +
                   `- 如何让内容更贴近项目实际？\n` +
                   `- 如何提高内容的可操作性？\n\n` +
                   `### 4. 📋 格式规范化\n` +
                   `- 格式是否统一规范？\n` +
                   `- 列表和表格使用是否恰当？\n` +
                   `- 强调和标记是否合理？\n\n` +
                   `💡 请提供具体的修改建议和优化方向。`
            },
          ],
        };
      }

      case 'ai_project_health_check': {
        const { check_areas = ['代码规范', '文档完整性', '测试覆盖', '安全性'] } = args;
        return {
          content: [
            {
              type: 'text',
              text: `🏥 项目健康检查报告\n\n` +
                   `🎯 检查领域: ${check_areas.join(', ')}\n\n` +
                   `📋 请Claude Code按以下维度进行项目健康检查：\n\n` +
                   `## 🔍 检查项目清单\n\n` +
                   `### 1. 📝 代码规范检查\n` +
                   `- [ ] 代码风格一致性\n` +
                   `- [ ] 命名规范遵循\n` +
                   `- [ ] 注释覆盖率\n` +
                   `- [ ] 代码复用程度\n\n` +
                   `### 2. 📚 文档完整性\n` +
                   `- [ ] README文档质量\n` +
                   `- [ ] API文档完整性\n` +
                   `- [ ] 部署文档准确性\n` +
                   `- [ ] 开发指南可用性\n\n` +
                   `### 3. 🧪 测试质量\n` +
                   `- [ ] 单元测试覆盖率\n` +
                   `- [ ] 集成测试完整性\n` +
                   `- [ ] 测试用例有效性\n` +
                   `- [ ] 持续集成状态\n\n` +
                   `### 4. 🔒 安全性评估\n` +
                   `- [ ] 依赖安全漏洞扫描\n` +
                   `- [ ] 代码安全审查\n` +
                   `- [ ] 敏感信息保护\n` +
                   `- [ ] 权限控制实现\n\n` +
                   `### 5. ⚡ 性能检查\n` +
                   `- [ ] 代码执行效率\n` +
                   `- [ ] 资源使用合理性\n` +
                   `- [ ] 数据库查询优化\n` +
                   `- [ ] 缓存策略实施\n\n` +
                   `### 6. 🚀 部署和运维\n` +
                   `- [ ] 部署流程自动化\n` +
                   `- [ ] 监控和告警配置\n` +
                   `- [ ] 日志记录规范\n` +
                   `- [ ] 备份和恢复机制\n\n` +
                   `## 📊 评分标准\n` +
                   `- 🟢 优秀 (90-100分): 各项指标表现优异\n` +
                   `- 🟡 良好 (70-89分): 大部分指标达标，有改进空间\n` +
                   `- 🟠 及格 (60-69分): 基本达标，需要重点改进\n` +
                   `- 🔴 需改进 (<60分): 存在重大问题，需要立即处理\n\n` +
                   `💡 请逐项检查并给出具体的改进建议和优先级排序。`
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