#!/usr/bin/env python3
"""
Claude Code Control Center - 真正的并行多实例版本
通过为每个实例分配独立的 session-id 实现真正并行
"""

import asyncio
import json
import uuid
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
    session_id: str  # 独立的会话ID
    process: Optional[asyncio.subprocess.Process] = None
    status: str = "idle"
    current_task: Optional[ClaudeTask] = None
    output: List[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __post_init__(self):
        if self.output is None:
            self.output = []


class ParallelClaudeControlCenter:
    """真正并行的 Claude 控制中心"""

    def __init__(self, max_instances: int = 3):
        self.max_instances = max_instances
        self.instances: List[ClaudeInstance] = []
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, dict] = {}

        # 为每个实例创建独立的 session ID
        for i in range(max_instances):
            session_id = str(uuid.uuid4())
            self.instances.append(ClaudeInstance(
                id=f"claude-{i+1}",
                name=f"Claude Worker {i+1}",
                session_id=session_id
            ))
            print(f"📋 Created {self.instances[-1].name} with session-id: {session_id}")

    async def execute_task(self, instance: ClaudeInstance, task: ClaudeTask):
        """在指定实例上执行任务"""
        instance.status = "running"
        instance.current_task = task
        instance.start_time = datetime.now()

        # 构建 claude 命令 - 使用独立的 session-id
        cmd = [
            "claude",
            "--print",
            "--session-id", instance.session_id,  # 关键：独立会话
            "--allowedTools", " ".join(task.allowed_tools),
            "--permission-mode", task.permission_mode,
            "--output-format", "json",
            task.prompt
        ]

        try:
            print(f"🚀 [{instance.name}] Starting: {task.name}")
            print(f"🔧 [{instance.name}] Session: {instance.session_id[:8]}...")

            # 启动 Claude Code 进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=task.working_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            instance.process = process

            # 实时读取输出
            async def read_stream(stream, is_error=False):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded_line = line.decode().strip()
                    if decoded_line:  # 忽略空行
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
                "session_id": instance.session_id,
                "status": instance.status,
                "output": instance.output,
                "duration": (instance.end_time - instance.start_time).total_seconds(),
                "return_code": process.returncode
            }

            print(f"✅ [{instance.name}] Completed: {task.name} ({instance.end_time - instance.start_time})")

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
        color_code = 31 if is_error else (32 + (int(instance.id.split('-')[1]) % 6))
        prefix = "❌" if is_error else "  "
        print(f"\033[{color_code}m[{timestamp}] {prefix} [{instance.name}]\033[0m {line}")

    async def worker(self, instance: ClaudeInstance):
        """工作线程：从队列获取任务并执行"""
        while True:
            try:
                task = await self.task_queue.get()

                if task is None:  # 结束信号
                    break

                await self.execute_task(instance, task)
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
        print("\n" + "=" * 80)
        print("🎮 Parallel Claude Code Control Center Starting...")
        print(f"📊 Max parallel instances: {self.max_instances}")
        print(f"📋 Total tasks in queue: {self.task_queue.qsize()}")
        print("=" * 80 + "\n")

        # 启动所有工作线程（真正并行）
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

        completed = sum(1 for r in self.results.values() if r["status"] == "completed")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")
        total = len(self.results)

        print(f"\n✅ Completed: {completed}/{total}")
        print(f"❌ Failed: {failed}/{total}\n")

        for task_id, result in self.results.items():
            status_icon = "✅" if result["status"] == "completed" else "❌"
            task = result["task"]
            duration = result.get("duration", 0)

            print(f"{status_icon} {task.name}")
            print(f"   Instance: {result['instance']} (session: {result.get('session_id', 'N/A')[:8]}...)")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Status: {result['status']}")

            if result["status"] == "failed" and "error" in result:
                print(f"   Error: {result['error']}")
            print()


async def main():
    """示例：运行多个并行任务"""

    # 创建并行控制中心
    control_center = ParallelClaudeControlCenter(max_instances=3)

    # 定义测试任务（简单任务，便于测试）
    tasks = [
        ClaudeTask(
            id="task-1",
            name="List Python files",
            prompt="List all Python files in the current directory using Glob tool",
            working_dir=str(Path.cwd()),
            allowed_tools=["Glob"],
            permission_mode="acceptEdits"
        ),
        ClaudeTask(
            id="task-2",
            name="Check git status",
            prompt="Run 'git status' and summarize the repository state",
            working_dir=str(Path.cwd()),
            allowed_tools=["Bash"],
            permission_mode="acceptEdits"
        ),
        ClaudeTask(
            id="task-3",
            name="Read README",
            prompt="Read PROJECT_SUMMARY.md and provide a one-sentence summary",
            working_dir=str(Path.cwd()),
            allowed_tools=["Read"],
            permission_mode="acceptEdits"
        ),
    ]

    # 添加任务
    await control_center.add_tasks(tasks)

    # 启动并行执行
    await control_center.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Control Center interrupted by user")
        sys.exit(0)
