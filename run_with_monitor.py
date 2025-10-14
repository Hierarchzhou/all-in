#!/usr/bin/env python3
"""
带实时监控的控制中心 - 清晰显示每个 Worker 在做什么
"""

import asyncio
import yaml
import time
from pathlib import Path
from datetime import datetime
from claude_control_center_parallel import ParallelClaudeControlCenter, ClaudeTask


class MonitoredControlCenter(ParallelClaudeControlCenter):
    """带实时监控的控制中心"""

    def __init__(self, max_instances: int = 3):
        super().__init__(max_instances)
        self.task_start_times = {}

    async def execute_task(self, instance, task):
        """重写执行任务，添加详细监控"""
        self.task_start_times[task.id] = datetime.now()

        # 打印更详细的开始信息
        print(f"\n{'='*80}")
        print(f"🚀 [{instance.name}] 开始执行任务")
        print(f"{'='*80}")
        print(f"📌 任务名称: {task.name}")
        print(f"📋 任务ID: {task.id}")
        print(f"📝 任务提示:\n{task.prompt.strip()[:200]}...")
        print(f"🔧 允许工具: {', '.join(task.allowed_tools)}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}\n")

        # 执行原始任务
        await super().execute_task(instance, task)

        # 打印完成信息
        if task.id in self.results:
            result = self.results[task.id]
            duration = result.get('duration', 0)
            print(f"\n{'='*80}")
            print(f"✅ [{instance.name}] 任务完成")
            print(f"{'='*80}")
            print(f"📌 任务: {task.name}")
            print(f"⏱️  耗时: {duration:.2f}秒")
            print(f"✨ 状态: {result['status']}")
            print(f"{'='*80}\n")

    def _print_instance_output(self, instance, line, is_error=False):
        """重写输出格式，更清晰"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        task_name = instance.current_task.name if instance.current_task else "空闲"

        # 不同颜色
        colors = [32, 33, 34, 35, 36]
        worker_num = int(instance.id.split('-')[1]) - 1
        color_code = 31 if is_error else colors[worker_num % len(colors)]

        prefix = "❌ ERR" if is_error else "📤 OUT"

        # 只打印JSON结果，不打印中间输出（减少噪音）
        if '"type":"result"' in line or is_error:
            print(f"\033[{color_code}m[{timestamp}] {prefix} [{instance.name}]\033[0m")
            if '"type":"result"' in line:
                try:
                    import json
                    data = json.loads(line)
                    result_text = data.get('result', '')[:300]  # 只显示前300字符
                    print(f"   结果预览: {result_text}...")
                except:
                    pass


def load_tasks_from_yaml(yaml_path: str):
    """从 YAML 加载任务"""
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

    tasks.sort(key=lambda t: t.priority)
    return max_instances, tasks


async def main():
    """主函数"""
    config_path = Path('claude_tasks.yaml')

    if not config_path.exists():
        print(f"❌ 找不到配置文件: {config_path}")
        return

    print("\n" + "="*80)
    print("🎮 Claude 控制中心 - 实时监控模式")
    print("="*80)

    # 加载配置
    max_instances, tasks = load_tasks_from_yaml(str(config_path))

    print(f"\n📋 配置信息:")
    print(f"   - 最大并行实例: {max_instances}")
    print(f"   - 任务总数: {len(tasks)}")
    print(f"\n📝 任务列表:")
    for i, task in enumerate(tasks, 1):
        print(f"   {i}. [{task.id}] {task.name} (优先级: {task.priority})")

    print("\n" + "="*80)
    input("按 Enter 开始执行...")
    print()

    start_time = time.time()

    # 创建监控版控制中心
    control_center = MonitoredControlCenter(max_instances=max_instances)

    # 添加并执行任务
    await control_center.add_tasks(tasks)
    await control_center.start()

    end_time = time.time()
    total_time = end_time - start_time

    # 最终汇总
    print("\n" + "="*80)
    print("🎯 最终执行汇总")
    print("="*80)
    print(f"\n⏱️  总耗时: {total_time:.2f} 秒")

    completed = sum(1 for r in control_center.results.values() if r['status'] == 'completed')
    failed = sum(1 for r in control_center.results.values() if r['status'] == 'failed')

    print(f"✅ 成功: {completed}/{len(tasks)}")
    print(f"❌ 失败: {failed}/{len(tasks)}")

    print("\n📊 各任务详情:")
    for task_id, result in control_center.results.items():
        status_icon = "✅" if result['status'] == 'completed' else "❌"
        print(f"   {status_icon} {result['task'].name}")
        print(f"      Worker: {result['instance']}")
        print(f"      耗时: {result.get('duration', 0):.2f}秒")
        if 'error' in result:
            print(f"      错误: {result['error']}")
        print()

    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        import sys
        sys.exit(0)
