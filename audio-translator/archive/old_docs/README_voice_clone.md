# 音频翻译工具 - 声音克隆版

## 功能特点

✨ **保留原始音色** - 使用声音克隆技术，让中文翻译保持原说话者的音色特征
🌍 **跨语言翻译** - 英文音频 → 中文音频，声音风格一致
🎯 **多引擎支持** - 支持 ElevenLabs、OpenAI、Edge TTS 三种引擎

## 工作流程

```
英文音频 → [Whisper识别] → 英文文本 → [Claude翻译] → 中文文本 → [声音克隆TTS] → 中文音频
```

## TTS 引擎对比

| 引擎 | 声音克隆 | 音质 | 成本 | 推荐度 |
|------|---------|------|------|--------|
| **ElevenLabs** | ✅ 支持 | ⭐⭐⭐⭐⭐ | $1/1000字符 | ⭐⭐⭐⭐⭐ |
| **OpenAI TTS** | ❌ 固定音色 | ⭐⭐⭐⭐ | $0.015/1000字符 | ⭐⭐⭐ |
| **Edge TTS** | ❌ 固定音色 | ⭐⭐ | 免费 | ⭐⭐ |

## 安装依赖

```bash
# 确保在虚拟环境中
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install openai anthropic requests edge-tts
```

## 环境变量配置

```bash
# 必需 - Claude API (用于翻译)
export ANTHROPIC_API_KEY='your-claude-api-key'

# 必需 - OpenAI API (用于Whisper语音识别)
export OPENAI_API_KEY='your-openai-api-key'

# 可选 - ElevenLabs API (用于声音克隆，强烈推荐)
export ELEVENLABS_API_KEY='your-elevenlabs-api-key'

# 可选 - 自定义Claude API地址
export ANTHROPIC_BASE_URL='https://your-custom-api.com/claude'
```

## 获取 ElevenLabs API Key

1. 访问 [ElevenLabs](https://elevenlabs.io/)
2. 注册账号（有免费额度）
3. 进入 Profile Settings → API Keys
4. 创建新的 API Key

**免费额度**：每月 10,000 字符（约3-5分钟音频）

## 使用方法

### 基础用法（使用 ElevenLabs 声音克隆）

```bash
python audio_translator_voice_clone.py podcast.mp3
```

### 指定 TTS 引擎

```bash
# 使用 ElevenLabs（推荐，效果最好）
python audio_translator_voice_clone.py podcast.mp3 elevenlabs

# 使用 OpenAI TTS（固定音色但音质好）
python audio_translator_voice_clone.py podcast.mp3 openai

# 使用 Edge TTS（免费但电子音）
python audio_translator_voice_clone.py podcast.mp3 edge
```

## 输出文件

所有输出文件保存在 `<音频名>_voice_clone/` 目录：

```
podcast_voice_clone/
├── transcript_en.txt      # 英文转录
├── transcript_zh.txt      # 中文翻译
└── podcast_zh.mp3         # 中文音频（保留原音色）
```

## 示例效果对比

### 使用 Edge TTS（旧版）
- ❌ 电子合成音
- ❌ 无个性化音色
- ✅ 免费

### 使用 ElevenLabs 声音克隆（新版）
- ✅ 保留原说话者音色特征
- ✅ 自然真实的语音
- ✅ 跨语言音色迁移
- ⚠️ 需要付费API（有免费额度）

## 注意事项

1. **音频质量**：原音频质量越好，克隆效果越好
2. **音频时长**：
   - Whisper API 限制：25MB 以内
   - 建议使用 3-30 秒的清晰人声片段进行克隆
3. **成本控制**：
   - ElevenLabs 按字符收费
   - 建议先测试短音频
4. **隐私保护**：声音克隆功能仅用于个人学习和授权使用

## 快速测试

```bash
# 1. 准备一个英文音频文件（建议10-30秒）
# 2. 设置环境变量
export ANTHROPIC_API_KEY='your-key'
export OPENAI_API_KEY='your-key'
export ELEVENLABS_API_KEY='your-key'

# 3. 运行测试
python audio_translator_voice_clone.py test.mp3 elevenlabs

# 4. 对比效果
# 原音频: test.mp3
# 新音频: test_voice_clone/test_zh.mp3
```

## 故障排查

### 问题：Whisper 识别失败
```bash
# 检查文件大小
ls -lh podcast.mp3

# 如果超过25MB，压缩音频
ffmpeg -i podcast.mp3 -ar 16000 -ac 1 podcast_compressed.mp3
```

### 问题：ElevenLabs API 调用失败
```bash
# 检查 API key 是否正确
echo $ELEVENLABS_API_KEY

# 检查配额
curl https://api.elevenlabs.io/v1/user \
  -H "xi-api-key: $ELEVENLABS_API_KEY"
```

### 问题：声音克隆效果不好
- 确保原音频人声清晰，背景噪音少
- 尝试使用更长的音频片段（10-30秒最佳）
- 调整 `voice_settings` 参数（在代码中）

## 高级功能

### 批量处理

```bash
# 创建批处理脚本
for file in *.mp3; do
    python audio_translator_voice_clone.py "$file" elevenlabs
done
```

### 自定义翻译风格

修改脚本中的 `step2_translate()` 函数的 prompt，例如：

```python
prompt = f"""请将以下英文翻译成中文。要求：
1. 使用专业术语
2. 保持学术风格
3. 适合播客朗读

英文原文：
{text}"""
```

## 相关资源

- [ElevenLabs 文档](https://elevenlabs.io/docs)
- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text)
- [Claude API](https://docs.anthropic.com/)

## 许可证

仅供个人学习和授权使用。使用声音克隆功能前，请确保已获得相关授权。
