#!/bin/bash
# AI Duet 安装脚本

set -e  # 遇到错误立即退出

echo "🚀 开始安装 AI Duet 协作系统..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python版本检查通过: $python_version"
else
    echo "❌ 需要Python 3.8或更高版本，当前版本: $python_version"
    exit 1
fi

# 创建虚拟环境（可选）
if [ "$1" = "--venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv ai_duet_env
    source ai_duet_env/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 安装本地包
echo "🔧 安装 AI Duet..."
pip install -e .

# 验证安装
echo "🧪 验证安装..."
if python -c "import ai_duet; print('AI Duet 导入成功')" 2>/dev/null; then
    echo "✅ 安装成功！"
else
    echo "❌ 安装验证失败"
    exit 1
fi

echo ""
echo "🎉 AI Duet 安装完成！"
echo ""
echo "使用方法:"
echo "1. 设置环境变量:"
echo "   export OPENAI_API_KEY='your-openai-key'"
echo "   export ANTHROPIC_API_KEY='your-anthropic-key'"
echo ""
echo "2. 运行协作:"
echo "   python -m ai_duet \"你的任务描述\""
echo "   或者"
echo "   ai-duet \"你的任务描述\""
echo ""
echo "3. 查看帮助:"
echo "   python -m ai_duet --help"
echo ""

if [ "$1" = "--venv" ]; then
    echo "注意: 每次使用前需要激活虚拟环境:"
    echo "   source ai_duet_env/bin/activate"
fi