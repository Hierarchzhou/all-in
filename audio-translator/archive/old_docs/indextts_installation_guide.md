# IndexTTS 手动安装指南

## 当前状态
- ✅ IndexTTS 代码已克隆到: `/mnt/c/Users/Administrator/Desktop/all-in/indextts`
- ⏳ 需要下载模型文件和依赖包

## 方案一：自动安装（推荐但较慢）

在 WSL 中运行以下命令，让它在后台慢慢下载：

```bash
cd /mnt/c/Users/Administrator/Desktop/all-in/indextts

# 使用国内镜像加速
/mnt/c/Users/Administrator/Desktop/all-in/venv/bin/uv sync --all-extras \
  --default-index "https://mirrors.aliyun.com/pypi/simple"
```

预计需要 20-30 分钟。

## 方案二：手动下载模型（更快）

### 步骤 1: 下载 IndexTTS-2 模型

**选项 A - HuggingFace（推荐）**

访问：https://huggingface.co/IndexTeam/IndexTTS-2/tree/main

需要下载的文件（放到 `indextts/checkpoints/` 目录）：
```
checkpoints/
├── config.yaml
├── model.pth
├── vocos_checkpoint_hificodec.pth
├── pinyin.vocab
└── (其他配置文件)
```

你可以：
1. 用浏览器直接下载
2. 或使用 Git LFS:
   ```bash
   cd /mnt/c/Users/Administrator/Desktop/all-in/indextts

   # 如果还没安装 git-lfs
   git lfs install

   # 下载模型到 checkpoints 目录
   git clone https://huggingface.co/IndexTeam/IndexTTS-2 checkpoints
   ```

**选项 B - ModelScope（国内镜像，更快）**

访问：https://modelscope.cn/models/IndexTeam/IndexTTS-2/files

直接下载文件，放到 `C:\Users\Administrator\Desktop\all-in\indextts\checkpoints\` 目录

### 步骤 2: 安装 Python 依赖

如果模型已下载，依赖安装会快很多：

```bash
cd /mnt/c/Users/Administrator/Desktop/all-in/indextts

# 继续之前中断的安装
/mnt/c/Users/Administrator/Desktop/all-in/venv/bin/uv sync --all-extras \
  --default-index "https://mirrors.aliyun.com/pypi/simple"
```

## 方案三：使用现有项目的 IndexTTS

如果你之前的 `claude_video_tranlater` 项目已经配置好了 IndexTTS，可以直接复用：

```bash
# 检查是否已有 indextts 目录
ls /mnt/c/Users/Administrator/Desktop/all-in/workspace/待处理/claude_video_tranlater/indextts

# 检查是否已有模型文件
ls /mnt/c/Users/Administrator/Desktop/all-in/workspace/待处理/claude_video_tranlater/checkpoints
```

如果有，直接复制过来：
```bash
cp -r /mnt/c/Users/Administrator/Desktop/all-in/workspace/待处理/claude_video_tranlater/indextts \
      /mnt/c/Users/Administrator/Desktop/all-in/

cp -r /mnt/c/Users/Administrator/Desktop/all-in/workspace/待处理/claude_video_tranlater/checkpoints \
      /mnt/c/Users/Administrator/Desktop/all-in/indextts/
```

## 验证安装

安装完成后，测试一下：

```bash
cd /mnt/c/Users/Administrator/Desktop/all-in/indextts

# 检查 GPU
/mnt/c/Users/Administrator/Desktop/all-in/venv/bin/uv run tools/gpu_check.py

# 启动 Web UI 测试
/mnt/c/Users/Administrator/Desktop/all-in/venv/bin/uv run webui.py
```

然后访问 http://127.0.0.1:7860

## 所需磁盘空间

- IndexTTS 代码: ~50MB
- Python 依赖: ~3GB
- 模型文件: ~2-3GB
- **总计: 约 6GB**

## 下一步

安装完成后，我会帮你创建集成 IndexTTS 的音频翻译脚本。

---

## 当前最快的方式

**推荐顺序**：
1. 先检查 claude_video_tranlater 是否已有 IndexTTS（最快）
2. 如果没有，从 ModelScope 下载模型（国内快）
3. 然后安装依赖

告诉我你选择哪个方案，我继续帮你！
