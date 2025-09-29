#!/usr/bin/env python3
"""
AI规则遵守MCP工具测试脚本
验证主要功能和可选功能
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
    ai_add_custom_rule,
    ai_enable_collaboration,
    ai_send_message,
    ai_read_messages,
    ai_collaboration_status
)


async def test_basic_rule_features():
    """测试基本规则功能"""
    print("🧪 测试基本规则功能...\n")

    # 1. 测试规则提醒
    print("1️⃣ 测试规则提醒功能:")
    context = "我要写一个登录API处理用户密码"
    reminder = await ai_rule_reminder(context)
    print(f"上下文: {context}")
    print(f"提醒结果:\n{reminder}\n")

    # 2. 测试代码合规检查
    print("2️⃣ 测试代码合规检查:")
    bad_code = '''
def LoginUser(username, password):
	sql = "SELECT * FROM users WHERE username='" + username + "'"
	password_plain = password
    '''
    compliance = await ai_check_compliance(bad_code)
    print(f"检查代码:\n{bad_code}")
    print(f"合规结果:\n{compliance}\n")

    # 3. 测试获取规则
    print("3️⃣ 测试获取安全规则:")
    security_rules = await ai_get_rules("security")
    print(f"安全规则:\n{security_rules}\n")

    # 4. 测试添加自定义规则
    print("4️⃣ 测试添加自定义规则:")
    add_result = await ai_add_custom_rule(
        "注释规范",
        "函数,方法,类",
        "所有公开的函数和类都必须有文档字符串"
    )
    print(f"添加结果: {add_result}\n")

    return True


async def test_collaboration_features():
    """测试协作功能"""
    print("🤝 测试协作功能...\n")

    # 1. 检查初始协作状态
    print("1️⃣ 检查初始协作状态:")
    status = await ai_collaboration_status()
    print(f"协作状态:\n{status}\n")

    # 2. 启用协作功能
    print("2️⃣ 启用协作功能:")
    enable_result = await ai_enable_collaboration(True)
    print(f"启用结果: {enable_result}\n")

    # 3. 发送协作消息
    print("3️⃣ 发送协作消息:")
    send_result1 = await ai_send_message("我开始实现用户认证功能", "claude_code")
    print(f"Claude Code发送: {send_result1}")

    send_result2 = await ai_send_message("收到，我会审查你的认证实现", "codex")
    print(f"Codex发送: {send_result2}\n")

    # 4. 读取协作消息
    print("4️⃣ 读取协作消息:")
    messages = await ai_read_messages()
    print(f"所有消息:\n{messages}\n")

    # 5. 读取特定AI的消息
    print("5️⃣ 读取Claude Code的消息:")
    claude_messages = await ai_read_messages("claude_code")
    print(f"Claude消息:\n{claude_messages}\n")

    # 6. 检查协作状态
    print("6️⃣ 检查启用后的协作状态:")
    final_status = await ai_collaboration_status()
    print(f"最终状态:\n{final_status}\n")

    return True


async def test_rule_triggers():
    """测试规则触发机制"""
    print("🎯 测试规则触发机制...\n")

    test_cases = [
        ("编写用户注册函数", "应该触发编码规范和安全规则"),
        ("创建新的API目录", "应该触发项目结构规则"),
        ("实现数据库查询", "应该触发安全规则和错误处理"),
        ("写单元测试", "应该触发项目结构规则"),
        ("优化算法性能", "应该触发编码规范")
    ]

    for i, (context, expectation) in enumerate(test_cases, 1):
        print(f"{i}️⃣ 测试用例: {context}")
        print(f"   期望: {expectation}")

        reminder = await ai_rule_reminder(context)
        print(f"   实际提醒:\n{reminder}\n")

    return True


async def test_comprehensive_scenario():
    """测试综合场景"""
    print("🏗️ 测试综合开发场景...\n")

    # 场景：Claude Code 开发登录功能
    print("📝 场景：Claude Code 开发登录功能")

    # 1. 启动开发前的规则检查
    print("\n🔍 步骤1：开发前规则检查")
    context = "开始实现用户登录认证功能，包括密码验证和JWT token生成"
    reminder = await ai_rule_reminder(context)
    print(f"Claude Code 询问规则:\n{reminder}")

    # 2. 代码实现过程中的合规检查
    print("\n💻 步骤2：代码实现")
    code = '''
def authenticate_user(username: str, password: str) -> dict:
    """验证用户登录"""
    try:
        # 参数化查询防止SQL注入
        query = "SELECT id, hashed_password FROM users WHERE username = %s"
        user = db.execute_query(query, (username,))

        if user and verify_password(password, user['hashed_password']):
            token = generate_jwt_token(user['id'])
            return {"success": True, "token": token}
        else:
            return {"success": False, "error": "Invalid credentials"}
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return {"success": False, "error": "Authentication failed"}
    '''

    compliance = await ai_check_compliance(code)
    print(f"代码合规检查:\n{compliance}")

    # 3. 如果启用了协作，通知其他AI
    collaboration_enabled = True  # 假设用户启用了协作
    if collaboration_enabled:
        print("\n🤝 步骤3：协作通知")
        await ai_enable_collaboration(True)
        notify_result = await ai_send_message(
            "登录功能实现完成，请审查authenticate_user函数的安全性",
            "claude_code"
        )
        print(f"通知结果: {notify_result}")

    print("\n✅ 综合场景测试完成")
    return True


async def main():
    """运行所有测试"""
    print("🚀 AI规则遵守MCP工具测试开始...\n")
    print("="*60)

    tests = [
        ("基本规则功能", test_basic_rule_features),
        ("协作功能", test_collaboration_features),
        ("规则触发机制", test_rule_triggers),
        ("综合开发场景", test_comprehensive_scenario)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 测试：{test_name}")
        print("-" * 40)
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"✅ {test_name} 测试通过\n")
            else:
                print(f"❌ {test_name} 测试失败\n")
        except Exception as e:
            print(f"❌ {test_name} 测试错误: {e}\n")
            import traceback
            traceback.print_exc()

    print("="*60)
    print(f"📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！AI规则遵守MCP工具可以使用")
        print("\n🛠️ 可用功能:")
        print("  📋 ai_rule_reminder() - 智能规则提醒")
        print("  🔍 ai_check_compliance() - 代码合规检查")
        print("  📚 ai_get_rules() - 获取规则清单")
        print("  ⚙️ ai_add_custom_rule() - 添加自定义规则")
        print("  🤝 ai_enable_collaboration() - 启用协作功能")
        print("  💬 ai_send_message() - 发送协作消息")
        print("  📖 ai_read_messages() - 读取协作消息")
        print("  📊 ai_collaboration_status() - 查看协作状态")
    else:
        print(f"⚠️  {total - passed} 个测试失败，需要修复问题")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)