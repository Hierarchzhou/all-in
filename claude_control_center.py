#!/usr/bin/env python3
"""
Claude Code Control Center - 多实例管理中心
统一调度和监控多个 Claude Code 实例，实现并行任务执行
"""

import asyncio
import json
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import sys


@dataclass
class ClaudeTask:
    """Claude 任务定义"""
    id: str
    name: str
    prompt: str
    working_dir: str
    allowed_tools: List[str] = None
    permission_mode: str = "acceptEdits"
    priority: int = 0

    def __post_init__(self):
        if self.allowed_tools is None:
            self.allowed_tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]


@dataclass
class ClaudeInstance:
    """Claude Code 实例"""
    id: str
    name: str
    process: Optional[asyncio.subprocess.Process] = None
    status: str = "idle"  # idle, running, completed, failed
    current_task: Optional[ClaudeTask] = None
    output: List[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __post_init__(self):
        if self.output is None:
            self.output = []


class ClaudeControlCenter:
    """Claude Code 多实例控制中心"""

    def __init__(self, max_instances: int = 3):
        self.max_instances = max_instances
        self.instances: List[ClaudeInstance] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, dict] = {}

        # 初始化实例池
        for i in range(max_instances):
            self.instances.append(ClaudeInstance(
                id=f"claude-{i+1}",
                name=f"Claude Worker {i+1}"
            ))

    async def execute_task(self, instance: ClaudeInstance, task: ClaudeTask):
        """在指定实例上执行任务"""
        instance.status = "running"
        instance.current_task = task
        instance.start_time = datetime.now()

        # 构建 claude 命令
        cmd = [
            "claude",
            "--print",  # 使用 --print 而不是 -p
            "--allowedTools", " ".join(task.allowed_tools),  # 空格分隔，不是逗号
            "--permission-mode", task.permission_mode,
            "--output-format", "json",
            task.prompt  # prompt 作为最后一个参数
        ]

        try:
            print(f"🔧 [{instance.name}] Command: {' '.join(cmd)}")

            # 启动 Claude Code headless 进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=task.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            instance.process = process

            # 实时读取输出和错误
            async def read_stream(stream, is_error=False):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded_line = line.decode().strip()
                    instance.output.append(f"{'[ERR] ' if is_error else ''}{decoded_line}")
                    self._print_instance_output(instance, decoded_line, is_error)

            # 并行读取 stdout 和 stderr
            await asyncio.gather(
                read_stream(process.stdout, False),
                read_stream(process.stderr, True)
            )

            # 等待进程完成
            await process.wait()

            instance.end_time = datetime.now()
            instance.status = "completed" if process.returncode == 0 else "failed"

            # 保存结果
            self.results[task.id] = {
                "task": task,
                "instance": instance.id,
                "status": instance.status,
                "output": instance.output,
                "duration": (instance.end_time - instance.start_time).total_seconds(),
                "return_code": process.returncode
            }

        except Exception as e:
            instance.status = "failed"
            instance.end_time = datetime.now()
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.results[task.id] = {
                "task": task,
                "instance": instance.id,
                "status": "failed",
                "error": error_msg,
                "output": instance.output
            }
            print(f"❌ [{instance.name}] FATAL ERROR: {error_msg}")
            import traceback
            traceback.print_exc()

        finally:
            instance.current_task = None
            instance.process = None

    def _print_instance_output(self, instance: ClaudeInstance, line: str, is_error: bool = False):
        """格式化输出实例日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_code = 31 if is_error else (32 + (int(instance.id.split('-')[1]) % 6))  # 错误用红色
        prefix = "❌" if is_error else "📤"
        print(f"\033[{color_code}m[{timestamp}] {prefix} [{instance.name}]\033[0m {line}")

    async def worker(self, instance: ClaudeInstance):
        """工作线程：从队列获取任务并执行"""
        while True:
            try:
                # 从队列获取任务
                task = await self.task_queue.get()

                if task is None:  # 结束信号
                    break

                print(f"🚀 [{instance.name}] Starting task: {task.name}")
                await self.execute_task(instance, task)
                print(f"✅ [{instance.name}] Completed task: {task.name}")

                self.task_queue.task_done()

            except Exception as e:
                print(f"❌ [{instance.name}] Worker error: {e}")

    async def add_task(self, task: ClaudeTask):
        """添加任务到队列"""
        await self.task_queue.put(task)
        print(f"📝 Added task to queue: {task.name}")

    async def add_tasks(self, tasks: List[ClaudeTask]):
        """批量添加任务"""
        for task in tasks:
            await self.add_task(task)

    async def start(self):
        """启动控制中心"""
        print("=" * 80)
        print("🎮 Claude Code Control Center Starting...")
        print(f"📊 Max instances: {self.max_instances}")
        print("=" * 80)

        # 启动所有工作线程
        workers = [
            asyncio.create_task(self.worker(instance))
            for instance in self.instances
        ]

        # 等待所有任务完成
        await self.task_queue.join()

        # 发送结束信号
        for _ in self.instances:
            await self.task_queue.put(None)

        # 等待所有工作线程结束
        await asyncio.gather(*workers)

        self._print_summary()

    def _print_summary(self):
        """打印执行摘要"""
        print("\n" + "=" * 80)
        print("📊 Execution Summary")
        print("=" * 80)

        for task_id, result in self.results.items():
            status_icon = "✅" if result["status"] == "completed" else "❌"
            task = result["task"]
            duration = result.get("duration", 0)

            print(f"{status_icon} {task.name}")
            print(f"   Instance: {result['instance']}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Status: {result['status']}")

            if result["status"] == "failed" and "error" in result:
                print(f"   Error: {result['error']}")
            print()

    def get_status_dashboard(self) -> str:
        """获取实时状态面板"""
        lines = ["\n" + "=" * 80]
        lines.append("🎮 Claude Control Center - Live Status")
        lines.append("=" * 80)

        for instance in self.instances:
            status_icon = {
                "idle": "⚪",
                "running": "🟢",
                "completed": "✅",
                "failed": "❌"
            }.get(instance.status, "⚪")

            lines.append(f"{status_icon} {instance.name}: {instance.status}")

            if instance.current_task:
                lines.append(f"   Task: {instance.current_task.name}")
                if instance.start_time:
                    elapsed = (datetime.now() - instance.start_time).total_seconds()
                    lines.append(f"   Running: {elapsed:.1f}s")

        lines.append("=" * 80)
        return "\n".join(lines)


async def main():
    """示例：运行多个并行任务"""

    # 创建控制中心（最多3个并行实例）
    control_center = ClaudeControlCenter(max_instances=3)

    # 定义任务
    tasks = [
        ClaudeTask(
            id="task-1",
            name="Analyze audio_translator.py",
            prompt="Analyze the audio_translator.py file and provide a summary of its architecture, key functions, and potential improvements",
            working_dir=str(Path.cwd()),
            allowed_tools=["Read", "Glob", "Grep"]
        ),
        ClaudeTask(
            id="task-2",
            name="Review indextts structure",
            prompt="Review the indextts/ directory structure and document the project organization",
            working_dir=str(Path.cwd()),
            allowed_tools=["Bash", "Read", "Glob"]
        ),
        ClaudeTask(
            id="task-3",
            name="Test coverage analysis",
            prompt="Analyze test_indextts_simple.py and test_indextts_quick.py, identify what's being tested and what's missing",
            working_dir=str(Path.cwd()),
            allowed_tools=["Read", "Grep"]
        ),
        ClaudeTask(
            id="task-4",
            name="Check dependencies",
            prompt="Read requirements.txt and check if all dependencies are properly documented and up-to-date",
            working_dir=str(Path.cwd()),
            allowed_tools=["Read", "Bash"]
        ),
        ClaudeTask(
            id="task-5",
            name="Documentation review",
            prompt="Review all README files and identify documentation gaps or areas needing improvement",
            working_dir=str(Path.cwd()),
            allowed_tools=["Read", "Glob", "Grep"]
        )
    ]

    # 添加任务到队列
    await control_center.add_tasks(tasks)

    # 启动执行
    await control_center.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Control Center interrupted by user")
        sys.exit(0)
