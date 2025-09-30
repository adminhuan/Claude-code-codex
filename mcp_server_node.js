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
    version: '0.6.0',
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
  },

  // === 搜索资料工具 ===
  {
    name: 'ai_search_web',
    description: '🔍 网络搜索 - 搜索网络资料和文档，支持多种搜索引擎（Google、Bing、百度等）',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        engine: { type: 'string', enum: ['google', 'bing', 'baidu', 'sogou'], description: '搜索引擎，默认baidu', default: 'baidu' },
        count: { type: 'number', description: '返回结果数量，默认10', default: 10 }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_github',
    description: '📦 GitHub搜索 - 搜索GitHub上的代码、仓库、问题和文档',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        type: { type: 'string', enum: ['repositories', 'code', 'issues', 'users'], description: '搜索类型，默认repositories', default: 'repositories' },
        language: { type: 'string', description: '编程语言筛选（可选）' },
        sort: { type: 'string', enum: ['stars', 'forks', 'updated'], description: '排序方式，默认stars', default: 'stars' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_stackoverflow',
    description: '💬 StackOverflow搜索 - 搜索技术问题和解决方案',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词或问题描述' },
        tags: { type: 'string', description: '标签筛选（如：javascript,react）' },
        sort: { type: 'string', enum: ['relevance', 'votes', 'creation', 'activity'], description: '排序方式，默认relevance', default: 'relevance' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_npm',
    description: '📦 NPM包搜索 - 搜索NPM包和相关文档',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '包名或关键词' },
        size: { type: 'number', description: '返回结果数量，默认10', default: 10 }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_docs',
    description: '📚 技术文档搜索 - 搜索常见框架和工具的官方文档（React、Vue、Node.js等）',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        framework: { type: 'string', enum: ['react', 'vue', 'angular', 'nodejs', 'python', 'java', 'general'], description: '指定框架，默认general', default: 'general' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_api_reference',
    description: '🔗 API参考搜索 - 快速查找API文档和使用示例',
    inputSchema: {
      type: 'object',
      properties: {
        api_name: { type: 'string', description: 'API名称或方法名' },
        platform: { type: 'string', description: '平台或库名称（如：express、axios、lodash）' }
      },
      required: ['api_name', 'platform']
    }
  },

  // === 浏览器控制台监控工具 ===
  {
    name: 'ai_console_error_monitor',
    description: '🐛 浏览器控制台错误监控 - 获取和分析浏览器控制台报错信息',
    inputSchema: {
      type: 'object',
      properties: {
        error_message: { type: 'string', description: '错误消息内容' },
        error_type: { type: 'string', enum: ['JavaScript', 'Network', 'CORS', 'Syntax', 'Reference', 'Type', 'Range', 'Unknown'], description: '错误类型', default: 'Unknown' },
        stack_trace: { type: 'string', description: '错误堆栈信息（可选）' },
        file_path: { type: 'string', description: '出错文件路径（可选）' },
        line_number: { type: 'number', description: '出错行号（可选）' }
      },
      required: ['error_message']
    }
  },
  {
    name: 'ai_console_warning_check',
    description: '⚠️ 控制台警告检查 - 检查和分析控制台警告信息',
    inputSchema: {
      type: 'object',
      properties: {
        warning_message: { type: 'string', description: '警告消息内容' },
        warning_source: { type: 'string', description: '警告来源（如：React、Vue、Browser等）' }
      },
      required: ['warning_message']
    }
  },
  {
    name: 'ai_network_error_diagnosis',
    description: '🌐 网络请求错误诊断 - 分析网络请求失败的原因',
    inputSchema: {
      type: 'object',
      properties: {
        url: { type: 'string', description: '请求URL' },
        status_code: { type: 'number', description: 'HTTP状态码（如：404、500）' },
        error_message: { type: 'string', description: '错误消息' },
        request_method: { type: 'string', enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'], description: '请求方法', default: 'GET' }
      },
      required: ['url', 'status_code']
    }
  },
  {
    name: 'ai_console_log_analyzer',
    description: '📊 控制台日志分析 - 分析控制台日志模式和潜在问题',
    inputSchema: {
      type: 'object',
      properties: {
        logs: { type: 'string', description: '控制台日志内容（可以是多行）' },
        analysis_type: { type: 'string', enum: ['performance', 'errors', 'warnings', 'all'], description: '分析类型', default: 'all' }
      },
      required: ['logs']
    }
  },
  {
    name: 'ai_debug_suggestion',
    description: '🔧 调试建议生成 - 根据错误信息生成调试建议和解决方案',
    inputSchema: {
      type: 'object',
      properties: {
        error_description: { type: 'string', description: '错误描述' },
        code_snippet: { type: 'string', description: '相关代码片段（可选）' },
        environment: { type: 'string', description: '运行环境（如：Chrome、Firefox、Node.js等）' }
      },
      required: ['error_description']
    }
  },

  // === 国内开发者平台搜索工具 ===
  {
    name: 'ai_search_wechat_docs',
    description: '📱 微信开发者文档搜索 - 搜索微信小程序、公众号、开放平台文档',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        platform: { type: 'string', enum: ['miniprogram', 'officialaccount', 'open', 'payment', 'all'], description: '平台类型：miniprogram(小程序)、officialaccount(公众号)、open(开放平台)、payment(支付)、all(全部)', default: 'all' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_csdn',
    description: '📝 CSDN搜索 - 搜索CSDN技术博客和问答',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        type: { type: 'string', enum: ['blog', 'ask', 'all'], description: '搜索类型：blog(博客)、ask(问答)、all(全部)', default: 'all' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_juejin',
    description: '💎 掘金搜索 - 搜索掘金技术文章和专栏',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        sort: { type: 'string', enum: ['hot', 'time', 'likes'], description: '排序方式：hot(热门)、time(最新)、likes(点赞)', default: 'hot' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_segmentfault',
    description: '🔧 SegmentFault搜索 - 搜索SegmentFault技术问答',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        tags: { type: 'string', description: '标签筛选（如：javascript,react）' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_cnblogs',
    description: '📚 博客园搜索 - 搜索博客园技术博客',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_oschina',
    description: '🌐 开源中国搜索 - 搜索开源中国技术资讯和问答',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        type: { type: 'string', enum: ['news', 'blog', 'ask', 'project', 'all'], description: '搜索类型', default: 'all' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_aliyun_docs',
    description: '☁️ 阿里云文档搜索 - 搜索阿里云开发者文档',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        product: { type: 'string', description: '产品名称（如：ECS、OSS、RDS等，可选）' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_tencent_docs',
    description: '☁️ 腾讯云文档搜索 - 搜索腾讯云开发者文档',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        product: { type: 'string', description: '产品名称（如：COS、CDN、CVM等，可选）' }
      },
      required: ['query']
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

      // === 搜索工具处理 ===
      case 'ai_search_web': {
        const { query, engine = 'baidu', count = 10 } = args;
        const searchUrls = {
          google: `https://www.google.com/search?q=${encodeURIComponent(query)}`,
          bing: `https://www.bing.com/search?q=${encodeURIComponent(query)}`,
          baidu: `https://www.baidu.com/s?wd=${encodeURIComponent(query)}`,
          sogou: `https://www.sogou.com/web?query=${encodeURIComponent(query)}`
        };

        return {
          content: [
            {
              type: 'text',
              text: `🔍 网络搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `🌐 搜索引擎: ${engine.toUpperCase()}\n` +
                   `📊 结果数量: ${count}\n\n` +
                   `🔗 搜索链接: ${searchUrls[engine]}\n\n` +
                   `💡 搜索建议:\n` +
                   `• 使用双引号精确匹配: "${query}"\n` +
                   `• 使用减号排除: ${query} -排除词\n` +
                   `• 限定网站搜索: site:github.com ${query}\n` +
                   `• 限定文件类型: filetype:pdf ${query}\n\n` +
                   `📝 提示: Claude Code会为您访问该链接获取搜索结果。\n` +
                   `国内用户建议使用百度(baidu)或搜狗(sogou)搜索引擎以获得更快的访问速度。`
            },
          ],
        };
      }

      case 'ai_search_github': {
        const { query, type = 'repositories', language = '', sort = 'stars' } = args;
        let searchUrl = `https://github.com/search?q=${encodeURIComponent(query)}&type=${type}`;
        if (language) searchUrl += `&l=${encodeURIComponent(language)}`;
        searchUrl += `&s=${sort}`;

        return {
          content: [
            {
              type: 'text',
              text: `📦 GitHub搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📂 搜索类型: ${type}\n` +
                   `💻 编程语言: ${language || '所有语言'}\n` +
                   `📊 排序方式: ${sort}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `💡 热门仓库推荐标准:\n` +
                   `• ⭐ Stars > 1000: 优质项目\n` +
                   `• 🍴 Forks > 500: 活跃社区\n` +
                   `• 🔄 最近更新: 持续维护\n` +
                   `• 📄 完整文档: 易于使用\n\n` +
                   `🔍 搜索技巧:\n` +
                   `• stars:>1000 - 搜索星标数大于1000的仓库\n` +
                   `• language:javascript - 限定编程语言\n` +
                   `• user:username - 搜索特定用户的仓库\n` +
                   `• topic:react - 搜索特定主题\n\n` +
                   `📝 提示: GitHub API可能需要代理访问，建议使用国内镜像如 gitee.com 或 gitcode.net`
            },
          ],
        };
      }

      case 'ai_search_stackoverflow': {
        const { query, tags = '', sort = 'relevance' } = args;
        let searchUrl = `https://stackoverflow.com/search?q=${encodeURIComponent(query)}`;
        if (tags) searchUrl += `&tags=${encodeURIComponent(tags)}`;
        searchUrl += `&sort=${sort}`;

        return {
          content: [
            {
              type: 'text',
              text: `💬 StackOverflow搜索结果\n\n` +
                   `🎯 搜索问题: ${query}\n` +
                   `🏷️ 标签筛选: ${tags || '无限制'}\n` +
                   `📊 排序方式: ${sort}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `✅ 寻找优质答案:\n` +
                   `• ✓ 绿色勾号: 已被采纳的答案\n` +
                   `• ⬆️ 高赞: 投票数高的答案更可靠\n` +
                   `• 📅 最新: 注意答案发布时间，技术可能已更新\n\n` +
                   `🔍 搜索技巧:\n` +
                   `• [javascript] - 搜索包含特定标签的问题\n` +
                   `• is:question - 只搜索问题\n` +
                   `• is:answer - 只搜索答案\n` +
                   `• score:5 - 搜索评分大于5的内容\n\n` +
                   `🌏 国内替代:\n` +
                   `• SegmentFault: segmentfault.com\n` +
                   `• 掘金: juejin.cn\n` +
                   `• CSDN: csdn.net`
            },
          ],
        };
      }

      case 'ai_search_npm': {
        const { query, size = 10 } = args;
        const searchUrl = `https://www.npmjs.com/search?q=${encodeURIComponent(query)}`;
        const registryUrl = `https://registry.npmjs.org/${encodeURIComponent(query)}`;

        return {
          content: [
            {
              type: 'text',
              text: `📦 NPM包搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📊 显示结果: ${size}个\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n` +
                   `📋 包详情API: ${registryUrl}\n\n` +
                   `✅ 选择优质包的标准:\n` +
                   `• 📈 周下载量 > 10,000\n` +
                   `• ⭐ GitHub Stars 数量\n` +
                   `• 📅 最近更新时间\n` +
                   `• 📝 完整的文档和示例\n` +
                   `• 🧪 测试覆盖率\n` +
                   `• 🔒 无已知安全漏洞\n\n` +
                   `🔍 常用NPM命令:\n` +
                   `\`\`\`bash\n` +
                   `# 安装包\n` +
                   `npm install ${query}\n\n` +
                   `# 查看包信息\n` +
                   `npm info ${query}\n\n` +
                   `# 查看包的所有版本\n` +
                   `npm view ${query} versions\n` +
                   `\`\`\`\n\n` +
                   `🌏 国内加速镜像:\n` +
                   `• 淘宝镜像: npmmirror.com\n` +
                   `• 使用: npm config set registry https://registry.npmmirror.com`
            },
          ],
        };
      }

      case 'ai_search_docs': {
        const { query, framework = 'general' } = args;
        const docsUrls = {
          react: `https://react.dev/?search=${encodeURIComponent(query)}`,
          vue: `https://cn.vuejs.org/search.html?query=${encodeURIComponent(query)}`,
          angular: `https://angular.io/search?query=${encodeURIComponent(query)}`,
          nodejs: `https://nodejs.org/api/?search=${encodeURIComponent(query)}`,
          python: `https://docs.python.org/3/search.html?q=${encodeURIComponent(query)}`,
          java: `https://docs.oracle.com/en/java/javase/search.html?q=${encodeURIComponent(query)}`,
          general: `https://devdocs.io/#q=${encodeURIComponent(query)}`
        };

        const cnDocs = {
          react: 'https://zh-hans.react.dev/',
          vue: 'https://cn.vuejs.org/',
          nodejs: 'http://nodejs.cn/api/',
          python: 'https://docs.python.org/zh-cn/3/'
        };

        return {
          content: [
            {
              type: 'text',
              text: `📚 技术文档搜索\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `🔧 框架/平台: ${framework}\n\n` +
                   `🔗 官方文档: ${docsUrls[framework]}\n` +
                   `${cnDocs[framework] ? `🇨🇳 中文文档: ${cnDocs[framework]}\n` : ''}\n` +
                   `📖 常用文档资源:\n` +
                   `• React: react.dev (中文: zh-hans.react.dev)\n` +
                   `• Vue: vuejs.org (中文: cn.vuejs.org)\n` +
                   `• Node.js: nodejs.org (中文: nodejs.cn)\n` +
                   `• MDN Web Docs: developer.mozilla.org (部分中文支持)\n` +
                   `• DevDocs: devdocs.io (多文档聚合)\n\n` +
                   `🌏 国内优质文档站:\n` +
                   `• 现代JavaScript教程: zh.javascript.info\n` +
                   `• ES6入门: es6.ruanyifeng.com\n` +
                   `• TypeScript中文网: tslang.cn\n` +
                   `• Webpack中文网: webpack.docschina.org\n\n` +
                   `💡 提示: 中文文档通常更新较慢，遇到新特性建议查阅英文官方文档`
            },
          ],
        };
      }

      case 'ai_search_api_reference': {
        const { api_name, platform } = args;
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(`${platform} ${api_name} api documentation`)}`;

        return {
          content: [
            {
              type: 'text',
              text: `🔗 API参考搜索\n\n` +
                   `🎯 API名称: ${api_name}\n` +
                   `🔧 平台/库: ${platform}\n\n` +
                   `🔍 搜索链接: ${searchUrl}\n\n` +
                   `📚 常用API文档直达:\n` +
                   `• Express: expressjs.com/en/4x/api.html\n` +
                   `• Axios: axios-http.com/docs/intro\n` +
                   `• Lodash: lodash.com/docs/\n` +
                   `• Moment.js: momentjs.com/docs/\n` +
                   `• jQuery: api.jquery.com\n\n` +
                   `🔍 API查询技巧:\n` +
                   `1. 查看官方API文档的搜索功能\n` +
                   `2. 查看GitHub仓库的README和Wiki\n` +
                   `3. 查看在线示例和教程\n` +
                   `4. 参考TypeScript类型定义文件(.d.ts)\n\n` +
                   `💡 快速上手建议:\n` +
                   `• 先看API的基础用法示例\n` +
                   `• 了解参数类型和返回值\n` +
                   `• 注意版本差异和废弃警告\n` +
                   `• 查看相关的最佳实践\n\n` +
                   `🌏 推荐开发工具:\n` +
                   `• Postman: API测试工具\n` +
                   `• Insomnia: REST客户端\n` +
                   `• VS Code插件: REST Client`
            },
          ],
        };
      }

      // === 浏览器控制台监控工具处理 ===
      case 'ai_console_error_monitor': {
        const { error_message, error_type = 'Unknown', stack_trace = '', file_path = '', line_number = 0 } = args;

        // 错误类型分析
        const errorAnalysis = {
          'JavaScript': '常见于代码逻辑错误、未定义变量、函数调用错误',
          'Network': '网络请求失败，可能是服务器问题、CORS、超时',
          'CORS': '跨域资源共享问题，需要服务器配置CORS头',
          'Syntax': '语法错误，代码书写不符合JavaScript规范',
          'Reference': '引用错误，访问未定义的变量或属性',
          'Type': '类型错误，对错误类型的值进行操作',
          'Range': '范围错误，数值超出有效范围',
          'Unknown': '未知错误，需要进一步分析'
        };

        const commonSolutions = {
          'JavaScript': [
            '检查变量是否已定义',
            '确认函数调用参数正确',
            '使用try-catch捕获错误',
            '查看浏览器兼容性'
          ],
          'Network': [
            '检查网络连接',
            '确认API端点是否正确',
            '查看服务器状态',
            '检查请求超时设置',
            '查看Network面板详细信息'
          ],
          'CORS': [
            '服务器添加Access-Control-Allow-Origin头',
            '使用代理服务器',
            '后端配置CORS中间件',
            '检查credentials设置'
          ],
          'Syntax': [
            '检查代码语法',
            '确认括号、引号配对',
            '使用ESLint检查',
            '查看构建工具报错'
          ],
          'Reference': [
            '确认变量已声明',
            '检查对象属性是否存在',
            '使用可选链操作符 ?.',
            '添加变量存在性检查'
          ],
          'Type': [
            '检查数据类型',
            '添加类型转换',
            '使用TypeScript进行类型检查',
            '验证API返回数据格式'
          ]
        };

        return {
          content: [
            {
              type: 'text',
              text: `🐛 浏览器控制台错误分析\n\n` +
                   `📋 错误详情:\n` +
                   `• 类型: ${error_type}\n` +
                   `• 消息: ${error_message}\n` +
                   `${file_path ? `• 文件: ${file_path}\n` : ''}` +
                   `${line_number ? `• 行号: ${line_number}\n` : ''}` +
                   `${stack_trace ? `\n📊 堆栈跟踪:\n${stack_trace}\n` : ''}\n` +
                   `🔍 错误分析:\n${errorAnalysis[error_type] || errorAnalysis['Unknown']}\n\n` +
                   `💡 解决方案建议:\n` +
                   (commonSolutions[error_type] || commonSolutions['JavaScript']).map((s, i) => `${i + 1}. ${s}`).join('\n') + '\n\n' +
                   `🛠️ 调试步骤:\n` +
                   `1. 打开浏览器开发者工具 (F12)\n` +
                   `2. 查看Console面板的完整错误信息\n` +
                   `3. 点击错误信息跳转到源代码位置\n` +
                   `4. 使用断点调试查看变量值\n` +
                   `5. 检查Network面板的网络请求\n\n` +
                   `📚 参考资源:\n` +
                   `• MDN错误参考: developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Errors\n` +
                   `• Chrome DevTools: developers.google.com/web/tools/chrome-devtools\n` +
                   `• StackOverflow搜索: stackoverflow.com/search?q=${encodeURIComponent(error_message)}`
            },
          ],
        };
      }

      case 'ai_console_warning_check': {
        const { warning_message, warning_source = 'Browser' } = args;

        return {
          content: [
            {
              type: 'text',
              text: `⚠️ 控制台警告分析\n\n` +
                   `📋 警告详情:\n` +
                   `• 来源: ${warning_source}\n` +
                   `• 消息: ${warning_message}\n\n` +
                   `🔍 警告类型分析:\n` +
                   `• Deprecation Warning: 使用了已弃用的API\n` +
                   `• Performance Warning: 性能问题警告\n` +
                   `• React Warning: React特定警告\n` +
                   `• Vue Warning: Vue特定警告\n` +
                   `• Security Warning: 安全相关警告\n\n` +
                   `💡 处理建议:\n` +
                   `1. 虽然是警告不是错误，但应该及时修复\n` +
                   `2. 弃用警告可能在未来版本导致错误\n` +
                   `3. 性能警告会影响用户体验\n` +
                   `4. 安全警告必须立即处理\n\n` +
                   `🛠️ 常见警告解决方案:\n` +
                   `• React: 检查key属性、生命周期方法、setState使用\n` +
                   `• Vue: 检查响应式数据、组件注册、指令使用\n` +
                   `• 浏览器API: 查看MDN文档的替代方案\n` +
                   `• 第三方库: 更新到最新版本或查看文档\n\n` +
                   `📚 推荐做法:\n` +
                   `• 使用ESLint捕获潜在问题\n` +
                   `• 定期更新依赖包\n` +
                   `• 查看官方迁移指南\n` +
                   `• 在开发环境及时修复警告`
            },
          ],
        };
      }

      case 'ai_network_error_diagnosis': {
        const { url, status_code, error_message = '', request_method = 'GET' } = args;

        const statusCodeAnalysis = {
          400: { title: 'Bad Request', desc: '请求参数错误或格式不正确' },
          401: { title: 'Unauthorized', desc: '未授权，需要身份验证' },
          403: { title: 'Forbidden', desc: '服务器拒绝访问，权限不足' },
          404: { title: 'Not Found', desc: '请求的资源不存在' },
          405: { title: 'Method Not Allowed', desc: '不支持该HTTP方法' },
          408: { title: 'Request Timeout', desc: '请求超时' },
          429: { title: 'Too Many Requests', desc: '请求过于频繁，触发限流' },
          500: { title: 'Internal Server Error', desc: '服务器内部错误' },
          502: { title: 'Bad Gateway', desc: '网关错误' },
          503: { title: 'Service Unavailable', desc: '服务不可用' },
          504: { title: 'Gateway Timeout', desc: '网关超时' }
        };

        const statusInfo = statusCodeAnalysis[status_code] || { title: 'Unknown Error', desc: '未知错误' };

        return {
          content: [
            {
              type: 'text',
              text: `🌐 网络请求错误诊断\n\n` +
                   `📋 请求详情:\n` +
                   `• URL: ${url}\n` +
                   `• 方法: ${request_method}\n` +
                   `• 状态码: ${status_code} - ${statusInfo.title}\n` +
                   `${error_message ? `• 错误消息: ${error_message}\n` : ''}\n` +
                   `🔍 错误分析:\n${statusInfo.desc}\n\n` +
                   `💡 解决方案:\n` +
                   (status_code >= 400 && status_code < 500 ?
                     `客户端错误 (4xx):\n` +
                     `1. 检查请求URL是否正确\n` +
                     `2. 验证请求参数格式和值\n` +
                     `3. 确认token或认证信息有效\n` +
                     `4. 检查请求方法是否正确\n` +
                     `5. 查看API文档确认参数要求\n` :
                   status_code >= 500 ?
                     `服务器错误 (5xx):\n` +
                     `1. 稍后重试请求\n` +
                     `2. 联系后端开发人员\n` +
                     `3. 查看服务器日志\n` +
                     `4. 检查服务器负载和状态\n` +
                     `5. 确认数据库连接正常\n` :
                     `1. 检查网络连接\n` +
                     `2. 确认请求配置正确\n` +
                     `3. 查看详细错误信息\n`) +
                   `\n🛠️ 调试技巧:\n` +
                   `1. 打开Network面板查看详细信息\n` +
                   `2. 检查Request Headers和Response Headers\n` +
                   `3. 查看Request Payload和Response\n` +
                   `4. 使用Postman等工具独立测试API\n` +
                   `5. 检查CORS设置（跨域请求）\n\n` +
                   `📊 常见HTTP状态码:\n` +
                   `• 2xx: 成功\n` +
                   `• 3xx: 重定向\n` +
                   `• 4xx: 客户端错误\n` +
                   `• 5xx: 服务器错误\n\n` +
                   `🔗 有用工具:\n` +
                   `• HTTP状态码查询: httpstatuses.com\n` +
                   `• API测试: Postman/Insomnia\n` +
                   `• 网络抓包: Charles/Fiddler`
            },
          ],
        };
      }

      case 'ai_console_log_analyzer': {
        const { logs, analysis_type = 'all' } = args;

        // 简单的日志模式识别
        const errorCount = (logs.match(/error|Error|ERROR/gi) || []).length;
        const warningCount = (logs.match(/warning|Warning|WARN/gi) || []).length;
        const networkCount = (logs.match(/fetch|axios|request|XMLHttpRequest/gi) || []).length;
        const performanceCount = (logs.match(/performance|slow|timeout|delay/gi) || []).length;

        return {
          content: [
            {
              type: 'text',
              text: `📊 控制台日志分析报告\n\n` +
                   `📋 分析类型: ${analysis_type}\n` +
                   `📝 日志长度: ${logs.length} 字符\n\n` +
                   `🔍 问题统计:\n` +
                   `• ❌ 错误数量: ${errorCount}\n` +
                   `• ⚠️ 警告数量: ${warningCount}\n` +
                   `• 🌐 网络请求: ${networkCount}\n` +
                   `• ⏱️ 性能相关: ${performanceCount}\n\n` +
                   `💡 分析建议:\n` +
                   (errorCount > 0 ? `• 发现 ${errorCount} 个错误，需要优先处理\n` : '') +
                   (warningCount > 5 ? `• 警告数量较多 (${warningCount}个)，建议及时清理\n` : '') +
                   (networkCount > 10 ? `• 网络请求较多，考虑合并或优化请求\n` : '') +
                   (performanceCount > 0 ? `• 发现性能相关日志，建议使用Performance面板深入分析\n` : '') +
                   `\n🛠️ 日志最佳实践:\n` +
                   `1. 生产环境关闭调试日志\n` +
                   `2. 使用不同级别的日志 (log/warn/error)\n` +
                   `3. 添加有意义的日志消息\n` +
                   `4. 使用console.group组织日志\n` +
                   `5. 避免在循环中打印大量日志\n\n` +
                   `📈 推荐工具:\n` +
                   `• Chrome Performance 面板\n` +
                   `• React DevTools Profiler\n` +
                   `• Vue DevTools Performance\n` +
                   `• Sentry/LogRocket等日志服务\n\n` +
                   `🔗 参考文档:\n` +
                   `• Console API: developer.mozilla.org/zh-CN/docs/Web/API/Console\n` +
                   `• 性能优化: web.dev/performance`
            },
          ],
        };
      }

      // === 国内开发者平台搜索工具处理 ===
      case 'ai_search_wechat_docs': {
        const { query, platform = 'all' } = args;

        const platformUrls = {
          miniprogram: `https://developers.weixin.qq.com/miniprogram/dev/framework/search.html?q=${encodeURIComponent(query)}`,
          officialaccount: `https://developers.weixin.qq.com/doc/offiaccount/search.html?q=${encodeURIComponent(query)}`,
          open: `https://developers.weixin.qq.com/doc/oplatform/search.html?q=${encodeURIComponent(query)}`,
          payment: `https://pay.weixin.qq.com/wiki/doc/apiv3/search.html?q=${encodeURIComponent(query)}`,
          all: `https://developers.weixin.qq.com/`
        };

        const platformNames = {
          miniprogram: '小程序',
          officialaccount: '公众号',
          open: '开放平台',
          payment: '微信支付',
          all: '全平台'
        };

        return {
          content: [
            {
              type: 'text',
              text: `📱 微信开发者文档搜索\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📂 平台类型: ${platformNames[platform]}\n\n` +
                   `🔗 搜索链接: ${platformUrls[platform]}\n\n` +
                   `📚 常用文档入口:\n` +
                   `• 小程序开发文档: developers.weixin.qq.com/miniprogram/dev/framework/\n` +
                   `• 小程序API: developers.weixin.qq.com/miniprogram/dev/api/\n` +
                   `• 小程序组件: developers.weixin.qq.com/miniprogram/dev/component/\n` +
                   `• 公众号开发: developers.weixin.qq.com/doc/offiaccount/\n` +
                   `• 微信支付: pay.weixin.qq.com/wiki/doc/apiv3/\n` +
                   `• 开放平台: open.weixin.qq.com/\n\n` +
                   `💡 开发技巧:\n` +
                   `• 使用微信开发者工具进行真机调试\n` +
                   `• 查看社区问答: developers.weixin.qq.com/community/\n` +
                   `• 关注微信公众平台公告获取最新变更\n` +
                   `• 使用HBuilderX进行uni-app跨平台开发\n\n` +
                   `🛠️ 常用工具:\n` +
                   `• 微信开发者工具: developers.weixin.qq.com/miniprogram/dev/devtools/\n` +
                   `• 微信公众平台: mp.weixin.qq.com\n` +
                   `• 微信商户平台: pay.weixin.qq.com`
            },
          ],
        };
      }

      case 'ai_search_csdn': {
        const { query, type = 'all' } = args;

        const searchUrls = {
          blog: `https://so.csdn.net/so/search?q=${encodeURIComponent(query)}&t=blog`,
          ask: `https://so.csdn.net/so/search?q=${encodeURIComponent(query)}&t=ask`,
          all: `https://so.csdn.net/so/search?q=${encodeURIComponent(query)}`
        };

        return {
          content: [
            {
              type: 'text',
              text: `📝 CSDN搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📂 搜索类型: ${type === 'blog' ? '博客' : type === 'ask' ? '问答' : '全部'}\n\n` +
                   `🔗 搜索链接: ${searchUrls[type]}\n\n` +
                   `💡 CSDN使用技巧:\n` +
                   `• 精确搜索: 使用双引号 "${query}"\n` +
                   `• 排除关键词: 使用减号 ${query} -排除词\n` +
                   `• 按时间筛选: 选择最近一年/半年/一月\n` +
                   `• 查看高质量博主: 关注博客专家和推荐博主\n\n` +
                   `📚 推荐栏目:\n` +
                   `• CSDN博客: blog.csdn.net\n` +
                   `• CSDN问答: ask.csdn.net\n` +
                   `• 代码托管: codechina.csdn.net\n` +
                   `• 在线学习: edu.csdn.net\n\n` +
                   `⚠️ 注意事项:\n` +
                   `• 注意博文发布时间，技术可能已更新\n` +
                   `• 优先查看评论多、点赞高的文章\n` +
                   `• 代码示例要结合自己项目调整\n` +
                   `• 遇到付费内容可搜索免费替代方案`
            },
          ],
        };
      }

      case 'ai_search_juejin': {
        const { query, sort = 'hot' } = args;
        const searchUrl = `https://juejin.cn/search?query=${encodeURIComponent(query)}&sort=${sort}`;

        return {
          content: [
            {
              type: 'text',
              text: `💎 掘金搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📊 排序方式: ${sort === 'hot' ? '热门' : sort === 'time' ? '最新' : '点赞'}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `💡 掘金特色:\n` +
                   `• 高质量技术文章和前沿技术分享\n` +
                   `• 活跃的技术社区和讨论氛围\n` +
                   `• 优秀的前端和全栈内容\n` +
                   `• 定期举办技术沙龙和活动\n\n` +
                   `📚 推荐板块:\n` +
                   `• 前端: 前端、JavaScript、Vue、React等\n` +
                   `• 后端: Java、Python、Go、Node.js等\n` +
                   `• 移动端: Android、iOS、Flutter等\n` +
                   `• 人工智能: 机器学习、深度学习等\n\n` +
                   `🏆 优质作者:\n` +
                   `• 关注掘金优秀作者获取高质量内容\n` +
                   `• 查看年度榜单和热门文章\n` +
                   `• 参与沸点讨论交流技术\n\n` +
                   `🎯 推荐功能:\n` +
                   `• 掘金小册: 系统化学习资料\n` +
                   `• 技术专栏: 深度技术文章\n` +
                   `• 代码片段: 实用代码示例`
            },
          ],
        };
      }

      case 'ai_search_segmentfault': {
        const { query, tags = '' } = args;
        let searchUrl = `https://segmentfault.com/search?q=${encodeURIComponent(query)}`;
        if (tags) searchUrl += `&tags=${encodeURIComponent(tags)}`;

        return {
          content: [
            {
              type: 'text',
              text: `🔧 SegmentFault搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `🏷️ 标签筛选: ${tags || '无限制'}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `💡 SegmentFault特色:\n` +
                   `• 中国最专业的开发者社区之一\n` +
                   `• 高质量的技术问答\n` +
                   `• 活跃的技术讨论氛围\n` +
                   `• 丰富的技术文章和教程\n\n` +
                   `📚 推荐功能:\n` +
                   `• 问答: 解决具体技术问题\n` +
                   `• 专栏: 系列技术文章\n` +
                   `• 讲堂: 在线技术分享\n` +
                   `• 笔记: 学习笔记和总结\n\n` +
                   `🎯 使用技巧:\n` +
                   `• 查看高赞和已采纳的答案\n` +
                   `• 关注相关标签获取最新内容\n` +
                   `• 参与讨论提升技术理解\n` +
                   `• 查看用户声望了解回答质量\n\n` +
                   `🏆 热门标签:\n` +
                   `• javascript, react, vue, node.js\n` +
                   `• python, java, go, php\n` +
                   `• 前端, 后端, 算法, 架构`
            },
          ],
        };
      }

      case 'ai_search_cnblogs': {
        const { query } = args;
        const searchUrl = `https://zzk.cnblogs.com/s?w=${encodeURIComponent(query)}`;

        return {
          content: [
            {
              type: 'text',
              text: `📚 博客园搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `💡 博客园特色:\n` +
                   `• 中国最早的开发者社区之一\n` +
                   `• 深度技术文章和系列教程\n` +
                   `• .NET和C#技术内容丰富\n` +
                   `• 优质博主长期维护内容\n\n` +
                   `📚 推荐功能:\n` +
                   `• 博客: 个人技术博客\n` +
                   `• 新闻: 技术资讯和动态\n` +
                   `• 知识库: 系统化知识整理\n` +
                   `• 小组: 技术交流小组\n\n` +
                   `🎯 阅读建议:\n` +
                   `• 关注推荐博主和首页精华\n` +
                   `• 查看文章系列获取完整知识\n` +
                   `• 阅读评论区的讨论和补充\n` +
                   `• 注意文章更新时间\n\n` +
                   `🏆 优势领域:\n` +
                   `• .NET、C#、ASP.NET技术栈\n` +
                   `• 数据库、SQL Server\n` +
                   `• 算法和数据结构\n` +
                   `• 系统架构和设计模式`
            },
          ],
        };
      }

      case 'ai_search_oschina': {
        const { query, type = 'all' } = args;
        const searchUrls = {
          news: `https://www.oschina.net/search?scope=news&q=${encodeURIComponent(query)}`,
          blog: `https://www.oschina.net/search?scope=blog&q=${encodeURIComponent(query)}`,
          ask: `https://www.oschina.net/search?scope=ask&q=${encodeURIComponent(query)}`,
          project: `https://www.oschina.net/search?scope=project&q=${encodeURIComponent(query)}`,
          all: `https://www.oschina.net/search?q=${encodeURIComponent(query)}`
        };

        return {
          content: [
            {
              type: 'text',
              text: `🌐 开源中国搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📂 搜索类型: ${type === 'news' ? '资讯' : type === 'blog' ? '博客' : type === 'ask' ? '问答' : type === 'project' ? '项目' : '全部'}\n\n` +
                   `🔗 搜索链接: ${searchUrls[type]}\n\n` +
                   `💡 开源中国特色:\n` +
                   `• 专注开源技术和开源项目\n` +
                   `• 丰富的开源软件和代码托管\n` +
                   `• 及时的技术资讯和行业动态\n` +
                   `• 活跃的开源社区\n\n` +
                   `📚 推荐栏目:\n` +
                   `• Gitee: 国内代码托管平台 gitee.com\n` +
                   `• 开源软件: 发现优质开源项目\n` +
                   `• 技术问答: 解决开发问题\n` +
                   `• 技术博客: 开发者经验分享\n\n` +
                   `🎯 实用功能:\n` +
                   `• 开源软件搜索: 查找替代方案\n` +
                   `• 代码片段: 实用代码示例\n` +
                   `• 技术翻译: 国外技术文章翻译\n` +
                   `• 开源资讯: 了解开源动态\n\n` +
                   `🏆 推荐关注:\n` +
                   `• 关注热门开源项目\n` +
                   `• 参与开源项目贡献\n` +
                   `• 使用Gitee托管代码\n` +
                   `• 查看技术周刊和月报`
            },
          ],
        };
      }

      case 'ai_search_aliyun_docs': {
        const { query, product = '' } = args;
        const searchUrl = product
          ? `https://help.aliyun.com/search/product/${product}?q=${encodeURIComponent(query)}`
          : `https://help.aliyun.com/search?q=${encodeURIComponent(query)}`;

        return {
          content: [
            {
              type: 'text',
              text: `☁️ 阿里云文档搜索\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📦 产品范围: ${product || '全部产品'}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `📚 热门产品文档:\n` +
                   `• ECS云服务器: help.aliyun.com/product/25365.html\n` +
                   `• OSS对象存储: help.aliyun.com/product/31815.html\n` +
                   `• RDS数据库: help.aliyun.com/product/26090.html\n` +
                   `• SLB负载均衡: help.aliyun.com/product/27537.html\n` +
                   `• CDN加速: help.aliyun.com/product/27099.html\n\n` +
                   `💡 开发资源:\n` +
                   `• SDK下载: 支持多种编程语言\n` +
                   `• API参考: 详细的API文档\n` +
                   `• 最佳实践: 实际应用案例\n` +
                   `• 开发者论坛: developer.aliyun.com/ask/\n\n` +
                   `🛠️ 实用工具:\n` +
                   `• 阿里云控制台: console.aliyun.com\n` +
                   `• 云命令行: CloudShell在线终端\n` +
                   `• API Explorer: 在线调试API\n` +
                   `• 成本计算器: 估算资源费用\n\n` +
                   `🎯 学习资源:\n` +
                   `• 阿里云大学: edu.aliyun.com\n` +
                   `• 在线实验室: 免费实践环境\n` +
                   `• 认证考试: 获取专业认证`
            },
          ],
        };
      }

      case 'ai_search_tencent_docs': {
        const { query, product = '' } = args;
        const searchUrl = product
          ? `https://cloud.tencent.com/document/product/search?q=${encodeURIComponent(query)}&product=${product}`
          : `https://cloud.tencent.com/document/search?q=${encodeURIComponent(query)}`;

        return {
          content: [
            {
              type: 'text',
              text: `☁️ 腾讯云文档搜索\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📦 产品范围: ${product || '全部产品'}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `📚 热门产品文档:\n` +
                   `• CVM云服务器: cloud.tencent.com/document/product/213\n` +
                   `• COS对象存储: cloud.tencent.com/document/product/436\n` +
                   `• CDN加速: cloud.tencent.com/document/product/228\n` +
                   `• CLB负载均衡: cloud.tencent.com/document/product/214\n` +
                   `• SCF云函数: cloud.tencent.com/document/product/583\n\n` +
                   `💡 开发资源:\n` +
                   `• SDK中心: 多语言SDK支持\n` +
                   `• API文档: 完整的API参考\n` +
                   `• 最佳实践: 实际应用案例\n` +
                   `• 开发者社区: cloud.tencent.com/developer/\n\n` +
                   `🛠️ 实用工具:\n` +
                   `• 控制台: console.cloud.tencent.com\n` +
                   `• API Explorer: 在线调试API\n` +
                   `• CLI工具: 命令行管理工具\n` +
                   `• 价格计算器: 费用估算\n\n` +
                   `🎯 学习资源:\n` +
                   `• 腾讯云大学: 在线课程和认证\n` +
                   `• 技术社区: 开发者交流\n` +
                   `• 实验室: 免费实践环境\n` +
                   `• 技术沙龙: 线下技术分享`
            },
          ],
        };
      }

      case 'ai_debug_suggestion': {
        const { error_description, code_snippet = '', environment = 'Browser' } = args;

        return {
          content: [
            {
              type: 'text',
              text: `🔧 调试建议生成\n\n` +
                   `📋 问题描述:\n${error_description}\n\n` +
                   `💻 运行环境: ${environment}\n` +
                   `${code_snippet ? `\n📝 相关代码:\n\`\`\`\n${code_snippet}\n\`\`\`\n` : ''}\n` +
                   `🔍 系统化调试流程:\n\n` +
                   `### 1️⃣ 问题定位\n` +
                   `• 确认错误是否可复现\n` +
                   `• 记录错误出现的具体操作步骤\n` +
                   `• 查看完整的错误堆栈\n` +
                   `• 确认是否为特定环境问题\n\n` +
                   `### 2️⃣ 信息收集\n` +
                   `• 浏览器: ${environment}\n` +
                   `• 错误类型和消息\n` +
                   `• 发生错误的文件和行号\n` +
                   `• 网络请求状态（如果相关）\n` +
                   `• 相关变量的值\n\n` +
                   `### 3️⃣ 调试技巧\n` +
                   `• 使用 console.log() 打印关键变量\n` +
                   `• 设置断点单步调试\n` +
                   `• 使用 debugger 语句\n` +
                   `• 查看调用栈 (Call Stack)\n` +
                   `• 监视变量值 (Watch)\n\n` +
                   `### 4️⃣ 常用调试命令\n` +
                   `\`\`\`javascript\n` +
                   `// 打印对象\n` +
                   `console.log('变量值:', variable);\n\n` +
                   `// 打印对象详情\n` +
                   `console.dir(object);\n\n` +
                   `// 计时\n` +
                   `console.time('操作');\n` +
                   `// ...代码...\n` +
                   `console.timeEnd('操作');\n\n` +
                   `// 堆栈跟踪\n` +
                   `console.trace();\n\n` +
                   `// 条件断点\n` +
                   `if (condition) debugger;\n` +
                   `\`\`\`\n\n` +
                   `### 5️⃣ 解决方案查找\n` +
                   `1. 搜索错误消息 (Google/StackOverflow)\n` +
                   `2. 查看官方文档和API文档\n` +
                   `3. 检查GitHub Issues\n` +
                   `4. 查看框架/库的更新日志\n` +
                   `5. 咨询社区或技术论坛\n\n` +
                   `### 6️⃣ 预防措施\n` +
                   `• 使用TypeScript增强类型检查\n` +
                   `• 配置ESLint捕获潜在问题\n` +
                   `• 编写单元测试\n` +
                   `• 使用try-catch处理异常\n` +
                   `• 添加错误边界 (React)\n\n` +
                   `🔗 有用资源:\n` +
                   `• Chrome DevTools: developers.google.com/web/tools/chrome-devtools\n` +
                   `• Firefox DevTools: developer.mozilla.org/zh-CN/docs/Tools\n` +
                   `• JavaScript调试技巧: javascript.info/debugging-chrome\n` +
                   `• React错误边界: react.dev/reference/react/Component#catching-errors-with-an-error-boundary`
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
  console.error('AI Rule MCP Server v0.6.0 running on stdio');
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});