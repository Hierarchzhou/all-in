# 音频翻译工具

将英文音频翻译为中文并生成中文配音。

## 功能特点

- ✅ 自动语音识别（Whisper）
- ✅ 智能翻译（Claude AI）
- ✅ 中文语音合成（Edge TTS - 免费）
- ✅ 完整的工作流程自动化

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装系统依赖

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

#### Windows
下载并安装 [FFmpeg](https://ffmpeg.org/download.html)

### 3. 配置 API 密钥

设置 Claude API 密钥：

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

或者添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## 使用方法

### 基本用法

```bash
python audio_translator.py podcast.mp3
```

### 处理流程

1. **语音识别** - Whisper 将英文音频转为文本
2. **翻译** - Claude 将英文文本翻译成中文
3. **语音合成** - Edge TTS 生成中文语音

### 输出文件

所有文件会保存在 `{原文件名}_translated/` 目录下：

```
podcast_translated/
├── transcript_en.txt    # 英文转录
├── transcript_zh.txt    # 中文翻译
├── subtitles_en.srt     # 英文字幕（如果生成）
└── podcast_zh.mp3       # 中文音频
```

## 配置选项

### Whisper 模型大小

在 `audio_translator.py` 中修改模型：

```python
"--model", "base",  # 可选: tiny, base, small, medium, large
```

模型对比：
- `tiny` - 最快，准确度较低
- `base` - 平衡（推荐）
- `small` - 较准确
- `medium` - 很准确，较慢
- `large` - 最准确，很慢

### TTS 语音选择

Edge TTS 支持多种中文声音：

```python
# 女声
"zh-CN-XiaoxiaoNeural"  # 晓晓（默认）
"zh-CN-XiaoyiNeural"    # 晓伊

# 男声
"zh-CN-YunxiNeural"     # 云希
"zh-CN-YunyangNeural"   # 云扬
```

查看所有可用声音：
```bash
edge-tts --list-voices | grep zh-CN
```

## 升级到 ElevenLabs（可选）

如果需要更高音质或音色克隆，可以使用 ElevenLabs：

### 1. 安装
```bash
pip install elevenlabs
```

### 2. 配置 API 密钥
```bash
export ELEVEN_API_KEY='your-elevenlabs-api-key'
```

### 3. 修改代码

在 `audio_translator.py` 的 `step3_text_to_speech` 方法中替换为：

```python
from elevenlabs import generate, set_api_key, clone

def step3_text_to_speech_elevenlabs(self, text):
    """使用 ElevenLabs 生成中文语音（支持音色克隆）"""
    set_api_key(os.environ.get("ELEVEN_API_KEY"))

    # 使用克隆的声音
    audio = generate(
        text=text,
        voice="your_cloned_voice_id",  # 或使用预设声音
        model="eleven_multilingual_v2"
    )

    with open(self.audio_output, 'wb') as f:
        f.write(audio)
```

## 常见问题

### Q: Whisper 安装失败？
A: 需要先安装 Rust：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Q: 如何提高翻译质量？
A: 可以修改翻译提示词，添加更多上下文信息

### Q: 支持其他语言吗？
A: 支持！修改 Whisper 的 `--language` 参数和目标翻译语言即可

### Q: 音频太长处理很慢？
A: 可以先用 FFmpeg 切割音频：
```bash
ffmpeg -i long_audio.mp3 -ss 00:00:00 -t 00:05:00 part1.mp3
```

## 开源协议

MIT License

## 参考项目

- [claude_video_translator](https://github.com/wizlijun/claude_video_tranlater)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Edge TTS](https://github.com/rany2/edge-tts)
