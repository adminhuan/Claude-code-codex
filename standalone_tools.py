#!/usr/bin/env python3
"""
独立工具脚本 - 不依赖MCP协议直接使用AI规则工具
适用于Claude Code无法安装MCP服务器的情况
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from ai_duet.mcp.tools import (
    ai_rule_reminder,
    ai_check_compliance,
    ai_get_rules,
    ai_switch_mode,
    ai_get_current_mode,
    ai_list_modes,
    ai_create_plan,
    ai_submit_feature_request
)


async def interactive_menu():
    """交互式菜单"""
    print("🛠️ AI规则遵守工具 - 独立版本")
    print("=" * 50)

    while True:
        print("\n📋 可用功能:")
        print("1. 🎯 获取规则提醒")
        print("2. 🔍 检查代码合规性")
        print("3. 📜 查看所有规则")
        print("4. 🔄 切换工作模式")
        print("5. 📊 查看当前模式")
        print("6. 📋 创建开发计划")
        print("7. 💡 提交功能请求")
        print("8. 🚪 退出")

        choice = input("\n请选择功能 (1-8): ").strip()

        try:
            if choice == "1":
                context = input("请输入开发任务描述: ")
                result = await ai_rule_reminder(context)
                print(f"\n📝 规则提醒:\n{result}")

            elif choice == "2":
                code = input("请输入要检查的代码: ")
                result = await ai_check_compliance(code)
                print(f"\n✅ 合规检查结果:\n{result}")

            elif choice == "3":
                result = await ai_get_rules()
                print(f"\n📜 规则清单:\n{result}")

            elif choice == "4":
                modes = await ai_list_modes()
                print(f"\n{modes}")
                mode = input("请输入要切换的模式 (normal/plan/pr/fr): ")
                result = await ai_switch_mode(mode)
                print(f"\n🔄 {result}")

            elif choice == "5":
                result = await ai_get_current_mode()
                print(f"\n📊 {result}")

            elif choice == "6":
                title = input("计划标题: ")
                description = input("计划描述: ")
                creator = input("创建者: ")
                result = await ai_create_plan(title, description, creator)
                print(f"\n📋 {result}")

            elif choice == "7":
                title = input("功能请求标题: ")
                description = input("功能请求描述: ")
                submitter = input("提交者: ")
                result = await ai_submit_feature_request(title, description, submitter)
                print(f"\n💡 {result}")

            elif choice == "8":
                print("👋 再见!")
                break

            else:
                print("❌ 无效选择，请输入 1-8")

        except Exception as e:
            print(f"❌ 执行出错: {e}")

        input("\n按回车键继续...")


async def quick_demo():
    """快速演示所有功能"""
    print("🚀 快速演示所有功能\n")

    # 1. 规则提醒
    print("1️⃣ 规则提醒演示:")
    result = await ai_rule_reminder("实现用户登录API")
    print(f"{result}\n")

    # 2. 模式管理
    print("2️⃣ 模式管理演示:")
    await ai_switch_mode("plan")
    mode = await ai_get_current_mode()
    print(f"{mode}\n")

    # 3. 创建计划
    print("3️⃣ 创建计划演示:")
    plan = await ai_create_plan("用户认证系统", "实现完整的登录注册功能", "demo_user")
    print(f"{plan}\n")

    # 4. 功能请求
    print("4️⃣ 功能请求演示:")
    fr = await ai_submit_feature_request("增加代码格式化检查", "建议添加自动代码格式化规则", "demo_user")
    print(f"{fr}\n")

    print("✅ 演示完成!")


async def main():
    """主函数"""
    print("🎯 欢迎使用AI规则遵守工具!")
    print("\n由于Claude Code无法安装第三方MCP服务器，")
    print("我们提供了这个独立版本供您使用。\n")

    mode = input("请选择模式:\n1. 交互式使用\n2. 快速演示\n请输入 (1/2): ").strip()

    if mode == "1":
        await interactive_menu()
    elif mode == "2":
        await quick_demo()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(main())