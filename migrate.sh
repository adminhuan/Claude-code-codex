#!/bin/bash
# Smart Search MCP 迁移脚本
# 从 ai-rule-mcp-server 升级到 smart-search-mcp

set -e

echo "🔄 Smart Search MCP 迁移脚本"
echo "=================================================="
echo ""
echo "此脚本将帮助你从旧版本 ai-rule-mcp-server 升级到新版本 smart-search-mcp"
echo ""

# 1. 检查是否安装了旧版本
echo "📋 检查旧版本..."
if npm list -g ai-rule-mcp-server &> /dev/null; then
    echo "✅ 发现旧版本 ai-rule-mcp-server"

    read -p "是否卸载旧版本？(y/n): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo "🗑️  卸载旧版本..."
        npm uninstall -g ai-rule-mcp-server
        echo "✅ 旧版本已卸载"
    fi
else
    echo "ℹ️  未发现全局安装的旧版本"
fi

# 2. 清理旧配置
echo ""
echo "📋 检查配置文件..."

CLAUDE_CONFIG="$HOME/.claude.json"
OLD_CONFIG_FOUND=false

if [ -f "$CLAUDE_CONFIG" ]; then
    echo "✅ 发现配置文件: $CLAUDE_CONFIG"

    # 使用Python/Node.js精确检测是否存在旧配置（而不是用grep）
    if command -v python3 &> /dev/null; then
        HAS_OLD_CONFIG=$(python3 -c "
import json
import sys
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)

found = False
if 'mcpServers' in config and 'ai-rule-mcp-server' in config['mcpServers']:
    found = True
if 'projects' in config:
    for project_config in config['projects'].values():
        if 'mcpServers' in project_config and 'ai-rule-mcp-server' in project_config['mcpServers']:
            found = True
            break

print('yes' if found else 'no')
" 2>/dev/null)
    elif command -v node &> /dev/null; then
        HAS_OLD_CONFIG=$(node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$CLAUDE_CONFIG', 'utf8'));

let found = false;
if (config.mcpServers && config.mcpServers['ai-rule-mcp-server']) {
    found = true;
}
if (config.projects) {
    for (const projectConfig of Object.values(config.projects)) {
        if (projectConfig.mcpServers && projectConfig.mcpServers['ai-rule-mcp-server']) {
            found = true;
            break;
        }
    }
}

console.log(found ? 'yes' : 'no');
" 2>/dev/null)
    else
        HAS_OLD_CONFIG="unknown"
    fi

    if [ "$HAS_OLD_CONFIG" = "yes" ]; then
        echo "⚠️  发现旧配置 ai-rule-mcp-server"
        OLD_CONFIG_FOUND=true

        # 备份配置文件
        cp "$CLAUDE_CONFIG" "$CLAUDE_CONFIG.backup"
        echo "✅ 已备份配置文件到: $CLAUDE_CONFIG.backup"

        echo "🗑️  自动删除旧配置..."
        # 使用Python/Node.js删除JSON中的旧配置（包括所有项目）
        if command -v python3 &> /dev/null; then
            python3 -c "
import json
with open('$CLAUDE_CONFIG', 'r') as f:
    config = json.load(f)

deleted_count = 0

# 删除全局配置
if 'mcpServers' in config and 'ai-rule-mcp-server' in config['mcpServers']:
    del config['mcpServers']['ai-rule-mcp-server']
    deleted_count += 1
    print('✅ 已删除全局配置')

# 删除所有项目中的配置
if 'projects' in config:
    for project_path, project_config in config['projects'].items():
        if 'mcpServers' in project_config and 'ai-rule-mcp-server' in project_config['mcpServers']:
            del project_config['mcpServers']['ai-rule-mcp-server']
            deleted_count += 1
            print(f'✅ 已删除项目配置: {project_path}')

with open('$CLAUDE_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)

if deleted_count > 0:
    print(f'✅ 共删除 {deleted_count} 个旧配置')
else:
    print('ℹ️  未找到需要删除的配置')
"
        elif command -v node &> /dev/null; then
            node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('$CLAUDE_CONFIG', 'utf8'));

let deletedCount = 0;

// 删除全局配置
if (config.mcpServers && config.mcpServers['ai-rule-mcp-server']) {
    delete config.mcpServers['ai-rule-mcp-server'];
    deletedCount++;
    console.log('✅ 已删除全局配置');
}

// 删除所有项目中的配置
if (config.projects) {
    for (const [projectPath, projectConfig] of Object.entries(config.projects)) {
        if (projectConfig.mcpServers && projectConfig.mcpServers['ai-rule-mcp-server']) {
            delete projectConfig.mcpServers['ai-rule-mcp-server'];
            deletedCount++;
            console.log('✅ 已删除项目配置: ' + projectPath);
        }
    }
}

fs.writeFileSync('$CLAUDE_CONFIG', JSON.stringify(config, null, 2));

if (deletedCount > 0) {
    console.log('✅ 共删除 ' + deletedCount + ' 个旧配置');
} else {
    console.log('ℹ️  未找到需要删除的配置');
}
"
        else
            echo "⚠️  需要 Python 或 Node.js 来自动删除配置"
            echo "请手动编辑: $CLAUDE_CONFIG"
            echo "删除 'ai-rule-mcp-server' 配置项"
            read -p "删除完成后，按回车键继续..."
        fi
    elif [ "$HAS_OLD_CONFIG" = "no" ]; then
        echo "✅ 配置文件中未发现旧配置"
    else
        echo "⚠️  无法检测配置（需要 Python 或 Node.js）"
        echo "请手动检查: $CLAUDE_CONFIG"
    fi
else
    echo "ℹ️  配置文件不存在"
fi

# 3. 安装新版本
echo ""
echo "📦 安装新版本 smart-search-mcp..."
echo ""

# 自动尝试使用Claude MCP命令
if command -v claude &> /dev/null; then
    echo "✅ 检测到 claude 命令，使用 Claude MCP 安装"

    # 检查是否已经存在
    if claude mcp list 2>/dev/null | grep -q "smart-search-mcp"; then
        echo "ℹ️  检测到 smart-search-mcp 已存在"
        read -p "是否重新配置？(y/n): " reconfig
        if [ "$reconfig" = "y" ] || [ "$reconfig" = "Y" ]; then
            echo "🔄 删除旧配置..."
            claude mcp remove smart-search-mcp 2>/dev/null || true
            echo "📦 添加新配置..."
            claude mcp add smart-search-mcp npx smart-search-mcp
        else
            echo "⏭️  跳过配置"
        fi
    else
        claude mcp add smart-search-mcp npx smart-search-mcp
    fi

    echo ""
    echo "✅ MCP服务器配置完成！"
else
    echo "ℹ️  未找到 claude 命令，使用全局安装"
    npm install -g smart-search-mcp
    echo ""
    echo "✅ 全局安装完成！"
    echo ""
    echo "📝 请运行以下命令配置："
    echo "claude mcp add smart-search-mcp npx smart-search-mcp"
fi

echo ""
echo "🎉 迁移完成！"
echo ""
echo "📚 下一步："
echo "1. 重启 Claude Code"
echo "2. 试试说: '搜索React Hooks最佳实践'"
echo "3. 或者说: '搜索微信小程序一键登录'"
echo ""
echo "📖 更多信息: https://github.com/adminhuan/smart-search-mcp"