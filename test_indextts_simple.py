#!/usr/bin/env python3
"""
简单测试 IndexTTS2 是否能正常工作
"""

import sys
sys.path.insert(0, '.')

from indextts.infer_v2 import IndexTTS2

print("→ 正在初始化 IndexTTS2 模型...")
print("  (第一次运行可能需要下载额外的模型文件,请耐心等待)")

try:
    tts = IndexTTS2(
        cfg_path="checkpoints/config.yaml",
        model_dir="checkpoints",
        use_fp16=True,  # 使用半精度,更快
        use_cuda_kernel=False,
        use_deepspeed=False
    )
    print("✓ IndexTTS2 模型初始化成功!")

    # 简单测试
    print("\n→ 测试语音合成...")
    text = "你好,这是一个测试。"

    # 检查示例文件
    import os
    voice_file = "examples/voice_01.wav"
    if not os.path.exists(voice_file):
        print(f"✗ 示例文件不存在: {voice_file}")
        print("  请提供一个音频文件进行测试")
        sys.exit(1)

    tts.infer(
        spk_audio_prompt=voice_file,
        text=text,
        output_path="test_output.wav",
        verbose=True
    )

    print("✓ 语音合成成功!")
    print(f"  输出文件: test_output.wav")

except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
