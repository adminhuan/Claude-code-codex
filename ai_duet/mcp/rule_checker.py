"""
AI规则遵守检查器
主功能：提醒AI遵守各种规则
可选功能：AI之间的协作通信
"""
import yaml
import re
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class AIRuleChecker:
    """AI规则检查和提醒系统"""

    def __init__(self, rules_dir: str = ".ai_rules"):
        self.rules_dir = Path(rules_dir)
        self.config_file = self.rules_dir / "config.yaml"
        self.collaboration_dir = self.rules_dir / "collaboration"

        # 确保目录存在
        self.rules_dir.mkdir(exist_ok=True)
        self.collaboration_dir.mkdir(exist_ok=True)

        # 加载规则配置
        self.rules = self.load_rules()

    def load_rules(self) -> Dict[str, Any]:
        """加载规则配置"""
        if not self.config_file.exists():
            return self.create_default_rules()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载规则配置失败: {e}")
            return self.create_default_rules()

    def create_default_rules(self) -> Dict[str, Any]:
        """创建默认规则配置"""
        default_rules = {
            "settings": {
                "collaboration_enabled": False,
                "auto_reminder": True,
                "reminder_frequency": "smart",  # smart/always/minimal
                "project_root": "."
            },

            "coding_standards": [
                {
                    "name": "代码格式规范",
                    "triggers": ["写代码", "创建文件", "修改代码", "实现", "编写", "def ", "class "],
                    "rules": [
                        "使用4空格缩进，不要使用Tab",
                        "函数名使用snake_case格式",
                        "类名使用PascalCase格式",
                        "常量使用UPPER_CASE格式",
                        "每行代码不超过100字符"
                    ]
                }
            ],

            "security_rules": [
                {
                    "name": "安全检查",
                    "triggers": ["用户输入", "数据库", "SQL", "API", "密码", "认证", "登录"],
                    "rules": [
                        "验证所有用户输入，防止注入攻击",
                        "使用参数化查询，不要拼接SQL语句",
                        "密码必须加密存储，不要明文保存",
                        "API密钥放在环境变量中，不要硬编码",
                        "敏感信息不要记录在日志中"
                    ]
                }
            ],

            "project_conventions": [
                {
                    "name": "项目结构约定",
                    "triggers": ["创建文件", "新建", "目录", "文件夹", "组织"],
                    "rules": [
                        "API接口文件放在 /api/ 目录下",
                        "工具函数放在 /utils/ 目录下",
                        "测试文件放在 /tests/ 目录下",
                        "配置文件放在 /config/ 目录下",
                        "文档文件放在 /docs/ 目录下"
                    ]
                }
            ],

            "error_handling": [
                {
                    "name": "错误处理规范",
                    "triggers": ["函数", "方法", "API调用", "文件操作", "网络请求"],
                    "rules": [
                        "每个可能失败的操作都要有try-catch处理",
                        "错误信息要详细记录，便于调试",
                        "给用户友好的错误提示",
                        "不要忽略或吞噬异常",
                        "关键操作失败时要有回滚机制"
                    ]
                }
            ],

            "collaboration_rules": {
                "enabled": False,
                "rules": [
                    {
                        "name": "协作流程",
                        "triggers": ["开始任务", "完成功能", "需要审查"],
                        "rules": [
                            "开始重要任务前检查其他AI的工作状态",
                            "完成功能后及时通知协作伙伴",
                            "重要决定和设计要与其他AI讨论",
                            "代码完成后请求同行审查"
                        ]
                    }
                ]
            },

            "user_custom_rules": []
        }

        # 保存默认配置
        self.save_rules(default_rules)
        return default_rules

    def save_rules(self, rules: Dict[str, Any]):
        """保存规则配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(rules, f, allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存规则配置失败: {e}")

    def check_triggers(self, context: str) -> List[Dict]:
        """检查上下文触发了哪些规则"""
        triggered_rules = []
        context_lower = context.lower()

        # 检查编码规范
        for rule_group in self.rules.get("coding_standards", []):
            if self._matches_triggers(context_lower, rule_group.get("triggers", [])):
                triggered_rules.append({
                    "category": "编码规范",
                    "name": rule_group["name"],
                    "rules": rule_group["rules"]
                })

        # 检查安全规则
        for rule_group in self.rules.get("security_rules", []):
            if self._matches_triggers(context_lower, rule_group.get("triggers", [])):
                triggered_rules.append({
                    "category": "安全规范",
                    "name": rule_group["name"],
                    "rules": rule_group["rules"]
                })

        # 检查项目约定
        for rule_group in self.rules.get("project_conventions", []):
            if self._matches_triggers(context_lower, rule_group.get("triggers", [])):
                triggered_rules.append({
                    "category": "项目约定",
                    "name": rule_group["name"],
                    "rules": rule_group["rules"]
                })

        # 检查错误处理
        for rule_group in self.rules.get("error_handling", []):
            if self._matches_triggers(context_lower, rule_group.get("triggers", [])):
                triggered_rules.append({
                    "category": "错误处理",
                    "name": rule_group["name"],
                    "rules": rule_group["rules"]
                })

        # 检查协作规则（如果启用）
        collab_rules = self.rules.get("collaboration_rules", {})
        if collab_rules.get("enabled", False):
            for rule_group in collab_rules.get("rules", []):
                if self._matches_triggers(context_lower, rule_group.get("triggers", [])):
                    triggered_rules.append({
                        "category": "协作规范",
                        "name": rule_group["name"],
                        "rules": rule_group["rules"]
                    })

        # 检查用户自定义规则
        for rule in self.rules.get("user_custom_rules", []):
            if self._matches_triggers(context_lower, rule.get("triggers", [])):
                triggered_rules.append({
                    "category": "自定义规则",
                    "name": rule.get("name", "用户规则"),
                    "rules": [rule.get("rule", "")]
                })

        return triggered_rules

    def _matches_triggers(self, context: str, triggers: List[str]) -> bool:
        """检查上下文是否匹配触发词"""
        for trigger in triggers:
            if trigger.lower() in context:
                return True
        return False

    def check_compliance(self, code_or_action: str) -> List[str]:
        """检查代码或操作的合规性"""
        issues = []

        # 检查常见的代码问题
        if "password" in code_or_action.lower() and "plain" in code_or_action.lower():
            issues.append("❌ 安全问题：密码不应该明文存储")

        # 检查SQL注入风险
        if re.search(r'sql.*\+.*[\'"]', code_or_action, re.IGNORECASE):
            issues.append("❌ 安全问题：检测到SQL拼接，建议使用参数化查询")

        # 检查函数命名
        if re.search(r'def\s+[A-Z][a-zA-Z]*\s*\(', code_or_action):
            issues.append("❌ 命名规范：函数名应使用snake_case格式")

        # 检查类命名
        if re.search(r'class\s+[a-z][a-zA-Z]*\s*[:(\[]', code_or_action):
            issues.append("❌ 命名规范：类名应使用PascalCase格式")

        # 检查缩进
        if re.search(r'^\t', code_or_action, re.MULTILINE):
            issues.append("❌ 格式规范：应使用4空格缩进，不要使用Tab")

        # 检查长行
        lines = code_or_action.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"❌ 格式规范：第{i}行超过100字符限制")

        # 检查错误处理
        if re.search(r'open\s*\(|requests\.|urllib\.', code_or_action) and 'try:' not in code_or_action:
            issues.append("❌ 错误处理：文件操作和网络请求应该使用try-catch处理")

        return issues

    def format_reminder(self, triggered_rules: List[Dict]) -> str:
        """格式化规则提醒消息"""
        if not triggered_rules:
            return "✅ 当前操作无特殊规则要求"

        reminder = "⚠️ 规则提醒：\n\n"

        # 按类别分组
        categories = {}
        for rule_group in triggered_rules:
            category = rule_group["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(rule_group)

        # 格式化输出
        for category, groups in categories.items():
            reminder += f"📋 {category}：\n"
            for group in groups:
                if group["name"] != category:
                    reminder += f"   🎯 {group['name']}：\n"
                for rule in group["rules"]:
                    reminder += f"   • {rule}\n"
            reminder += "\n"

        return reminder.strip()

    def add_custom_rule(self, name: str, triggers: List[str], rule_text: str) -> bool:
        """添加用户自定义规则"""
        try:
            new_rule = {
                "name": name,
                "triggers": triggers,
                "rule": rule_text,
                "added_at": datetime.now().isoformat()
            }

            if "user_custom_rules" not in self.rules:
                self.rules["user_custom_rules"] = []

            self.rules["user_custom_rules"].append(new_rule)
            self.save_rules(self.rules)
            return True
        except Exception as e:
            print(f"添加自定义规则失败: {e}")
            return False

    def enable_collaboration(self, enabled: bool = True) -> bool:
        """启用或禁用协作功能"""
        try:
            if "collaboration_rules" not in self.rules:
                self.rules["collaboration_rules"] = {"enabled": False, "rules": []}

            self.rules["collaboration_rules"]["enabled"] = enabled
            self.save_rules(self.rules)
            return True
        except Exception as e:
            print(f"设置协作功能失败: {e}")
            return False

    def is_collaboration_enabled(self) -> bool:
        """检查协作功能是否启用"""
        return self.rules.get("collaboration_rules", {}).get("enabled", False)

    # 协作相关方法（可选功能）
    def write_collaboration_message(self, sender: str, message: str) -> bool:
        """写入协作消息（当协作功能启用时）"""
        if not self.is_collaboration_enabled():
            return False

        try:
            message_file = self.collaboration_dir / f"{sender}_messages.md"
            timestamp = datetime.now().strftime("%H:%M:%S")

            with open(message_file, 'a', encoding='utf-8') as f:
                f.write(f"\n## [{timestamp}] {message}\n")

            return True
        except Exception as e:
            print(f"写入协作消息失败: {e}")
            return False

    def read_collaboration_messages(self, from_ai: str = None) -> str:
        """读取协作消息（当协作功能启用时）"""
        if not self.is_collaboration_enabled():
            return "ℹ️ 协作功能未启用"

        try:
            messages = []

            if from_ai:
                # 读取特定AI的消息
                message_file = self.collaboration_dir / f"{from_ai}_messages.md"
                if message_file.exists():
                    content = message_file.read_text(encoding='utf-8')
                    messages.append(f"📝 来自 {from_ai} 的消息：\n{content}")
            else:
                # 读取所有协作消息
                for message_file in self.collaboration_dir.glob("*_messages.md"):
                    ai_name = message_file.stem.replace("_messages", "")
                    content = message_file.read_text(encoding='utf-8')
                    if content.strip():
                        messages.append(f"📝 来自 {ai_name} 的消息：\n{content}")

            return "\n\n".join(messages) if messages else "📭 暂无协作消息"

        except Exception as e:
            print(f"读取协作消息失败: {e}")
            return f"❌ 读取失败: {e}"