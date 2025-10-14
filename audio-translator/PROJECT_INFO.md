# Audio Translator - 项目信息

**重构完成时间**: 2025-10-11
**版本**: 1.0.0

---

## 📊 项目概览

**Audio Translator** 是一个基于 AI 的音频翻译工具，支持将英文音频翻译为中文音频，并使用声音克隆技术保留原说话者的音色特征。

### 核心功能

- 🎯 **零样本声音克隆** - 使用 IndexTTS-2 保留原音色
- 🌍 **跨语言翻译** - 英文 → 中文
- 🎨 **多引擎支持** - IndexTTS / ElevenLabs / OpenAI / Edge TTS
- ⚡ **GPU 加速** - CUDA 12.x 支持
- 🔧 **高度可配置** - YAML + 环境变量

---

## 📁 项目结构

```
audio-translator/
├── README.md                          # 主文档 ⭐
├── config.yaml                        # 主配置文件 ⚙️
├── requirements.txt                   # Python 依赖
├── .env.example                       # 环境变量示例
├── .gitignore                         # Git 忽略规则
│
├── src/                              # 源代码（未来模块化）
│   ├── core/                         # 核心模块
│   └── engines/                      # TTS 引擎
│
├── scripts/                          # 可执行脚本 🚀
│   ├── basic_translator.py           # 基础版（Edge TTS）
│   ├── api_translator.py             # API 版
│   ├── voice_clone_translator.py     # 云端声音克隆
│   └── indextts_translator.py        # 本地声音克隆 ⭐
│
├── tools/                            # 工具脚本 🛠️
│   ├── test_indextts_simple.py       # IndexTTS 简单测试
│   ├── test_indextts_quick.py        # IndexTTS 快速测试
│   └── generate_chinese_audio.py     # 音频生成工具
│
├── docs/                             # 完整文档 📚
│   ├── installation.md               # 安装指南
│   └── usage.md                      # 使用指南
│
├── archive/                          # 归档文件 📦
│   ├── old_docs/                     # 旧文档
│   └── old_scripts/                  # 旧脚本
│
├── models/                           # 模型目录 📦
│   ├── indextts -> ../../indextts/   # IndexTTS 主模型 (6.5GB)
│   └── checkpoints -> ../../checkpoints/  # HF 缓存模型 (2.8GB)
│
├── outputs/                          # 输出目录
├── temp/                             # 临时文件
└── tests/                            # 测试（待实现）
```

---

## 🎯 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入 API 密钥
# - ANTHROPIC_API_KEY（必需）
# - OPENAI_API_KEY（必需）
```

### 2. 运行测试

```bash
# 基础版（免费）
python scripts/basic_translator.py test.mp3

# IndexTTS 声音克隆（最佳效果）
python scripts/indextts_translator.py test.mp3
```

---

## 🔧 可用脚本

### scripts/basic_translator.py
- **功能**: Edge TTS（免费）
- **优点**: 完全免费，无需 GPU
- **缺点**: 电子音，无声音克隆
- **适用**: 快速测试

### scripts/api_translator.py
- **功能**: API 版本
- **优点**: 支持自定义 API 端点
- **缺点**: 需要 API 密钥
- **适用**: API 集成

### scripts/voice_clone_translator.py
- **功能**: 云端声音克隆
- **支持引擎**: ElevenLabs / OpenAI / Edge
- **优点**: 无需 GPU，高质量
- **缺点**: 需要付费 API
- **适用**: 偶尔使用

### scripts/indextts_translator.py ⭐ 推荐
- **功能**: 本地 IndexTTS 声音克隆
- **优点**: 最佳效果，完全免费
- **缺点**: 需要 GPU（8GB+ 显存）
- **适用**: 大量处理，追求质量

---

## 📚 文档导航

### 核心文档
- [README.md](README.md) - 项目主页，快速开始
- [config.yaml](config.yaml) - 完整配置说明
- [.env.example](.env.example) - 环境变量模板

### 详细指南
- [docs/installation.md](docs/installation.md) - 完整安装指南
- [docs/usage.md](docs/usage.md) - 详细使用说明

### 归档文档
- [archive/old_docs/](archive/old_docs/) - 旧版文档
  - PROJECT_SUMMARY.md - 项目原始总结
  - README_audio_translator.md - 基础版文档
  - README_voice_clone.md - 声音克隆文档
  - indextts_installation_guide.md - IndexTTS 安装

---

## 🔗 外部依赖

### IndexTTS 主模型
- **位置**: `models/indextts/` → `../../indextts/`
- **大小**: 约 6.5 GB
- **来源**: ModelScope / HuggingFace
- **内容**:
  - gpt.pth (3.3GB) - GPT 主模型
  - s2mel.pth (1.2GB) - 声学模型
  - qwen0.6bemo4-merge/ (1.1GB) - Qwen 情感模型
  - 配置文件和词表

### HuggingFace 缓存模型
- **位置**: `models/checkpoints/hf_cache/` → `../../checkpoints/hf_cache/`
- **大小**: 约 2.8 GB
- **来源**: 自动从 HuggingFace 下载
- **内容** (IndexTTS 的辅助模型):
  - **facebook/w2v-bert-2.0** (2.2GB) - Wav2Vec2-BERT 语音特征提取
  - **nvidia/bigvgan_v2** (429MB) - BigVGAN 声码器
  - **amphion/MaskGCT** (169MB) - 语义编解码器
  - **funasr/campplus** (27MB) - 说话人识别

### 模型工作流程
```
参考音频
    ↓
[CAM++ 说话人识别] ← funasr/campplus
    ↓
[Wav2Vec2 特征提取] ← facebook/w2v-bert-2.0
    ↓
[IndexTTS GPT 生成] ← gpt.pth + qwen (主模型)
    ↓
[MaskGCT 语义处理] ← amphion/MaskGCT
    ↓
[BigVGAN 声码器] ← nvidia/bigvgan
    ↓
输出音频
```

---

## ⚙️ 配置文件说明

### .env（环境变量）
```bash
ANTHROPIC_API_KEY=sk-ant-xxx    # Claude API（必需）
OPENAI_API_KEY=sk-xxx           # OpenAI API（必需）
ELEVENLABS_API_KEY=xxx          # ElevenLabs API（可选）
HF_ENDPOINT=https://hf-mirror.com  # HuggingFace 镜像
```

### config.yaml（主配置）
- TTS 引擎配置（4种引擎）
- 语音识别配置（Whisper）
- 翻译配置（Claude）
- 输出配置
- 音频处理配置
- 性能优化配置

---

## 🚀 工作流程

```
英文音频 (podcast.mp3)
    ↓
[Whisper API 语音识别]
    ↓
英文文本 (transcript_en.txt)
    ↓
[Claude API 翻译]
    ↓
中文文本 (transcript_zh.txt)
    ↓
[IndexTTS 声音克隆]
    ↓
中文音频 (podcast_zh.mp3)
```

---

## 📊 性能数据

基于 RTX 4080 16GB GPU：

| 音频时长 | 处理时间 | GPU 占用 | 引擎 |
|---------|---------|---------|------|
| 1 分钟  | ~15 秒  | 4.5 GB  | IndexTTS (FP16) |
| 5 分钟  | ~60 秒  | 4.8 GB  | IndexTTS (FP16) |
| 10 分钟 | ~120 秒 | 5.2 GB  | IndexTTS (FP16) |

---

## 🔄 项目重构历史

### 之前的状态
- ❌ 文件散乱（多个独立脚本）
- ❌ 文档分散（多个 README）
- ❌ 缺少统一配置
- ❌ 项目结构不清晰

### 重构后的改进
- ✅ 清晰的目录结构
- ✅ 统一的配置管理
- ✅ 完整的文档系统
- ✅ 归档旧文件
- ✅ Git 规范化

---

## 🎯 下一步开发

### 待实现功能
- [ ] 实现 src/core/ 核心模块
- [ ] 实现 src/engines/ TTS 引擎封装
- [ ] 添加 Python API 接口
- [ ] 编写单元测试
- [ ] 添加批量处理脚本
- [ ] 实现字幕生成功能
- [ ] 支持更多语言

### 文档待补充
- [ ] docs/engines.md - TTS 引擎详解
- [ ] docs/api-reference.md - API 参考
- [ ] examples/ - 示例代码
- [ ] CONTRIBUTING.md - 贡献指南
- [ ] CHANGELOG.md - 更新日志

---

## 🐛 已知问题

### 当前限制
1. ⚠️ src/ 目录只有结构，未实现代码
2. ⚠️ scripts/ 是独立脚本，未模块化
3. ⚠️ 缺少单元测试
4. ⚠️ 缺少 CLI 统一入口

### 解决方案
- 逐步将 scripts/ 重构为模块化代码
- 实现统一的 CLI 入口（src/cli.py）
- 添加测试覆盖

---

## 📞 联系信息

- 📂 项目位置: `/mnt/c/Users/Administrator/Desktop/all-in/audio-translator`
- 📝 主文档: [README.md](README.md)
- 🐛 问题反馈: GitHub Issues
- 💬 讨论: GitHub Discussions

---

## 📄 许可证

MIT License - 仅供学习和个人使用

**注意事项**:
- ⚠️ 使用声音克隆前需获得授权
- ⚠️ 禁止商业用途
- ⚠️ 遵守各平台使用条款

---

**最后更新**: 2025-10-11
**维护状态**: 活跃开发中
**版本**: 1.0.0
