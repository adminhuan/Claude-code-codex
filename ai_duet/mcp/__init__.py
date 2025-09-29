"""
AI规则遵守MCP工具模块
"""
from .tools import (
    # 主要功能：规则遵守提醒
    ai_rule_reminder,
    ai_check_compliance,
    ai_get_rules,
    ai_add_custom_rule,

    # 可选功能：AI协作通信
    ai_enable_collaboration,
    ai_send_message,
    ai_read_messages,
    ai_collaboration_status,

    # 功能请求(FR)管理
    ai_submit_feature_request,
    ai_vote_feature_request,
    ai_list_feature_requests,
    ai_get_feature_request,
    ai_suggest_rule_improvements,

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

    # 内部组件
    get_rule_checker,
    get_fr_manager,
    get_mode_manager
)

__all__ = [
    # 主要功能
    "ai_rule_reminder",
    "ai_check_compliance",
    "ai_get_rules",
    "ai_add_custom_rule",

    # 可选功能
    "ai_enable_collaboration",
    "ai_send_message",
    "ai_read_messages",
    "ai_collaboration_status",

    # 功能请求管理
    "ai_submit_feature_request",
    "ai_vote_feature_request",
    "ai_list_feature_requests",
    "ai_get_feature_request",
    "ai_suggest_rule_improvements",

    # 模式管理
    "ai_switch_mode",
    "ai_get_current_mode",
    "ai_list_modes",
    "ai_get_mode_statistics",

    # Plan模式功能
    "ai_create_plan",
    "ai_add_task_to_plan",
    "ai_update_task_status",
    "ai_list_plans",
    "ai_get_plan_details",

    # PR模式功能
    "ai_create_pr",
    "ai_add_review_comment",
    "ai_update_pr_status",
    "ai_list_prs",
    "ai_get_pr_details",

    # 内部组件
    "get_rule_checker",
    "get_fr_manager",
    "get_mode_manager"
]