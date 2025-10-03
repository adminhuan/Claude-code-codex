#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { mkdir, writeFile } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

const server = new Server(
  {
    name: 'smart-search-mcp',
    version: '2.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const makeTextResponse = (text) => ({
  content: [
    {
      type: 'text',
      text,
    },
  ],
});

const pickKey = (map, key, fallback) => {
  if (key && Object.prototype.hasOwnProperty.call(map, key)) {
    return key;
  }
  return fallback;
};

const normalizeString = (value) => (typeof value === 'string' ? value.trim() : '');

const clampNumber = (value, min, max, fallback) => {
  const num = Number(value);
  if (Number.isFinite(num)) {
    const rounded = Math.round(num);
    if (rounded < min) return min;
    if (rounded > max) return max;
    return rounded;
  }
  return fallback;
};

const saveSearchResult = async (toolName, query, details) => {
  try {
    const resultsDir = join(process.cwd(), '.search-results');
    if (!existsSync(resultsDir)) {
      await mkdir(resultsDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    const filename = `${toolName}-${timestamp}.md`;
    const filepath = join(resultsDir, filename);

    await writeFile(filepath, details, 'utf-8');
    return filepath;
  } catch (error) {
    console.error('Failed to save search result:', error);
    return null;
  }
};

// Smart Search MCP 工具定义
// 只保留搜索功能：14个搜索工具
const AI_TOOLS = [
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
      // === 搜索工具处理 ===
      case 'ai_search_web': {
        const rawQuery = normalizeString(args.query);
        const requestedEngine = normalizeString(args.engine).toLowerCase();
        const resolvedCount = clampNumber(args.count, 1, 50, 10);

        if (!rawQuery) {
          throw new Error('搜索关键词不能为空');
        }

        const searchUrls = {
          google: `https://www.google.com/search?q=${encodeURIComponent(rawQuery)}&num=${resolvedCount}`,
          bing: `https://www.bing.com/search?q=${encodeURIComponent(rawQuery)}&count=${resolvedCount}`,
          baidu: `https://www.baidu.com/s?wd=${encodeURIComponent(rawQuery)}&rn=${resolvedCount}`,
          sogou: `https://www.sogou.com/web?query=${encodeURIComponent(rawQuery)}&num=${resolvedCount}`
        };

        const engineNames = {
          google: 'Google',
          bing: 'Bing (必应)',
          baidu: '百度',
          sogou: '搜狗'
        };

        const resolvedEngine = pickKey(searchUrls, requestedEngine, 'baidu');
        const searchUrl = searchUrls[resolvedEngine];

        const tips = [
          `精确匹配: "${rawQuery}"`,
          `排除关键词: ${rawQuery} -排除词`,
          `限定站点: site:github.com ${rawQuery}`,
          `文件类型: ${rawQuery} filetype:pdf`,
          `时间范围: ${rawQuery} after:2023`,
        ];

        const relatedSearches = [
          `${rawQuery} 教程`,
          `${rawQuery} 最佳实践`,
          `${rawQuery} 示例`,
          `${rawQuery} 文档`
        ];

        const detailsContent = `🔍 网络搜索\n\n` +
          `**搜索关键词**: ${rawQuery}\n` +
          `**搜索引擎**: ${engineNames[resolvedEngine]}\n` +
          `**期望结果数**: ${resolvedCount} 条\n\n` +
          `---\n\n` +
          `🔗 **搜索链接**: ${searchUrl}\n\n` +
          `⚠️ **请使用 WebFetch 工具获取搜索结果**:\n` +
          `\`\`\`javascript\n` +
          `WebFetch({\n` +
          `  url: "${searchUrl}",\n` +
          `  prompt: "提取前${resolvedCount}条搜索结果，包括：标题、链接、摘要"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **高级搜索技巧**:\n` +
          tips.map(tip => `• ${tip}`).join('\n') +
          `\n\n📌 **相关搜索建议**:\n` +
          relatedSearches.map(s => `• ${s}`).join('\n') +
          `\n\n🌐 **其他搜索引擎**:\n` +
          Object.keys(searchUrls)
            .filter(e => e !== resolvedEngine)
            .map(e => `• ${engineNames[e]}: ${searchUrls[e]}`)
            .join('\n');

        const filepath = await saveSearchResult('web-search', rawQuery, detailsContent);

        return makeTextResponse(
          `🔍 **网络搜索** (${engineNames[resolvedEngine]})\n\n` +
          `**关键词**: ${rawQuery}\n` +
          `**搜索链接**: ${searchUrl}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
      }

      case 'ai_search_github': {
        const rawQuery = normalizeString(args.query);
        const languageFilter = normalizeString(args.language);
        const requestedType = normalizeString(args.type).toLowerCase();
        const requestedSort = normalizeString(args.sort).toLowerCase();

        if (!rawQuery) {
          throw new Error('搜索关键词不能为空');
        }

        const typeNames = {
          repositories: '仓库',
          code: '代码',
          issues: '问题',
          users: '用户'
        };

        const sortNames = {
          stars: 'Star数',
          forks: 'Fork数',
          updated: '更新时间'
        };

        const typeKey = pickKey(typeNames, requestedType, 'repositories');
        const sortKey = pickKey(sortNames, requestedSort, 'stars');

        // 构建搜索URL
        let searchUrl = `https://github.com/search?q=${encodeURIComponent(rawQuery)}`;
        if (languageFilter) searchUrl += `+language:${encodeURIComponent(languageFilter)}`;
        searchUrl += `&type=${typeKey}&s=${sortKey}&o=desc`;

        // GitHub 搜索技巧
        const tips = [
          `Stars数量: ${rawQuery} stars:>1000`,
          `Fork数量: ${rawQuery} forks:>100`,
          `特定语言: ${rawQuery} language:javascript`,
          `最近更新: ${rawQuery} pushed:>2024-01-01`,
          `主题标签: ${rawQuery} topic:react`,
          `组织仓库: ${rawQuery} org:facebook`,
          `仓库大小: ${rawQuery} size:>10000`
        ];

        // 相关搜索建议
        const relatedSearches = [];
        if (typeKey === 'repositories') {
          relatedSearches.push(
            `${rawQuery} stars:>1000`,
            `${rawQuery} language:${languageFilter || 'javascript'}`,
            `awesome ${rawQuery}`
          );
        } else if (typeKey === 'code') {
          relatedSearches.push(
            `${rawQuery} extension:js`,
            `${rawQuery} path:src`,
            `${rawQuery} filename:README`
          );
        }

        const detailsContent = `🐙 GitHub 搜索\n\n` +
          `**搜索关键词**: ${rawQuery}\n` +
          `**搜索类型**: ${typeNames[typeKey]}\n` +
          `**编程语言**: ${languageFilter || '全部语言'}\n` +
          `**排序方式**: ${sortNames[sortKey]}\n\n` +
          `---\n\n` +
          `🔗 **搜索链接**: ${searchUrl}\n\n` +
          `⚠️ **请使用 WebFetch 工具获取搜索结果**:\n` +
          `\`\`\`javascript\n` +
          `WebFetch({\n` +
          `  url: "${searchUrl}",\n` +
          `  prompt: "提取前10个${typeNames[typeKey]}的名称、描述、${typeKey === 'repositories' ? 'Star数、Fork数' : '相关信息'}和链接"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **GitHub 高级搜索技巧**:\n` +
          tips.map(tip => `• ${tip}`).join('\n') +
          (relatedSearches.length > 0
            ? `\n\n📌 **相关搜索建议**:\n` + relatedSearches.map(s => `• ${s}`).join('\n')
            : '') +
          `\n\n📚 **更多搜索类型**:\n` +
          Object.keys(typeNames)
            .filter(t => t !== typeKey)
            .map((t) => {
              let altUrl = `https://github.com/search?q=${encodeURIComponent(rawQuery)}`;
              if (languageFilter) altUrl += `+language:${encodeURIComponent(languageFilter)}`;
              altUrl += `&type=${t}&s=${sortKey}&o=desc`;
              return `• ${typeNames[t]}: ${altUrl}`;
            })
            .join('\n');

        const filepath = await saveSearchResult('github-search', rawQuery, detailsContent);

        return makeTextResponse(
          `🐙 **GitHub搜索**\n\n` +
          `**关键词**: ${rawQuery}\n` +
          `**搜索链接**: ${searchUrl}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
      }

      case 'ai_search_stackoverflow': {
        const rawQuery = normalizeString(args.query);
        const tagsInput = normalizeString(args.tags);
        const requestedSort = normalizeString(args.sort).toLowerCase();

        if (!rawQuery) {
          throw new Error('搜索关键词不能为空');
        }

        const sortNames = {
          relevance: '相关性',
          votes: '投票数',
          creation: '创建时间',
          activity: '活跃度'
        };

        const sortKey = pickKey(sortNames, requestedSort, 'relevance');

        let searchQuery = rawQuery;
        let tagList = [];
        if (tagsInput) {
          tagList = tagsInput
            .split(',')
            .map((t) => normalizeString(t))
            .filter(Boolean);
          if (tagList.length > 0) {
            searchQuery += ` ${tagList.map(t => `[${t}]`).join(' ')}`;
          }
        }

        const searchUrl = `https://stackoverflow.com/search?q=${encodeURIComponent(searchQuery)}&sort=${sortKey}`;
        const tagsDisplay = tagList.length > 0 ? tagList.join(', ') : '无';

        // StackOverflow 搜索技巧
        const tips = [
          `标签搜索: [javascript] ${rawQuery}`,
          `已回答问题: ${rawQuery} is:answer`,
          `已接受答案: ${rawQuery} isaccepted:yes`,
          `投票数筛选: ${rawQuery} score:5..`,
          `多个标签: [react] [hooks] ${rawQuery}`,
          `代码搜索: code:"${rawQuery}"`,
          `标题搜索: title:"${rawQuery}"`
        ];

        // 热门技术标签推荐
        const popularTags = [
          'javascript', 'python', 'java', 'react', 'node.js',
          'typescript', 'html', 'css', 'sql', 'docker'
        ];

        const detailsContent = `💬 StackOverflow 搜索\n\n` +
          `**搜索关键词**: ${rawQuery}\n` +
          `**标签筛选**: ${tagsDisplay}\n` +
          `**排序方式**: ${sortNames[sortKey]}\n\n` +
          `---\n\n` +
          `🔗 **搜索链接**: ${searchUrl}\n\n` +
          `⚠️ **请使用 WebFetch 工具获取搜索结果**:\n` +
          `\`\`\`javascript\n` +
          `WebFetch({\n` +
          `  url: "${searchUrl}",\n` +
          `  prompt: "提取前10个问题的标题、投票数、回答数、是否已解决和链接"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **高级搜索技巧**:\n` +
          tips.map(tip => `• ${tip}`).join('\n') +
          `\n\n🏷️ **热门技术标签**:\n` +
          popularTags.map(tag => `• [${tag}]`).join(' ') +
          `\n\n📊 **其他排序方式**:\n` +
          Object.keys(sortNames)
            .filter(s => s !== sortKey)
            .map((s) =>
              `• ${sortNames[s]}: https://stackoverflow.com/search?q=${encodeURIComponent(searchQuery)}&sort=${s}`
            )
            .join('\n');

        const filepath = await saveSearchResult('stackoverflow-search', rawQuery, detailsContent);

        return makeTextResponse(
          `💬 **StackOverflow搜索**\n\n` +
          `**关键词**: ${rawQuery}\n` +
          `**搜索链接**: ${searchUrl}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
      }

      case 'ai_search_npm': {
        const rawQuery = normalizeString(args.query);
        const resolvedSize = clampNumber(args.size, 1, 100, 10);

        if (!rawQuery) {
          throw new Error('搜索关键词不能为空');
        }

        const searchUrl = `https://www.npmjs.com/search?q=${encodeURIComponent(rawQuery)}`;
        const registryUrl = `https://registry.npmjs.org/-/v1/search?text=${encodeURIComponent(rawQuery)}&size=${resolvedSize}`;

        // NPM 搜索技巧
        const tips = [
          `精确包名: ${rawQuery} (使用完整包名)`,
          `关键词搜索: keywords:${rawQuery}`,
          `作者搜索: author:${rawQuery}`,
          `维护者: maintainer:${rawQuery}`,
          `作用域包: @scope/${rawQuery}`,
          `特定版本: ${rawQuery}@latest`
        ];

        // 相关搜索建议
        const relatedSearches = [
          `${rawQuery} typescript`,
          `${rawQuery} cli`,
          `${rawQuery} plugin`,
          `@types/${rawQuery}`
        ];

        // 热门类别推荐
        const categories = [
          'react', 'vue', 'express', 'webpack',
          'babel', 'eslint', 'testing', 'cli-tools'
        ];

        const detailsContent = `📦 NPM 包搜索\n\n` +
          `**搜索关键词**: ${rawQuery}\n` +
          `**期望结果数**: ${resolvedSize} 个\n\n` +
          `---\n\n` +
          `🔗 **网页搜索**: ${searchUrl}\n` +
          `🔗 **API搜索**: ${registryUrl}\n\n` +
          `⚠️ **请使用 WebFetch 工具获取搜索结果**:\n` +
          `\`\`\`javascript\n` +
          `// 方式1: 网页搜索\n` +
          `WebFetch({\n` +
          `  url: "${searchUrl}",\n` +
          `  prompt: "提取前${resolvedSize}个包的：包名、描述、版本号、周下载量、最后更新时间"\n` +
          `})\n\n` +
          `// 方式2: API搜索 (推荐，结构化数据)\n` +
          `WebFetch({\n` +
          `  url: "${registryUrl}",\n` +
          `  prompt: "解析JSON数据，提取包的名称、描述、版本、作者和下载统计"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **NPM 搜索技巧**:\n` +
          tips.map(tip => `• ${tip}`).join('\n') +
          `\n\n📌 **相关搜索建议**:\n` +
          relatedSearches.map(s => `• ${s}`).join('\n') +
          `\n\n🏷️ **热门包分类**:\n` +
          categories.map(cat => `• ${cat}`).join(' ') +
          `\n\n📚 **直接访问包详情**: https://www.npmjs.com/package/${rawQuery}`;

        const filepath = await saveSearchResult('npm-search', rawQuery, detailsContent);

        return makeTextResponse(
          `📦 **NPM包搜索**\n\n` +
          `**关键词**: ${rawQuery}\n` +
          `**搜索链接**: ${searchUrl}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
      }

      case 'ai_search_docs': {
        const rawQuery = normalizeString(args.query);
        const requestedFramework = normalizeString(args.framework).toLowerCase();

        if (!rawQuery) {
          throw new Error('搜索关键词不能为空');
        }

        const docUrls = {
          react: `https://react.dev/?search=${encodeURIComponent(rawQuery)}`,
          vue: `https://cn.vuejs.org/search/?query=${encodeURIComponent(rawQuery)}`,
          angular: `https://angular.io/api?query=${encodeURIComponent(rawQuery)}`,
          nodejs: `https://nodejs.org/api/all.html`,
          python: `https://docs.python.org/zh-cn/3/search.html?q=${encodeURIComponent(rawQuery)}`,
          java: `https://docs.oracle.com/en/java/javase/21/docs/api/search.html?q=${encodeURIComponent(rawQuery)}`,
          general: `https://developer.mozilla.org/zh-CN/search?q=${encodeURIComponent(rawQuery)}`
        };

        const frameworkNames = {
          react: 'React',
          vue: 'Vue.js',
          angular: 'Angular',
          nodejs: 'Node.js',
          python: 'Python',
          java: 'Java',
          general: 'MDN Web Docs'
        };

        const frameworkTips = {
          react: ['Hooks', 'Components', 'Props', 'State', 'Context', 'useEffect'],
          vue: ['组合式API', '响应式', 'computed', 'watch', '组件', '指令'],
          angular: ['Directives', 'Services', 'Modules', 'Components', 'Routing'],
          nodejs: ['fs', 'http', 'path', 'events', 'stream', 'crypto'],
          python: ['列表推导', '装饰器', '生成器', '异步', 'pandas', 'numpy'],
          java: ['Collections', 'Stream', 'Optional', 'Lambda', 'Generic'],
          general: ['HTML', 'CSS', 'JavaScript', 'Web API', 'HTTP']
        };

        const resolvedFramework = pickKey(docUrls, requestedFramework, 'general');

        const detailsContent = `📚 ${frameworkNames[resolvedFramework]} 文档搜索\n\n` +
          `**搜索关键词**: ${rawQuery}\n` +
          `**框架/语言**: ${frameworkNames[resolvedFramework]}\n\n` +
          `---\n\n` +
          `🔗 **文档链接**: ${docUrls[resolvedFramework]}\n\n` +
          `⚠️ **请使用 WebFetch 工具获取文档内容**:\n` +
          `\`\`\`javascript\n` +
          `WebFetch({\n` +
          `  url: "${docUrls[resolvedFramework]}",\n` +
          `  prompt: "查找'${rawQuery}'相关的：API说明、参数列表、返回值、使用示例、注意事项"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **${frameworkNames[resolvedFramework]} 常用主题**:\n` +
          frameworkTips[resolvedFramework].map(tip => `• ${tip}`).join(' | ') +
          `\n\n📚 **其他文档资源**:\n` +
          Object.keys(docUrls)
            .filter(f => f !== resolvedFramework)
            .map(f => `• ${frameworkNames[f]}: ${docUrls[f].replace(/\?.*$/, '')}`)
            .slice(0, 4)
            .join('\n');

        const filepath = await saveSearchResult('docs-search', rawQuery, detailsContent);

        return makeTextResponse(
          `📚 **技术文档搜索**\n\n` +
          `**关键词**: ${rawQuery}\n` +
          `**搜索链接**: ${docUrls[resolvedFramework]}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
      }

      case 'ai_search_api_reference': {
        const rawApiName = normalizeString(args.api_name);
        const rawPlatform = normalizeString(args.platform);

        if (!rawApiName) {
          throw new Error('API名称不能为空');
        }
        if (!rawPlatform) {
          throw new Error('平台/库名称不能为空');
        }

        const searchUrls = {
          google: `https://www.google.com/search?q=${encodeURIComponent(`${rawPlatform} ${rawApiName} API documentation`)}`,
          devdocs: `https://devdocs.io/#q=${encodeURIComponent(`${rawPlatform} ${rawApiName}`)}`,
          github: `https://github.com/search?q=${encodeURIComponent(`${rawPlatform} ${rawApiName}`)}&type=code`
        };

        // 常见平台的直接文档链接
        const platformDocs = {
          express: `https://expressjs.com/en/api.html`,
          axios: `https://axios-http.com/docs/api_intro`,
          lodash: `https://lodash.com/docs/`,
          mongoose: `https://mongoosejs.com/docs/api.html`,
          sequelize: `https://sequelize.org/api/`,
          'socket.io': `https://socket.io/docs/v4/`,
          jwt: `https://github.com/auth0/node-jsonwebtoken#readme`
        };

        const directDoc = platformDocs[rawPlatform.toLowerCase()];

        const detailsContent = `🔗 API 参考搜索\n\n` +
          `**平台/库**: ${rawPlatform}\n` +
          `**API名称**: ${rawApiName}\n\n` +
          `---\n\n` +
          `🔍 **搜索资源**:\n` +
          `• Google: ${searchUrls.google}\n` +
          `• DevDocs: ${searchUrls.devdocs}\n` +
          `• GitHub: ${searchUrls.github}\n` +
          (directDoc ? `• 官方文档: ${directDoc}\n` : '') +
          `\n⚠️ **请使用 WebFetch 工具获取API文档**:\n` +
          `\`\`\`javascript\n` +
          `// 推荐：先搜索官方文档\n` +
          `WebFetch({\n` +
          `  url: "${directDoc || searchUrls.google}",\n` +
          `  prompt: "查找'${rawApiName}'的：函数签名、参数说明、返回值、使用示例、注意事项"\n` +
          `})\n\n` +
          `// 备选：在DevDocs搜索\n` +
          `WebFetch({\n` +
          `  url: "${searchUrls.devdocs}",\n` +
          `  prompt: "提取${rawPlatform}的${rawApiName} API详细文档"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **查询提示**:\n` +
          `• 精确搜索: "${rawPlatform}.${rawApiName}()"\n` +
          `• 示例代码: ${rawPlatform} ${rawApiName} example\n` +
          `• 参数说明: ${rawPlatform} ${rawApiName} parameters\n` +
          `• 错误处理: ${rawPlatform} ${rawApiName} error handling\n\n` +
          `📚 **相关资源**:\n` +
          `• NPM包: https://www.npmjs.com/package/${rawPlatform}\n` +
          `• GitHub仓库: https://github.com/search?q=${encodeURIComponent(rawPlatform)}&type=repositories\n` +
          `• StackOverflow: https://stackoverflow.com/search?q=${encodeURIComponent(`${rawPlatform} ${rawApiName}`)}`;

        const filepath = await saveSearchResult('api-search', rawApiName, detailsContent);

        return makeTextResponse(
          `🔗 **API参考搜索**\n\n` +
          `**关键词**: ${rawApiName}\n` +
          `**搜索链接**: ${directDoc || searchUrls.google}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
      }

      // === 国内搜索工具 ===
      case 'ai_search_wechat_docs': {
        const rawQuery = normalizeString(args.query);
        const platformInput = normalizeString(args.platform).toLowerCase();

        if (!rawQuery) {
          throw new Error('搜索关键词不能为空');
        }

        const platformUrls = {
          miniprogram: `https://developers.weixin.qq.com/miniprogram/dev/framework/`,
          officialaccount: `https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html`,
          open: `https://developers.weixin.qq.com/doc/oplatform/Third-party_Platforms/2.0/getting_started/how_to_read.html`,
          payment: `https://pay.weixin.qq.com/wiki/doc/apiv3/index.shtml`,
          all: `https://developers.weixin.qq.com/`
        };

        // 构建搜索URL（微信文档使用百度站内搜索）
        const searchUrl = `https://www.baidu.com/s?wd=site:developers.weixin.qq.com ${encodeURIComponent(rawQuery)}`;

        const platformNames = {
          miniprogram: '小程序',
          officialaccount: '公众号',
          open: '开放平台',
          payment: '微信支付',
          all: '全平台'
        };

        const resolvedPlatform = pickKey(platformNames, platformInput, 'all');

        // 常用API分类
        const apiCategories = {
          miniprogram: ['wx.request', 'wx.getUserInfo', 'wx.login', 'wx.showToast', 'wx.navigateTo'],
          officialaccount: ['接收消息', '发送消息', '自定义菜单', '网页授权', '模板消息'],
          payment: ['JSAPI支付', '小程序支付', 'APP支付', '退款', '对账单']
        };

        const detailsContent = `📱 微信开发者文档搜索\n\n` +
          `**搜索关键词**: ${rawQuery}\n` +
          `**平台类型**: ${platformNames[resolvedPlatform]}\n\n` +
          `---\n\n` +
          `🔗 **站内搜索**: ${searchUrl}\n` +
          `🔗 **${platformNames[resolvedPlatform]}文档**: ${platformUrls[resolvedPlatform]}\n\n` +
          `⚠️ **请使用 WebFetch 工具获取搜索结果**:\n` +
          `\`\`\`javascript\n` +
          `// 方式1: 百度站内搜索\n` +
          `WebFetch({\n` +
          `  url: "${searchUrl}",\n` +
          `  prompt: "提取微信文档中关于'${rawQuery}'的搜索结果"\n` +
          `})\n\n` +
          `// 方式2: 直接访问文档首页\n` +
          `WebFetch({\n` +
          `  url: "${platformUrls[resolvedPlatform]}",\n` +
          `  prompt: "在文档中查找'${rawQuery}'相关内容"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **常用${platformNames[resolvedPlatform]}API**:\n` +
          (apiCategories[resolvedPlatform] || ['基础组件', 'API接口', '开发工具']).map(api => `• ${api}`).join(' | ') +
          `\n\n📚 **其他微信平台**:\n` +
          Object.keys(platformNames)
            .filter(p => p !== resolvedPlatform)
            .map(p => `• ${platformNames[p]}: ${platformUrls[p]}`)
            .slice(0, 3)
            .join('\n') +
          `\n\n🔗 **开发者社区**: https://developers.weixin.qq.com/community/`;

        const filepath = await saveSearchResult('wechat-docs', rawQuery, detailsContent);

        return makeTextResponse(
          `📱 **微信开发者文档搜索**\n\n` +
          `**关键词**: ${rawQuery}\n` +
          `**搜索链接**: ${searchUrl}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
      }

      case 'ai_search_csdn':
      case 'ai_search_juejin':
      case 'ai_search_segmentfault':
      case 'ai_search_cnblogs':
      case 'ai_search_oschina':
      case 'ai_search_aliyun_docs':
      case 'ai_search_tencent_docs': {
        const rawQuery = normalizeString(args.query);

        if (!rawQuery) {
          throw new Error('搜索关键词不能为空');
        }

        const searchUrls = {
          ai_search_csdn: `https://so.csdn.net/so/search?q=${encodeURIComponent(rawQuery)}`,
          ai_search_juejin: `https://juejin.cn/search?query=${encodeURIComponent(rawQuery)}`,
          ai_search_segmentfault: `https://segmentfault.com/search?q=${encodeURIComponent(rawQuery)}`,
          ai_search_cnblogs: `https://zzk.cnblogs.com/s?w=${encodeURIComponent(rawQuery)}`,
          ai_search_oschina: `https://www.oschina.net/search?scope=all&q=${encodeURIComponent(rawQuery)}`,
          ai_search_aliyun_docs: `https://help.aliyun.com/search?spm=a2c4g.11186623.0.0&k=${encodeURIComponent(rawQuery)}`,
          ai_search_tencent_docs: `https://cloud.tencent.com/search?s=doc&keyword=${encodeURIComponent(rawQuery)}`
        };

        const platformInfo = {
          ai_search_csdn: {
            name: 'CSDN',
            icon: '📝',
            description: '中国最大的IT社区和服务平台',
            tips: ['博客文章', '技术问答', '代码片段', '下载资源'],
            homepage: 'https://www.csdn.net/',
            toolKey: 'csdn-search'
          },
          ai_search_juejin: {
            name: '掘金',
            icon: '💎',
            description: '面向开发者的技术内容分享平台',
            tips: ['前端开发', '后端开发', 'Android', 'iOS', '人工智能'],
            homepage: 'https://juejin.cn/',
            toolKey: 'juejin-search'
          },
          ai_search_segmentfault: {
            name: 'SegmentFault',
            icon: '🔧',
            description: '中文技术问答社区',
            tips: ['技术问答', '技术文章', '活动沙龙', '编程挑战'],
            homepage: 'https://segmentfault.com/',
            toolKey: 'sf-search'
          },
          ai_search_cnblogs: {
            name: '博客园',
            icon: '📚',
            description: '开发者的网上家园',
            tips: ['.NET', 'C#', 'Java', 'Python', '数据库'],
            homepage: 'https://www.cnblogs.com/',
            toolKey: 'cnblogs-search'
          },
          ai_search_oschina: {
            name: '开源中国',
            icon: '🌐',
            description: '中国最大的开源技术社区',
            tips: ['开源项目', '技术资讯', '代码托管', '协作翻译'],
            homepage: 'https://www.oschina.net/',
            toolKey: 'oschina-search'
          },
          ai_search_aliyun_docs: {
            name: '阿里云文档',
            icon: '☁️',
            description: '阿里云产品文档中心',
            tips: ['ECS', 'OSS', 'RDS', 'SLB', '容器服务'],
            homepage: 'https://help.aliyun.com/',
            toolKey: 'aliyun-docs'
          },
          ai_search_tencent_docs: {
            name: '腾讯云文档',
            icon: '☁️',
            description: '腾讯云产品文档中心',
            tips: ['CVM', 'COS', 'CDN', 'SCF', '数据库'],
            homepage: 'https://cloud.tencent.com/document/product',
            toolKey: 'tencent-docs'
          }
        };

        const info = platformInfo[name];
        const searchUrl = searchUrls[name];

        const detailsContent = `${info.icon} ${info.name} 搜索\n\n` +
          `**搜索关键词**: ${rawQuery}\n` +
          `**平台介绍**: ${info.description}\n\n` +
          `---\n\n` +
          `🔗 **搜索链接**: ${searchUrl}\n\n` +
          `⚠️ **请使用 WebFetch 工具获取搜索结果**:\n` +
          `\`\`\`javascript\n` +
          `WebFetch({\n` +
          `  url: "${searchUrl}",\n` +
          `  prompt: "提取前10条搜索结果（标题、作者、发布时间、摘要、链接）"\n` +
          `})\n` +
          `\`\`\`\n\n` +
          `---\n\n` +
          `💡 **${info.name} 热门主题**:\n` +
          info.tips.map(tip => `• ${tip}`).join(' | ') +
          `\n\n🏠 **平台首页**: ${info.homepage}\n\n` +
          `📌 **搜索建议**:\n` +
          `• 使用精确关键词获得更好的结果\n` +
          `• 结合多个平台搜索可获得更全面的信息\n` +
          `• 关注文章的发布时间，优先查看最新内容`;

        const filepath = await saveSearchResult(info.toolKey, rawQuery, detailsContent);

        return makeTextResponse(
          `${info.icon} **${info.name}搜索**\n\n` +
          `**关键词**: ${rawQuery}\n` +
          `**搜索链接**: ${searchUrl}\n\n` +
          `✅ 详细信息已保存至: ${filepath || '保存失败'}\n` +
          `💡 使用 WebFetch 工具访问搜索链接获取结果`
        );
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
  console.error('Smart Search MCP Server v2.0.0 running on stdio');
  console.error('Tools: 14 search tools');
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});
