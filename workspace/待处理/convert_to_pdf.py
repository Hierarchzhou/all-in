#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import markdown2
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os

def convert_markdown_to_pdf(md_file, pdf_file):
    """将Markdown文件转换为PDF"""

    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # 转换Markdown为HTML
    html_content = markdown2.markdown(
        markdown_content,
        extras=[
            'tables',
            'fenced-code-blocks',
            'header-ids',
            'strike',
            'task_list'
        ]
    )

    # HTML模板和样式
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Livehouse 12.26 执行方案</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');

            body {{
                font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
                line-height: 1.8;
                color: #2c3e50;
                max-width: 900px;
                margin: 0 auto;
                padding: 40px 20px;
                background: #fff;
            }}

            h1 {{
                color: #00acc1;
                text-align: center;
                font-size: 36px;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #00bcd4;
                text-shadow: 0 2px 4px rgba(0,172,193,0.1);
            }}

            h2 {{
                color: #0097a7;
                font-size: 28px;
                margin-top: 40px;
                margin-bottom: 20px;
                padding-left: 15px;
                border-left: 5px solid #00bcd4;
                background: linear-gradient(90deg, rgba(0,188,212,0.05) 0%, transparent 100%);
            }}

            h3 {{
                color: #00838f;
                font-size: 22px;
                margin-top: 25px;
                margin-bottom: 15px;
            }}

            h4 {{
                color: #006064;
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
                font-weight: 600;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                box-shadow: 0 4px 6px rgba(0,188,212,0.1);
                border-radius: 8px;
                overflow: hidden;
            }}

            th {{
                background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
                color: white;
                padding: 14px 16px;
                text-align: left;
                font-weight: 500;
                text-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }}

            td {{
                padding: 12px 16px;
                border: 1px solid #e0f2f1;
                background: #fff;
            }}

            tr:nth-child(even) td {{
                background-color: #f0f9fa;
            }}

            tr:hover td {{
                background-color: #e0f7fa;
            }}

            blockquote {{
                background: #e0f7fa;
                border-left: 5px solid #00acc1;
                margin: 20px 0;
                padding: 15px 20px;
                font-style: italic;
                color: #00838f;
                border-radius: 0 8px 8px 0;
            }}

            ul, ol {{
                margin: 15px 0;
                padding-left: 30px;
                line-height: 2;
            }}

            li {{
                margin: 10px 0;
                color: #37474f;
            }}

            li strong {{
                color: #00838f;
            }}

            code {{
                background: #e0f7fa;
                padding: 3px 8px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
                color: #006064;
                font-size: 0.9em;
            }}

            pre {{
                background: #f0f9fa;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                border: 1px solid #b2dfdb;
            }}

            strong {{
                color: #00838f;
                font-weight: 600;
            }}

            em {{
                color: #546e7a;
                font-style: italic;
            }}

            hr {{
                border: none;
                height: 2px;
                background: linear-gradient(to right, #00bcd4, #00acc1, #00bcd4);
                margin: 40px 0;
                opacity: 0.6;
            }}

            /* 特殊样式 */
            .highlight {{
                background: linear-gradient(135deg, #00bcd4 0%, #00acc1 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                box-shadow: 0 4px 6px rgba(0,172,193,0.2);
            }}

            .info-box {{
                background: #e0f7fa;
                border: 2px solid #00acc1;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }}

            .warning-box {{
                background: #e1f5fe;
                border-left: 5px solid #0288d1;
                padding: 20px;
                margin: 20px 0;
                border-radius: 0 8px 8px 0;
            }}

            /* 打印优化 */
            @media print {{
                body {{
                    font-size: 12pt;
                }}

                h1 {{
                    font-size: 24pt;
                }}

                h2 {{
                    font-size: 18pt;
                    page-break-before: auto;
                }}

                table {{
                    page-break-inside: avoid;
                }}
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
    markdown_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/Livehouse执行方案_2025-09-16_美化版.md"
    pdf_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/Livehouse执行方案_2025-09-16_青色主题.pdf"

    # 转换文件
    convert_markdown_to_pdf(markdown_file, pdf_file)