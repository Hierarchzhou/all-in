#!/usr/bin/env python3
"""
音频翻译工具 - 将英文音频翻译为中文并配音
基于 claude_video_translator 项目改造

流程：
1. Whisper 语音识别（英文 → 文本）
2. Claude/GPT 翻译（英文文本 → 中文文本）
3. TTS 配音（中文文本 → 中文语音）
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import anthropic


class AudioTranslator:
    def __init__(self, audio_file):
        self.audio_file = Path(audio_file)
        self.work_dir = self.audio_file.parent / f"{self.audio_file.stem}_translated"
        self.work_dir.mkdir(exist_ok=True)

        # 输出文件路径
        self.transcript_file = self.work_dir / "transcript_en.txt"
        self.srt_file = self.work_dir / "subtitles_en.srt"
        self.translated_file = self.work_dir / "transcript_zh.txt"
        self.audio_output = self.work_dir / f"{self.audio_file.stem}_zh.mp3"

    def step1_transcribe(self):
        """使用 Whisper 进行语音识别"""
        print(f"\n[步骤1] 使用 Whisper 识别语音...")
        print(f"输入文件: {self.audio_file}")

        try:
            import whisper

            # 加载模型（base模型，平衡速度和准确度）
            print("加载 Whisper 模型（base）...")
            model = whisper.load_model("base")

            # 转录音频
            print("开始识别，这可能需要几分钟...")
            result = model.transcribe(
                str(self.audio_file),
                language="en",
                verbose=False
            )

            transcript = result["text"]

            # 保存转录文本
            with open(self.transcript_file, 'w', encoding='utf-8') as f:
                f.write(transcript)

            print("✓ 语音识别完成")
            print(f"✓ 转录文本已保存到: {self.transcript_file}")
            print(f"\n预览: {transcript[:200]}...")

            return transcript

        except Exception as e:
            print(f"✗ Whisper 识别失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def step2_translate(self, text):
        """使用 Claude API 翻译文本"""
        print(f"\n[步骤2] 使用 Claude 翻译文本...")

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        api_base = os.environ.get("ANTHROPIC_BASE_URL")

        if not api_key:
            print("✗ 错误: 未设置 ANTHROPIC_API_KEY 环境变量")
            print("请运行: export ANTHROPIC_API_KEY='your-api-key'")
            sys.exit(1)

        # 支持自定义API地址
        client_kwargs = {"api_key": api_key}
        if api_base:
            client_kwargs["base_url"] = api_base
            print(f"使用自定义API地址: {api_base}")

        client = anthropic.Anthropic(**client_kwargs)

        prompt = f"""请将以下英文文本翻译成中文。要求：
1. 保持自然流畅的中文表达
2. 适合语音播报的风格
3. 只返回翻译后的中文文本，不要添加任何说明

英文原文：
{text}"""

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            translated = message.content[0].text

            # 保存翻译结果
            with open(self.translated_file, 'w', encoding='utf-8') as f:
                f.write(translated)

            print("✓ 翻译完成")
            print(f"✓ 翻译文本已保存到: {self.translated_file}")
            return translated

        except Exception as e:
            print(f"✗ 翻译失败: {e}")
            sys.exit(1)

    def step3_text_to_speech(self, text):
        """使用 edge-tts 生成中文语音"""
        print(f"\n[步骤3] 生成中文语音...")

        # 使用微软 Edge TTS（免费）
        cmd = [
            "edge-tts",
            "--text", text,
            "--voice", "zh-CN-XiaoxiaoNeural",  # 中文女声
            "--write-media", str(self.audio_output)
        ]

        try:
            subprocess.run(cmd, check=True)
            print("✓ 语音生成完成")
            print(f"✓ 输出文件: {self.audio_output}")

        except subprocess.CalledProcessError as e:
            print(f"✗ TTS 生成失败: {e}")
            print("\n提示: 如果未安装 edge-tts，请运行:")
            print("  pip install edge-tts")
            sys.exit(1)

    def run(self):
        """执行完整的翻译流程"""
        print("=" * 60)
        print("音频翻译工具 - 英文 → 中文")
        print("=" * 60)

        if not self.audio_file.exists():
            print(f"✗ 错误: 音频文件不存在: {self.audio_file}")
            sys.exit(1)

        # 步骤1: 语音识别
        transcript_en = self.step1_transcribe()

        # 步骤2: 翻译
        transcript_zh = self.step2_translate(transcript_en)

        # 步骤3: 语音合成
        self.step3_text_to_speech(transcript_zh)

        print("\n" + "=" * 60)
        print("✓ 所有步骤完成！")
        print("=" * 60)
        print(f"\n工作目录: {self.work_dir}")
        print(f"英文转录: {self.transcript_file}")
        print(f"中文翻译: {self.translated_file}")
        print(f"中文音频: {self.audio_output}")
        print()


def main():
    if len(sys.argv) != 2:
        print("用法: python audio_translator.py <音频文件.mp3>")
        print("\n示例:")
        print("  python audio_translator.py podcast.mp3")
        sys.exit(1)

    audio_file = sys.argv[1]
    translator = AudioTranslator(audio_file)
    translator.run()


if __name__ == "__main__":
    main()
