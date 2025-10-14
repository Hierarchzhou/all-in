#!/usr/bin/env python3
"""
快速测试 IndexTTS 是否能正常工作（不需要示例文件）
"""

import sys
import os

# 设置 HuggingFace 镜像
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# 添加 indextts 到路径
sys.path.insert(0, '/mnt/c/Users/Administrator/Desktop/all-in/indextts')

print("=" * 70)
print("IndexTTS 快速测试")
print("=" * 70)

print("\n[步骤1] 导入 IndexTTS 模块...")
try:
    from indextts.infer_v2 import IndexTTS2
    print("✓ 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

print("\n[步骤2] 初始化模型...")
print("  (第一次运行可能需要下载额外文件，请耐心等待...)")

try:
    tts = IndexTTS2(
        cfg_path="/mnt/c/Users/Administrator/Desktop/all-in/indextts/checkpoints/config.yaml",
        model_dir="/mnt/c/Users/Administrator/Desktop/all-in/indextts/checkpoints",
        use_fp16=True,  # 使用半精度加速
        use_cuda_kernel=False,
        use_deepspeed=False
    )
    print("✓ 模型初始化成功!")
except Exception as e:
    print(f"✗ 模型初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✓ IndexTTS 可以正常使用!")
print("=" * 70)
print("\n你可以使用 audio_translator_indextts.py 进行完整的音频翻译了。")
