# 使用指南

完整的 Audio Translator 使用说明。

---

## 📋 目录

- [基础用法](#基础用法)
- [命令行工具](#命令行工具)
- [Python API](#python-api)
- [TTS 引擎选择](#tts-引擎选择)
- [高级功能](#高级功能)
- [批量处理](#批量处理)
- [最佳实践](#最佳实践)

---

## 🚀 基础用法

### 快速开始

```bash
# 使用默认 IndexTTS 引擎
python scripts/indextts_translator.py podcast.mp3

# 输出文件位置
ls outputs/podcast_indextts.mp3
```

### 指定 TTS 引擎

```bash
# IndexTTS (本地，最佳效果)
python scripts/indextts_translator.py audio.mp3

# ElevenLabs (云端，高质量)
python scripts/voice_clone_translator.py audio.mp3 elevenlabs

# OpenAI TTS (云端，平衡)
python scripts/voice_clone_translator.py audio.mp3 openai

# Edge TTS (免费，基础)
python scripts/basic_translator.py audio.mp3
```

---

## 🖥️ 命令行工具

### indextts_translator.py

使用 IndexTTS 进行本地声音克隆。

```bash
python scripts/indextts_translator.py [OPTIONS] <audio_file>

选项:
  --output-dir PATH      输出目录 (默认: outputs/)
  --device DEVICE        设备选择 (cuda/cpu)
  --fp16                 使用半精度 (节省显存)
  --verbose              详细输出

示例:
  python scripts/indextts_translator.py podcast.mp3 --fp16 --verbose
```

### voice_clone_translator.py

使用云端 API 进行声音克隆。

```bash
python scripts/voice_clone_translator.py <audio_file> [engine]

参数:
  audio_file            输入音频文件
  engine                TTS 引擎: elevenlabs/openai/edge

环境变量:
  ELEVENLABS_API_KEY    ElevenLabs API 密钥
  OPENAI_API_KEY        OpenAI API 密钥

示例:
  python scripts/voice_clone_translator.py test.mp3 elevenlabs
```

### api_translator.py

使用 API 的基础翻译。

```bash
python scripts/api_translator.py <audio_file>

环境变量:
  ANTHROPIC_API_KEY     Claude API 密钥
  OPENAI_API_KEY        OpenAI API 密钥

示例:
  python scripts/api_translator.py podcast.mp3
```

---

## 🐍 Python API

### 基础示例

```python
from src.translator import AudioTranslator

# 创建翻译器
translator = AudioTranslator(
    tts_engine="indextts",
    device="cuda",
    use_fp16=True
)

# 翻译音频
result = translator.translate(
    input_file="podcast.mp3",
    output_dir="outputs"
)

print(f"✓ 完成: {result.output_path}")
print(f"  转录: {result.transcript}")
print(f"  翻译: {result.translation}")
```

### 指定 TTS 引擎

```python
# IndexTTS (本地)
translator = AudioTranslator(
    tts_engine="indextts",
    device="cuda"
)

# ElevenLabs (云端)
translator = AudioTranslator(
    tts_engine="elevenlabs",
    api_key="your-elevenlabs-key"
)

# OpenAI TTS (云端)
translator = AudioTranslator(
    tts_engine="openai",
    api_key="your-openai-key"
)

# Edge TTS (免费)
translator = AudioTranslator(
    tts_engine="edge",
    voice="zh-CN-XiaoxiaoNeural"
)
```

### 自定义翻译提示词

```python
translator = AudioTranslator(
    tts_engine="indextts",
    translation_prompt="""
    请将以下英文翻译成专业的技术中文。
    要求：
    1. 保持术语准确性
    2. 适合技术演讲
    3. 自然流畅

    英文原文：
    {text}
    """
)
```

### 批量处理

```python
import os
from pathlib import Path

translator = AudioTranslator(tts_engine="indextts")

# 处理目录下所有音频
audio_dir = Path("audio_files")
for audio_file in audio_dir.glob("*.mp3"):
    print(f"处理: {audio_file.name}")
    translator.translate(
        input_file=str(audio_file),
        output_dir="outputs"
    )
```

### 错误处理

```python
from src.translator import AudioTranslator, TranslationError

translator = AudioTranslator(tts_engine="indextts")

try:
    result = translator.translate("podcast.mp3")
except TranslationError as e:
    print(f"翻译失败: {e}")
    # 记录错误日志
    logger.error(f"Translation failed: {e}")
```

---

## 🎨 TTS 引擎选择

### IndexTTS (推荐)

**优点**:
- ✅ 最佳声音克隆效果
- ✅ 完全免费
- ✅ 支持情感控制
- ✅ 本地运行，隐私安全

**缺点**:
- ❌ 需要 GPU
- ❌ 首次运行慢（模型加载）

**使用场景**:
- 需要高质量声音克隆
- 有 GPU 资源
- 大量音频处理

**配置**:
```python
translator = AudioTranslator(
    tts_engine="indextts",
    device="cuda",
    use_fp16=True,  # 节省显存
    use_cuda_kernel=False,
    use_deepspeed=False
)
```

### ElevenLabs

**优点**:
- ✅ 优秀的声音克隆
- ✅ 不需要 GPU
- ✅ 云端处理，速度快

**缺点**:
- ❌ 需要付费 API ($1/1000字符)
- ❌ 需要网络连接

**使用场景**:
- 没有 GPU
- 偶尔使用
- 要求高质量

**成本估算**:
- 1 分钟音频 ≈ 200 字符 ≈ $0.20
- 10 分钟音频 ≈ 2000 字符 ≈ $2.00

**配置**:
```python
translator = AudioTranslator(
    tts_engine="elevenlabs",
    api_key=os.getenv("ELEVENLABS_API_KEY"),
    voice_settings={
        "stability": 0.5,
        "similarity_boost": 0.75
    }
)
```

### OpenAI TTS

**优点**:
- ✅ 音质好
- ✅ 价格便宜 ($0.015/1000字符)
- ✅ 不需要 GPU

**缺点**:
- ❌ 不支持声音克隆
- ❌ 固定音色

**使用场景**:
- 不需要声音克隆
- 预算有限
- 要求稳定性

**配置**:
```python
translator = AudioTranslator(
    tts_engine="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
    voice="alloy",  # alloy/echo/fable/onyx/nova/shimmer
    speed=1.0
)
```

### Edge TTS

**优点**:
- ✅ 完全免费
- ✅ 不需要 GPU
- ✅ 不需要 API 密钥

**缺点**:
- ❌ 音质一般（电子音）
- ❌ 不支持声音克隆

**使用场景**:
- 快速测试
- 预算为零
- 对音质要求不高

**配置**:
```python
translator = AudioTranslator(
    tts_engine="edge",
    voice="zh-CN-XiaoxiaoNeural",
    rate="+0%",
    volume="+0%"
)
```

---

## 🔧 高级功能

### 1. 情感控制 (IndexTTS)

```python
from src.engines.indextts import IndexTTSEngine

engine = IndexTTSEngine(
    model_dir="models/indextts/checkpoints"
)

# 使用情感向量
# [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
result = engine.synthesize(
    text="这真是太棒了！",
    reference_audio="voice.wav",
    emotion_vector=[0.8, 0, 0, 0, 0, 0, 0.3, 0]  # 开心+平静
)

# 使用情感文本
result = engine.synthesize(
    text="这真是太棒了！",
    reference_audio="voice.wav",
    emotion_text="非常兴奋和激动",
    emotion_alpha=0.6
)
```

### 2. 语速调整

```python
# Edge TTS
translator = AudioTranslator(
    tts_engine="edge",
    rate="+20%"  # 加速 20%
)

# OpenAI TTS
translator = AudioTranslator(
    tts_engine="openai",
    speed=1.2  # 1.2 倍速
)
```

### 3. 音频后处理

```python
from pydub import AudioSegment

# 调整音量
audio = AudioSegment.from_file("output.mp3")
audio = audio + 5  # 提高 5dB
audio.export("output_louder.mp3", format="mp3")

# 降噪
audio = audio.low_pass_filter(3000)
audio.export("output_clean.mp3", format="mp3")
```

### 4. 字幕生成

```python
translator = AudioTranslator(
    tts_engine="indextts",
    generate_subtitles=True
)

result = translator.translate("podcast.mp3")
print(f"字幕文件: {result.subtitle_path}")
```

---

## 📦 批量处理

### 方法 1: Shell 脚本

```bash
#!/bin/bash
# batch_translate.sh

for file in audio_files/*.mp3; do
    echo "Processing: $file"
    python scripts/indextts_translator.py "$file"
done
```

### 方法 2: Python 脚本

```python
# batch_translate.py
from pathlib import Path
from src.translator import AudioTranslator
from tqdm import tqdm

translator = AudioTranslator(tts_engine="indextts")

audio_dir = Path("audio_files")
audio_files = list(audio_dir.glob("*.mp3"))

for audio_file in tqdm(audio_files, desc="翻译进度"):
    try:
        translator.translate(
            input_file=str(audio_file),
            output_dir="outputs"
        )
        print(f"✓ {audio_file.name}")
    except Exception as e:
        print(f"✗ {audio_file.name}: {e}")
```

### 方法 3: 并发处理

```python
from concurrent.futures import ThreadPoolExecutor
from src.translator import AudioTranslator

def translate_file(audio_file):
    translator = AudioTranslator(tts_engine="indextts")
    return translator.translate(audio_file)

audio_files = ["file1.mp3", "file2.mp3", "file3.mp3"]

with ThreadPoolExecutor(max_workers=2) as executor:
    results = executor.map(translate_file, audio_files)
```

---

## 💡 最佳实践

### 1. 音频质量

**推荐格式**:
- ✅ WAV (无损)
- ✅ FLAC (无损)
- ✅ MP3 (320kbps)

**避免**:
- ❌ 低比特率 MP3 (<128kbps)
- ❌ 压缩过度的音频

### 2. 音频长度

**推荐**:
- ✅ 单个文件 1-10 分钟
- ✅ 长音频分段处理

**原因**:
- API 限制（Whisper: 25MB）
- 内存占用
- 错误恢复

### 3. GPU 优化

```python
# 使用 FP16
translator = AudioTranslator(
    tts_engine="indextts",
    use_fp16=True  # 节省 50% 显存
)

# 批处理大小
translator.batch_size = 1  # 避免 OOM

# 内存清理
import torch
torch.cuda.empty_cache()
```

### 4. 错误处理

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation.log'),
        logging.StreamHandler()
    ]
)

translator = AudioTranslator(tts_engine="indextts")

try:
    result = translator.translate("audio.mp3")
except Exception as e:
    logging.error(f"Translation failed: {e}", exc_info=True)
```

### 5. 成本控制

```python
# 使用免费引擎
translator = AudioTranslator(tts_engine="edge")

# 或混合使用
def choose_engine(audio_duration):
    if audio_duration < 60:  # 1分钟内
        return "elevenlabs"  # 高质量
    else:
        return "indextts"  # 本地免费
```

---

## 📊 性能优化

### GPU 内存优化

```yaml
# config.yaml
indextts:
  use_fp16: true          # 半精度
  use_cuda_kernel: false  # 关闭 CUDA kernel
  optimize_memory: true   # 内存优化
```

### 批处理优化

```python
# 小批量处理
translator.batch_size = 1

# 预加载模型
translator.preload_models()

# 复用翻译器实例
for file in files:
    translator.translate(file)
```

---

## 🐛 故障排查

### 问题: 内存不足

```python
# 解决方案 1: 使用 FP16
translator = AudioTranslator(
    tts_engine="indextts",
    use_fp16=True
)

# 解决方案 2: 减小批处理
translator.batch_size = 1

# 解决方案 3: 清理缓存
import torch
torch.cuda.empty_cache()
```

### 问题: API 超时

```python
# 增加超时时间
translator = AudioTranslator(
    tts_engine="elevenlabs",
    timeout=300  # 5 分钟
)
```

### 问题: 声音克隆效果差

**检查清单**:
1. ✅ 原音频人声清晰
2. ✅ 背景噪音少
3. ✅ 音频长度 10-30 秒
4. ✅ 音频质量高

---

需要更多帮助？查看:
- [安装指南](installation.md)
- [引擎对比](engines.md)
- [API 参考](api-reference.md)
