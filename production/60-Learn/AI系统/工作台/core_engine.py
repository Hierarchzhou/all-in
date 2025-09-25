"""
核心引擎模块
智能调度中心，负责协调各功能模块的数据处理流程
"""

import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class CoreEngine:
    """智能调度中心"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化核心引擎

        Args:
            config: 配置参数
        """
        self.config = config or self._default_config()
        self.modules = {}  # 功能模块注册表
        self.rules = []  # 规则列表
        self.task_queue = []  # 任务队列
        self.executor = ThreadPoolExecutor(max_workers=self.config["max_workers"])
        self.processing_history = []  # 处理历史

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "max_workers": 4,
            "max_queue_size": 100,
            "timeout": 300,  # 5分钟超时
            "retry_count": 3,
            "enable_parallel": True
        }

    def register_module(self, name: str, module: Callable) -> None:
        """
        注册功能模块

        Args:
            name: 模块名称
            module: 模块处理函数
        """
        self.modules[name] = module
        logger.info(f"Module registered: {name}")

    def add_rule(self, rule: Dict[str, Any]) -> None:
        """
        添加处理规则

        Args:
            rule: 规则定义
        """
        self.rules.append(rule)
        logger.info(f"Rule added: {rule.get('name', 'unnamed')}")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理输入数据

        Args:
            data: 预处理后的数据

        Returns:
            处理结果
        """
        # 创建任务记录
        task = self._create_task(data)

        try:
            # 应用规则确定处理流程
            workflow = self._determine_workflow(data)

            # 执行工作流
            if self.config["enable_parallel"] and self._can_parallel(workflow):
                result = await self._execute_parallel(task, workflow)
            else:
                result = await self._execute_sequential(task, workflow)

            # 更新任务状态
            task["status"] = ProcessingStatus.COMPLETED.value
            task["result"] = result
            task["completed_at"] = datetime.now().isoformat()

        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            task["status"] = ProcessingStatus.FAILED.value
            task["error"] = str(e)
            result = {"error": str(e)}

        # 记录处理历史
        self._record_history(task)

        return result

    def _create_task(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建任务记录"""
        return {
            "id": self._generate_task_id(),
            "data": data,
            "status": ProcessingStatus.PENDING.value,
            "priority": self._determine_priority(data),
            "created_at": datetime.now().isoformat(),
            "modules_executed": []
        }

    def _determine_workflow(self, data: Dict[str, Any]) -> List[str]:
        """
        根据规则确定处理工作流

        Args:
            data: 输入数据

        Returns:
            需要执行的模块列表
        """
        workflow = []

        # 根据内容类别确定基础工作流
        category = data.get("category", "")

        if category == "task":
            workflow = ["information_extraction", "task_management"]
        elif category == "knowledge":
            workflow = ["content_analysis", "knowledge_organization"]
        elif category == "document":
            workflow = ["information_extraction", "content_analysis", "knowledge_organization"]
        elif category == "decision":
            workflow = ["content_analysis", "decision_support"]
        else:
            workflow = ["information_extraction", "content_analysis"]

        # 应用规则修改工作流
        for rule in self.rules:
            if self._match_rule(rule, data):
                if rule.get("action") == "add_module":
                    workflow.append(rule["module"])
                elif rule.get("action") == "remove_module":
                    if rule["module"] in workflow:
                        workflow.remove(rule["module"])
                elif rule.get("action") == "replace_workflow":
                    workflow = rule["workflow"]

        return workflow

    def _match_rule(self, rule: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """判断规则是否匹配"""
        conditions = rule.get("conditions", [])

        for condition in conditions:
            field = condition["field"]
            operator = condition["operator"]
            value = condition["value"]

            data_value = self._get_nested_value(data, field)

            if operator == "equals":
                if data_value != value:
                    return False
            elif operator == "contains":
                if value not in str(data_value):
                    return False
            elif operator == "greater_than":
                if float(data_value) <= float(value):
                    return False
            elif operator == "less_than":
                if float(data_value) >= float(value):
                    return False
            elif operator == "in":
                if data_value not in value:
                    return False
            elif operator == "exists":
                if data_value is None:
                    return False

        return True

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """获取嵌套字段值"""
        keys = path.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value

    async def _execute_sequential(self, task: Dict[str, Any], workflow: List[str]) -> Dict[str, Any]:
        """顺序执行工作流"""
        result = task["data"].copy()

        for module_name in workflow:
            if module_name in self.modules:
                logger.info(f"Executing module: {module_name}")
                module = self.modules[module_name]

                try:
                    # 执行模块
                    module_result = await self._run_module(module, result)
                    result.update(module_result)
                    task["modules_executed"].append(module_name)
                except Exception as e:
                    logger.error(f"Module {module_name} failed: {str(e)}")
                    if self.config.get("stop_on_error", True):
                        raise

        return result

    async def _execute_parallel(self, task: Dict[str, Any], workflow: List[str]) -> Dict[str, Any]:
        """并行执行工作流"""
        result = task["data"].copy()
        futures = []

        with ThreadPoolExecutor(max_workers=len(workflow)) as executor:
            for module_name in workflow:
                if module_name in self.modules:
                    module = self.modules[module_name]
                    future = executor.submit(self._run_module_sync, module, result.copy())
                    futures.append((module_name, future))

            # 收集结果
            for module_name, future in futures:
                try:
                    module_result = future.result(timeout=self.config["timeout"])
                    result.update(module_result)
                    task["modules_executed"].append(module_name)
                    logger.info(f"Module {module_name} completed")
                except Exception as e:
                    logger.error(f"Module {module_name} failed: {str(e)}")
                    if self.config.get("stop_on_error", True):
                        raise

        return result

    async def _run_module(self, module: Callable, data: Dict[str, Any]) -> Dict[str, Any]:
        """异步运行模块"""
        if asyncio.iscoroutinefunction(module):
            return await module(data)
        else:
            # 在线程池中运行同步函数
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(self.executor, module, data)

    def _run_module_sync(self, module: Callable, data: Dict[str, Any]) -> Dict[str, Any]:
        """同步运行模块"""
        return module(data)

    def _can_parallel(self, workflow: List[str]) -> bool:
        """判断工作流是否可以并行执行"""
        # 简单规则：如果模块之间没有依赖关系，则可以并行
        # 这里可以实现更复杂的依赖检查逻辑
        return len(workflow) > 1

    def _determine_priority(self, data: Dict[str, Any]) -> int:
        """确定任务优先级"""
        # 基于内容类别和关键词确定优先级
        category = data.get("category", "")
        content = data.get("content", "")

        if "紧急" in content or "urgent" in content.lower():
            return TaskPriority.CRITICAL.value
        elif category == "task":
            return TaskPriority.HIGH.value
        elif category == "decision":
            return TaskPriority.HIGH.value
        else:
            return TaskPriority.NORMAL.value

    def _generate_task_id(self) -> str:
        """生成任务ID"""
        import uuid
        return str(uuid.uuid4())

    def _record_history(self, task: Dict[str, Any]) -> None:
        """记录处理历史"""
        self.processing_history.append(task)

        # 限制历史记录数量
        if len(self.processing_history) > 1000:
            self.processing_history = self.processing_history[-500:]

    def get_statistics(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        total_tasks = len(self.processing_history)
        completed_tasks = sum(1 for t in self.processing_history if t["status"] == ProcessingStatus.COMPLETED.value)
        failed_tasks = sum(1 for t in self.processing_history if t["status"] == ProcessingStatus.FAILED.value)

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "registered_modules": list(self.modules.keys()),
            "active_rules": len(self.rules)
        }


# 功能模块示例
def information_extraction_module(data: Dict[str, Any]) -> Dict[str, Any]:
    """信息提取模块"""
    content = data.get("cleaned_content", data.get("content", ""))

    # 提取关键信息
    key_points = []

    # 查找列表项
    import re
    list_items = re.findall(r'^\s*[-*•]\s+(.+)$', content, re.MULTILINE)
    key_points.extend(list_items)

    # 查找重要句子（包含关键词的句子）
    important_keywords = ["重要", "关键", "核心", "必须", "important", "critical", "must", "key"]
    sentences = content.split("。")
    for sentence in sentences:
        if any(keyword in sentence.lower() for keyword in important_keywords):
            key_points.append(sentence.strip())

    return {
        "key_points": key_points[:10],  # 限制数量
        "extraction_completed": True
    }


def content_analysis_module(data: Dict[str, Any]) -> Dict[str, Any]:
    """内容分析模块"""
    content = data.get("cleaned_content", data.get("content", ""))

    # 模式识别
    patterns = {
        "problem_solution": bool(re.search(r'(问题|issue|problem).*(解决|solution|solve)', content, re.IGNORECASE)),
        "cause_effect": bool(re.search(r'(因为|because|due to).*(所以|therefore|thus)', content, re.IGNORECASE)),
        "comparison": bool(re.search(r'(相比|compared|versus|vs)', content, re.IGNORECASE)),
        "timeline": bool(re.search(r'\d{4}[-/年]', content))
    }

    # 主题识别
    themes = []
    theme_keywords = {
        "technology": ["AI", "技术", "系统", "开发", "编程", "software", "code"],
        "business": ["业务", "商业", "市场", "客户", "销售", "business", "market"],
        "learning": ["学习", "知识", "教育", "培训", "study", "learn", "education"]
    }

    for theme, keywords in theme_keywords.items():
        if any(keyword.lower() in content.lower() for keyword in keywords):
            themes.append(theme)

    return {
        "patterns_found": patterns,
        "themes": themes,
        "analysis_completed": True
    }


def task_management_module(data: Dict[str, Any]) -> Dict[str, Any]:
    """任务管理模块"""
    content = data.get("cleaned_content", data.get("content", ""))

    tasks = []

    # 提取任务（简单实现）
    task_patterns = [
        r'(?:TODO|待办|任务)[：:]\s*(.+)',
        r'(?:需要|need to|must)\s+(.+)',
        r'^\s*\d+\.\s+(.+)$'  # 编号列表
    ]

    for pattern in task_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            tasks.append({
                "description": match.strip(),
                "status": "pending",
                "created_at": datetime.now().isoformat()
            })

    # 提取截止日期
    dates = data.get("entities", {}).get("dates", [])
    if dates and tasks:
        # 简单地将第一个日期分配给第一个任务
        tasks[0]["deadline"] = dates[0]

    return {
        "tasks_extracted": tasks,
        "task_count": len(tasks)
    }


# 使用示例
if __name__ == "__main__":
    import asyncio

    async def main():
        # 初始化引擎
        engine = CoreEngine()

        # 注册模块
        engine.register_module("information_extraction", information_extraction_module)
        engine.register_module("content_analysis", content_analysis_module)
        engine.register_module("task_management", task_management_module)

        # 添加规则
        engine.add_rule({
            "name": "urgent_task_rule",
            "conditions": [
                {"field": "content", "operator": "contains", "value": "紧急"}
            ],
            "action": "add_module",
            "module": "task_management"
        })

        # 测试数据
        test_data = {
            "content": """
            紧急任务：需要完成以下工作
            1. 实现输入适配器模块
            2. 开发预处理器功能
            3. 构建核心调度引擎

            这是AI工作台架构的关键组件，必须在本周完成。
            """,
            "category": "task",
            "cleaned_content": "紧急任务：需要完成以下工作 1. 实现输入适配器模块 2. 开发预处理器功能 3. 构建核心调度引擎"
        }

        # 处理数据
        result = await engine.process(test_data)
        print("Processing result:", json.dumps(result, ensure_ascii=False, indent=2))

        # 获取统计信息
        stats = engine.get_statistics()
        print("\nStatistics:", json.dumps(stats, ensure_ascii=False, indent=2))

    # 运行示例
    asyncio.run(main())