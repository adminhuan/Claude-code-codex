#!/usr/bin/env python3
"""
功能请求(FR)管理使用示例
演示AI如何提出和管理功能改进建议
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from ai_duet.mcp.tools import (
    ai_submit_feature_request,
    ai_vote_feature_request,
    ai_list_feature_requests,
    ai_get_feature_request,
    ai_suggest_rule_improvements
)


async def demo_fr_workflow():
    """演示完整的FR工作流程"""
    print("🎯 功能请求(FR)管理演示\n")

    # 1. Claude Code发现问题并提出FR
    print("1️⃣ Claude Code 发现代码问题，提出改进建议:")
    fr1_result = await ai_submit_feature_request(
        title="增强SQL注入检测规则",
        description="当前规则只检测简单的字符串拼接，建议添加对动态查询构建、存储过程调用等场景的检测",
        submitter="claude_code",
        priority="high",
        category="rule_improvement"
    )
    print(f"📤 {fr1_result}\n")

    # 2. Codex提出UI改进建议
    print("2️⃣ Codex 提出用户体验改进:")
    fr2_result = await ai_submit_feature_request(
        title="规则提醒支持严重程度分级",
        description="目前所有规则提醒都是同等重要，建议按严重程度分级显示：🔴严重 🟡警告 🔵建议",
        submitter="codex",
        priority="medium",
        category="new_feature"
    )
    print(f"📤 {fr2_result}\n")

    # 3. 查看所有提议中的FR
    print("3️⃣ 查看待评审的功能请求:")
    proposed_frs = await ai_list_feature_requests(status="proposed")
    print(f"📋 {proposed_frs}\n")

    # 4. AI之间互相投票
    print("4️⃣ AI协作投票过程:")

    # 获取FR ID（从返回的结果中提取）
    import re
    fr1_match = re.search(r'FR ID: (FR\d+_\d+)', fr1_result)
    fr2_match = re.search(r'FR ID: (FR\d+_\d+)', fr2_result)

    if fr1_match and fr2_match:
        fr1_id = fr1_match.group(1)
        fr2_id = fr2_match.group(1)

        # Codex投票支持Claude的提议
        vote1 = await ai_vote_feature_request(fr1_id, "approve", "codex")
        print(f"🗳️ Codex投票: {vote1}\n")

        # Claude Code投票支持Codex的提议
        vote2 = await ai_vote_feature_request(fr2_id, "approve", "claude_code")
        print(f"🗳️ Claude投票: {vote2}\n")

        # 5. 查看FR详情
        print("5️⃣ 查看已投票的FR详情:")
        fr1_details = await ai_get_feature_request(fr1_id)
        print(f"📄 FR详情:\n{fr1_details}\n")

    # 6. 查看已批准的FR
    print("6️⃣ 查看已批准的功能请求:")
    approved_frs = await ai_list_feature_requests(status="approved")
    print(f"✅ {approved_frs}\n")

    return "✅ FR工作流程演示完成"


async def demo_intelligent_suggestions():
    """演示智能规则建议功能"""
    print("🧠 智能规则建议演示\n")

    # 模拟发现的代码问题
    code_issues = [
        "函数缺少错误处理",
        "数据库密码硬编码在配置文件中",
        "API调用没有超时设置",
        "用户输入未做SQL注入验证",
        "函数命名使用了camelCase而非snake_case"
    ]

    print("1️⃣ 发现的代码问题:")
    for i, issue in enumerate(code_issues, 1):
        print(f"   {i}. {issue}")

    print("\n2️⃣ AI智能分析并建议规则改进:")
    suggestions = await ai_suggest_rule_improvements(code_issues)
    print(f"{suggestions}\n")

    return "✅ 智能建议演示完成"


async def demo_collaborative_fr():
    """演示协作式FR管理"""
    print("🤝 协作式功能请求管理\n")

    # 1. 基于协作发现的问题提出FR
    print("1️⃣ 基于AI协作过程中发现的问题提出FR:")
    collab_fr = await ai_submit_feature_request(
        title="协作消息支持代码片段高亮",
        description="在AI协作过程中经常需要分享代码片段，建议消息支持Markdown格式和代码高亮",
        submitter="claude_code",
        priority="low",
        category="collaboration"
    )
    print(f"📤 {collab_fr}\n")

    # 2. 提出工具改进建议
    print("2️⃣ 提出开发工具改进:")
    tool_fr = await ai_submit_feature_request(
        title="规则配置支持团队模板",
        description="不同团队有不同的编码规范，建议支持团队规则模板，新项目可以一键导入",
        submitter="codex",
        priority="medium",
        category="new_feature"
    )
    print(f"📤 {tool_fr}\n")

    # 3. 查看所有类别的FR统计
    print("3️⃣ 各类别FR统计:")
    categories = ["rule_improvement", "new_feature", "collaboration", "ui"]

    for category in categories:
        frs = await ai_list_feature_requests(category=category)
        count = len([line for line in frs.split('\n') if line.startswith('🆕') or line.startswith('👀') or line.startswith('✅')])
        print(f"   🏷️ {category}: {count} 个FR")

    return "✅ 协作FR管理演示完成"


async def main():
    """运行所有FR演示"""
    print("🚀 AI功能请求(FR)管理系统演示\n")
    print("="*60)

    demos = [
        ("基础FR工作流程", demo_fr_workflow),
        ("智能规则建议", demo_intelligent_suggestions),
        ("协作式FR管理", demo_collaborative_fr)
    ]

    for demo_name, demo_func in demos:
        print(f"\n📋 演示: {demo_name}")
        print("-" * 40)
        try:
            result = await demo_func()
            print(f"{result}\n")
        except Exception as e:
            print(f"❌ 演示出错: {e}\n")
            import traceback
            traceback.print_exc()

    print("="*60)
    print("🎯 FR管理系统的价值:")
    print("\n💡 对于AI开发:")
    print("  🤖 AI可以主动发现问题并提出改进建议")
    print("  🔄 通过投票机制确保改进的合理性")
    print("  📊 系统化地管理功能演进")

    print("\n🤝 对于AI协作:")
    print("  💬 提供了AI之间讨论改进的结构化方式")
    print("  📋 记录了功能决策的完整过程")
    print("  🎯 确保重要改进不会被遗忘")

    print("\n📈 对于项目管理:")
    print("  📊 可视化的功能请求管理")
    print("  🗳️ 民主化的决策过程")
    print("  📝 详细的改进历史记录")

    print("\n🎉 FR功能已集成到MCP工具中！")


if __name__ == "__main__":
    asyncio.run(main())