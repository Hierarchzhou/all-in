#!/usr/bin/env python3
"""
GitHub 搜索任务 - 两个 Worker 并行搜索不同主题
"""

import asyncio
import yaml
import time
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, str(Path(__file__).parent))

from run_user_tasks import ProgressTrackingControlCenter, ClaudeTask


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
    config_path = Path('github_tasks.yaml')

    print("\n" + "="*80)
    print("🔍 GitHub 项目搜索 - 双 Worker 并行模式")
    print("="*80)
    print()
    print("📋 任务分配:")
    print("   Worker 1: 搜索 AI 信息筛选和价值判断工具")
    print("   Worker 2: 搜索 RSS 聚合和内容管理工具")
    print()
    print("🎯 目标:")
    print("   找到可以实现'AI分身'概念的开源工具")
    print("   - AI 自动判断信息价值")
    print("   - RSS 收集全网信息")
    print("   - 合规的内容管理方案")
    print()
    print("⚡ 优势:")
    print("   - 两个搜索同时进行，节省时间")
    print("   - 分别聚焦不同技术方向")
    print("   - 最后综合两个方向的结果")
    print()
    print("="*80)

    # 检查 gh CLI
    import subprocess
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ GitHub CLI (gh) 已安装")
            print(f"   版本: {result.stdout.split()[2] if len(result.stdout.split()) > 2 else 'unknown'}")
        else:
            print("⚠️  GitHub CLI 未登录，搜索功能可能受限")
    except FileNotFoundError:
        print("❌ 未检测到 GitHub CLI (gh)")
        print("   安装方法: https://cli.github.com/")
        print("   或者 Worker 会尝试使用 Web 搜索作为备选")
    except Exception as e:
        print(f"⚠️  检查 gh 时出错: {e}")

    print()
    input("按 Enter 开始 GitHub 搜索...")
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
    print("🎉 GitHub 搜索完成")
    print("="*80)
    print(f"\n⏱️  总耗时: {total_time:.2f} 秒")
    print()
    print("📊 结果汇总:")
    print("   - Worker 1: AI 信息筛选工具列表")
    print("   - Worker 2: RSS 聚合和内容管理工具列表")
    print()
    print("💡 下一步:")
    print("   1. 查看上面两个搜索报告")
    print("   2. 选择合适的工具组合")
    print("   3. 设计集成方案：RSS收集 + AI筛选 + 知识管理")
    print("   4. 开始部署和测试")
    print()
    print("="*80)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断搜索")
        sys.exit(0)
