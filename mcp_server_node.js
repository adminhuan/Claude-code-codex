#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

const server = new Server(
  {
    name: 'smart-search-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Smart Search MCP 工具定义
// 只保留真实可用的功能：1个规则提醒 + 14个搜索
const AI_TOOLS = [
  // === 规则提醒工具 (1个真实实现) ===
  {
    name: 'ai_coding_rules_reminder',
    description: '📋 编码规则提醒 - 读取项目中的编码规范文件并提醒Claude Code严格遵守\n\n功能：\n• 自动搜索项目中的规范文档（.md、.txt）\n• 读取并解析编码规范\n• 生成遵守提醒清单\n• 监督Claude Code的代码输出质量\n\n适用场景：\n• 开始编码前提醒规范\n• 代码审查时检查合规性\n• 团队协作时统一标准',
    inputSchema: {
      type: 'object',
      properties: {
        project_path: { type: 'string', description: '项目根目录路径（默认：当前目录）', default: '.' },
        focus_area: {
          type: 'string',
          enum: ['all', 'naming', 'structure', 'security', 'performance', 'documentation'],
          description: '关注领域：all(全部)、naming(命名)、structure(结构)、security(安全)、performance(性能)、documentation(文档)',
          default: 'all'
        },
        strict_mode: { type: 'boolean', description: '严格模式 - 启用时会更严格地检查规范遵守情况', default: false }
      }
    }
  },

  // === 国际搜索工具 (6个) ===
  {
    name: 'ai_search_web',
    description: '🔍 网络搜索 - 通用网络搜索（Google/Bing/百度/搜狗）\n\n【重要】此工具会返回搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        engine: { type: 'string', enum: ['google', 'bing', 'baidu', 'sogou'], description: '搜索引擎，默认baidu', default: 'baidu' },
        count: { type: 'number', description: '期望的结果数量，默认10', default: 10 }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_github',
    description: '🐙 GitHub搜索 - 搜索GitHub仓库、代码、问题和用户\n\n【重要】此工具会返回GitHub搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
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
    description: '💬 StackOverflow搜索 - 搜索技术问题和解决方案\n\n【重要】此工具会返回StackOverflow搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
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
    description: '📦 NPM包搜索 - 搜索NPM包和相关文档\n\n【重要】此工具会返回NPM搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
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
    description: '📚 技术文档搜索 - 搜索常见框架和工具的官方文档（React、Vue、Node.js等）\n\n【重要】此工具会返回文档搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
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
    description: '🔗 API参考搜索 - 快速查找API文档和使用示例\n\n【重要】此工具会返回API文档搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        api_name: { type: 'string', description: 'API名称或方法名' },
        platform: { type: 'string', description: '平台或库名称（如：express、axios、lodash）' }
      },
      required: ['api_name', 'platform']
    }
  },

  // === 国内搜索工具 (8个) ===
  {
    name: 'ai_search_wechat_docs',
    description: '📱 微信开发者文档搜索 - 搜索微信小程序、公众号、开放平台文档\n\n【重要】此工具会返回微信文档搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        platform: { type: 'string', enum: ['miniprogram', 'officialaccount', 'open', 'payment', 'all'], description: '平台类型', default: 'all' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_csdn',
    description: '📝 CSDN搜索 - 搜索CSDN技术博客和问答\n\n【重要】此工具会返回CSDN搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        type: { type: 'string', enum: ['blog', 'ask', 'all'], description: '搜索类型', default: 'all' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_juejin',
    description: '💎 掘金搜索 - 搜索掘金技术社区文章\n\n【重要】此工具会返回掘金搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        sort: { type: 'string', enum: ['hot', 'time', 'like'], description: '排序方式', default: 'hot' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_segmentfault',
    description: '🔧 SegmentFault搜索 - 搜索思否技术问答和文章\n\n【重要】此工具会返回SegmentFault搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        tags: { type: 'string', description: '标签筛选（可选）' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_cnblogs',
    description: '📚 博客园搜索 - 搜索博客园技术博客\n\n【重要】此工具会返回博客园搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
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
    description: '🌐 开源中国搜索 - 搜索开源中国技术资讯和项目\n\n【重要】此工具会返回开源中国搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
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
    description: '☁️ 阿里云文档搜索 - 搜索阿里云产品文档和API\n\n【重要】此工具会返回阿里云文档搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        product: { type: 'string', description: '产品名称（如：ecs、oss、rds等）' }
      },
      required: ['query']
    }
  },
  {
    name: 'ai_search_tencent_docs',
    description: '☁️ 腾讯云文档搜索 - 搜索腾讯云产品文档和API\n\n【重要】此工具会返回腾讯云文档搜索URL，Claude Code应该使用WebFetch工具访问该URL以获取真实搜索结果。',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '搜索关键词' },
        product: { type: 'string', description: '产品名称（如：cvm、cos、cdn等）' }
      },
      required: ['query']
    }
  }
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: AI_TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      // === 规则提醒工具处理 ===
      case 'ai_coding_rules_reminder': {
        const { project_path = '.', focus_area = 'all', strict_mode = false } = args;

        try {
          // 搜索项目中的规范文档
          const possibleRuleFiles = [
            'CODING_STANDARDS.md',
            'CODING_RULES.md',
            'STYLE_GUIDE.md',
            'CONTRIBUTING.md',
            'README.md',
            'docs/coding-standards.md',
            'docs/style-guide.md',
            '.github/CONTRIBUTING.md'
          ];

          let foundRules = [];
          let rulesContent = '';

          for (const fileName of possibleRuleFiles) {
            const filePath = join(project_path, fileName);
            if (existsSync(filePath)) {
              try {
                const content = await readFile(filePath, 'utf-8');
                foundRules.push(fileName);
                rulesContent += `\n\n### 📄 ${fileName}\n${content.slice(0, 2000)}${content.length > 2000 ? '...(内容过长已截断)' : ''}`;
              } catch (err) {
                // 忽略读取错误
              }
            }
          }

          const focusAreaText = {
            all: '全部规范',
            naming: '命名规范',
            structure: '代码结构',
            security: '安全规范',
            performance: '性能优化',
            documentation: '文档规范'
          }[focus_area];

          if (foundRules.length === 0) {
            // 没有找到规范文档，返回通用提醒
            return {
              content: [
                {
                  type: 'text',
                  text: `📋 编码规范提醒\n\n` +
                       `⚠️ 未在项目中找到编码规范文档\n\n` +
                       `💡 建议创建以下文件之一：\n` +
                       possibleRuleFiles.map(f => `• ${f}`).join('\n') + '\n\n' +
                       `## 🎯 通用编码规范提醒\n\n` +
                       `### 1. 代码可读性\n` +
                       `• 使用清晰的变量和函数命名\n` +
                       `• 保持函数简短，单一职责\n` +
                       `• 添加必要的注释说明\n\n` +
                       `### 2. 代码结构\n` +
                       `• 遵循项目的目录结构规范\n` +
                       `• 合理组织代码模块\n` +
                       `• 避免循环依赖\n\n` +
                       `### 3. 错误处理\n` +
                       `• 使用try-catch处理异常\n` +
                       `• 提供有意义的错误信息\n` +
                       `• 记录关键错误日志\n\n` +
                       `### 4. 性能考虑\n` +
                       `• 避免不必要的计算\n` +
                       `• 合理使用缓存\n` +
                       `• 优化数据库查询\n\n` +
                       `### 5. 安全实践\n` +
                       `• 验证所有输入数据\n` +
                       `• 防止SQL注入和XSS攻击\n` +
                       `• 不暴露敏感信息\n\n` +
                       `${strict_mode ? '⚠️ **严格模式已启用** - 请严格遵守以上规范，代码审查将更加严格！\n\n' : ''}` +
                       `💡 Claude Code，请在编写代码时**严格遵守**以上规范！`
                },
              ],
            };
          }

          // 找到规范文档，返回实际内容
          return {
            content: [
              {
                type: 'text',
                text: `📋 编码规范提醒 - ${focusAreaText}\n\n` +
                     `✅ 找到 ${foundRules.length} 个规范文档:\n${foundRules.map(f => `• ${f}`).join('\n')}\n` +
                     `${strict_mode ? '\n⚠️ **严格模式已启用** - 将严格检查规范遵守情况！\n' : ''}` +
                     `\n---\n` +
                     `${rulesContent}\n` +
                     `\n---\n\n` +
                     `## 🎯 重要提醒\n\n` +
                     `Claude Code，请务必**严格遵守**以上项目规范：\n\n` +
                     `### ✅ 编码时必须：\n` +
                     `• 遵循项目的命名约定\n` +
                     `• 保持代码风格一致\n` +
                     `• 添加必要的注释和文档\n` +
                     `• 进行充分的错误处理\n` +
                     `• 考虑性能和安全性\n\n` +
                     `### ❌ 编码时禁止：\n` +
                     `• 违反项目规范\n` +
                     `• 使用不规范的命名\n` +
                     `• 忽略错误处理\n` +
                     `• 写出低质量代码\n` +
                     `• 忽视安全问题\n\n` +
                     `${strict_mode ? '🚨 **严格模式警告**：任何违反规范的代码都将被要求重写！\n\n' : ''}` +
                     `💡 请在每次编写代码前回顾这些规范，确保代码质量！`
              },
            ],
          };
        } catch (error) {
          return {
            content: [
              {
                type: 'text',
                text: `❌ 读取规范文档时出错: ${error.message}\n\n` +
                     `💡 将使用通用编码规范提醒。`
              },
            ],
          };
        }
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
                   `📊 期望结果数: ${count}\n\n` +
                   `🔗 搜索链接: ${searchUrls[engine]}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实搜索结果。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${searchUrls[engine]}",\n` +
                   `  prompt: "提取前${count}条搜索结果的标题、链接和摘要"\n` +
                   `})\n` +
                   `\`\`\`\n\n` +
                   `💡 搜索技巧:\n` +
                   `• 使用双引号精确匹配: "${query}"\n` +
                   `• 使用减号排除: ${query} -排除词\n` +
                   `• 限定网站: site:github.com ${query}`
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
              text: `🐙 GitHub搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📂 搜索类型: ${type}\n` +
                   `💻 语言筛选: ${language || '全部语言'}\n` +
                   `📊 排序方式: ${sort}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实搜索结果。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${searchUrl}",\n` +
                   `  prompt: "提取前10个仓库的名称、描述、star数和链接"\n` +
                   `})\n` +
                   `\`\`\``
            },
          ],
        };
      }

      case 'ai_search_stackoverflow': {
        const { query, tags = '', sort = 'relevance' } = args;
        let searchUrl = `https://stackoverflow.com/search?q=${encodeURIComponent(query)}`;
        if (tags) searchUrl += `+[${tags.split(',').map(t => t.trim()).join(']+')}]`;
        searchUrl += `&sort=${sort}`;

        return {
          content: [
            {
              type: 'text',
              text: `💬 StackOverflow搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `🏷️ 标签筛选: ${tags || '无限制'}\n` +
                   `📊 排序方式: ${sort}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实搜索结果。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${searchUrl}",\n` +
                   `  prompt: "提取前10个问题的标题、投票数、回答数和链接"\n` +
                   `})\n` +
                   `\`\`\``
            },
          ],
        };
      }

      case 'ai_search_npm': {
        const { query, size = 10 } = args;
        const searchUrl = `https://www.npmjs.com/search?q=${encodeURIComponent(query)}`;

        return {
          content: [
            {
              type: 'text',
              text: `📦 NPM包搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📊 期望结果数: ${size}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实搜索结果。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${searchUrl}",\n` +
                   `  prompt: "提取前${size}个包的名称、描述、版本号、周下载量和链接"\n` +
                   `})\n` +
                   `\`\`\``
            },
          ],
        };
      }

      case 'ai_search_docs': {
        const { query, framework = 'general' } = args;
        const docUrls = {
          react: `https://react.dev/?search=${encodeURIComponent(query)}`,
          vue: `https://vuejs.org/search/?query=${encodeURIComponent(query)}`,
          angular: `https://angular.io/api?query=${encodeURIComponent(query)}`,
          nodejs: `https://nodejs.org/api/all.html#all_${encodeURIComponent(query)}`,
          python: `https://docs.python.org/3/search.html?q=${encodeURIComponent(query)}`,
          java: `https://docs.oracle.com/en/java/javase/search.html?q=${encodeURIComponent(query)}`,
          general: `https://developer.mozilla.org/zh-CN/search?q=${encodeURIComponent(query)}`
        };

        return {
          content: [
            {
              type: 'text',
              text: `📚 技术文档搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📖 文档框架: ${framework.toUpperCase()}\n\n` +
                   `🔗 搜索链接: ${docUrls[framework]}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实文档内容。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${docUrls[framework]}",\n` +
                   `  prompt: "提取与'${query}'相关的API文档、使用示例和说明"\n` +
                   `})\n` +
                   `\`\`\``
            },
          ],
        };
      }

      case 'ai_search_api_reference': {
        const { api_name, platform } = args;
        const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(platform + ' ' + api_name + ' api documentation')}`;

        return {
          content: [
            {
              type: 'text',
              text: `🔗 API参考搜索结果\n\n` +
                   `📦 平台/库: ${platform}\n` +
                   `🎯 API名称: ${api_name}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实API文档。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${searchUrl}",\n` +
                   `  prompt: "找到${platform}的${api_name} API官方文档链接，提取API用法、参数说明和示例代码"\n` +
                   `})\n` +
                   `\`\`\``
            },
          ],
        };
      }

      // === 国内搜索工具 ===
      case 'ai_search_wechat_docs': {
        const { query, platform = 'all' } = args;
        const platformUrls = {
          miniprogram: `https://developers.weixin.qq.com/miniprogram/dev/api/search.html?query=${encodeURIComponent(query)}`,
          officialaccount: `https://developers.weixin.qq.com/doc/offiaccount/search.html?query=${encodeURIComponent(query)}`,
          open: `https://developers.weixin.qq.com/doc/oplatform/search.html?query=${encodeURIComponent(query)}`,
          payment: `https://pay.weixin.qq.com/wiki/doc/api/search.php?query=${encodeURIComponent(query)}`,
          all: `https://developers.weixin.qq.com/search?query=${encodeURIComponent(query)}`
        };

        return {
          content: [
            {
              type: 'text',
              text: `📱 微信开发者文档搜索\n\n` +
                   `🎯 搜索关键词: ${query}\n` +
                   `📂 平台类型: ${platform}\n\n` +
                   `🔗 搜索链接: ${platformUrls[platform]}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实文档内容。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${platformUrls[platform]}",\n` +
                   `  prompt: "提取与'${query}'相关的API文档、使用说明和代码示例"\n` +
                   `})\n` +
                   `\`\`\``
            },
          ],
        };
      }

      case 'ai_search_csdn':
      case 'ai_search_juejin':
      case 'ai_search_segmentfault':
      case 'ai_search_cnblogs':
      case 'ai_search_oschina':
      case 'ai_search_aliyun_docs':
      case 'ai_search_tencent_docs': {
        const { query } = args;
        const searchUrls = {
          ai_search_csdn: `https://so.csdn.net/so/search?q=${encodeURIComponent(query)}`,
          ai_search_juejin: `https://juejin.cn/search?query=${encodeURIComponent(query)}`,
          ai_search_segmentfault: `https://segmentfault.com/search?q=${encodeURIComponent(query)}`,
          ai_search_cnblogs: `https://zzk.cnblogs.com/s?w=${encodeURIComponent(query)}`,
          ai_search_oschina: `https://www.oschina.net/search?q=${encodeURIComponent(query)}`,
          ai_search_aliyun_docs: `https://help.aliyun.com/search?q=${encodeURIComponent(query)}`,
          ai_search_tencent_docs: `https://cloud.tencent.com/document/search?q=${encodeURIComponent(query)}`
        };

        const platformNames = {
          ai_search_csdn: 'CSDN',
          ai_search_juejin: '掘金',
          ai_search_segmentfault: 'SegmentFault',
          ai_search_cnblogs: '博客园',
          ai_search_oschina: '开源中国',
          ai_search_aliyun_docs: '阿里云文档',
          ai_search_tencent_docs: '腾讯云文档'
        };

        const searchUrl = searchUrls[name];
        const platformName = platformNames[name];

        return {
          content: [
            {
              type: 'text',
              text: `🔍 ${platformName}搜索结果\n\n` +
                   `🎯 搜索关键词: ${query}\n\n` +
                   `🔗 搜索链接: ${searchUrl}\n\n` +
                   `⚠️ **重要提示**：\n` +
                   `Claude Code应该使用WebFetch工具访问上述URL以获取真实搜索结果。\n\n` +
                   `示例命令:\n` +
                   `\`\`\`\n` +
                   `WebFetch({\n` +
                   `  url: "${searchUrl}",\n` +
                   `  prompt: "提取前10条搜索结果的标题、摘要和链接"\n` +
                   `})\n` +
                   `\`\`\``
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
  console.error('Smart Search MCP Server v1.0.0 running on stdio');
  console.error('Tools: 15 (1 coding rules + 14 search)');
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});