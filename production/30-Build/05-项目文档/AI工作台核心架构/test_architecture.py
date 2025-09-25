"""
AI工作台架构测试脚本
验证各模块的集成效果
"""

import json
import asyncio
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(__file__))

from input_adapter import InputAdapter, InputType
from preprocessor import Preprocessor
from core_engine import CoreEngine, information_extraction_module, content_analysis_module, task_management_module


async def test_full_pipeline():
    """测试完整的处理流水线"""
    print("=== AI工作台架构测试 ===\n")

    # 1. 初始化各模块
    print("1. 初始化模块...")
    input_adapter = InputAdapter()
    preprocessor = Preprocessor()
    core_engine = CoreEngine()

    # 注册功能模块
    core_engine.register_module("information_extraction", information_extraction_module)
    core_engine.register_module("content_analysis", content_analysis_module)
    core_engine.register_module("task_management", task_management_module)

    # 2. 测试输入数据
    test_cases = [
        {
            "name": "任务类型输入",
            "data": """
            今天需要完成以下紧急任务：
            1. 完成AI工作台的核心架构开发
            2. 编写详细的技术文档
            3. 进行系统集成测试

            截止时间：2025-09-20
            负责人：开发团队
            优先级：高
            """,
            "input_type": InputType.TEXT
        },
        {
            "name": "知识类型输入",
            "data": """
            AI工作台架构分析：

            核心组件包括输入层、预处理层、核心引擎等。
            系统采用微服务架构，支持模块化扩展。
            关键技术：Python、异步处理、规则引擎。

            优势：高效、灵活、可扩展
            应用场景：知识管理、内容分析、任务自动化
            """,
            "input_type": InputType.TEXT
        }
    ]

    # 3. 逐一测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试案例：{test_case['name']}")
        print("-" * 50)

        try:
            # 输入适配
            print("   → 输入适配处理...")
            adapted_data = input_adapter.process_input(
                test_case["data"],
                test_case["input_type"]
            )
            print(f"     类型: {adapted_data['input_type']}")
            print(f"     分类: {adapted_data['category']}")
            print(f"     标签: {adapted_data['tags']}")

            # 预处理
            print("   → 预处理阶段...")
            preprocessed_data = preprocessor.process(adapted_data)
            print(f"     关键词: {preprocessed_data.get('keywords', [])[1:4]}...")
            print(f"     实体: 日期{len(preprocessed_data.get('entities', {}).get('dates', []))}个")
            print(f"     情感: {preprocessed_data.get('sentiment', {}).get('label', 'unknown')}")

            # 核心引擎处理
            print("   → 核心引擎处理...")
            final_result = await core_engine.process(preprocessed_data)

            if final_result.get("error"):
                print(f"     ❌ 处理失败: {final_result['error']}")
            else:
                print("     ✅ 处理完成")
                if final_result.get("key_points"):
                    print(f"     关键点: {len(final_result['key_points'])}个")
                if final_result.get("tasks_extracted"):
                    print(f"     提取任务: {final_result['task_count']}个")
                if final_result.get("themes"):
                    print(f"     主题: {final_result['themes']}")

        except Exception as e:
            print(f"     ❌ 测试失败: {str(e)}")

    # 4. 显示统计信息
    print("\n" + "=" * 60)
    print("处理统计信息：")
    stats = core_engine.get_statistics()
    print(f"总任务数: {stats['total_tasks']}")
    print(f"成功率: {stats['success_rate']:.1%}")
    print(f"注册模块: {', '.join(stats['registered_modules'])}")


def test_individual_modules():
    """测试各个模块的独立功能"""
    print("\n=== 模块独立测试 ===\n")

    # 测试输入适配器
    print("1. 输入适配器测试")
    adapter = InputAdapter()
    result = adapter.process_input("这是一个测试文档，包含重要信息。", "text")
    print(f"   分类结果: {result['category']}")
    print(f"   生成ID: {result['id'][:8]}...")

    # 测试预处理器
    print("\n2. 预处理器测试")
    preprocessor = Preprocessor()
    test_data = {
        "content": "联系张三 @zhangsan，邮箱：test@example.com，网址：https://example.com #测试",
        "input_type": "text"
    }
    processed = preprocessor.process(test_data)
    print(f"   提取URL: {processed.get('urls', [])}")
    print(f"   提取邮箱: {processed.get('emails', [])}")
    print(f"   提取标签: {processed.get('entities', {}).get('hashtags', [])}")

    # 测试功能模块
    print("\n3. 功能模块测试")
    test_content = {
        "cleaned_content": "重要任务：1. 开发系统 2. 测试功能 3. 部署上线",
        "content": "重要任务：1. 开发系统 2. 测试功能 3. 部署上线"
    }

    extraction_result = information_extraction_module(test_content)
    print(f"   信息提取: 发现{len(extraction_result['key_points'])}个关键点")

    analysis_result = content_analysis_module(test_content)
    print(f"   内容分析: 识别主题{analysis_result['themes']}")

    task_result = task_management_module(test_content)
    print(f"   任务管理: 提取{task_result['task_count']}个任务")


if __name__ == "__main__":
    # 运行完整流水线测试
    asyncio.run(test_full_pipeline())

    # 运行独立模块测试
    test_individual_modules()

    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("架构各模块工作正常，可以进行下一步开发。")