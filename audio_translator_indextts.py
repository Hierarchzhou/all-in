#!/usr/bin/env python3
"""
音频翻译工具 - IndexTTS 版本
使用 IndexTTS 进行高质量声音克隆

流程:
1. Whisper API 语音识别(英文 → 文本)
2. Claude API 翻译(英文 → 中文)
3. IndexTTS 声音克隆(使用原音频的音色生成中文)
"""

import os
import sys
import subprocess
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic


class IndexTTSTranslator:
    def __init__(self, audio_file):
        self.audio_file = Path(audio_file).absolute()
        self.work_dir = self.audio_file.parent / f"{self.audio_file.stem}_indextts"
        self.work_dir.mkdir(exist_ok=True)

        # IndexTTS 路径
        self.indextts_dir = Path(__file__).parent / "indextts"
        self.indextts_cli = self.indextts_dir / "cli.py"
        self.model_dir = self.indextts_dir / "checkpoints"

        # 输出文件
        self.transcript_file = self.work_dir / "transcript_en.txt"
        self.translated_file = self.work_dir / "transcript_zh.txt"
        self.audio_output = self.work_dir / f"{self.audio_file.stem}_zh.mp3"

        # API keys
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    def check_requirements(self):
        """检查必需的组件"""
        if not self.anthropic_key:
            print("✗ 错误: 需要设置 ANTHROPIC_API_KEY")
            return False

        if not self.openai_key:
            print("⚠️  警告: 未设置 OPENAI_API_KEY,将跳过 Whisper 识别")
            return "no_whisper"

        if not self.indextts_dir.exists():
            print(f"✗ 错误: IndexTTS 目录不存在: {self.indextts_dir}")
            return False

        if not self.model_dir.exists() or not (self.model_dir / "gpt.pth").exists():
            print(f"✗ 错误: IndexTTS 模型未下载: {self.model_dir}")
            return False

        return True

    def step1_transcribe(self):
        """使用 OpenAI Whisper API 识别语音"""
        print(f"\n[步骤1] 语音识别...")
        print(f"输入: {self.audio_file}")

        try:
            client = OpenAI(api_key=self.openai_key)

            file_size_mb = self.audio_file.stat().st_size / (1024 * 1024)
            print(f"文件大小: {file_size_mb:.2f} MB")

            if file_size_mb > 25:
                print("✗ 文件超过 25MB,请先压缩")
                return None

            with open(self.audio_file, 'rb') as audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"
                )

            text = transcript.text

            with open(self.transcript_file, 'w', encoding='utf-8') as f:
                f.write(text)

            print("✓ 识别完成")
            print(f"预览: {text[:200]}...")
            return text

        except Exception as e:
            print(f"✗ 识别失败: {e}")
            return None

    def step2_translate(self, text):
        """使用 Claude API 翻译"""
        print(f"\n[步骤2] 翻译文本...")

        try:
            api_base = os.environ.get("ANTHROPIC_BASE_URL")
            client_kwargs = {"api_key": self.anthropic_key}
            if api_base:
                client_kwargs["base_url"] = api_base

            client = Anthropic(**client_kwargs)

            prompt = f"""请将以下英文翻译成中文。要求:
1. 自然流畅,适合语音播报
2. 保持原意,语气一致
3. 只返回翻译文本,不要任何解释

英文原文:
{text}"""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}]
            )

            translated = message.content[0].text

            with open(self.translated_file, 'w', encoding='utf-8') as f:
                f.write(translated)

            print("✓ 翻译完成")
            print(f"预览: {translated[:200]}...")
            return translated

        except Exception as e:
            print(f"✗ 翻译失败: {e}")
            return None

    def step3_indextts(self, text):
        """使用 IndexTTS 生成声音克隆音频"""
        print(f"\n[步骤3] IndexTTS 声音克隆...")

        try:
            # 使用 all-in 项目的虚拟环境
            venv_python = Path(__file__).parent / "indextts" / ".venv" / "bin" / "python"

            if not venv_python.exists():
                print(f"⚠️  虚拟环境不存在,使用系统 Python")
                venv_python = "python"

            # 构建命令
            cmd = [
                str(venv_python),
                str(self.indextts_cli),
                text,
                "--voice", str(self.audio_file),
                "--output", str(self.audio_output),
                "--device", "cuda",  # 如果没有 GPU 会自动回退到 CPU
                "--model_dir", str(self.model_dir)
            ]

            print(f"→ 执行命令:")
            print(f"  {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                cwd=self.indextts_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✓ 生成完成")
                print(f"输出: {self.audio_output}")
                return True
            else:
                print(f"✗ 生成失败")
                print(f"错误: {result.stderr}")
                return False

        except Exception as e:
            print(f"✗ IndexTTS 调用失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self):
        """执行完整流程"""
        print("=" * 70)
        print("音频翻译工具 - IndexTTS 声音克隆版")
        print("=" * 70)

        if not self.audio_file.exists():
            print(f"✗ 文件不存在: {self.audio_file}")
            return False

        status = self.check_requirements()
        if status == False:
            return False

        # 步骤1: 语音识别
        if status == "no_whisper":
            if self.transcript_file.exists():
                with open(self.transcript_file, 'r', encoding='utf-8') as f:
                    transcript = f.read()
                print(f"✓ 从文件读取转录: {self.transcript_file}")
            else:
                print("✗ 无法继续")
                return False
        else:
            transcript = self.step1_transcribe()
            if not transcript:
                return False

        # 步骤2: 翻译
        translated = self.step2_translate(transcript)
        if not translated:
            return False

        # 步骤3: IndexTTS 声音克隆
        success = self.step3_indextts(translated)

        if success:
            print("\n" + "=" * 70)
            print("✓ 所有步骤完成!")
            print("=" * 70)
            print(f"\n📁 工作目录: {self.work_dir}")
            print(f"📄 英文转录: {self.transcript_file}")
            print(f"📄 中文翻译: {self.translated_file}")
            print(f"🔊 中文音频: {self.audio_output}")
            print(f"\nTTS引擎: IndexTTS (声音克隆)")

        return success


def main():
    if len(sys.argv) < 2:
        print("用法: python audio_translator_indextts.py <音频文件>")
        print("\n环境变量:")
        print("  ANTHROPIC_API_KEY   - Claude API (必需)")
        print("  OPENAI_API_KEY      - OpenAI API (Whisper 识别)")
        print("\n示例:")
        print("  python audio_translator_indextts.py podcast.mp3")
        sys.exit(1)

    audio_file = sys.argv[1]
    translator = IndexTTSTranslator(audio_file)
    translator.run()


if __name__ == "__main__":
    main()
