"""
MCP工具函数接口 - 38个AI规则遵守和协作工具
为所有支持MCP协议的AI工具提供智能规则提醒、模式管理、协作功能
"""
import asyncio
from typing import Dict, List, Any
from .rule_checker import AIRuleChecker
from .feature_requests import FeatureRequestManager
from .mode_manager import ModeManager


# 全局实例
_rule_checker = None
_fr_manager = None
_mode_manager = None


def get_rule_checker() -> AIRuleChecker:
    """获取规则检查器实例"""
    global _rule_checker
    if _rule_checker is None:
        _rule_checker = AIRuleChecker()
    return _rule_checker


def get_fr_manager() -> FeatureRequestManager:
    """获取功能请求管理器实例"""
    global _fr_manager
    if _fr_manager is None:
        _fr_manager = FeatureRequestManager()
    return _fr_manager


def get_mode_manager() -> ModeManager:
    """获取模式管理器实例"""
    global _mode_manager
    if _mode_manager is None:
        _mode_manager = ModeManager()
    return _mode_manager


# ====== 主要功能：规则遵守提醒 ======

async def ai_rule_reminder(context: str = "") -> str:
    """
    根据上下文自动提醒相关规则（主要功能）

    Args:
        context: 当前操作的上下文描述

    Returns:
        格式化的规则提醒信息
    """
    checker = get_rule_checker()
    triggered_rules = checker.check_triggers(context)
    return checker.format_reminder(triggered_rules)


async def ai_check_compliance(code_or_action: str) -> str:
    """
    检查代码或操作是否符合规则（主要功能）

    Args:
        code_or_action: 要检查的代码或操作描述

    Returns:
        合规性检查结果
    """
    checker = get_rule_checker()
    issues = checker.check_compliance(code_or_action)

    if not issues:
        return "✅ 代码检查通过，未发现规则违反"

    result = "🚨 发现以下规则违反：\n"
    for issue in issues:
        result += f"{issue}\n"

    return result.strip()


async def ai_get_rules(category: str = "all") -> str:
    """
    获取指定类别的规则清单（主要功能）

    Args:
        category: 规则类别 (all, coding, security, project, error_handling, collaboration)

    Returns:
        规则清单
    """
    checker = get_rule_checker()
    rules = checker.rules

    if category == "all":
        return _format_all_rules(rules)
    elif category == "coding":
        return _format_category_rules("编码规范", rules.get("coding_standards", []))
    elif category == "security":
        return _format_category_rules("安全规范", rules.get("security_rules", []))
    elif category == "project":
        return _format_category_rules("项目约定", rules.get("project_conventions", []))
    elif category == "error_handling":
        return _format_category_rules("错误处理", rules.get("error_handling", []))
    elif category == "collaboration":
        if checker.is_collaboration_enabled():
            collab_rules = rules.get("collaboration_rules", {}).get("rules", [])
            return _format_category_rules("协作规范", collab_rules)
        else:
            return "ℹ️ 协作功能未启用，使用 ai_enable_collaboration() 开启"
    else:
        return f"❌ 未知类别: {category}"


async def ai_add_custom_rule(name: str, triggers: str, rule_text: str) -> str:
    """
    添加用户自定义规则（主要功能）

    Args:
        name: 规则名称
        triggers: 触发词（用逗号分隔）
        rule_text: 规则内容

    Returns:
        添加结果
    """
    checker = get_rule_checker()
    trigger_list = [t.strip() for t in triggers.split(",") if t.strip()]

    if checker.add_custom_rule(name, trigger_list, rule_text):
        return f"✅ 已添加自定义规则：{name}"
    else:
        return f"❌ 添加自定义规则失败"


# ====== 可选功能：AI协作通信 ======

async def ai_enable_collaboration(enabled: bool = True) -> str:
    """
    启用/禁用AI协作功能（可选功能）

    Args:
        enabled: 是否启用协作功能

    Returns:
        设置结果
    """
    checker = get_rule_checker()

    if checker.enable_collaboration(enabled):
        status = "已启用" if enabled else "已禁用"
        return f"✅ AI协作功能{status}"
    else:
        return "❌ 设置协作功能失败"


async def ai_send_message(message: str, sender: str = "claude_code") -> str:
    """
    发送消息给协作伙伴（可选功能，需要先启用协作）

    Args:
        message: 要发送的消息
        sender: 发送者标识（claude_code 或 codex）

    Returns:
        发送结果
    """
    checker = get_rule_checker()

    if not checker.is_collaboration_enabled():
        return "ℹ️ 协作功能未启用，请先使用 ai_enable_collaboration(True) 开启"

    if checker.write_collaboration_message(sender, message):
        return f"📤 消息已发送: {message[:50]}{'...' if len(message) > 50 else ''}"
    else:
        return "❌ 发送消息失败"


async def ai_read_messages(from_ai: str = None) -> str:
    """
    读取协作消息（可选功能，需要先启用协作）

    Args:
        from_ai: 指定读取某个AI的消息，不指定则读取所有

    Returns:
        协作消息内容
    """
    checker = get_rule_checker()

    if not checker.is_collaboration_enabled():
        return "ℹ️ 协作功能未启用，请先使用 ai_enable_collaboration(True) 开启"

    return checker.read_collaboration_messages(from_ai)


async def ai_collaboration_status() -> str:
    """
    查看协作状态（可选功能）

    Returns:
        协作状态信息
    """
    checker = get_rule_checker()

    status = "已启用" if checker.is_collaboration_enabled() else "未启用"
    info = f"🤝 协作功能状态: {status}\n"

    if checker.is_collaboration_enabled():
        # 统计消息数量
        message_files = list(checker.collaboration_dir.glob("*_messages.md"))
        info += f"📊 活跃AI数量: {len(message_files)}\n"

        for file in message_files:
            ai_name = file.stem.replace("_messages", "")
            try:
                content = file.read_text(encoding='utf-8')
                msg_count = content.count("## [")
                info += f"   • {ai_name}: {msg_count} 条消息\n"
            except:
                info += f"   • {ai_name}: 读取失败\n"

    return info.strip()


# ====== 功能请求(FR)管理 ======

async def ai_submit_feature_request(title: str, description: str, submitter: str = "claude_code",
                                   priority: str = "medium", category: str = "rule_improvement") -> str:
    """
    提交功能请求

    Args:
        title: FR标题
        description: 详细描述
        submitter: 提交者 (claude_code, codex, user)
        priority: 优先级 (low, medium, high, critical)
        category: 类别 (rule_improvement, new_feature, collaboration, ui)

    Returns:
        FR ID和提交结果
    """
    fr_manager = get_fr_manager()
    fr_id = fr_manager.submit_request(title, description, submitter, priority, category)

    return f"✅ 功能请求已提交\n🆔 FR ID: {fr_id}\n📋 标题: {title}\n🔍 类别: {category}\n⚡ 优先级: {priority}"


async def ai_vote_feature_request(fr_id: str, vote: str, voter: str = "claude_code") -> str:
    """
    对功能请求投票

    Args:
        fr_id: 功能请求ID
        vote: 投票 (approve, reject, need_info)
        voter: 投票者

    Returns:
        投票结果
    """
    fr_manager = get_fr_manager()

    if fr_manager.vote_on_request(fr_id, voter, vote):
        fr = fr_manager.get_request_details(fr_id)
        if fr:
            votes_summary = ", ".join([f"{v}: {vote}" for v, vote in fr.votes.items()])
            return f"✅ 投票成功\n🆔 {fr_id}: {fr.title}\n🗳️ 当前投票: {votes_summary}\n📊 状态: {fr.status}"
        else:
            return f"❌ 找不到 FR {fr_id}"
    else:
        return f"❌ 投票失败，FR {fr_id} 不存在"


async def ai_list_feature_requests(status: str = None, category: str = None) -> str:
    """
    列出功能请求

    Args:
        status: 按状态过滤 (proposed, under_review, approved, implemented, rejected)
        category: 按类别过滤

    Returns:
        功能请求列表
    """
    fr_manager = get_fr_manager()
    requests = fr_manager.get_requests(status, category)

    if not requests:
        filter_info = f" (状态: {status or '全部'}, 类别: {category or '全部'})"
        return f"📭 暂无功能请求{filter_info}"

    result = f"📋 功能请求列表{f' - {status}' if status else ''}{f' - {category}' if category else ''}:\n\n"

    for fr in requests[:10]:  # 限制显示10个
        status_emoji = {
            "proposed": "🆕",
            "under_review": "👀",
            "approved": "✅",
            "implemented": "🎉",
            "rejected": "❌"
        }.get(fr.status, "❓")

        priority_emoji = {
            "low": "🔵",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }.get(fr.priority, "⚪")

        result += f"{status_emoji} {fr.id}: {fr.title}\n"
        result += f"   📝 {fr.description[:100]}{'...' if len(fr.description) > 100 else ''}\n"
        result += f"   👤 提交者: {fr.submitter} | {priority_emoji} {fr.priority} | 🏷️ {fr.category}\n"

        if fr.votes:
            votes = ", ".join([f"{voter}: {vote}" for voter, vote in fr.votes.items()])
            result += f"   🗳️ 投票: {votes}\n"

        result += "\n"

    return result.strip()


async def ai_get_feature_request(fr_id: str) -> str:
    """
    获取功能请求详情

    Args:
        fr_id: 功能请求ID

    Returns:
        详细信息
    """
    fr_manager = get_fr_manager()
    fr = fr_manager.get_request_details(fr_id)

    if not fr:
        return f"❌ 找不到功能请求 {fr_id}"

    status_emoji = {
        "proposed": "🆕",
        "under_review": "👀",
        "approved": "✅",
        "implemented": "🎉",
        "rejected": "❌"
    }.get(fr.status, "❓")

    result = f"{status_emoji} {fr.id}: {fr.title}\n\n"
    result += f"📝 描述:\n{fr.description}\n\n"
    result += f"👤 提交者: {fr.submitter}\n"
    result += f"⚡ 优先级: {fr.priority}\n"
    result += f"🏷️ 类别: {fr.category}\n"
    result += f"📊 状态: {fr.status}\n"
    result += f"📅 创建时间: {fr.created_at}\n"
    result += f"🔄 更新时间: {fr.updated_at}\n"

    if fr.votes:
        result += f"\n🗳️ 投票情况:\n"
        for voter, vote in fr.votes.items():
            vote_emoji = {"approve": "✅", "reject": "❌", "need_info": "❓"}.get(vote, "⚪")
            result += f"   {vote_emoji} {voter}: {vote}\n"

    if fr.implementation_notes:
        result += f"\n📋 实现备注:\n{fr.implementation_notes}\n"

    if fr.related_rules:
        result += f"\n🔗 相关规则: {', '.join(fr.related_rules)}\n"

    return result


async def ai_suggest_rule_improvements(code_issues: List[str] = None) -> str:
    """
    基于代码问题自动建议规则改进

    Args:
        code_issues: 发现的代码问题列表

    Returns:
        规则改进建议
    """
    if not code_issues:
        code_issues = ["缺少错误处理", "硬编码配置", "命名不规范"]

    fr_manager = get_fr_manager()
    suggestions = fr_manager.suggest_rules_from_code_issues(code_issues)

    if not suggestions:
        return "✅ 当前代码质量良好，暂无规则改进建议"

    result = "💡 基于代码问题的规则改进建议:\n\n"
    for i, suggestion in enumerate(suggestions, 1):
        result += f"{i}. {suggestion}\n"

    result += "\n💬 您可以使用 ai_submit_feature_request() 正式提交这些建议"
    return result


# ====== 模式管理 ======

async def ai_switch_mode(mode: str) -> str:
    """
    切换工作模式

    Args:
        mode: 模式名称 (normal, plan, pr, fr)

    Returns:
        切换结果
    """
    mode_manager = get_mode_manager()

    if mode_manager.switch_mode(mode):
        mode_names = {
            "normal": "普通模式",
            "plan": "计划模式",
            "pr": "代码审查模式",
            "fr": "功能请求模式"
        }
        return f"✅ 已切换到 {mode_names.get(mode, mode)} 模式"
    else:
        available = mode_manager.get_available_modes()
        modes_list = "\n".join([f"  • {m['mode']}: {m['name']} - {m['description']}" for m in available])
        return f"❌ 无效模式: {mode}\n\n可用模式:\n{modes_list}"


async def ai_get_current_mode() -> str:
    """
    获取当前工作模式

    Returns:
        当前模式信息
    """
    mode_manager = get_mode_manager()
    current_mode = mode_manager.get_current_mode()
    stats = mode_manager.get_mode_statistics()

    mode_names = {
        "normal": "普通模式",
        "plan": "计划模式",
        "pr": "代码审查模式",
        "fr": "功能请求模式"
    }

    result = f"🎯 当前模式: {mode_names.get(current_mode, current_mode)}\n\n"
    result += f"📊 统计信息:\n"
    result += f"  📋 计划: {stats['plans']['active']} 活跃 / {stats['plans']['total']} 总计\n"
    result += f"  🔍 PR: {stats['pull_requests']['pending_review']} 待审查 / {stats['pull_requests']['total']} 总计\n"

    return result


async def ai_list_modes() -> str:
    """
    列出所有可用模式

    Returns:
        模式列表
    """
    mode_manager = get_mode_manager()
    current_mode = mode_manager.get_current_mode()
    available_modes = mode_manager.get_available_modes()

    result = "🎛️ 可用工作模式:\n\n"

    for mode_info in available_modes:
        current_indicator = " 👈 当前" if mode_info["mode"] == current_mode else ""
        result += f"🔹 {mode_info['mode']}: {mode_info['name']}{current_indicator}\n"
        result += f"   📝 {mode_info['description']}\n\n"

    result += "💡 使用 ai_switch_mode('模式名') 切换模式"
    return result


# ====== 计划模式工具 ======

async def ai_create_plan(title: str, description: str, creator: str = "claude_code",
                        priority: str = "medium", estimated_hours: int = 0) -> str:
    """
    创建开发计划 (需要在plan模式下)

    Args:
        title: 计划标题
        description: 计划描述
        creator: 创建者
        priority: 优先级
        estimated_hours: 预估工时

    Returns:
        创建结果
    """
    mode_manager = get_mode_manager()

    if mode_manager.get_current_mode() != "plan":
        return "❌ 此功能需要在计划模式下使用，请先执行 ai_switch_mode('plan')"

    plan_id = mode_manager.create_plan(title, description, creator, priority, estimated_hours)
    return f"✅ 计划已创建\n🆔 计划ID: {plan_id}\n📋 标题: {title}\n⚡ 优先级: {priority}\n⏱️ 预估工时: {estimated_hours}小时"


async def ai_add_task(plan_id: str, task_title: str, task_description: str,
                     estimated_hours: int = 1, assignee: str = None) -> str:
    """
    向计划添加任务

    Args:
        plan_id: 计划ID
        task_title: 任务标题
        task_description: 任务描述
        estimated_hours: 预估工时
        assignee: 负责人

    Returns:
        添加结果
    """
    mode_manager = get_mode_manager()

    if mode_manager.add_task_to_plan(plan_id, task_title, task_description, estimated_hours, assignee):
        return f"✅ 任务已添加到计划 {plan_id}\n📋 任务: {task_title}\n👤 负责人: {assignee or '未指定'}\n⏱️ 预估: {estimated_hours}小时"
    else:
        return f"❌ 添加任务失败，计划 {plan_id} 不存在"


async def ai_update_task(plan_id: str, task_id: str, status: str, actual_hours: int = 0) -> str:
    """
    更新任务状态

    Args:
        plan_id: 计划ID
        task_id: 任务ID
        status: 新状态 (pending, in_progress, completed)
        actual_hours: 实际工时

    Returns:
        更新结果
    """
    mode_manager = get_mode_manager()

    if mode_manager.update_task_status(plan_id, task_id, status, actual_hours):
        status_names = {"pending": "待开始", "in_progress": "进行中", "completed": "已完成"}
        return f"✅ 任务状态已更新\n📊 状态: {status_names.get(status, status)}\n⏱️ 实际工时: {actual_hours}小时"
    else:
        return f"❌ 更新失败，计划 {plan_id} 或任务 {task_id} 不存在"


async def ai_list_plans(status: str = None) -> str:
    """
    列出计划

    Args:
        status: 按状态过滤 (draft, active, completed, cancelled)

    Returns:
        计划列表
    """
    mode_manager = get_mode_manager()
    plans = mode_manager.get_plans(status)

    if not plans:
        filter_info = f" (状态: {status})" if status else ""
        return f"📭 暂无计划{filter_info}"

    result = f"📋 开发计划{f' - {status}' if status else ''}:\n\n"

    for plan in plans[:10]:  # 限制显示10个
        status_emoji = {
            "draft": "📝",
            "active": "🔥",
            "completed": "✅",
            "cancelled": "❌"
        }.get(plan.status, "❓")

        priority_emoji = {
            "low": "🔵",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }.get(plan.priority, "⚪")

        completed_tasks = len([t for t in plan.tasks if t["status"] == "completed"])
        total_tasks = len(plan.tasks)

        result += f"{status_emoji} {plan.id}: {plan.title}\n"
        result += f"   📝 {plan.description[:100]}{'...' if len(plan.description) > 100 else ''}\n"
        result += f"   👤 创建者: {plan.creator} | {priority_emoji} {plan.priority}\n"
        result += f"   📊 进度: {completed_tasks}/{total_tasks} 任务完成\n"
        result += f"   ⏱️ 工时: {plan.actual_hours}/{plan.estimated_hours}h\n\n"

    return result.strip()


# ====== PR模式工具 ======

async def ai_create_pr(title: str, description: str, author: str, reviewer: str,
                      files_changed: List[str], priority: str = "medium") -> str:
    """
    创建代码审查PR (需要在pr模式下)

    Args:
        title: PR标题
        description: PR描述
        author: 作者
        reviewer: 审查者
        files_changed: 变更文件列表
        priority: 优先级

    Returns:
        创建结果
    """
    mode_manager = get_mode_manager()

    if mode_manager.get_current_mode() != "pr":
        return "❌ 此功能需要在PR模式下使用，请先执行 ai_switch_mode('pr')"

    pr_id = mode_manager.create_pull_request(title, description, author, reviewer, files_changed, priority)
    files_summary = ", ".join(files_changed[:3]) + ("..." if len(files_changed) > 3 else "")

    return f"✅ PR已创建\n🆔 PR ID: {pr_id}\n📋 标题: {title}\n👤 作者: {author} → 审查者: {reviewer}\n📁 文件: {files_summary}\n⚡ 优先级: {priority}"


async def ai_review_pr(pr_id: str, comment: str, reviewer: str,
                      file_path: str = None, line_number: int = None) -> str:
    """
    添加PR审查评论

    Args:
        pr_id: PR ID
        comment: 评论内容
        reviewer: 审查者
        file_path: 文件路径 (可选)
        line_number: 行号 (可选)

    Returns:
        评论结果
    """
    mode_manager = get_mode_manager()

    if mode_manager.add_review_comment(pr_id, reviewer, comment, file_path, line_number):
        location = f" ({file_path}:{line_number})" if file_path and line_number else ""
        return f"✅ 审查评论已添加\n🆔 PR: {pr_id}\n👤 审查者: {reviewer}\n💬 评论: {comment[:100]}{'...' if len(comment) > 100 else ''}{location}"
    else:
        return f"❌ 添加评论失败，PR {pr_id} 不存在"


async def ai_approve_pr(pr_id: str, reviewer: str) -> str:
    """
    批准PR

    Args:
        pr_id: PR ID
        reviewer: 审查者

    Returns:
        批准结果
    """
    mode_manager = get_mode_manager()

    if mode_manager.update_pr_status(pr_id, "approved", reviewer):
        return f"✅ PR已批准\n🆔 PR: {pr_id}\n👤 审查者: {reviewer}\n📊 状态: 已批准，可以合并"
    else:
        return f"❌ 批准失败，PR {pr_id} 不存在"


async def ai_list_prs(status: str = None, reviewer: str = None) -> str:
    """
    列出PR

    Args:
        status: 按状态过滤
        reviewer: 按审查者过滤

    Returns:
        PR列表
    """
    mode_manager = get_mode_manager()
    prs = mode_manager.get_pull_requests(status, reviewer)

    if not prs:
        filters = []
        if status: filters.append(f"状态: {status}")
        if reviewer: filters.append(f"审查者: {reviewer}")
        filter_info = f" ({', '.join(filters)})" if filters else ""
        return f"📭 暂无PR{filter_info}"

    result = f"🔍 代码审查PR{f' - {status}' if status else ''}:\n\n"

    for pr in prs[:10]:  # 限制显示10个
        status_emoji = {
            "draft": "📝",
            "review_requested": "👀",
            "approved": "✅",
            "rejected": "❌",
            "merged": "🎉"
        }.get(pr.status, "❓")

        result += f"{status_emoji} {pr.id}: {pr.title}\n"
        result += f"   📝 {pr.description[:100]}{'...' if len(pr.description) > 100 else ''}\n"
        result += f"   👤 {pr.author} → {pr.reviewer} | ⚡ {pr.priority}\n"
        result += f"   📁 {len(pr.files_changed)} 个文件变更\n"
        result += f"   💬 {len(pr.review_comments)} 条评论\n\n"

    return result.strip()


# ====== 工具函数 ======

def _format_all_rules(rules: Dict[str, Any]) -> str:
    """格式化所有规则"""
    result = "📋 完整规则清单：\n\n"

    # 编码规范
    if "coding_standards" in rules:
        result += "🔧 编码规范：\n"
        for group in rules["coding_standards"]:
            result += f"   📝 {group['name']}：\n"
            for rule in group["rules"]:
                result += f"      • {rule}\n"
        result += "\n"

    # 安全规范
    if "security_rules" in rules:
        result += "🔒 安全规范：\n"
        for group in rules["security_rules"]:
            result += f"   🛡️ {group['name']}：\n"
            for rule in group["rules"]:
                result += f"      • {rule}\n"
        result += "\n"

    # 项目约定
    if "project_conventions" in rules:
        result += "📁 项目约定：\n"
        for group in rules["project_conventions"]:
            result += f"   🏗️ {group['name']}：\n"
            for rule in group["rules"]:
                result += f"      • {rule}\n"
        result += "\n"

    # 错误处理
    if "error_handling" in rules:
        result += "⚠️ 错误处理：\n"
        for group in rules["error_handling"]:
            result += f"   🚨 {group['name']}：\n"
            for rule in group["rules"]:
                result += f"      • {rule}\n"
        result += "\n"

    # 协作规范（如果启用）
    collab_rules = rules.get("collaboration_rules", {})
    if collab_rules.get("enabled", False):
        result += "🤝 协作规范：\n"
        for group in collab_rules.get("rules", []):
            result += f"   🔄 {group['name']}：\n"
            for rule in group["rules"]:
                result += f"      • {rule}\n"
        result += "\n"

    # 自定义规则
    custom_rules = rules.get("user_custom_rules", [])
    if custom_rules:
        result += "⚙️ 自定义规则：\n"
        for rule in custom_rules:
            result += f"   📌 {rule.get('name', '未命名')}：{rule.get('rule', '')}\n"

    return result.strip()


def _format_category_rules(category_name: str, rule_groups: List[Dict]) -> str:
    """格式化特定类别的规则"""
    if not rule_groups:
        return f"📭 {category_name}类别暂无规则"

    result = f"📋 {category_name}：\n\n"

    for group in rule_groups:
        result += f"🎯 {group.get('name', '未命名规则组')}：\n"
        for rule in group.get("rules", []):
            result += f"   • {rule}\n"
        result += "\n"

    return result.strip()


# ====== 模式管理功能 ======

async def ai_switch_mode(mode: str) -> str:
    """切换工作模式"""
    manager = get_mode_manager()
    success = manager.switch_mode(mode)

    if success:
        return f"✅ 已切换到 {mode} 模式"
    else:
        available_modes = ", ".join([m["mode"] for m in manager.get_available_modes()])
        return f"❌ 模式切换失败。可用模式：{available_modes}"


async def ai_get_current_mode() -> str:
    """获取当前工作模式"""
    manager = get_mode_manager()
    current = manager.get_current_mode()

    mode_descriptions = {
        "normal": "普通模式 - 基础规则提醒功能",
        "plan": "计划模式 - 制定和管理开发计划",
        "pr": "代码审查模式 - PR创建和审查流程",
        "fr": "功能请求模式 - 功能改进建议和投票"
    }

    desc = mode_descriptions.get(current, "未知模式")
    return f"📍 当前模式：{current} ({desc})"


async def ai_list_modes() -> str:
    """列出所有可用的工作模式"""
    manager = get_mode_manager()
    modes = manager.get_available_modes()

    result = "🔄 可用工作模式：\n\n"
    for mode in modes:
        result += f"🎯 {mode['mode']} - {mode['name']}\n"
        result += f"   📝 {mode['description']}\n\n"

    result += "💡 使用 ai_switch_mode(\"模式名\") 切换模式"
    return result


async def ai_get_mode_statistics() -> str:
    """获取各模式统计信息"""
    manager = get_mode_manager()
    stats = manager.get_mode_statistics()

    result = f"📊 系统统计信息：\n\n"
    result += f"📍 当前模式：{stats['current_mode']}\n\n"

    result += f"📋 计划统计：\n"
    result += f"   • 总计划数：{stats['plans']['total']}\n"
    result += f"   • 活跃计划：{stats['plans']['active']}\n"
    result += f"   • 已完成：{stats['plans']['completed']}\n\n"

    result += f"🔍 PR统计：\n"
    result += f"   • 总PR数：{stats['pull_requests']['total']}\n"
    result += f"   • 待审查：{stats['pull_requests']['pending_review']}\n"
    result += f"   • 已批准：{stats['pull_requests']['approved']}\n"

    return result


# ====== Plan模式功能 ======

async def ai_create_plan(title: str, description: str, creator: str,
                        priority: str = "medium", estimated_hours: int = 0) -> str:
    """创建开发计划"""
    manager = get_mode_manager()
    plan_id = manager.create_plan(title, description, creator, priority, estimated_hours)

    return f"✅ 开发计划创建成功！\n📋 计划ID: {plan_id}\n🎯 标题: {title}\n⏱️ 预估工时: {estimated_hours}小时"


async def ai_add_task_to_plan(plan_id: str, task_title: str, task_description: str,
                             estimated_hours: int = 1, assignee: str = None) -> str:
    """向计划添加任务"""
    manager = get_mode_manager()
    success = manager.add_task_to_plan(plan_id, task_title, task_description, estimated_hours, assignee)

    if success:
        assignee_info = f" (分配给: {assignee})" if assignee else ""
        return f"✅ 任务已添加到计划 {plan_id}\n🎯 任务: {task_title}{assignee_info}\n⏱️ 预估: {estimated_hours}小时"
    else:
        return f"❌ 添加任务失败，计划 {plan_id} 不存在"


async def ai_update_task_status(plan_id: str, task_id: str, status: str, actual_hours: int = 0) -> str:
    """更新任务状态"""
    manager = get_mode_manager()
    success = manager.update_task_status(plan_id, task_id, status, actual_hours)

    if success:
        hours_info = f" (实际耗时: {actual_hours}小时)" if actual_hours > 0 else ""
        return f"✅ 任务状态已更新\n📋 计划: {plan_id}\n🎯 任务: {task_id}\n📊 状态: {status}{hours_info}"
    else:
        return f"❌ 更新失败，计划或任务不存在"


async def ai_list_plans(status: str = None) -> str:
    """列出开发计划"""
    manager = get_mode_manager()
    plans = manager.get_plans(status)

    if not plans:
        status_filter = f" (状态: {status})" if status else ""
        return f"📭 暂无开发计划{status_filter}"

    result = f"📋 开发计划列表{' (状态: ' + status + ')' if status else ''}：\n\n"

    for plan in plans:
        result += f"🎯 {plan.title} (ID: {plan.id})\n"
        result += f"   📊 状态: {plan.status} | 优先级: {plan.priority}\n"
        result += f"   👤 创建者: {plan.creator}\n"
        result += f"   📋 任务数: {len(plan.tasks)} | 预估: {plan.estimated_hours}h\n"
        result += f"   📅 创建时间: {plan.created_at[:10]}\n\n"

    return result.strip()


async def ai_get_plan_details(plan_id: str) -> str:
    """获取计划详情"""
    manager = get_mode_manager()
    plan = manager._find_plan(plan_id)

    if not plan:
        return f"❌ 计划 {plan_id} 不存在"

    result = f"📋 计划详情：{plan.title}\n\n"
    result += f"🆔 ID: {plan.id}\n"
    result += f"📝 描述: {plan.description}\n"
    result += f"📊 状态: {plan.status}\n"
    result += f"⚡ 优先级: {plan.priority}\n"
    result += f"👤 创建者: {plan.creator}\n"
    result += f"⏱️ 预估工时: {plan.estimated_hours}小时\n"
    result += f"⏰ 实际工时: {plan.actual_hours}小时\n"
    result += f"🏷️ 标签: {', '.join(plan.tags) if plan.tags else '无'}\n"
    result += f"📅 创建时间: {plan.created_at}\n"
    result += f"🔄 更新时间: {plan.updated_at}\n\n"

    if plan.tasks:
        result += f"📋 任务列表 ({len(plan.tasks)}个)：\n"
        for i, task in enumerate(plan.tasks, 1):
            status_emoji = {"pending": "⏳", "in_progress": "🚧", "completed": "✅"}.get(task["status"], "❓")
            result += f"{i}. {status_emoji} {task['title']}\n"
            result += f"   📝 {task['description']}\n"
            result += f"   ⏱️ 预估: {task['estimated_hours']}h | 实际: {task['actual_hours']}h\n"
            if task.get("assignee"):
                result += f"   👤 负责人: {task['assignee']}\n"
            result += "\n"
    else:
        result += "📭 暂无任务\n"

    return result


# ====== PR模式功能 ======

async def ai_create_pr(title: str, description: str, author: str, reviewer: str,
                      files_changed: List[str], priority: str = "medium") -> str:
    """创建代码审查PR"""
    manager = get_mode_manager()
    pr_id = manager.create_pull_request(title, description, author, reviewer, files_changed, priority)

    files_info = f"\n📁 修改文件: {', '.join(files_changed)}"
    return f"✅ PR创建成功！\n🔍 PR ID: {pr_id}\n🎯 标题: {title}\n👤 作者: {author} → 审查者: {reviewer}{files_info}"


async def ai_add_review_comment(pr_id: str, commenter: str, comment: str,
                               file_path: str = None, line_number: int = None) -> str:
    """添加PR审查评论"""
    manager = get_mode_manager()
    success = manager.add_review_comment(pr_id, commenter, comment, file_path, line_number)

    if success:
        location_info = ""
        if file_path:
            location_info = f"\n📁 文件: {file_path}"
            if line_number:
                location_info += f" (第{line_number}行)"
        return f"✅ 审查评论已添加\n🔍 PR: {pr_id}\n👤 评论者: {commenter}{location_info}\n💬 评论: {comment}"
    else:
        return f"❌ 添加评论失败，PR {pr_id} 不存在"


async def ai_update_pr_status(pr_id: str, status: str, reviewer: str) -> str:
    """更新PR状态"""
    manager = get_mode_manager()
    success = manager.update_pr_status(pr_id, status, reviewer)

    if success:
        status_emoji = {
            "draft": "📝", "review_requested": "🔍", "approved": "✅",
            "rejected": "❌", "merged": "🔀"
        }.get(status, "📊")
        return f"✅ PR状态已更新\n🔍 PR: {pr_id}\n{status_emoji} 新状态: {status}\n👤 操作者: {reviewer}"
    else:
        return f"❌ 更新失败，PR {pr_id} 不存在"


async def ai_list_prs(status: str = None, reviewer: str = None) -> str:
    """列出代码审查PR"""
    manager = get_mode_manager()
    prs = manager.get_pull_requests(status, reviewer)

    if not prs:
        filter_info = []
        if status:
            filter_info.append(f"状态: {status}")
        if reviewer:
            filter_info.append(f"审查者: {reviewer}")
        filter_text = f" ({', '.join(filter_info)})" if filter_info else ""
        return f"📭 暂无PR{filter_text}"

    result = f"🔍 PR列表"
    if status or reviewer:
        filter_info = []
        if status:
            filter_info.append(f"状态: {status}")
        if reviewer:
            filter_info.append(f"审查者: {reviewer}")
        result += f" ({', '.join(filter_info)})"
    result += "：\n\n"

    for pr in prs:
        status_emoji = {
            "draft": "📝", "review_requested": "🔍", "approved": "✅",
            "rejected": "❌", "merged": "🔀"
        }.get(pr.status, "📊")

        result += f"{status_emoji} {pr.title} (ID: {pr.id})\n"
        result += f"   👤 {pr.author} → {pr.reviewer}\n"
        result += f"   📊 状态: {pr.status} | 优先级: {pr.priority}\n"
        result += f"   📁 文件数: {len(pr.files_changed)} | 评论数: {len(pr.review_comments)}\n"
        result += f"   📅 创建时间: {pr.created_at[:10]}\n\n"

    return result.strip()


async def ai_get_pr_details(pr_id: str) -> str:
    """获取PR详情"""
    manager = get_mode_manager()
    pr = manager._find_pr(pr_id)

    if not pr:
        return f"❌ PR {pr_id} 不存在"

    status_emoji = {
        "draft": "📝", "review_requested": "🔍", "approved": "✅",
        "rejected": "❌", "merged": "🔀"
    }.get(pr.status, "📊")

    result = f"🔍 PR详情：{pr.title}\n\n"
    result += f"🆔 ID: {pr.id}\n"
    result += f"📝 描述: {pr.description}\n"
    result += f"{status_emoji} 状态: {pr.status}\n"
    result += f"⚡ 优先级: {pr.priority}\n"
    result += f"👤 作者: {pr.author}\n"
    result += f"👨‍💻 审查者: {pr.reviewer}\n"
    result += f"🚫 合并冲突: {'是' if pr.merge_conflicts else '否'}\n"
    result += f"📅 创建时间: {pr.created_at}\n"
    result += f"🔄 更新时间: {pr.updated_at}\n\n"

    result += f"📁 修改的文件 ({len(pr.files_changed)}个)：\n"
    for file in pr.files_changed:
        result += f"   • {file}\n"
    result += "\n"

    if pr.review_comments:
        result += f"💬 审查评论 ({len(pr.review_comments)}条)：\n"
        for comment in pr.review_comments:
            result += f"👤 {comment['commenter']} ({comment['created_at'][:10]}):\n"
            result += f"   💬 {comment['comment']}\n"
            if comment.get('file_path'):
                location = comment['file_path']
                if comment.get('line_number'):
                    location += f":L{comment['line_number']}"
                result += f"   📁 位置: {location}\n"
            result += "\n"
    else:
        result += "💬 暂无审查评论\n"

    return result