#!/usr/bin/env python3
"""
AI规则遵守MCP工具使用示例
演示如何在实际开发中使用这些工具
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
    ai_read_messages
)


async def demo_for_claude_code():
    """演示Claude Code如何使用规则工具"""
    print("🤖 Claude Code 使用示例:\n")

    # 1. 开始任务前检查规则
    print("1️⃣ 开始开发前询问规则:")
    context = "我要实现一个用户注册API，包括邮箱验证和密码加密"
    reminder = await ai_rule_reminder(context)
    print(f"📝 任务: {context}")
    print(f"🔔 规则提醒:\n{reminder}\n")

    # 2. 写代码时检查合规性
    print("2️⃣ 代码实现阶段:")
    code = '''
def register_user(email: str, password: str):
    """用户注册函数"""
    # 输入验证
    if not validate_email(email):
        raise ValueError("无效邮箱格式")

    # 密码加密
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # 数据库操作
    try:
        query = "INSERT INTO users (email, password) VALUES (%s, %s)"
        db.execute(query, (email, hashed_password))
        return {"success": True, "message": "注册成功"}
    except Exception as e:
        logger.error(f"注册失败: {e}")
        raise DatabaseError("注册失败，请稍后重试")
    '''

    compliance = await ai_check_compliance(code)
    print(f"💻 实现的代码:\n{code}")
    print(f"✅ 合规检查: {compliance}\n")

    # 3. 添加项目特定规则
    print("3️⃣ 添加项目特定规则:")
    add_result = await ai_add_custom_rule(
        "邮箱验证",
        "注册,邮箱,email",
        "所有邮箱地址必须发送验证邮件确认"
    )
    print(f"📋 {add_result}\n")

    return "✅ Claude Code 示例完成"


async def demo_for_codex():
    """演示Codex如何使用规则工具"""
    print("🔧 Codex 使用示例:\n")

    # 1. 审查代码时检查规则
    print("1️⃣ 代码审查阶段:")
    review_context = "审查Claude Code提交的用户注册功能代码"
    reminder = await ai_rule_reminder(review_context)
    print(f"🔍 审查任务: {review_context}")
    print(f"📋 审查规则:\n{reminder}\n")

    # 2. 检查不安全的代码
    print("2️⃣ 发现问题代码:")
    bad_code = '''
def login_user(username, password):
    sql = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(sql)
    if user:
        return {"token": "abc123", "user_id": user[0]}
    '''

    compliance = await ai_check_compliance(bad_code)
    print(f"⚠️ 问题代码:\n{bad_code}")
    print(f"🚨 发现问题:\n{compliance}\n")

    # 3. 查看特定类别规则
    print("3️⃣ 查看安全规则清单:")
    security_rules = await ai_get_rules("security")
    print(f"🔒 安全规则:\n{security_rules}\n")

    return "✅ Codex 示例完成"


async def demo_collaboration():
    """演示AI协作功能"""
    print("🤝 AI协作功能演示:\n")

    # 1. 启用协作功能
    print("1️⃣ 启用协作功能:")
    enable_result = await ai_enable_collaboration(True)
    print(f"⚙️ {enable_result}\n")

    # 2. Claude Code 开始工作并通知
    print("2️⃣ Claude Code 开始工作:")
    claude_msg = await ai_send_message(
        "开始实现用户认证系统，预计包含注册、登录、密码重置功能",
        "claude_code"
    )
    print(f"📤 Claude: {claude_msg}")

    # 3. Codex 响应
    print("3️⃣ Codex 响应:")
    codex_msg = await ai_send_message(
        "收到！我会重点关注认证安全性，特别是密码存储和session管理",
        "codex"
    )
    print(f"📤 Codex: {codex_msg}")

    # 4. Claude Code 请求审查
    print("4️⃣ Claude Code 请求审查:")
    review_request = await ai_send_message(
        "认证模块已完成，请审查 auth.py 文件，特别关注JWT实现的安全性",
        "claude_code"
    )
    print(f"📤 Claude: {review_request}")

    # 5. 查看所有消息
    print("5️⃣ 查看协作记录:")
    all_messages = await ai_read_messages()
    print(f"💬 协作记录:\n{all_messages}\n")

    return "✅ 协作演示完成"


async def main():
    """运行所有示例"""
    print("🚀 AI规则遵守MCP工具使用演示\n")
    print("="*60)

    demos = [
        ("Claude Code 开发流程", demo_for_claude_code),
        ("Codex 审查流程", demo_for_codex),
        ("AI协作功能", demo_collaboration)
    ]

    for demo_name, demo_func in demos:
        print(f"\n📋 演示: {demo_name}")
        print("-" * 40)
        try:
            result = await demo_func()
            print(f"{result}\n")
        except Exception as e:
            print(f"❌ 演示出错: {e}\n")

    print("="*60)
    print("🎯 总结：AI规则遵守MCP工具主要功能")
    print("\n📋 主要功能（规则遵守）:")
    print("  🔔 ai_rule_reminder() - 根据上下文智能提醒相关规则")
    print("  🔍 ai_check_compliance() - 检查代码是否符合规范")
    print("  📚 ai_get_rules() - 获取指定类别的规则清单")
    print("  ⚙️ ai_add_custom_rule() - 添加项目特定的自定义规则")

    print("\n🤝 可选功能（AI协作）:")
    print("  🔧 ai_enable_collaboration() - 启用/禁用AI协作功能")
    print("  💬 ai_send_message() - 向协作伙伴发送消息")
    print("  📖 ai_read_messages() - 查看协作消息记录")

    print("\n🎉 工具已准备就绪，可以集成到MCP系统中！")


if __name__ == "__main__":
    asyncio.run(main())