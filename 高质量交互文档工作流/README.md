# 高质量交互文档工作流

## 📁 文件夹说明

本文件夹包含完整的高质量交互文档生成工作流，可以将任意原始文档转换为专业的交互式文档。

---

## 📋 文件清单

### 1. 核心文档
- **`高质量交互文档工作流模板.md`** - 完整的工作流程文档和使用指南

### 2. 生成脚本
- **`convert_research_to_pdf.py`** - PDF生成脚本（青色主题）
- **`convert_to_interactive_html.py`** - 通用HTML生成脚本（青色主题）
- **`convert_livehouse_to_html.py`** - Livehouse专用HTML生成脚本（月光主题）

---

## 🚀 快速使用

### 步骤1：准备Markdown文件
将原始文档整理为标准化的Markdown格式。

### 步骤2：生成PDF
```bash
python3 convert_research_to_pdf.py
```

### 步骤3：生成交互式HTML
```bash
# 通用青色主题
python3 convert_to_interactive_html.py

# 或者使用Livehouse月光主题
python3 convert_livehouse_to_html.py
```

---

## 🎨 主题特色

### 青色主题（通用）
- 🌊 青色系渐变
- 💎 现代商务风格
- 📊 适合调研报告、技术文档

### 月光主题（Livehouse专用）
- 🌙 紫色系渐变
- ⭐ 星空背景动画
- 🎵 适合创意项目、娱乐活动

---

## 📖 详细使用说明

请参考 `高质量交互文档工作流模板.md` 获取：
- 完整工作流程
- 标准提示词模板
- 技术实现细节
- 质量检查清单
- 常见问题解答

---

## 🔧 环境依赖

```bash
pip install markdown2 weasyprint
```

---

## 📞 技术支持

使用标准提示词让Claude按工作流处理您的文档：

```markdown
请使用高质量交互文档工作流处理这个文件：[文件路径]
要求：标准化格式、准确引用、生成PDF和交互式HTML版本
```

---

*Created: 2025-09-16*
*Version: 1.0*