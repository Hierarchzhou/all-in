#!/usr/bin/env python3
"""
音频翻译工具 - 声音克隆版本
支持保留原始音色的跨语言翻译

TTS引擎选项:
1. elevenlabs - 高质量声音克隆 (需要API key)
2. openai - OpenAI TTS (固定音色但音质好)
3. edge - Edge TTS (免费但电子音)

流程：
1. Whisper API 语音识别（英文 → 文本）
2. Claude API 翻译（英文 → 中文）
3. 声音克隆 TTS（使用原音频的音色生成中文）
"""

import os
import sys
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic
import subprocess
import requests


class VoiceCloneTranslator:
    def __init__(self, audio_file, tts_engine="elevenlabs"):
        self.audio_file = Path(audio_file)
        self.work_dir = self.audio_file.parent / f"{self.audio_file.stem}_voice_clone"
        self.work_dir.mkdir(exist_ok=True)

        self.tts_engine = tts_engine

        # 输出文件
        self.transcript_file = self.work_dir / "transcript_en.txt"
        self.translated_file = self.work_dir / "transcript_zh.txt"
        self.audio_output = self.work_dir / f"{self.audio_file.stem}_zh.mp3"

        # API keys
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")

    def check_requirements(self):
        """检查必需的API keys"""
        if not self.anthropic_key:
            print("✗ 错误: 需要设置 ANTHROPIC_API_KEY")
            return False

        if not self.openai_key:
            print("⚠️  警告: 未设置 OPENAI_API_KEY，将跳过Whisper识别")
            return "no_whisper"

        if self.tts_engine == "elevenlabs" and not self.elevenlabs_key:
            print("⚠️  警告: 未设置 ELEVENLABS_API_KEY，将使用Edge TTS")
            self.tts_engine = "edge"

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
                print("✗ 文件超过25MB，请先压缩")
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

            prompt = f"""请将以下英文翻译成中文。要求：
1. 自然流畅，适合语音播报
2. 保持原意，语气一致
3. 只返回翻译文本，不要任何解释

英文原文：
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

    def step3_voice_clone_tts(self, text):
        """使用声音克隆生成中文语音"""
        print(f"\n[步骤3] 生成中文语音（引擎: {self.tts_engine}）...")

        if self.tts_engine == "elevenlabs":
            return self._elevenlabs_voice_clone(text)
        elif self.tts_engine == "openai":
            return self._openai_tts(text)
        else:
            return self._edge_tts(text)

    def _elevenlabs_voice_clone(self, text):
        """ElevenLabs 声音克隆"""
        print("使用 ElevenLabs 声音克隆...")

        try:
            # 第一步：上传原始音频作为声音样本
            print("→ 上传原始音频作为声音样本...")

            headers = {"xi-api-key": self.elevenlabs_key}

            # 创建临时voice
            add_voice_url = "https://api.elevenlabs.io/v1/voices/add"

            with open(self.audio_file, 'rb') as audio_file:
                files = {
                    'files': (self.audio_file.name, audio_file, 'audio/mpeg')
                }
                data = {
                    'name': f'voice_clone_{self.audio_file.stem}',
                    'description': 'Auto-generated voice clone'
                }

                response = requests.post(add_voice_url, headers=headers, data=data, files=files)

                if response.status_code != 200:
                    print(f"✗ 声音克隆失败: {response.text}")
                    return False

                voice_id = response.json()['voice_id']
                print(f"✓ 声音已克隆，voice_id: {voice_id}")

            # 第二步：使用克隆的声音生成中文
            print("→ 生成中文语音...")

            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

            tts_data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",  # 支持中文
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            response = requests.post(tts_url, headers=headers, json=tts_data)

            if response.status_code == 200:
                with open(self.audio_output, 'wb') as f:
                    f.write(response.content)
                print(f"✓ 生成完成: {self.audio_output}")
                return True
            else:
                print(f"✗ 生成失败: {response.text}")
                return False

        except Exception as e:
            print(f"✗ ElevenLabs 调用失败: {e}")
            print("→ 回退到 Edge TTS...")
            return self._edge_tts(text)

    def _openai_tts(self, text):
        """OpenAI TTS（固定音色但音质好）"""
        print("使用 OpenAI TTS...")

        try:
            client = OpenAI(api_key=self.openai_key)

            response = client.audio.speech.create(
                model="tts-1-hd",
                voice="nova",  # 可选: alloy, echo, fable, onyx, nova, shimmer
                input=text
            )

            response.stream_to_file(self.audio_output)
            print(f"✓ 生成完成: {self.audio_output}")
            return True

        except Exception as e:
            print(f"✗ OpenAI TTS 失败: {e}")
            return False

    def _edge_tts(self, text):
        """Edge TTS（免费但电子音）"""
        print("使用 Edge TTS...")

        try:
            cmd = [
                "edge-tts",
                "--text", text,
                "--voice", "zh-CN-XiaoxiaoNeural",
                "--write-media", str(self.audio_output)
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✓ 生成完成: {self.audio_output}")
            return True

        except Exception as e:
            print(f"✗ Edge TTS 失败: {e}")
            return False

    def run(self):
        """执行完整流程"""
        print("=" * 70)
        print("音频翻译工具 - 声音克隆版")
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

        # 步骤3: 声音克隆 + TTS
        success = self.step3_voice_clone_tts(translated)

        if success:
            print("\n" + "=" * 70)
            print("✓ 所有步骤完成！")
            print("=" * 70)
            print(f"\n📁 工作目录: {self.work_dir}")
            print(f"📄 英文转录: {self.transcript_file}")
            print(f"📄 中文翻译: {self.translated_file}")
            print(f"🔊 中文音频: {self.audio_output}")
            print(f"\nTTS引擎: {self.tts_engine}")

        return success


def main():
    if len(sys.argv) < 2:
        print("用法: python audio_translator_voice_clone.py <音频文件> [tts引擎]")
        print("\nTTS引擎选项:")
        print("  elevenlabs - 高质量声音克隆（需要 ELEVENLABS_API_KEY）")
        print("  openai     - OpenAI TTS（固定音色）")
        print("  edge       - Edge TTS（免费但电子音）")
        print("\n示例:")
        print("  python audio_translator_voice_clone.py podcast.mp3 elevenlabs")
        print("\n环境变量:")
        print("  ANTHROPIC_API_KEY   - Claude API (必需)")
        print("  OPENAI_API_KEY      - OpenAI API (Whisper识别)")
        print("  ELEVENLABS_API_KEY  - ElevenLabs API (声音克隆)")
        sys.exit(1)

    audio_file = sys.argv[1]
    tts_engine = sys.argv[2] if len(sys.argv) > 2 else "elevenlabs"

    translator = VoiceCloneTranslator(audio_file, tts_engine)
    translator.run()


if __name__ == "__main__":
    main()
