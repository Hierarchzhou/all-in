#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import markdown2
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os
import re

def convert_markdown_to_pdf(md_file, pdf_file):
    """将调研报告Markdown文件转换为PDF"""

    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # 处理图片占位符，转换为更美观的HTML
    def replace_image_placeholder(match):
        text = match.group(1)
        if "图片位置" in text:
            lines = text.strip().split('\n')
            title = lines[0].replace('**', '').replace('📌 ', '')
            desc = '\n'.join(lines[1:]) if len(lines) > 1 else ''
            return f'''
            <div class="image-placeholder">
                <div class="image-icon">🖼️</div>
                <div class="image-title">{title}</div>
                <div class="image-desc">{desc}</div>
            </div>
            '''
        return match.group(0)

    # 替换图片占位符
    markdown_content = re.sub(r'> (📌 \*\*图片位置.*?\n(?:> .*\n)*)',
                              replace_image_placeholder,
                              markdown_content,
                              flags=re.MULTILINE)

    # 转换Markdown为HTML
    html_content = markdown2.markdown(
        markdown_content,
        extras=[
            'tables',
            'fenced-code-blocks',
            'header-ids',
            'strike',
            'task_list',
            'break-on-newline'
        ]
    )

    # HTML模板和样式 - 青色主题
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>个人信息管理系统调研报告</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

            /* 基础样式 */
            body {{
                font-family: 'Noto Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif;
                line-height: 1.8;
                color: #2c3e50;
                max-width: 1000px;
                margin: 0 auto;
                padding: 40px 30px;
                background: #fff;
            }}

            /* 标题样式 */
            h1 {{
                color: #00acc1;
                text-align: center;
                font-size: 42px;
                margin-bottom: 10px;
                padding-bottom: 25px;
                border-bottom: 4px solid #00bcd4;
                font-weight: 700;
                letter-spacing: 2px;
            }}

            h1 + h2 {{
                text-align: center;
                color: #0097a7;
                font-size: 20px;
                font-weight: 400;
                margin-top: -10px;
                margin-bottom: 30px;
            }}

            h2 {{
                color: #0097a7;
                font-size: 30px;
                margin-top: 50px;
                margin-bottom: 25px;
                padding-left: 20px;
                border-left: 6px solid #00bcd4;
                background: linear-gradient(90deg, rgba(0,188,212,0.05) 0%, transparent 100%);
                page-break-before: auto;
            }}

            h3 {{
                color: #00838f;
                font-size: 24px;
                margin-top: 30px;
                margin-bottom: 20px;
                padding-left: 10px;
                border-left: 4px solid #4dd0e1;
            }}

            h4 {{
                color: #006064;
                font-size: 20px;
                margin-top: 25px;
                margin-bottom: 15px;
                font-weight: 600;
            }}

            /* 表格样式 */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
                box-shadow: 0 4px 8px rgba(0,188,212,0.12);
                border-radius: 10px;
                overflow: hidden;
                font-size: 14px;
            }}

            th {{
                background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
                color: white;
                padding: 14px 18px;
                text-align: left;
                font-weight: 500;
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
                font-size: 15px;
            }}

            td {{
                padding: 12px 18px;
                border-bottom: 1px solid #e0f2f1;
                background: #fff;
            }}

            tr:nth-child(even) td {{
                background-color: #f0fafb;
            }}

            tr:last-child td {{
                border-bottom: none;
            }}

            /* 引用样式 */
            blockquote {{
                background: #e0f7fa;
                border-left: 5px solid #00acc1;
                margin: 25px 0;
                padding: 18px 25px;
                font-style: italic;
                color: #00838f;
                border-radius: 0 10px 10px 0;
                box-shadow: 0 2px 6px rgba(0,172,193,0.1);
            }}

            blockquote p {{
                margin: 10px 0;
            }}

            /* 列表样式 */
            ul, ol {{
                margin: 20px 0;
                padding-left: 35px;
                line-height: 2.2;
            }}

            li {{
                margin: 12px 0;
                color: #37474f;
            }}

            li strong {{
                color: #00838f;
                font-weight: 600;
            }}

            /* 代码样式 */
            code {{
                background: #e0f7fa;
                padding: 4px 10px;
                border-radius: 5px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                color: #006064;
                font-size: 0.9em;
            }}

            pre {{
                background: #f0f9fa;
                padding: 20px;
                border-radius: 10px;
                overflow-x: auto;
                border: 1px solid #b2dfdb;
                margin: 25px 0;
            }}

            pre code {{
                background: transparent;
                padding: 0;
                color: #004d40;
            }}

            /* 文本样式 */
            strong {{
                color: #00838f;
                font-weight: 600;
            }}

            em {{
                color: #546e7a;
                font-style: italic;
            }}

            a {{
                color: #0288d1;
                text-decoration: none;
                border-bottom: 1px dotted #0288d1;
            }}

            a:hover {{
                color: #0277bd;
                border-bottom-style: solid;
            }}

            /* 分割线 */
            hr {{
                border: none;
                height: 3px;
                background: linear-gradient(to right, transparent, #00bcd4, #00acc1, #00bcd4, transparent);
                margin: 50px 0;
                opacity: 0.6;
            }}

            /* 图片占位符样式 */
            .image-placeholder {{
                background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
                border: 2px dashed #00acc1;
                border-radius: 12px;
                padding: 40px;
                margin: 25px 0;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,172,193,0.1);
            }}

            .image-icon {{
                font-size: 48px;
                margin-bottom: 15px;
            }}

            .image-title {{
                color: #00838f;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 10px;
            }}

            .image-desc {{
                color: #546e7a;
                font-size: 14px;
                line-height: 1.6;
            }}

            /* 特殊容器 */
            .highlight-box {{
                background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
                color: white;
                padding: 25px 30px;
                border-radius: 12px;
                margin: 30px 0;
                box-shadow: 0 6px 12px rgba(0,172,193,0.25);
            }}

            .info-box {{
                background: #e0f7fa;
                border: 2px solid #00acc1;
                padding: 25px 30px;
                border-radius: 12px;
                margin: 30px 0;
            }}

            .warning-box {{
                background: #fff8e1;
                border-left: 5px solid #ffc107;
                padding: 20px 25px;
                margin: 25px 0;
                border-radius: 0 10px 10px 0;
            }}

            /* 页面布局优化 */
            p {{
                margin: 18px 0;
                text-align: justify;
                text-justify: inter-ideograph;
            }}

            /* 打印优化 */
            @media print {{
                body {{
                    font-size: 11pt;
                    padding: 20px;
                }}

                h1 {{
                    font-size: 28pt;
                    page-break-after: avoid;
                }}

                h2 {{
                    font-size: 20pt;
                    page-break-after: avoid;
                    page-break-before: auto;
                }}

                h3 {{
                    font-size: 16pt;
                    page-break-after: avoid;
                }}

                table {{
                    page-break-inside: avoid;
                }}

                .image-placeholder {{
                    page-break-inside: avoid;
                    padding: 20px;
                }}

                pre {{
                    page-break-inside: avoid;
                }}

                blockquote {{
                    page-break-inside: avoid;
                }}
            }}

            /* 目录样式 */
            .toc {{
                background: #f8fafb;
                border: 1px solid #e0f2f1;
                border-radius: 10px;
                padding: 25px;
                margin: 30px 0;
            }}

            .toc h3 {{
                color: #00838f;
                border: none;
                padding: 0;
                margin-top: 0;
            }}

            .toc ul {{
                list-style: none;
                padding-left: 20px;
            }}

            .toc li {{
                margin: 8px 0;
            }}

            /* 页脚样式 */
            .footer {{
                margin-top: 60px;
                padding-top: 30px;
                border-top: 2px solid #e0f2f1;
                text-align: center;
                color: #78909c;
                font-size: 14px;
            }}

            /* 封面样式 */
            .cover {{
                text-align: center;
                padding: 100px 50px;
                page-break-after: always;
            }}

            .cover h1 {{
                font-size: 48px;
                margin-bottom: 30px;
                border: none;
            }}

            .cover .subtitle {{
                font-size: 22px;
                color: #546e7a;
                margin-bottom: 50px;
            }}

            .cover .meta {{
                font-size: 16px;
                color: #78909c;
                line-height: 2;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # 配置字体
    font_config = FontConfiguration()

    # 创建HTML对象并生成PDF
    html = HTML(string=html_template)

    # 生成PDF
    html.write_pdf(
        pdf_file,
        font_config=font_config
    )

    print(f"✅ PDF文件已生成：{pdf_file}")

if __name__ == "__main__":
    # 输入和输出文件路径
    markdown_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/个人信息管理系统调研报告_2025-09-16.md"
    pdf_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/个人信息管理系统调研报告_2025-09-16.pdf"

    # 转换文件
    convert_markdown_to_pdf(markdown_file, pdf_file)