#!/usr/bin/env python3
"""
模式管理系统使用示例
演示Plan模式、PR模式、FR模式的切换和使用
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from ai_duet.mcp.tools import (
    # 模式管理
    ai_switch_mode,
    ai_get_current_mode,
    ai_list_modes,
    ai_get_mode_statistics,

    # Plan模式功能
    ai_create_plan,
    ai_add_task_to_plan,
    ai_update_task_status,
    ai_list_plans,
    ai_get_plan_details,

    # PR模式功能
    ai_create_pr,
    ai_add_review_comment,
    ai_update_pr_status,
    ai_list_prs,
    ai_get_pr_details,

    # FR模式功能
    ai_submit_feature_request,
    ai_vote_feature_request,
    ai_list_feature_requests
)


async def demo_mode_switching():
    """演示模式切换功能"""
    print("🔄 模式切换演示\n")

    # 1. 查看当前模式
    current = await ai_get_current_mode()
    print(f"📍 当前模式: {current}")

    # 2. 查看所有可用模式
    modes = await ai_list_modes()
    print(f"📋 可用模式:\n{modes}\n")

    # 3. 切换到不同模式
    modes_to_test = ["plan", "pr", "fr", "normal"]

    for mode in modes_to_test:
        print(f"🔄 切换到 {mode} 模式...")
        result = await ai_switch_mode(mode)
        print(f"✅ {result}")

        current = await ai_get_current_mode()
        print(f"📍 确认当前模式: {current}\n")

    return "✅ 模式切换演示完成"


async def demo_plan_mode():
    """演示Plan模式功能"""
    print("📋 Plan模式演示\n")

    # 切换到Plan模式
    await ai_switch_mode("plan")
    print("🔄 已切换到Plan模式\n")

    # 1. 创建开发计划
    print("1️⃣ 创建开发计划:")
    plan_result = await ai_create_plan(
        title="AI协作功能增强",
        description="改进AI之间的协作效率，增加更多智能化功能",
        creator="claude_code",
        priority="high",
        estimated_hours=40
    )
    print(f"📝 {plan_result}\n")

    # 提取计划ID
    import re
    plan_match = re.search(r'计划ID: (PLAN_\d+_\d+)', plan_result)
    if plan_match:
        plan_id = plan_match.group(1)

        # 2. 添加任务
        print("2️⃣ 添加计划任务:")
        tasks = [
            ("实现智能代码审查", "基于AI的自动代码质量检查", 8),
            ("优化协作消息系统", "改进AI之间的通信机制", 12),
            ("增加实时状态同步", "确保AI状态的实时同步", 6),
            ("完善错误处理机制", "增强系统的健壮性", 8),
            ("添加性能监控", "监控AI协作的性能指标", 6)
        ]

        for title, desc, hours in tasks:
            task_result = await ai_add_task_to_plan(plan_id, title, desc, hours, "claude_code")
            print(f"  ✅ {task_result}")

        print()

        # 3. 查看计划详情
        print("3️⃣ 查看计划详情:")
        details = await ai_get_plan_details(plan_id)
        print(f"📊 {details}\n")

        # 4. 更新任务状态
        print("4️⃣ 模拟任务进度更新:")
        # 这里需要从详情中提取任务ID，简化演示
        print("  🚧 (模拟)第一个任务开始进行中...")
        print("  ✅ (模拟)第二个任务已完成...\n")

    # 5. 查看所有计划
    print("5️⃣ 查看所有计划:")
    all_plans = await ai_list_plans()
    print(f"📋 {all_plans}\n")

    return "✅ Plan模式演示完成"


async def demo_pr_mode():
    """演示PR模式功能"""
    print("🔍 PR模式演示\n")

    # 切换到PR模式
    await ai_switch_mode("pr")
    print("🔄 已切换到PR模式\n")

    # 1. 创建PR
    print("1️⃣ 创建代码审查PR:")
    pr_result = await ai_create_pr(
        title="重构AI协作核心模块",
        description="优化代码结构，提高可维护性和性能",
        author="claude_code",
        reviewer="codex",
        files_changed=["ai_duet/core/collaboration.py", "ai_duet/agents/orchestrator.py"],
        priority="high"
    )
    print(f"📤 {pr_result}\n")

    # 提取PR ID
    import re
    pr_match = re.search(r'PR ID: (PR\d+_\d+)', pr_result)
    if pr_match:
        pr_id = pr_match.group(1)

        # 2. 添加审查评论
        print("2️⃣ 添加审查评论:")
        comments = [
            ("代码整体结构清晰，但建议在关键函数添加类型注解", "ai_duet/core/collaboration.py", 45),
            ("异常处理可以更加细粒度，建议区分不同类型的错误", "ai_duet/agents/orchestrator.py", 123),
            ("性能优化做得很好，建议添加单元测试覆盖新功能", None, None)
        ]

        for comment, file_path, line_num in comments:
            comment_result = await ai_add_review_comment(pr_id, "codex", comment, file_path, line_num)
            print(f"  💬 {comment_result}")

        print()

        # 3. 更新PR状态
        print("3️⃣ 更新PR状态:")
        status_result = await ai_update_pr_status(pr_id, "approved", "codex")
        print(f"✅ {status_result}\n")

        # 4. 查看PR详情
        print("4️⃣ 查看PR详情:")
        pr_details = await ai_get_pr_details(pr_id)
        print(f"📊 {pr_details}\n")

    # 5. 查看所有PR
    print("5️⃣ 查看所有PR:")
    all_prs = await ai_list_prs()
    print(f"📋 {all_prs}\n")

    return "✅ PR模式演示完成"


async def demo_fr_mode():
    """演示FR模式功能"""
    print("💡 FR模式演示\n")

    # 切换到FR模式
    await ai_switch_mode("fr")
    print("🔄 已切换到FR模式\n")

    # 1. 提交功能请求
    print("1️⃣ 提交功能改进请求:")
    fr_result = await ai_submit_feature_request(
        title="增加AI协作模式的可视化界面",
        description="当前AI协作都是通过文本进行，建议添加图形界面显示协作状态、进度等信息",
        submitter="claude_code",
        priority="medium",
        category="new_feature"
    )
    print(f"📤 {fr_result}\n")

    # 2. 查看功能请求
    print("2️⃣ 查看所有功能请求:")
    all_frs = await ai_list_feature_requests()
    print(f"📋 {all_frs}\n")

    # 3. 投票功能请求
    print("3️⃣ 对功能请求投票:")
    import re
    fr_match = re.search(r'FR ID: (FR\d+_\d+)', fr_result)
    if fr_match:
        fr_id = fr_match.group(1)
        vote_result = await ai_vote_feature_request(fr_id, "approve", "codex")
        print(f"🗳️ {vote_result}\n")

    return "✅ FR模式演示完成"


async def demo_statistics():
    """演示统计信息查看"""
    print("📊 系统统计信息\n")

    stats = await ai_get_mode_statistics()
    print(f"📈 {stats}\n")

    return "✅ 统计信息演示完成"


async def main():
    """运行所有模式演示"""
    print("🚀 AI模式管理系统演示\n")
    print("=" * 60)

    demos = [
        ("模式切换功能", demo_mode_switching),
        ("Plan模式功能", demo_plan_mode),
        ("PR模式功能", demo_pr_mode),
        ("FR模式功能", demo_fr_mode),
        ("系统统计信息", demo_statistics)
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

    print("=" * 60)
    print("🎯 模式管理系统的优势:")
    print("\n🔄 灵活的模式切换:")
    print("  📋 Plan模式: 专注于项目规划和任务管理")
    print("  🔍 PR模式: 专注于代码审查和质量控制")
    print("  💡 FR模式: 专注于功能改进和创新建议")
    print("  ⚙️ Normal模式: 基础的规则提醒功能")

    print("\n🎛️ 模式特性:")
    print("  🎯 每个模式都有专门的工具和工作流")
    print("  📊 独立的数据管理和状态跟踪")
    print("  🔗 模式间可以无缝切换")
    print("  📈 统一的统计和监控")

    print("\n🤖 对AI协作的价值:")
    print("  🎪 提供了结构化的协作环境")
    print("  📋 明确了不同场景下的工作重点")
    print("  🔄 支持灵活的工作流调整")
    print("  📊 便于跟踪和管理协作进度")

    print("\n🎉 模式管理系统已完成集成！")


if __name__ == "__main__":
    asyncio.run(main())