#!/usr/bin/env python3
"""
AI工作台专家代理调度系统示例代码
演示如何将wshobson/agents集成到AI工作台
"""

import json
import asyncio
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


# 代理模型层级
class ModelTier(Enum):
    HAIKU = "haiku"     # 快速响应
    SONNET = "sonnet"   # 标准任务
    OPUS = "opus"       # 复杂推理


# 任务类型
class TaskType(Enum):
    ARCHITECTURE = "架构设计"
    DEVELOPMENT = "代码开发"
    DATA_ANALYSIS = "数据分析"
    BUSINESS = "业务分析"
    SECURITY = "安全审计"
    DOCUMENTATION = "文档编写"
    TESTING = "测试验证"
    DEPLOYMENT = "部署运维"


@dataclass
class Agent:
    """代理定义"""
    name: str
    model_tier: ModelTier
    capabilities: List[str]
    max_tokens: int = 4000
    temperature: float = 0.7
    specialization: str = ""


@dataclass
class Task:
    """任务定义"""
    id: str
    content: str
    type: TaskType
    priority: int = 0
    context: Dict = None
    created_at: datetime = None


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    agent_name: str
    result: Any
    execution_time: float
    success: bool = True
    error: Optional[str] = None


class AgentRegistry:
    """代理注册表"""

    def __init__(self):
        self.agents = self._initialize_agents()

    def _initialize_agents(self) -> Dict[str, Agent]:
        """初始化代理配置"""
        return {
            # Opus层级 - 复杂任务
            "system-architect": Agent(
                name="system-architect",
                model_tier=ModelTier.OPUS,
                capabilities=["系统设计", "架构决策", "技术选型"],
                specialization="整体架构设计"
            ),
            "security-auditor": Agent(
                name="security-auditor",
                model_tier=ModelTier.OPUS,
                capabilities=["安全审计", "漏洞分析", "风险评估"],
                specialization="安全分析"
            ),
            "ml-engineer": Agent(
                name="ml-engineer",
                model_tier=ModelTier.OPUS,
                capabilities=["机器学习", "模型优化", "AI应用"],
                specialization="AI/ML工程"
            ),

            # Sonnet层级 - 标准任务
            "python-expert": Agent(
                name="python-expert",
                model_tier=ModelTier.SONNET,
                capabilities=["Python开发", "数据处理", "自动化"],
                specialization="Python编程"
            ),
            "backend-developer": Agent(
                name="backend-developer",
                model_tier=ModelTier.SONNET,
                capabilities=["API开发", "数据库设计", "微服务"],
                specialization="后端开发"
            ),
            "frontend-developer": Agent(
                name="frontend-developer",
                model_tier=ModelTier.SONNET,
                capabilities=["UI开发", "React/Vue", "响应式设计"],
                specialization="前端开发"
            ),
            "data-scientist": Agent(
                name="data-scientist",
                model_tier=ModelTier.SONNET,
                capabilities=["数据分析", "统计建模", "可视化"],
                specialization="数据科学"
            ),
            "devops-engineer": Agent(
                name="devops-engineer",
                model_tier=ModelTier.SONNET,
                capabilities=["CI/CD", "容器化", "自动化部署"],
                specialization="DevOps"
            ),

            # Haiku层级 - 快速任务
            "code-formatter": Agent(
                name="code-formatter",
                model_tier=ModelTier.HAIKU,
                capabilities=["代码格式化", "风格检查"],
                specialization="代码格式化",
                max_tokens=2000
            ),
            "file-organizer": Agent(
                name="file-organizer",
                model_tier=ModelTier.HAIKU,
                capabilities=["文件整理", "目录结构"],
                specialization="文件组织",
                max_tokens=2000
            ),
        }

    def get_agent(self, name: str) -> Optional[Agent]:
        """获取指定代理"""
        return self.agents.get(name)

    def get_agents_by_capability(self, capability: str) -> List[Agent]:
        """根据能力获取代理列表"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities
        ]


class TaskAnalyzer:
    """任务分析器"""

    def __init__(self):
        self.keywords = {
            TaskType.ARCHITECTURE: ["架构", "设计", "系统", "微服务", "分布式"],
            TaskType.DEVELOPMENT: ["开发", "编写", "实现", "代码", "功能"],
            TaskType.DATA_ANALYSIS: ["分析", "数据", "统计", "预测", "模型"],
            TaskType.BUSINESS: ["业务", "需求", "流程", "产品", "用户"],
            TaskType.SECURITY: ["安全", "漏洞", "风险", "审计", "加密"],
            TaskType.DOCUMENTATION: ["文档", "说明", "注释", "API文档"],
            TaskType.TESTING: ["测试", "验证", "单元测试", "集成测试"],
            TaskType.DEPLOYMENT: ["部署", "发布", "运维", "监控", "容器"],
        }

    def analyze_task_type(self, content: str) -> TaskType:
        """分析任务类型"""
        scores = {}
        for task_type, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            scores[task_type] = score

        return max(scores, key=scores.get) if scores else TaskType.DEVELOPMENT

    def calculate_complexity(self, content: str) -> int:
        """计算任务复杂度（0-100）"""
        complexity = 30  # 基础复杂度

        # 根据内容长度调整
        if len(content) > 500:
            complexity += 20
        elif len(content) > 200:
            complexity += 10

        # 检查是否包含复杂关键词
        complex_keywords = ["架构", "优化", "重构", "分析", "设计", "集成", "迁移"]
        for keyword in complex_keywords:
            if keyword in content:
                complexity += 10

        return min(complexity, 100)


class AgentRouter:
    """代理路由器"""

    def __init__(self, registry: AgentRegistry, analyzer: TaskAnalyzer):
        self.registry = registry
        self.analyzer = analyzer
        self.routing_rules = self._initialize_routing_rules()

    def _initialize_routing_rules(self) -> Dict[TaskType, Dict[str, List[str]]]:
        """初始化路由规则"""
        return {
            TaskType.ARCHITECTURE: {
                "primary": ["system-architect"],
                "support": ["security-auditor", "devops-engineer"]
            },
            TaskType.DEVELOPMENT: {
                "primary": ["python-expert", "backend-developer"],
                "support": ["frontend-developer", "code-formatter"]
            },
            TaskType.DATA_ANALYSIS: {
                "primary": ["data-scientist"],
                "support": ["ml-engineer", "python-expert"]
            },
            TaskType.BUSINESS: {
                "primary": ["system-architect"],
                "support": ["backend-developer"]
            },
            TaskType.SECURITY: {
                "primary": ["security-auditor"],
                "support": ["backend-developer"]
            },
            TaskType.DEPLOYMENT: {
                "primary": ["devops-engineer"],
                "support": ["backend-developer"]
            },
        }

    def route_task(self, task: Task) -> Dict[str, Any]:
        """为任务选择合适的代理"""
        # 分析任务
        task_type = task.type or self.analyzer.analyze_task_type(task.content)
        complexity = self.analyzer.calculate_complexity(task.content)

        # 选择模型层级
        if complexity < 30:
            preferred_tier = ModelTier.HAIKU
        elif complexity < 70:
            preferred_tier = ModelTier.SONNET
        else:
            preferred_tier = ModelTier.OPUS

        # 获取推荐代理
        rules = self.routing_rules.get(task_type, {})
        primary_agents = []
        support_agents = []

        for agent_name in rules.get("primary", []):
            agent = self.registry.get_agent(agent_name)
            if agent:
                primary_agents.append(agent)

        for agent_name in rules.get("support", []):
            agent = self.registry.get_agent(agent_name)
            if agent:
                support_agents.append(agent)

        return {
            "task_type": task_type.value,
            "complexity": complexity,
            "preferred_tier": preferred_tier.value,
            "primary_agents": [a.name for a in primary_agents],
            "support_agents": [a.name for a in support_agents],
            "execution_mode": "parallel" if support_agents else "single"
        }


class AgentExecutor:
    """代理执行器（模拟）"""

    async def execute(self, agent: Agent, task: Task) -> TaskResult:
        """执行任务（模拟）"""
        start_time = datetime.now()

        # 模拟执行延迟
        delay = {"haiku": 0.5, "sonnet": 1.0, "opus": 2.0}
        await asyncio.sleep(delay[agent.model_tier.value])

        # 模拟结果
        result = {
            "agent": agent.name,
            "specialization": agent.specialization,
            "task_content": task.content[:100] + "...",
            "analysis": f"{agent.name}正在处理: {task.content[:50]}...",
            "recommendations": [
                f"建议1: 基于{agent.specialization}的最佳实践",
                f"建议2: 考虑使用{agent.capabilities[0]}技术",
            ]
        }

        execution_time = (datetime.now() - start_time).total_seconds()

        return TaskResult(
            task_id=task.id,
            agent_name=agent.name,
            result=result,
            execution_time=execution_time,
            success=True
        )


class AIWorkbenchScheduler:
    """AI工作台调度器"""

    def __init__(self):
        self.registry = AgentRegistry()
        self.analyzer = TaskAnalyzer()
        self.router = AgentRouter(self.registry, self.analyzer)
        self.executor = AgentExecutor()
        self.task_queue = asyncio.Queue()
        self.results = []

    async def submit_task(self, content: str, priority: int = 0) -> str:
        """提交任务"""
        task = Task(
            id=f"task_{datetime.now().timestamp()}",
            content=content,
            type=self.analyzer.analyze_task_type(content),
            priority=priority,
            created_at=datetime.now()
        )
        await self.task_queue.put(task)
        return task.id

    async def process_task(self, task: Task) -> List[TaskResult]:
        """处理单个任务"""
        # 路由任务到合适的代理
        routing_result = self.router.route_task(task)
        print(f"\n任务路由结果:")
        print(f"  任务类型: {routing_result['task_type']}")
        print(f"  复杂度: {routing_result['complexity']}")
        print(f"  推荐模型: {routing_result['preferred_tier']}")
        print(f"  主要代理: {routing_result['primary_agents']}")
        print(f"  辅助代理: {routing_result['support_agents']}")

        # 并行执行代理任务
        tasks = []
        all_agents = routing_result['primary_agents'] + routing_result['support_agents']

        for agent_name in all_agents:
            agent = self.registry.get_agent(agent_name)
            if agent:
                tasks.append(self.executor.execute(agent, task))

        results = await asyncio.gather(*tasks)
        self.results.extend(results)
        return results

    async def run(self):
        """运行调度器"""
        print("AI工作台调度器已启动...")
        while True:
            try:
                # 获取任务（超时等待）
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                print(f"\n处理任务: {task.id}")
                results = await self.process_task(task)

                # 打印结果
                for result in results:
                    print(f"\n{result.agent_name} 执行结果:")
                    print(f"  执行时间: {result.execution_time:.2f}秒")
                    print(f"  结果: {json.dumps(result.result, ensure_ascii=False, indent=2)}")

            except asyncio.TimeoutError:
                continue
            except KeyboardInterrupt:
                print("\n调度器已停止")
                break


async def demo():
    """演示代理调度系统"""
    scheduler = AIWorkbenchScheduler()

    # 创建调度器任务
    scheduler_task = asyncio.create_task(scheduler.run())

    # 提交测试任务
    test_tasks = [
        "设计一个微服务架构的电商系统",
        "使用Python编写数据分析脚本",
        "分析用户行为数据并生成报告",
        "审计系统安全漏洞",
        "优化数据库查询性能",
        "部署应用到Kubernetes集群"
    ]

    print("\n提交测试任务...")
    for content in test_tasks:
        task_id = await scheduler.submit_task(content)
        print(f"已提交: {task_id} - {content[:30]}...")
        await asyncio.sleep(0.5)  # 避免任务堆积

    # 等待所有任务完成
    await asyncio.sleep(15)

    # 打印统计信息
    print("\n\n=== 执行统计 ===")
    print(f"总任务数: {len(test_tasks)}")
    print(f"完成结果数: {len(scheduler.results)}")

    # 统计各代理使用情况
    agent_stats = {}
    for result in scheduler.results:
        agent_stats[result.agent_name] = agent_stats.get(result.agent_name, 0) + 1

    print("\n代理使用统计:")
    for agent_name, count in sorted(agent_stats.items(), key=lambda x: x[1], reverse=True):
        agent = scheduler.registry.get_agent(agent_name)
        print(f"  {agent_name} ({agent.model_tier.value}): {count}次")

    # 取消调度器
    scheduler_task.cancel()


if __name__ == "__main__":
    print("=" * 50)
    print("AI工作台专家代理调度系统演示")
    print("=" * 50)

    # 运行演示
    asyncio.run(demo())