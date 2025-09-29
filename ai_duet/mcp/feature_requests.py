"""
功能请求(FR)管理模块
用于AI之间提出和管理功能改进建议
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class FeatureRequest:
    """功能请求数据结构"""
    id: str
    title: str
    description: str
    submitter: str  # claude_code, codex, user
    priority: str  # low, medium, high, critical
    category: str  # rule_improvement, new_feature, collaboration, ui
    status: str  # proposed, under_review, approved, implemented, rejected
    created_at: str
    updated_at: str
    votes: Dict[str, str]  # AI投票: {"claude_code": "approve", "codex": "approve"}
    implementation_notes: str = ""
    related_rules: List[str] = None

    def __post_init__(self):
        if self.related_rules is None:
            self.related_rules = []


class FeatureRequestManager:
    """功能请求管理器"""

    def __init__(self, fr_dir: str = ".ai_rules/feature_requests"):
        self.fr_dir = Path(fr_dir)
        self.fr_dir.mkdir(parents=True, exist_ok=True)

        self.requests_file = self.fr_dir / "requests.json"
        self.requests: List[FeatureRequest] = []

        self._load_requests()

    def _generate_fr_id(self) -> str:
        """生成FR ID"""
        timestamp = int(time.time())
        count = len(self.requests) + 1
        return f"FR{count:03d}_{timestamp}"

    def _load_requests(self):
        """加载已有的功能请求"""
        if not self.requests_file.exists():
            return

        try:
            with open(self.requests_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    fr = FeatureRequest(**item)
                    self.requests.append(fr)
        except Exception as e:
            print(f"加载功能请求失败: {e}")

    def _save_requests(self):
        """保存功能请求"""
        try:
            data = [asdict(fr) for fr in self.requests]
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存功能请求失败: {e}")

    def submit_request(self, title: str, description: str, submitter: str,
                      priority: str = "medium", category: str = "rule_improvement") -> str:
        """提交功能请求"""
        fr_id = self._generate_fr_id()

        fr = FeatureRequest(
            id=fr_id,
            title=title,
            description=description,
            submitter=submitter,
            priority=priority,
            category=category,
            status="proposed",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            votes={}
        )

        self.requests.append(fr)
        self._save_requests()

        return fr_id

    def vote_on_request(self, fr_id: str, voter: str, vote: str) -> bool:
        """对功能请求投票"""
        fr = self._find_request(fr_id)
        if not fr:
            return False

        fr.votes[voter] = vote
        fr.updated_at = datetime.now().isoformat()

        # 自动更新状态
        if len(fr.votes) >= 2:  # 假设需要至少2票
            approvals = sum(1 for v in fr.votes.values() if v == "approve")
            if approvals >= 2:
                fr.status = "approved"
            elif len(fr.votes) - approvals >= 2:
                fr.status = "rejected"

        self._save_requests()
        return True

    def update_status(self, fr_id: str, status: str, notes: str = "") -> bool:
        """更新功能请求状态"""
        fr = self._find_request(fr_id)
        if not fr:
            return False

        fr.status = status
        fr.updated_at = datetime.now().isoformat()
        if notes:
            fr.implementation_notes = notes

        self._save_requests()
        return True

    def get_requests(self, status: str = None, category: str = None) -> List[FeatureRequest]:
        """获取功能请求列表"""
        filtered = self.requests

        if status:
            filtered = [fr for fr in filtered if fr.status == status]

        if category:
            filtered = [fr for fr in filtered if fr.category == category]

        return sorted(filtered, key=lambda x: x.created_at, reverse=True)

    def _find_request(self, fr_id: str) -> Optional[FeatureRequest]:
        """查找功能请求"""
        for fr in self.requests:
            if fr.id == fr_id:
                return fr
        return None

    def get_request_details(self, fr_id: str) -> Optional[FeatureRequest]:
        """获取功能请求详情"""
        return self._find_request(fr_id)

    def suggest_rules_from_code_issues(self, code_issues: List[str]) -> List[str]:
        """基于代码问题自动建议规则改进"""
        suggestions = []

        issue_patterns = {
            "缺少错误处理": "建议添加强制错误处理规则",
            "硬编码": "建议添加禁止硬编码配置的规则",
            "SQL注入": "建议加强数据库安全规则",
            "命名不规范": "建议细化命名规范规则",
            "缺少注释": "建议添加强制文档注释规则"
        }

        for issue in code_issues:
            for pattern, suggestion in issue_patterns.items():
                if pattern in issue:
                    suggestions.append(suggestion)

        return list(set(suggestions))  # 去重