#!/usr/bin/env python3
"""
快速演示版 - 运行简单任务展示并行效果
"""

import asyncio
import yaml
import time
from pathlib import Path
from datetime import datetime
from claude_control_center_parallel import ParallelClaudeControlCenter, ClaudeTask


def load_tasks_from_yaml(yaml_path: str):
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
            allowed_tools=task_config.get('allowed_tools', ['Bash', 'Read']),
            permission_mode=task_config.get('permission_mode', 'acceptEdits'),
            priority=task_config.get('priority', 0)
        )
        tasks.append(task)

    tasks.sort(key=lambda t: t.priority)
    return max_instances, tasks


async def main():
    config_path = Path('demo_tasks.yaml')

    print("\n" + "="*80)
    print("🎮 Claude 控制中心 - 快速演示")
    print("="*80)

    # 加载配置
    max_instances, tasks = load_tasks_from_yaml(str(config_path))

    print(f"\n📋 将要执行 {len(tasks)} 个任务，最多 {max_instances} 个并行")
    print("\n任务列表:")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. {task.name}")

    print("\n" + "="*80)
    print("开始执行...\n")

    start_time = time.time()

    # 创建并执行
    control_center = ParallelClaudeControlCenter(max_instances=max_instances)
    await control_center.add_tasks(tasks)
    await control_center.start()

    end_time = time.time()
    total_time = end_time - start_time

    # 汇总
    print("\n" + "="*80)
    print("🎯 执行完成！")
    print("="*80)
    print(f"\n⏱️  总耗时: {total_time:.2f} 秒")

    completed = sum(1 for r in control_center.results.values() if r['status'] == 'completed')
    failed = sum(1 for r in control_center.results.values() if r['status'] == 'failed')

    print(f"✅ 成功: {completed}/{len(tasks)}")
    print(f"❌ 失败: {failed}/{len(tasks)}")

    # 计算如果串行需要多少时间
    total_individual = sum(r.get('duration', 0) for r in control_center.results.values())
    saved_time = total_individual - total_time
    efficiency = (saved_time / total_individual * 100) if total_individual > 0 else 0

    print(f"\n📊 效率分析:")
    print(f"   串行总时间: {total_individual:.2f} 秒")
    print(f"   并行总时间: {total_time:.2f} 秒")
    print(f"   节省时间: {saved_time:.2f} 秒 ({efficiency:.1f}%)")

    print("\n📝 各任务详情:")
    for task_id, result in sorted(control_center.results.items(),
                                   key=lambda x: x[1].get('duration', 0),
                                   reverse=True):
        status_icon = "✅" if result['status'] == 'completed' else "❌"
        print(f"   {status_icon} {result['task'].name}: {result.get('duration', 0):.2f}秒")

    print("\n" + "="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        import sys
        sys.exit(0)
