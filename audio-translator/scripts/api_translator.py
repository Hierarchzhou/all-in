#!/usr/bin/env python3
"""
音频翻译工具 - API版本（无需本地安装Whisper）
使用 OpenAI API 和 Claude API 完成翻译

流程：
1. OpenAI Whisper API 语音识别（英文 → 文本）
2. Claude API 翻译（英文文本 → 中文文本）
3. Edge TTS 配音（中文文本 → 中文语音）
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic


class AudioTranslatorAPI:
    def __init__(self, audio_file):
        self.audio_file = Path(audio_file)
        self.work_dir = self.audio_file.parent / f"{self.audio_file.stem}_translated"
        self.work_dir.mkdir(exist_ok=True)

        # 输出文件
        self.transcript_file = self.work_dir / "transcript_en.txt"
        self.translated_file = self.work_dir / "transcript_zh.txt"
        self.audio_output = self.work_dir / f"{self.audio_file.stem}_zh.mp3"

        # 初始化API客户端
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    def check_api_keys(self):
        """检查API密钥"""
        if not self.anthropic_key:
            print("✗ 错误: 未设置 ANTHROPIC_API_KEY")
            print("请运行: export ANTHROPIC_API_KEY='your-key'")
            return False

        if not self.openai_key:
            print("⚠️  警告: 未设置 OPENAI_API_KEY")
            print("将跳过语音识别步骤，请手动提供英文转录文本")
            return "no_whisper"

        return True

    def step1_transcribe_api(self):
        """使用 OpenAI Whisper API 识别语音"""
        print(f"\n[步骤1] 使用 OpenAI Whisper API 识别语音...")
        print(f"输入文件: {self.audio_file}")

        try:
            client = OpenAI(api_key=self.openai_key)

            # 分块处理大文件（API限制25MB）
            file_size_mb = self.audio_file.stat().st_size / (1024 * 1024)
            print(f"文件大小: {file_size_mb:.2f} MB")

            if file_size_mb > 25:
                print("⚠️  文件超过25MB，需要先压缩或分割")
                print("提示: 使用 ffmpeg 压缩:")
                print(f"  ffmpeg -i '{self.audio_file}' -ar 16000 -ac 1 '{self.audio_file.stem}_compressed.mp3'")
                return None

            # 调用Whisper API
            with open(self.audio_file, 'rb') as audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"
                )

            text = transcript.text

            # 保存转录
            with open(self.transcript_file, 'w', encoding='utf-8') as f:
                f.write(text)

            print("✓ 语音识别完成")
            print(f"✓ 转录文本已保存到: {self.transcript_file}")
            print(f"\n预览: {text[:200]}...")

            return text

        except Exception as e:
            print(f"✗ Whisper API 调用失败: {e}")
            return None

    def step2_translate(self, text):
        """使用 Claude API 翻译"""
        print(f"\n[步骤2] 使用 Claude API 翻译...")

        try:
            client = Anthropic(api_key=self.anthropic_key)

            prompt = f"""请将以下英文文本翻译成中文。要求：
1. 保持自然流畅的中文表达
2. 适合语音播报的风格
3. 只返回翻译后的中文文本，不要添加任何说明

英文原文：
{text}"""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}]
            )

            translated = message.content[0].text

            # 保存翻译
            with open(self.translated_file, 'w', encoding='utf-8') as f:
                f.write(translated)

            print("✓ 翻译完成")
            print(f"✓ 翻译已保存到: {self.translated_file}")
            print(f"\n预览: {translated[:200]}...")

            return translated

        except Exception as e:
            print(f"✗ 翻译失败: {e}")
            return None

    def step3_tts(self, text):
        """使用 Edge TTS 生成中文语音"""
        print(f"\n[步骤3] 生成中文语音...")

        import subprocess

        try:
            # 使用 edge-tts 命令
            cmd = [
                "edge-tts",
                "--text", text,
                "--voice", "zh-CN-XiaoxiaoNeural",
                "--write-media", str(self.audio_output)
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            print("✓ 语音生成完成")
            print(f"✓ 输出: {self.audio_output}")

        except FileNotFoundError:
            print("✗ edge-tts 未安装")
            print("安装命令: pip install edge-tts")
        except Exception as e:
            print(f"✗ TTS 生成失败: {e}")

    def run(self):
        """执行完整流程"""
        print("=" * 70)
        print("音频翻译工具 (API版本) - 英文 → 中文")
        print("=" * 70)

        if not self.audio_file.exists():
            print(f"✗ 错误: 文件不存在: {self.audio_file}")
            sys.exit(1)

        # 检查API密钥
        key_status = self.check_api_keys()
        if key_status == False:
            sys.exit(1)

        # 步骤1: 语音识别
        if key_status == "no_whisper":
            print("\n请手动提供英文文本，或设置 OPENAI_API_KEY")
            if self.transcript_file.exists():
                with open(self.transcript_file, 'r', encoding='utf-8') as f:
                    transcript = f.read()
                print(f"✓ 从已有文件读取: {self.transcript_file}")
            else:
                print("✗ 无法继续")
                sys.exit(1)
        else:
            transcript = self.step1_transcribe_api()
            if not transcript:
                sys.exit(1)

        # 步骤2: 翻译
        translated = self.step2_translate(transcript)
        if not translated:
            sys.exit(1)

        # 步骤3: 语音合成
        self.step3_tts(translated)

        print("\n" + "=" * 70)
        print("✓ 处理完成！")
        print("=" * 70)
        print(f"\n📁 工作目录: {self.work_dir}")
        print(f"📄 英文转录: {self.transcript_file}")
        print(f"📄 中文翻译: {self.translated_file}")
        print(f"🔊 中文音频: {self.audio_output}")


def main():
    if len(sys.argv) != 2:
        print("用法: python audio_translator_api.py <音频文件>")
        print("\n示例:")
        print("  python audio_translator_api.py podcast.mp3")
        print("\n环境变量:")
        print("  ANTHROPIC_API_KEY - Claude API密钥 (必需)")
        print("  OPENAI_API_KEY - OpenAI API密钥 (可选，用于Whisper)")
        sys.exit(1)

    translator = AudioTranslatorAPI(sys.argv[1])
    translator.run()


if __name__ == "__main__":
    main()
