#!/usr/bin/env python3
"""
Claude Code Control Center - Advanced Version with Rich TUI
增强版：带实时 TUI 界面的多实例管理中心
"""

import asyncio
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import sys

try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.layout import Layout
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  'rich' library not found. Install with: pip install rich")
    print("    Falling back to basic output mode\n")

from claude_control_center import ClaudeTask, ClaudeInstance, ClaudeControlCenter


class AdvancedClaudeControlCenter(ClaudeControlCenter):
    """增强版控制中心 - 带实时 TUI 界面"""

    def __init__(self, max_instances: int = 3, use_rich: bool = True):
        super().__init__(max_instances)
        self.use_rich = use_rich and RICH_AVAILABLE
        self.console = Console() if self.use_rich else None

    def generate_dashboard(self) -> Table:
        """生成实时仪表板"""
        table = Table(title="🎮 Claude Control Center", box=box.ROUNDED)

        table.add_column("Instance", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Current Task", style="green")
        table.add_column("Duration", style="yellow")
        table.add_column("Output Lines", style="blue")

        for instance in self.instances:
            status_icon = {
                "idle": "⚪ Idle",
                "running": "🟢 Running",
                "completed": "✅ Done",
                "failed": "❌ Failed"
            }.get(instance.status, "⚪ Unknown")

            task_name = instance.current_task.name if instance.current_task else "-"

            duration = "-"
            if instance.start_time:
                if instance.end_time:
                    duration = f"{(instance.end_time - instance.start_time).total_seconds():.1f}s"
                else:
                    duration = f"{(datetime.now() - instance.start_time).total_seconds():.1f}s"

            output_count = str(len(instance.output))

            table.add_row(
                instance.name,
                status_icon,
                task_name,
                duration,
                output_count
            )

        return table

    def generate_summary_panel(self) -> Panel:
        """生成任务摘要面板"""
        completed = sum(1 for r in self.results.values() if r["status"] == "completed")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")
        total = len(self.results)

        summary = f"""
📊 Total Tasks: {total}
✅ Completed: {completed}
❌ Failed: {failed}
⏳ Queue Size: {self.task_queue.qsize()}
        """

        return Panel(summary, title="Summary", border_style="green")

    async def start_with_live_display(self):
        """启动控制中心（带实时显示）"""
        if not self.use_rich:
            await self.start()
            return

        self.console.print("\n[bold green]🎮 Claude Code Control Center[/bold green]")
        self.console.print(f"[cyan]📊 Max instances: {self.max_instances}[/cyan]\n")

        # 启动所有工作线程
        workers = [
            asyncio.create_task(self.worker(instance))
            for instance in self.instances
        ]

        # 实时显示仪表板
        with Live(self.generate_dashboard(), refresh_per_second=2, console=self.console) as live:
            # 在后台更新显示
            async def update_display():
                while not self.task_queue.empty() or any(i.status == "running" for i in self.instances):
                    live.update(self.generate_dashboard())
                    await asyncio.sleep(0.5)

            display_task = asyncio.create_task(update_display())

            # 等待所有任务完成
            await self.task_queue.join()

            # 发送结束信号
            for _ in self.instances:
                await self.task_queue.put(None)

            # 等待所有工作线程结束
            await asyncio.gather(*workers)

            # 停止显示更新
            await display_task

            # 最终更新
            live.update(self.generate_dashboard())

        self._print_rich_summary()

    def _print_rich_summary(self):
        """打印增强版摘要"""
        if not self.use_rich:
            self._print_summary()
            return

        self.console.print("\n")
        self.console.print(self.generate_summary_panel())

        # 详细结果表格
        results_table = Table(title="📋 Task Results", box=box.ROUNDED)
        results_table.add_column("Task", style="cyan")
        results_table.add_column("Instance", style="magenta")
        results_table.add_column("Status", style="green")
        results_table.add_column("Duration", style="yellow")

        for task_id, result in self.results.items():
            status_style = "green" if result["status"] == "completed" else "red"
            status_text = f"[{status_style}]{result['status']}[/{status_style}]"

            duration = f"{result.get('duration', 0):.2f}s" if "duration" in result else "-"

            results_table.add_row(
                result["task"].name,
                result["instance"],
                status_text,
                duration
            )

        self.console.print(results_table)


def load_tasks_from_yaml(yaml_path: str) -> Tuple[int, List[ClaudeTask]]:
    """从 YAML 配置文件加载任务"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    max_instances = config.get('max_instances', 3)
    tasks = []

    for task_config in config.get('tasks', []):
        task = ClaudeTask(
            id=task_config['id'],
            name=task_config['name'],
            prompt=task_config['prompt'],
            working_dir=task_config.get('working_dir', '.'),
            allowed_tools=task_config.get('allowed_tools', ['Bash', 'Read', 'Write', 'Edit']),
            permission_mode=task_config.get('permission_mode', 'acceptEdits'),
            priority=task_config.get('priority', 0)
        )
        tasks.append(task)

    # 按优先级排序
    tasks.sort(key=lambda t: t.priority)

    return max_instances, tasks


async def main():
    """主函数：从配置文件启动"""
    import argparse

    parser = argparse.ArgumentParser(description="Claude Code Control Center")
    parser.add_argument(
        '--config',
        default='claude_tasks.yaml',
        help='Path to task configuration file (default: claude_tasks.yaml)'
    )
    parser.add_argument(
        '--max-instances',
        type=int,
        help='Override max instances from config'
    )
    parser.add_argument(
        '--no-rich',
        action='store_true',
        help='Disable rich TUI interface'
    )

    args = parser.parse_args()

    # 加载配置
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        print("\n💡 Creating example config file...")

        # 创建示例配置
        example_config = """# Claude Control Center - Task Configuration
max_instances: 3

tasks:
  - id: "example-task"
    name: "Example Task"
    prompt: "List all Python files in the current directory"
    working_dir: "."
    allowed_tools:
      - Bash
      - Read
      - Glob
    priority: 1
"""
        config_path.write_text(example_config, encoding='utf-8')
        print(f"✅ Created example config: {config_path}")
        print("   Edit this file and run again!")
        return

    # 加载任务
    max_instances, tasks = load_tasks_from_yaml(str(config_path))

    if args.max_instances:
        max_instances = args.max_instances

    # 创建控制中心
    control_center = AdvancedClaudeControlCenter(
        max_instances=max_instances,
        use_rich=not args.no_rich
    )

    # 添加任务
    await control_center.add_tasks(tasks)

    # 启动
    if control_center.use_rich:
        await control_center.start_with_live_display()
    else:
        await control_center.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Control Center interrupted by user")
        sys.exit(0)
