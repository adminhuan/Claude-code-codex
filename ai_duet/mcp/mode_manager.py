"""
模式管理器
支持Plan模式、PR模式、FR模式的切换和管理
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class WorkMode(Enum):
    """工作模式枚举"""
    NORMAL = "normal"      # 普通模式：只有规则提醒
    PLAN = "plan"          # 计划模式：制定和管理开发计划
    PR = "pr"              # 代码审查模式：PR创建和审查流程
    FR = "fr"              # 功能请求模式：功能改进建议和投票


@dataclass
class Plan:
    """开发计划数据结构"""
    id: str
    title: str
    description: str
    tasks: List[Dict[str, Any]]  # 任务列表
    creator: str
    status: str  # draft, active, completed, cancelled
    priority: str  # low, medium, high, critical
    created_at: str
    updated_at: str
    estimated_hours: int = 0
    actual_hours: int = 0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class PullRequest:
    """代码审查PR数据结构"""
    id: str
    title: str
    description: str
    author: str
    reviewer: str
    files_changed: List[str]
    status: str  # draft, review_requested, approved, rejected, merged
    priority: str
    created_at: str
    updated_at: str
    review_comments: List[Dict[str, Any]] = None
    merge_conflicts: bool = False

    def __post_init__(self):
        if self.review_comments is None:
            self.review_comments = []


class ModeManager:
    """模式管理器"""

    def __init__(self, config_dir: str = ".ai_rules"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        # 模式配置文件
        self.mode_config_file = self.config_dir / "mode_config.json"
        self.plans_file = self.config_dir / "plans.json"
        self.prs_file = self.config_dir / "pull_requests.json"

        # 当前状态
        self.current_mode = WorkMode.NORMAL
        self.mode_config = {}
        self.plans: List[Plan] = []
        self.pull_requests: List[PullRequest] = []

        # 加载配置
        self._load_config()

    def _generate_id(self, prefix: str) -> str:
        """生成ID"""
        timestamp = int(time.time())
        return f"{prefix}{timestamp}"

    def _load_config(self):
        """加载模式配置"""
        if self.mode_config_file.exists():
            try:
                with open(self.mode_config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_mode = WorkMode(data.get("current_mode", "normal"))
                    self.mode_config = data.get("config", {})
            except Exception as e:
                print(f"加载模式配置失败: {e}")

        # 加载计划
        if self.plans_file.exists():
            try:
                with open(self.plans_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.plans = [Plan(**item) for item in data]
            except Exception as e:
                print(f"加载计划失败: {e}")

        # 加载PR
        if self.prs_file.exists():
            try:
                with open(self.prs_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.pull_requests = [PullRequest(**item) for item in data]
            except Exception as e:
                print(f"加载PR失败: {e}")

    def _save_config(self):
        """保存模式配置"""
        try:
            data = {
                "current_mode": self.current_mode.value,
                "config": self.mode_config,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.mode_config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存模式配置失败: {e}")

    def _save_plans(self):
        """保存计划"""
        try:
            data = [asdict(plan) for plan in self.plans]
            with open(self.plans_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存计划失败: {e}")

    def _save_prs(self):
        """保存PR"""
        try:
            data = [asdict(pr) for pr in self.pull_requests]
            with open(self.prs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存PR失败: {e}")

    # ====== 模式管理 ======

    def switch_mode(self, mode: str) -> bool:
        """切换工作模式"""
        try:
            new_mode = WorkMode(mode)
            self.current_mode = new_mode
            self.mode_config["switched_at"] = datetime.now().isoformat()
            self._save_config()
            return True
        except ValueError:
            return False

    def get_current_mode(self) -> str:
        """获取当前模式"""
        return self.current_mode.value

    def get_available_modes(self) -> List[Dict[str, str]]:
        """获取可用模式列表"""
        return [
            {"mode": "normal", "name": "普通模式", "description": "基础规则提醒功能"},
            {"mode": "plan", "name": "计划模式", "description": "制定和管理开发计划"},
            {"mode": "pr", "name": "代码审查模式", "description": "PR创建和审查流程"},
            {"mode": "fr", "name": "功能请求模式", "description": "功能改进建议和投票"}
        ]

    # ====== 计划模式功能 ======

    def create_plan(self, title: str, description: str, creator: str,
                   priority: str = "medium", estimated_hours: int = 0) -> str:
        """创建开发计划"""
        plan_id = self._generate_id("PLAN_")

        plan = Plan(
            id=plan_id,
            title=title,
            description=description,
            tasks=[],
            creator=creator,
            status="draft",
            priority=priority,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            estimated_hours=estimated_hours
        )

        self.plans.append(plan)
        self._save_plans()
        return plan_id

    def add_task_to_plan(self, plan_id: str, task_title: str, task_description: str,
                        estimated_hours: int = 1, assignee: str = None) -> bool:
        """向计划添加任务"""
        plan = self._find_plan(plan_id)
        if not plan:
            return False

        task = {
            "id": self._generate_id("TASK_"),
            "title": task_title,
            "description": task_description,
            "status": "pending",  # pending, in_progress, completed
            "estimated_hours": estimated_hours,
            "actual_hours": 0,
            "assignee": assignee,
            "created_at": datetime.now().isoformat()
        }

        plan.tasks.append(task)
        plan.updated_at = datetime.now().isoformat()
        self._save_plans()
        return True

    def update_task_status(self, plan_id: str, task_id: str, status: str, actual_hours: int = 0) -> bool:
        """更新任务状态"""
        plan = self._find_plan(plan_id)
        if not plan:
            return False

        for task in plan.tasks:
            if task["id"] == task_id:
                task["status"] = status
                if actual_hours > 0:
                    task["actual_hours"] = actual_hours
                task["updated_at"] = datetime.now().isoformat()

                # 更新计划状态
                if status == "completed" and all(t["status"] == "completed" for t in plan.tasks):
                    plan.status = "completed"

                plan.updated_at = datetime.now().isoformat()
                self._save_plans()
                return True

        return False

    def get_plans(self, status: str = None) -> List[Plan]:
        """获取计划列表"""
        plans = self.plans
        if status:
            plans = [p for p in plans if p.status == status]
        return sorted(plans, key=lambda x: x.created_at, reverse=True)

    def _find_plan(self, plan_id: str) -> Optional[Plan]:
        """查找计划"""
        for plan in self.plans:
            if plan.id == plan_id:
                return plan
        return None

    # ====== PR模式功能 ======

    def create_pull_request(self, title: str, description: str, author: str,
                           reviewer: str, files_changed: List[str],
                           priority: str = "medium") -> str:
        """创建PR"""
        pr_id = self._generate_id("PR_")

        pr = PullRequest(
            id=pr_id,
            title=title,
            description=description,
            author=author,
            reviewer=reviewer,
            files_changed=files_changed,
            status="review_requested",
            priority=priority,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        self.pull_requests.append(pr)
        self._save_prs()
        return pr_id

    def add_review_comment(self, pr_id: str, commenter: str, comment: str,
                          file_path: str = None, line_number: int = None) -> bool:
        """添加审查评论"""
        pr = self._find_pr(pr_id)
        if not pr:
            return False

        comment_data = {
            "id": self._generate_id("COMMENT_"),
            "commenter": commenter,
            "comment": comment,
            "file_path": file_path,
            "line_number": line_number,
            "created_at": datetime.now().isoformat()
        }

        pr.review_comments.append(comment_data)
        pr.updated_at = datetime.now().isoformat()
        self._save_prs()
        return True

    def update_pr_status(self, pr_id: str, status: str, reviewer: str) -> bool:
        """更新PR状态"""
        pr = self._find_pr(pr_id)
        if not pr:
            return False

        pr.status = status
        pr.updated_at = datetime.now().isoformat()

        # 记录状态变更
        status_comment = {
            "id": self._generate_id("STATUS_"),
            "commenter": reviewer,
            "comment": f"状态更新为: {status}",
            "created_at": datetime.now().isoformat()
        }
        pr.review_comments.append(status_comment)

        self._save_prs()
        return True

    def get_pull_requests(self, status: str = None, reviewer: str = None) -> List[PullRequest]:
        """获取PR列表"""
        prs = self.pull_requests
        if status:
            prs = [pr for pr in prs if pr.status == status]
        if reviewer:
            prs = [pr for pr in prs if pr.reviewer == reviewer]
        return sorted(prs, key=lambda x: x.created_at, reverse=True)

    def _find_pr(self, pr_id: str) -> Optional[PullRequest]:
        """查找PR"""
        for pr in self.pull_requests:
            if pr.id == pr_id:
                return pr
        return None

    # ====== 通用功能 ======

    def get_mode_statistics(self) -> Dict[str, Any]:
        """获取各模式统计信息"""
        return {
            "current_mode": self.current_mode.value,
            "plans": {
                "total": len(self.plans),
                "active": len([p for p in self.plans if p.status == "active"]),
                "completed": len([p for p in self.plans if p.status == "completed"])
            },
            "pull_requests": {
                "total": len(self.pull_requests),
                "pending_review": len([pr for pr in self.pull_requests if pr.status == "review_requested"]),
                "approved": len([pr for pr in self.pull_requests if pr.status == "approved"])
            }
        }