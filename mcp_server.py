#!/usr/bin/env python3
"""
AI规则遵守MCP服务器
为Claude Code提供规则提醒和协作功能的MCP工具
"""
import asyncio
import json
from typing import Dict, Any, List

# 注意：实际MCP包可能有不同的导入路径
# 这里提供模拟的MCP接口结构
try:
    from mcp import types
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except ImportError:
    # 如果没有安装MCP包，提供模拟接口
    print("警告：未找到MCP包，使用模拟接口")

    class types:
        class Tool:
            def __init__(self, name, description, inputSchema):
                self.name = name
                self.description = description
                self.inputSchema = inputSchema

        class TextContent:
            def __init__(self, type, text):
                self.type = type
                self.text = text

    class Server:
        def __init__(self, name):
            self.name = name

        def list_tools(self):
            def decorator(func):
                return func
            return decorator

        def call_tool(self):
            def decorator(func):
                return func
            return decorator

        def create_initialization_options(self):
            return {}

        async def run(self, read_stream, write_stream, options):
            print(f"模拟MCP服务器 '{self.name}' 正在运行...")
            await asyncio.sleep(1)

    def stdio_server():
        class MockContext:
            async def __aenter__(self):
                return None, None
            async def __aexit__(self, *args):
                pass
        return MockContext()

# 导入我们的工具函数
from ai_duet.mcp.tools import (
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
)

# 创建MCP服务器实例
server = Server("ai-rule-mcp")


@server.list_tools()
async def list_tools() -> List[types.Tool]:
    """列出所有可用的MCP工具"""
    return [
        # 主要功能：规则遵守提醒
        types.Tool(
            name="ai_rule_reminder",
            description="智能规则提醒 - 根据代码上下文提供相关的编码规范提醒",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "当前代码上下文或开发任务描述"
                    },
                    "file_type": {
                        "type": "string",
                        "description": "文件类型（可选）",
                        "enum": ["python", "javascript", "typescript", "java", "cpp", "other"]
                    }
                },
                "required": ["context"]
            }
        ),
        types.Tool(
            name="ai_check_compliance",
            description="代码合规检查 - 检查代码是否符合项目规范",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要检查的代码"
                    },
                    "language": {
                        "type": "string",
                        "description": "编程语言",
                        "enum": ["python", "javascript", "typescript", "java", "cpp", "other"]
                    }
                },
                "required": ["code"]
            }
        ),
        types.Tool(
            name="ai_get_rules",
            description="获取规则清单 - 查看当前配置的所有编码规范",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "规则分类（可选）"
                    }
                }
            }
        ),
        types.Tool(
            name="ai_add_custom_rule",
            description="添加自定义规则 - 为项目添加特定的编码规范",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_name": {
                        "type": "string",
                        "description": "规则名称"
                    },
                    "description": {
                        "type": "string",
                        "description": "规则描述"
                    },
                    "category": {
                        "type": "string",
                        "description": "规则分类"
                    }
                },
                "required": ["rule_name", "description", "category"]
            }
        ),

        # 模式管理
        types.Tool(
            name="ai_switch_mode",
            description="切换工作模式 - 在Normal/Plan/PR/FR模式间切换",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "目标模式",
                        "enum": ["normal", "plan", "pr", "fr"]
                    }
                },
                "required": ["mode"]
            }
        ),
        types.Tool(
            name="ai_get_current_mode",
            description="获取当前工作模式",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="ai_list_modes",
            description="列出所有可用的工作模式",
            inputSchema={"type": "object", "properties": {}}
        ),

        # Plan模式功能
        types.Tool(
            name="ai_create_plan",
            description="创建开发计划 - Plan模式下创建项目计划",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "计划标题"},
                    "description": {"type": "string", "description": "计划描述"},
                    "creator": {"type": "string", "description": "创建者"},
                    "priority": {
                        "type": "string",
                        "description": "优先级",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "estimated_hours": {"type": "integer", "description": "预估工时"}
                },
                "required": ["title", "description", "creator"]
            }
        ),

        # PR模式功能
        types.Tool(
            name="ai_create_pr",
            description="创建代码审查PR - PR模式下创建代码审查请求",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "PR标题"},
                    "description": {"type": "string", "description": "PR描述"},
                    "author": {"type": "string", "description": "作者"},
                    "reviewer": {"type": "string", "description": "审查者"},
                    "files_changed": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "修改的文件列表"
                    }
                },
                "required": ["title", "description", "author", "reviewer", "files_changed"]
            }
        ),

        # FR功能
        types.Tool(
            name="ai_submit_feature_request",
            description="提交功能请求 - 提出功能改进建议",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "功能请求标题"},
                    "description": {"type": "string", "description": "功能请求描述"},
                    "submitter": {"type": "string", "description": "提交者"},
                    "priority": {
                        "type": "string",
                        "description": "优先级",
                        "enum": ["low", "medium", "high", "critical"]
                    },
                    "category": {
                        "type": "string",
                        "description": "分类",
                        "enum": ["rule_improvement", "new_feature", "collaboration", "ui"]
                    }
                },
                "required": ["title", "description", "submitter"]
            }
        ),

        # 协作功能（可选）
        types.Tool(
            name="ai_enable_collaboration",
            description="启用AI协作功能 - 开启AI间的协作通信",
            inputSchema={
                "type": "object",
                "properties": {
                    "enabled": {
                        "type": "boolean",
                        "description": "是否启用协作功能"
                    }
                },
                "required": ["enabled"]
            }
        ),
        types.Tool(
            name="ai_send_message",
            description="发送协作消息 - 向协作伙伴发送消息",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "消息内容"},
                    "sender": {"type": "string", "description": "发送者"}
                },
                "required": ["message", "sender"]
            }
        ),
        types.Tool(
            name="ai_collaboration_status",
            description="查看协作状态 - 检查协作功能状态",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """调用MCP工具"""
    try:
        # 映射工具名称到函数
        tool_functions = {
            # 主要功能
            "ai_rule_reminder": ai_rule_reminder,
            "ai_check_compliance": ai_check_compliance,
            "ai_get_rules": ai_get_rules,
            "ai_add_custom_rule": ai_add_custom_rule,

            # 模式管理
            "ai_switch_mode": ai_switch_mode,
            "ai_get_current_mode": ai_get_current_mode,
            "ai_list_modes": ai_list_modes,
            "ai_get_mode_statistics": ai_get_mode_statistics,

            # Plan模式
            "ai_create_plan": ai_create_plan,
            "ai_add_task_to_plan": ai_add_task_to_plan,
            "ai_update_task_status": ai_update_task_status,
            "ai_list_plans": ai_list_plans,
            "ai_get_plan_details": ai_get_plan_details,

            # PR模式
            "ai_create_pr": ai_create_pr,
            "ai_add_review_comment": ai_add_review_comment,
            "ai_update_pr_status": ai_update_pr_status,
            "ai_list_prs": ai_list_prs,
            "ai_get_pr_details": ai_get_pr_details,

            # FR功能
            "ai_submit_feature_request": ai_submit_feature_request,
            "ai_vote_feature_request": ai_vote_feature_request,
            "ai_list_feature_requests": ai_list_feature_requests,
            "ai_get_feature_request": ai_get_feature_request,
            "ai_suggest_rule_improvements": ai_suggest_rule_improvements,

            # 协作功能
            "ai_enable_collaboration": ai_enable_collaboration,
            "ai_send_message": ai_send_message,
            "ai_read_messages": ai_read_messages,
            "ai_collaboration_status": ai_collaboration_status,
        }

        if name not in tool_functions:
            return [types.TextContent(
                type="text",
                text=f"错误：未知的工具 '{name}'"
            )]

        # 调用对应的工具函数
        result = await tool_functions[name](**arguments)

        return [types.TextContent(
            type="text",
            text=str(result)
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"工具调用出错: {str(e)}"
        )]


async def main():
    """运行MCP服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())