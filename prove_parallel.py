#!/usr/bin/env python3
"""
简单直观的并行证明：通过实时时间戳看到同时执行
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from claude_control_center_parallel import ParallelClaudeControlCenter, ClaudeTask


async def main():
    control_center = ParallelClaudeControlCenter(max_instances=3)

    # 3个简单快速的任务
    tasks = [
        ClaudeTask(
            id="task-a",
            name="任务A: 列出.py文件",
            prompt="Use Glob to list all .py files",
            working_dir=str(Path.cwd()),
            allowed_tools=["Glob"],
        ),
        ClaudeTask(
            id="task-b",
            name="任务B: 列出.md文件",
            prompt="Use Glob to list all .md files",
            working_dir=str(Path.cwd()),
            allowed_tools=["Glob"],
        ),
        ClaudeTask(
            id="task-c",
            name="任务C: 列出.yaml文件",
            prompt="Use Glob to list all .yaml files",
            working_dir=str(Path.cwd()),
            allowed_tools=["Glob"],
        ),
    ]

    print("\n" + "="*80)
    print("🔬 并行执行证明实验")
    print("="*80)
    print("👀 仔细观察下面的时间戳：")
    print("   如果并行: 3个任务的启动时间应该在同一秒内")
    print("   如果串行: 启动时间会相差至少5-10秒")
    print("="*80 + "\n")

    start = datetime.now()

    await control_center.add_tasks(tasks)
    await control_center.start()

    end = datetime.now()

    print("\n" + "="*80)
    print("📊 执行证明")
    print("="*80)

    # 分析启动时间
    task_times = []
    for task_id, result in control_center.results.items():
        if 'duration' in result:
            task_times.append((result['task'].name, result['duration']))

    print(f"\n总耗时: {(end - start).total_seconds():.2f} 秒")
    print("\n各任务耗时:")
    for name, duration in task_times:
        print(f"  - {name}: {duration:.2f}秒")

    total_individual = sum(d for _, d in task_times)
    actual_time = (end - start).total_seconds()

    print(f"\n如果串行总时间: {total_individual:.2f} 秒")
    print(f"实际总时间: {actual_time:.2f} 秒")
    print(f"时间节省: {((total_individual - actual_time) / total_individual * 100):.1f}%")

    if actual_time < total_individual * 0.6:  # 如果实际时间少于串行时间的60%
        print("\n✅ 证明成功！这些任务确实是并行执行的！")
    else:
        print("\n⚠️  可能是串行执行或网络延迟影响")

    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试中断")
        sys.exit(0)
