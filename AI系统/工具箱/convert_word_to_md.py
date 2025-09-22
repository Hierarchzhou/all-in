#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
from docx import Document
import sys

def extract_text_from_docx(file_path):
    """从Word文档提取文本内容"""
    try:
        doc = Document(file_path)
        content = []

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                # 检测是否是标题（通常标题较短且不包含太多标点）
                if len(text) < 50 and not '。' in text:
                    content.append(f"## {text}")
                else:
                    content.append(text)
                content.append("")  # 添加空行

        return "\n".join(content)
    except Exception as e:
        print(f"读取文件 {file_path} 失败: {e}")
        return None

def get_main_theme(content):
    """从内容中提取主题（取前100个字符中的关键内容）"""
    # 移除markdown标记
    clean_content = re.sub(r'#+ ', '', content)
    # 取第一行作为主题
    first_line = clean_content.split('\n')[0] if clean_content else ""
    # 限制长度
    theme = first_line[:30] if len(first_line) > 30 else first_line
    # 清理特殊字符
    theme = re.sub(r'[^\w\s\u4e00-\u9fff]', '', theme)
    return theme.strip()

def extract_date_from_filename(filename):
    """从文件名中提取日期"""
    # 匹配 2025-09-15 或 2025-09-1500-15-33 等格式
    date_pattern = r'(\d{4})-(\d{2})-(\d{2})'
    match = re.search(date_pattern, filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    # 如果没有日期，返回标记
    return "待补充日期"

def convert_word_to_markdown(input_dir, output_dir):
    """批量转换Word文档为Markdown"""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    docx_files = [f for f in os.listdir(input_dir) if f.endswith('.docx')]

    print(f"找到 {len(docx_files)} 个Word文档")
    print("-" * 50)

    converted_count = 0

    for docx_file in docx_files:
        input_path = os.path.join(input_dir, docx_file)

        # 提取文档内容
        content = extract_text_from_docx(input_path)
        if not content:
            continue

        # 获取主题
        theme = get_main_theme(content)
        if not theme:
            # 如果无法从内容提取主题，使用文件名
            theme = docx_file.replace('.docx', '').replace('微信', '').strip()
            theme = re.sub(r'[\d\-\s]+', '', theme)  # 移除数字和横线

        # 获取日期
        date = extract_date_from_filename(docx_file)

        # 生成新文件名：主题_日期.md
        new_filename = f"{theme}_{date}.md"
        # 清理文件名中的特殊字符
        new_filename = re.sub(r'[<>:"/\\|?*]', '_', new_filename)

        output_path = os.path.join(output_dir, new_filename)

        # 添加文档元数据
        markdown_content = f"""# {theme}

**日期**: {date}
**原始文件**: {docx_file}

---

{content}
"""

        # 写入Markdown文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✅ 转换成功: {docx_file}")
            print(f"   → {new_filename}")
            converted_count += 1
        except Exception as e:
            print(f"❌ 写入失败: {docx_file}")
            print(f"   错误: {e}")

        print()

    print("-" * 50)
    print(f"转换完成！共转换 {converted_count}/{len(docx_files)} 个文档")

if __name__ == "__main__":
    input_dir = "待处理"
    output_dir = "06-待整理文档"

    convert_word_to_markdown(input_dir, output_dir)