# 安装指南

本指南将帮你完成 Audio Translator 的安装配置。

---

## 📋 系统要求

### 基础要求

- **操作系统**: Linux / macOS / Windows (WSL2)
- **Python**: 3.10 或更高版本
- **磁盘空间**: 至少 10 GB

### GPU 支持（可选，用于 IndexTTS）

- **GPU**: NVIDIA GPU（推荐 8GB+ 显存）
- **CUDA**: 12.x
- **显存**:
  - FP32: 8-10 GB
  - FP16: 4-5 GB（推荐）

---

## 🚀 快速安装

### 方案一：基础安装（Edge TTS）

适合快速测试，完全免费。

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd audio-translator

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install anthropic openai edge-tts pydub

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 API 密钥

# 5. 测试
python scripts/basic_translator.py test.mp3
```

---

## 🔥 完整安装（IndexTTS）

推荐方案，支持本地声音克隆。

### 步骤 1: 安装基础依赖

```bash
cd audio-translator
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

### 步骤 2: 安装 IndexTTS

#### 方法 A: 使用 uv (推荐)

```bash
# 1. 安装 uv 包管理器
pip install -U uv

# 2. 进入 IndexTTS 目录
cd models/indextts

# 3. 安装依赖（国内镜像加速）
uv sync --all-extras --default-index "https://mirrors.aliyun.com/pypi/simple"
```

#### 方法 B: 使用 pip

```bash
cd models/indextts

# 安装 PyTorch (CUDA 12.8)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128

# 安装 IndexTTS
pip install -e .
```

### 步骤 3: 下载模型

#### 选项 A: ModelScope (国内推荐)

```bash
# 安装 modelscope 工具
uv tool install modelscope

# 下载模型到 checkpoints 目录
modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints
```

#### 选项 B: HuggingFace

```bash
# 安装 huggingface-cli
uv tool install "huggingface-hub[cli,hf_xet]"

# 下载模型
hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```

**模型文件大小**: 约 6.5 GB
**预计下载时间**:
- 国内 (ModelScope): 5-10 分钟
- 国外 (HuggingFace): 30-60 分钟

### 步骤 4: 验证安装

```bash
# 检查 GPU 支持
cd models/indextts
uv run tools/gpu_check.py

# 启动 Web UI 测试
uv run webui.py
# 访问 http://127.0.0.1:7860

# 简单测试
cd ../..
python tools/test_indextts.py
```

---

## 🌐 API 密钥配置

### 1. 复制配置文件

```bash
cp .env.example .env
```

### 2. 编辑 .env 文件

```bash
# 必需 - Claude API (用于翻译)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# 必需 - OpenAI API (用于 Whisper 语音识别)
OPENAI_API_KEY=sk-your-key-here

# 可选 - ElevenLabs API (云端声音克隆)
ELEVENLABS_API_KEY=your-elevenlabs-key-here

# 可选 - 镜像加速
HF_ENDPOINT=https://hf-mirror.com
```

### 3. 获取 API 密钥

**Claude API:**
1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 创建 API Key

**OpenAI API:**
1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 创建 API Key

**ElevenLabs API (可选):**
1. 访问 https://elevenlabs.io/
2. 注册账号（有免费额度）
3. Profile Settings → API Keys

---

## 🔧 环境特定安装

### Windows (WSL2)

```bash
# 1. 安装 WSL2
wsl --install

# 2. 安装 Python
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip

# 3. 安装 CUDA (如需 GPU 支持)
# 参考: https://docs.nvidia.com/cuda/wsl-user-guide/

# 4. 按正常流程安装
```

### macOS

```bash
# 1. 安装 Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. 安装 Python
brew install python@3.10

# 3. 安装 FFmpeg
brew install ffmpeg

# 4. 按正常流程安装
```

### Ubuntu/Debian

```bash
# 1. 安装系统依赖
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip ffmpeg

# 2. 安装 CUDA (如需 GPU 支持)
# 参考: https://developer.nvidia.com/cuda-downloads

# 3. 按正常流程安装
```

---

## 🐛 常见安装问题

### 问题 1: CUDA 版本不匹配

**症状**: `RuntimeError: CUDA version mismatch`

**解决**:
```bash
# 检查 CUDA 版本
nvidia-smi

# 重新安装匹配的 PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### 问题 2: Git LFS 文件下载失败

**症状**: 模型文件只有几 KB

**解决**:
```bash
# 安装 Git LFS
git lfs install

# 重新拉取大文件
cd models/indextts
git lfs pull
```

### 问题 3: 国内下载速度慢

**解决**:
```bash
# 使用国内镜像
export HF_ENDPOINT="https://hf-mirror.com"

# 使用 ModelScope 下载模型
modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints
```

### 问题 4: Windows 路径问题

**症状**: `FileNotFoundError` 或路径错误

**解决**:
```bash
# 使用 WSL2，避免 Windows 原生路径问题
# 或在代码中使用 pathlib.Path
```

### 问题 5: 虚拟环境激活失败

**解决**:
```bash
# Linux/Mac
source venv/bin/activate

# Windows (原生)
venv\Scripts\activate

# Windows (WSL2)
source venv/bin/activate
```

---

## ✅ 安装验证清单

完成安装后，运行以下检查：

```bash
# 1. Python 版本
python --version  # 应该 >= 3.10

# 2. 依赖包
pip list | grep -E "anthropic|openai|torch"

# 3. GPU 支持 (如需要)
python -c "import torch; print(torch.cuda.is_available())"

# 4. IndexTTS 模型
ls -lh models/indextts/checkpoints/gpt.pth

# 5. 环境变量
echo $ANTHROPIC_API_KEY

# 6. 完整测试
python scripts/basic_translator.py --help
```

---

## 🎓 下一步

- [使用指南](usage.md) - 学习如何使用
- [引擎对比](engines.md) - 选择合适的 TTS 引擎
- [API 参考](api-reference.md) - Python API 文档

---

## 💡 推荐配置

### 最小配置（测试用）

- CPU: 4 核
- 内存: 8 GB
- 磁盘: 2 GB
- TTS: Edge TTS (免费)

### 推荐配置（生产用）

- CPU: 8 核+
- 内存: 16 GB+
- GPU: NVIDIA RTX 3060+ (12GB+)
- 磁盘: 20 GB+
- TTS: IndexTTS (本地)

### 高端配置（大规模）

- CPU: 16 核+
- 内存: 32 GB+
- GPU: NVIDIA RTX 4080+ (16GB+)
- 磁盘: 50 GB+ SSD
- TTS: IndexTTS (本地) + DeepSpeed

---

需要帮助？查看 [常见问题](../README.md#常见问题) 或提交 [Issue](https://github.com/your-repo/issues)。
