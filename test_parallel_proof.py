#!/usr/bin/env python3
"""
测试并行执行的证明脚本
通过时间戳和慢任务来验证是否真的并行
"""

import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from claude_control_center_parallel import ParallelClaudeControlCenter, ClaudeTask


async def main():
    """创建3个慢任务，如果并行执行应该和最慢的任务时间相近"""

    control_center = ParallelClaudeControlCenter(max_instances=3)

    # 创建3个需要时间的任务（每个大约10秒）
    tasks = [
        ClaudeTask(
            id="slow-1",
            name="慢任务1: 查找所有Python文件并统计行数",
            prompt="使用 Glob 找到所有 .py 文件，然后用 Read 工具读取每个文件并统计总行数",
            working_dir=str(Path.cwd()),
            allowed_tools=["Glob", "Read", "Bash"],
            permission_mode="acceptEdits"
        ),
        ClaudeTask(
            id="slow-2",
            name="慢任务2: 搜索所有TODO和FIXME",
            prompt="使用 Grep 在所有 .py 文件中搜索 TODO 和 FIXME 注释，并统计数量",
            working_dir=str(Path.cwd()),
            allowed_tools=["Grep"],
            permission_mode="acceptEdits"
        ),
        ClaudeTask(
            id="slow-3",
            name="慢任务3: 分析git历史",
            prompt="运行 'git log --oneline -20' 并总结最近的提交趋势",
            working_dir=str(Path.cwd()),
            allowed_tools=["Bash"],
            permission_mode="acceptEdits"
        ),
    ]

    print("\n" + "="*80)
    print("🧪 并行执行测试")
    print("="*80)
    print("如果是串行: 预计耗时 ~30-40秒 (每个任务10秒)")
    print("如果是并行: 预计耗时 ~10-15秒 (最慢任务的时间)")
    print("="*80 + "\n")

    import time
    start_time = time.time()

    await control_center.add_tasks(tasks)
    await control_center.start()

    end_time = time.time()
    total_time = end_time - start_time

    print("\n" + "="*80)
    print("🎯 并行测试结果")
    print("="*80)
    print(f"总耗时: {total_time:.2f} 秒")

    if total_time < 20:
        print("✅ 证明成功！任务是并行执行的！")
        print(f"   如果串行至少需要30秒，实际只用了 {total_time:.1f}秒")
    else:
        print("⚠️  可能是串行执行，或网络较慢")

    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(0)
