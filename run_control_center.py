#!/usr/bin/env python3
"""
从 claude_tasks.yaml 加载配置并运行控制中心
"""

import asyncio
import yaml
from pathlib import Path
from claude_control_center_parallel import ParallelClaudeControlCenter, ClaudeTask


def load_tasks_from_yaml(yaml_path: str):
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

    # 加载配置
    config_path = Path('claude_tasks.yaml')

    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("\n请确保 claude_tasks.yaml 在当前目录")
        return

    print("📋 正在加载配置文件...")
    max_instances, tasks = load_tasks_from_yaml(str(config_path))

    print(f"✅ 加载成功！")
    print(f"   - 最大并行数: {max_instances}")
    print(f"   - 任务数量: {len(tasks)}")
    print()

    # 创建控制中心
    control_center = ParallelClaudeControlCenter(max_instances=max_instances)

    # 添加任务
    await control_center.add_tasks(tasks)

    # 启动执行
    await control_center.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Control Center interrupted by user")
        import sys
        sys.exit(0)
