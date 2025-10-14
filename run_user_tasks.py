#!/usr/bin/env python3
"""
运行用户任务 - 带详细进度可视化
"""

import asyncio
import yaml
import time
from pathlib import Path
from datetime import datetime
from claude_control_center_parallel import ParallelClaudeControlCenter, ClaudeTask


class ProgressTrackingControlCenter(ParallelClaudeControlCenter):
    """带进度追踪的控制中心"""

    def __init__(self, max_instances: int = 2):
        super().__init__(max_instances)
        self.step_logs = {}  # 记录每个任务的步骤日志

    async def execute_task(self, instance, task):
        """重写执行，添加详细进度追踪"""
        task_id = task.id
        self.step_logs[task_id] = []

        print("\n" + "="*80)
        print(f"🚀 [{instance.name}] 开始执行")
        print("="*80)
        print(f"📌 任务: {task.name}")
        print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🆔 会话ID: {instance.session_id[:8]}...")
        print("="*80)
        print()

        # 记录开始
        self.log_step(task_id, "开始执行任务", "⏳")

        # 执行任务
        await super().execute_task(instance, task)

        # 完成总结
        print("\n" + "="*80)
        if task_id in self.results and self.results[task_id]['status'] == 'completed':
            print(f"✅ [{instance.name}] 任务完成成功！")
            self.log_step(task_id, "任务执行完成", "✅")
        else:
            print(f"❌ [{instance.name}] 任务执行失败")
            self.log_step(task_id, "任务执行失败", "❌")

        duration = self.results[task_id].get('duration', 0) if task_id in self.results else 0
        print(f"⏱️  总耗时: {duration:.2f} 秒")
        print("="*80)
        print()

    def _print_instance_output(self, instance, line, is_error=False):
        """捕获输出并检测进度关键词"""
        task_id = instance.current_task.id if instance.current_task else None

        # 检测步骤标记
        if "步骤" in line or "✅" in line or "进度" in line:
            print(f"\n{'='*60}")
            print(f"📍 [{instance.name}] 关键节点")
            print(f"{'='*60}")

        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = [32, 33, 34, 35, 36]
        worker_num = int(instance.id.split('-')[1]) - 1
        color_code = 31 if is_error else colors[worker_num % len(colors)]

        prefix = "❌" if is_error else "📤"
        print(f"\033[{color_code}m[{timestamp}] {prefix} [{instance.name}]\033[0m {line[:200]}")

        # 检测完成信号
        if '"type":"result"' in line:
            try:
                import json
                data = json.loads(line)
                result_text = data.get('result', '')

                # 提取关键信息
                if task_id:
                    self.log_step(task_id, "收到结果数据", "📊")

                print(f"\n{'='*60}")
                print(f"📊 [{instance.name}] 结果预览")
                print(f"{'='*60}")
                # 只显示前500字符
                preview = result_text[:500]
                if len(result_text) > 500:
                    preview += "...\n(结果较长，已截断)"
                print(preview)
                print(f"{'='*60}\n")
            except:
                pass

        if "error" in line.lower() and is_error:
            if task_id:
                self.log_step(task_id, f"遇到错误: {line[:100]}", "⚠️")

    def log_step(self, task_id, message, icon="ℹ️"):
        """记录步骤日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {icon} {message}"
        if task_id in self.step_logs:
            self.step_logs[task_id].append(log_entry)

    def _print_summary(self):
        """打印增强版摘要"""
        print("\n" + "="*80)
        print("🎯 任务执行完整报告")
        print("="*80)

        completed = sum(1 for r in self.results.values() if r['status'] == 'completed')
        failed = sum(1 for r in self.results.values() if r['status'] == 'failed')
        total = len(self.results)

        print(f"\n📊 总体统计:")
        print(f"   ✅ 成功: {completed}/{total}")
        print(f"   ❌ 失败: {failed}/{total}")
        print()

        # 详细报告
        for task_id, result in self.results.items():
            task = result['task']
            status_icon = "✅" if result['status'] == 'completed' else "❌"
            duration = result.get('duration', 0)

            print(f"{status_icon} {task.name}")
            print(f"   执行实例: {result['instance']}")
            print(f"   耗时: {duration:.2f}秒")
            print(f"   状态: {result['status']}")

            # 显示步骤日志
            if task_id in self.step_logs and self.step_logs[task_id]:
                print(f"   关键步骤:")
                for log in self.step_logs[task_id]:
                    print(f"      {log}")

            if 'error' in result:
                print(f"   ❌ 错误: {result['error']}")

            print()

        print("="*80)
        print()


def load_tasks_from_yaml(yaml_path: str):
    """加载任务配置"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    max_instances = config.get('max_instances', 2)
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
    """主函数"""
    config_path = Path('user_tasks.yaml')

    print("\n" + "="*80)
    print("🎮 用户任务执行中心 - 带进度可视化")
    print("="*80)
    print()
    print("📋 任务概述:")
    print("   1. 分析用户图片")
    print("   2. 设计全网信息收集和引流工作流")
    print()
    print("✨ 特性:")
    print("   - 2个任务并行执行")
    print("   - 实时进度反馈")
    print("   - 关键节点可视化")
    print("   - 详细执行报告")
    print()
    print("="*80)
    input("按 Enter 开始执行...")
    print()

    # 加载任务
    max_instances, tasks = load_tasks_from_yaml(str(config_path))

    start_time = time.time()

    # 创建进度追踪控制中心
    control_center = ProgressTrackingControlCenter(max_instances=max_instances)

    # 添加并执行任务
    await control_center.add_tasks(tasks)
    await control_center.start()

    end_time = time.time()
    total_time = end_time - start_time

    # 最终汇总
    print("\n" + "="*80)
    print("🏁 全部任务执行完毕")
    print("="*80)
    print(f"\n⏱️  总耗时: {total_time:.2f} 秒")
    print()
    print("📁 下一步:")
    print("   1. 查看上面的详细分析报告")
    print("   2. 根据建议制定具体实施计划")
    print("   3. 如需要可以继续提问或调整方案")
    print()
    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断执行")
        import sys
        sys.exit(0)
