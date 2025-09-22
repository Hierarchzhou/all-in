#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import markdown2
import re
import os

def create_livehouse_interactive_html(md_file, html_file):
    """创建Livehouse执行方案的交互式HTML版本"""

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
            'task_list',
            'break-on-newline',
            'footnotes'
        ]
    )

    # 创建Livehouse主题的交互式HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Livehouse 12.26 执行方案 - 交互版</title>

    <!-- 字体 -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">

    <!-- 图标 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {{
            /* Livehouse主题色彩 - 月光系列 */
            --primary-color: #6366f1;        /* 深紫色 - 夜空色 */
            --primary-dark: #4f46e5;         /* 更深的紫色 */
            --primary-light: #a5b4fc;        /* 浅紫色 - 月光色 */
            --secondary-color: #8b5cf6;      /* 紫罗兰色 */
            --accent-color: #c084fc;         /* 浅紫色强调色 */
            --gold-color: #fbbf24;           /* 金色 - 月光色 */
            --text-primary: #1e1b4b;         /* 深蓝紫色 */
            --text-secondary: #64748b;       /* 灰蓝色 */
            --bg-primary: #ffffff;           /* 白色背景 */
            --bg-secondary: #f8fafc;         /* 浅灰背景 */
            --bg-accent: #f1f5f9;           /* 紫色渐变背景 */
            --border-color: #e2e8f0;         /* 边框色 */
            --shadow-sm: 0 2px 4px rgba(99,102,241,0.1);
            --shadow-md: 0 4px 8px rgba(99,102,241,0.15);
            --shadow-lg: 0 8px 16px rgba(99,102,241,0.2);
            --sidebar-width: 320px;
        }}

        /* 深色模式 - 夜空主题 */
        [data-theme="dark"] {{
            --primary-color: #a5b4fc;
            --primary-dark: #8b5cf6;
            --primary-light: #c084fc;
            --secondary-color: #8b5cf6;
            --accent-color: #fbbf24;
            --gold-color: #f59e0b;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --bg-primary: #0f0f23;          /* 深夜蓝 */
            --bg-secondary: #1e1b4b;        /* 夜空紫 */
            --bg-accent: #312e81;           /* 深紫色 */
            --border-color: #475569;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 8px rgba(0,0,0,0.4);
            --shadow-lg: 0 8px 16px rgba(0,0,0,0.5);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', 'Noto Sans SC', sans-serif;
            line-height: 1.8;
            color: var(--text-primary);
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            transition: all 0.3s ease;
            overflow-x: hidden;
            min-height: 100vh;
        }}

        /* 星空背景效果 */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                radial-gradient(2px 2px at 20px 30px, var(--accent-color), transparent),
                radial-gradient(2px 2px at 40px 70px, var(--primary-light), transparent),
                radial-gradient(1px 1px at 90px 40px, var(--gold-color), transparent),
                radial-gradient(1px 1px at 130px 80px, var(--primary-color), transparent),
                radial-gradient(2px 2px at 160px 30px, var(--accent-color), transparent);
            background-repeat: repeat;
            background-size: 200px 100px;
            opacity: 0.1;
            z-index: -1;
            animation: starfield 20s linear infinite;
        }}

        @keyframes starfield {{
            from {{ transform: translateY(0); }}
            to {{ transform: translateY(-100px); }}
        }}

        /* 加载动画 - 月亮主题 */
        .loader {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            transition: opacity 0.5s;
        }}

        .loader.hidden {{
            opacity: 0;
            pointer-events: none;
        }}

        .loader-content {{
            text-align: center;
        }}

        .moon {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, var(--gold-color) 0%, var(--accent-color) 100%);
            border-radius: 50%;
            position: relative;
            animation: moonGlow 2s ease-in-out infinite alternate;
            margin: 0 auto 20px;
        }}

        .moon::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 120%;
            height: 120%;
            background: radial-gradient(circle, var(--primary-light) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            opacity: 0.6;
            animation: moonHalo 3s linear infinite;
        }}

        @keyframes moonGlow {{
            0% {{ box-shadow: 0 0 20px var(--gold-color); }}
            100% {{ box-shadow: 0 0 40px var(--primary-color), 0 0 60px var(--accent-color); }}
        }}

        @keyframes moonHalo {{
            0% {{ transform: translate(-50%, -50%) rotate(0deg) scale(1); }}
            100% {{ transform: translate(-50%, -50%) rotate(360deg) scale(1.1); }}
        }}

        .loader-text {{
            color: var(--primary-color);
            font-size: 16px;
            font-weight: 500;
        }}

        /* 顶部导航栏 */
        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 70px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            padding: 0 30px;
            z-index: 1000;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
        }}

        [data-theme="dark"] .navbar {{
            background: rgba(15, 15, 35, 0.95);
        }}

        .navbar.scrolled {{
            box-shadow: var(--shadow-md);
            height: 60px;
        }}

        .navbar-brand {{
            font-size: 24px;
            font-weight: 700;
            color: var(--primary-color);
            text-decoration: none;
            margin-left: 50px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .navbar-brand::before {{
            content: '🌙';
            font-size: 28px;
            animation: rotate 10s linear infinite;
        }}

        @keyframes rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}

        .navbar-subtitle {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-left: 10px;
        }}

        .navbar-actions {{
            margin-left: auto;
            display: flex;
            gap: 15px;
        }}

        .navbar-btn {{
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 18px;
            cursor: pointer;
            padding: 10px;
            border-radius: 12px;
            transition: all 0.3s;
            position: relative;
        }}

        .navbar-btn:hover {{
            background: var(--bg-accent);
            color: var(--primary-color);
            transform: translateY(-2px);
        }}

        .navbar-btn:active {{
            transform: translateY(0);
        }}

        /* 侧边栏 */
        .sidebar {{
            position: fixed;
            top: 70px;
            left: 0;
            width: var(--sidebar-width);
            height: calc(100vh - 70px);
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 30px 20px;
            transform: translateX(0);
            transition: transform 0.3s ease;
            z-index: 999;
        }}

        [data-theme="dark"] .sidebar {{
            background: rgba(30, 27, 75, 0.95);
        }}

        .sidebar.collapsed {{
            transform: translateX(-100%);
        }}

        .sidebar-toggle {{
            position: fixed;
            top: 85px;
            left: 15px;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            justify-content: center;
            align-items: center;
            font-size: 20px;
            box-shadow: var(--shadow-lg);
            z-index: 998;
            transition: all 0.3s;
        }}

        .sidebar-toggle:hover {{
            transform: scale(1.1);
            box-shadow: 0 8px 20px rgba(99,102,241,0.3);
        }}

        .sidebar-toggle.active {{
            left: calc(var(--sidebar-width) - 25px);
        }}

        /* 目录样式 */
        .toc-title {{
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--primary-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .toc-title::before {{
            content: '📋';
            font-size: 20px;
        }}

        .toc-list {{
            list-style: none;
        }}

        .toc-item {{
            margin: 8px 0;
        }}

        .toc-link {{
            color: var(--text-secondary);
            text-decoration: none;
            padding: 12px 15px;
            display: block;
            border-radius: 12px;
            transition: all 0.3s;
            font-size: 14px;
            position: relative;
            overflow: hidden;
        }}

        .toc-link::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, var(--primary-light), transparent);
            transition: left 0.6s;
        }}

        .toc-link:hover {{
            background: var(--bg-accent);
            color: var(--primary-color);
            padding-left: 25px;
            transform: translateX(5px);
        }}

        .toc-link:hover::before {{
            left: 100%;
        }}

        .toc-link.active {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            font-weight: 500;
        }}

        .toc-list .toc-list {{
            margin-left: 20px;
            border-left: 2px solid var(--primary-light);
            padding-left: 10px;
        }}

        .toc-list .toc-list .toc-link {{
            font-size: 13px;
            padding: 8px 12px;
        }}

        /* 主内容区 */
        .main-container {{
            margin-left: var(--sidebar-width);
            margin-top: 70px;
            padding: 50px 40px;
            max-width: 1200px;
            transition: margin-left 0.3s ease;
            position: relative;
        }}

        .main-container.full-width {{
            margin-left: 0;
        }}

        /* 内容样式 */
        h1 {{
            color: var(--primary-color);
            font-size: 48px;
            margin-bottom: 20px;
            padding-bottom: 25px;
            border-bottom: 3px solid var(--gold-color);
            animation: fadeInUp 0.8s ease;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        h1 + h2 {{
            color: var(--text-secondary);
            font-size: 20px;
            font-weight: 400;
            margin-top: -10px;
            margin-bottom: 40px;
            text-align: center;
        }}

        h2 {{
            color: var(--primary-dark);
            font-size: 32px;
            margin-top: 50px;
            margin-bottom: 25px;
            padding: 20px 0 20px 25px;
            border-left: 5px solid var(--gold-color);
            background: linear-gradient(90deg, rgba(99,102,241,0.05) 0%, transparent 100%);
            border-radius: 0 15px 15px 0;
            scroll-margin-top: 100px;
            animation: fadeInLeft 0.6s ease;
            position: relative;
        }}

        h2::before {{
            content: '';
            position: absolute;
            left: -5px;
            top: 0;
            width: 5px;
            height: 100%;
            background: linear-gradient(180deg, var(--gold-color), var(--primary-color));
            border-radius: 3px;
        }}

        h3 {{
            color: var(--primary-dark);
            font-size: 24px;
            margin-top: 35px;
            margin-bottom: 20px;
            scroll-margin-top: 100px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        h3::before {{
            content: '▶';
            color: var(--gold-color);
            font-size: 16px;
        }}

        h4 {{
            color: var(--text-primary);
            font-size: 20px;
            margin-top: 30px;
            margin-bottom: 15px;
            font-weight: 600;
        }}

        /* 段落和文本 */
        p {{
            margin: 20px 0;
            text-align: justify;
            line-height: 1.8;
        }}

        strong {{
            color: var(--primary-dark);
            font-weight: 600;
            background: linear-gradient(135deg, var(--primary-light), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        em {{
            color: var(--text-secondary);
            font-style: italic;
        }}

        /* 链接 */
        a {{
            color: var(--primary-color);
            text-decoration: none;
            border-bottom: 1px dotted var(--primary-color);
            transition: all 0.3s;
            position: relative;
        }}

        a:hover {{
            color: var(--primary-dark);
            border-bottom-style: solid;
            text-shadow: 0 0 8px var(--primary-light);
        }}

        /* 列表 */
        ul, ol {{
            margin: 25px 0;
            padding-left: 35px;
        }}

        li {{
            margin: 15px 0;
            position: relative;
        }}

        ul li::marker {{
            color: var(--gold-color);
        }}

        /* 引用块 */
        blockquote {{
            background: linear-gradient(135deg, var(--bg-accent) 0%, rgba(99,102,241,0.05) 100%);
            border-left: 5px solid var(--primary-color);
            margin: 30px 0;
            padding: 25px 30px;
            border-radius: 0 15px 15px 0;
            position: relative;
            overflow: hidden;
        }}

        blockquote::before {{
            content: '"';
            position: absolute;
            top: -10px;
            left: 15px;
            font-size: 100px;
            color: var(--primary-light);
            opacity: 0.2;
            font-family: serif;
        }}

        blockquote::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100%;
            background: linear-gradient(90deg, transparent, var(--primary-light));
            opacity: 0.1;
        }}

        /* 表格 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            background: var(--bg-primary);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-color);
        }}

        th {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            text-align: left;
            font-weight: 500;
            font-size: 16px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}

        td {{
            padding: 18px 20px;
            border-bottom: 1px solid var(--border-color);
            transition: all 0.3s;
        }}

        tr:hover td {{
            background: var(--bg-accent);
            transform: scale(1.01);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        /* 代码块 */
        code {{
            background: var(--bg-accent);
            padding: 4px 12px;
            border-radius: 8px;
            font-family: 'Monaco', 'Courier New', monospace;
            color: var(--primary-dark);
            font-size: 0.9em;
            border: 1px solid var(--border-color);
        }}

        pre {{
            background: var(--bg-secondary);
            padding: 25px;
            border-radius: 15px;
            overflow-x: auto;
            margin: 25px 0;
            border: 1px solid var(--border-color);
            position: relative;
            box-shadow: var(--shadow-sm);
        }}

        pre code {{
            background: transparent;
            padding: 0;
            color: var(--text-primary);
            border: none;
        }}

        /* 任务列表 */
        .task-list-item {{
            list-style: none;
            margin: 15px 0;
            position: relative;
            padding-left: 35px;
        }}

        .task-list-item input[type="checkbox"] {{
            position: absolute;
            left: 0;
            top: 5px;
            transform: scale(1.2);
            accent-color: var(--primary-color);
        }}

        .task-list-item input[type="checkbox"]:checked + label {{
            text-decoration: line-through;
            color: var(--text-secondary);
        }}

        /* 复制按钮 */
        .code-copy-btn {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.3s;
        }}

        pre:hover .code-copy-btn {{
            opacity: 1;
        }}

        .code-copy-btn:hover {{
            transform: scale(1.05);
        }}

        /* 分割线 */
        hr {{
            border: none;
            height: 3px;
            background: linear-gradient(to right, transparent, var(--gold-color), var(--primary-color), var(--gold-color), transparent);
            margin: 50px 0;
            border-radius: 3px;
        }}

        /* 进度条 */
        .progress-bar {{
            position: fixed;
            top: 70px;
            left: 0;
            width: 0%;
            height: 4px;
            background: linear-gradient(90deg, var(--gold-color), var(--primary-color), var(--secondary-color));
            z-index: 1001;
            transition: width 0.3s ease;
        }}

        /* 返回顶部按钮 */
        .back-to-top {{
            position: fixed;
            bottom: 40px;
            right: 40px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            font-size: 24px;
            box-shadow: var(--shadow-lg);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s;
            z-index: 999;
        }}

        .back-to-top.visible {{
            opacity: 1;
            pointer-events: all;
        }}

        .back-to-top:hover {{
            transform: translateY(-5px) scale(1.1);
            box-shadow: 0 12px 25px rgba(99,102,241,0.4);
        }}

        /* 搜索框 */
        .search-container {{
            position: fixed;
            top: 80px;
            right: 30px;
            width: 350px;
            z-index: 999;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s;
        }}

        .search-container.active {{
            opacity: 1;
            pointer-events: all;
        }}

        .search-input {{
            width: 100%;
            padding: 15px 25px;
            border: 2px solid var(--primary-color);
            border-radius: 30px;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.95);
            color: var(--text-primary);
            outline: none;
            backdrop-filter: blur(20px);
            box-shadow: var(--shadow-md);
        }}

        [data-theme="dark"] .search-input {{
            background: rgba(30, 27, 75, 0.95);
        }}

        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 15px;
            margin-top: 10px;
            max-height: 400px;
            overflow-y: auto;
            box-shadow: var(--shadow-lg);
        }}

        [data-theme="dark"] .search-results {{
            background: rgba(30, 27, 75, 0.95);
        }}

        .search-result-item {{
            padding: 15px 25px;
            cursor: pointer;
            transition: background 0.3s;
            border-bottom: 1px solid var(--border-color);
        }}

        .search-result-item:last-child {{
            border-bottom: none;
        }}

        .search-result-item:hover {{
            background: var(--bg-accent);
        }}

        /* 动画 */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes fadeInLeft {{
            from {{
                opacity: 0;
                transform: translateX(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        /* 响应式设计 */
        @media (max-width: 1024px) {{
            .sidebar {{
                transform: translateX(-100%);
            }}

            .sidebar.active {{
                transform: translateX(0);
            }}

            .sidebar-toggle {{
                display: flex;
            }}

            .main-container {{
                margin-left: 0;
                padding: 40px 25px;
            }}

            .navbar-brand {{
                margin-left: 70px;
            }}

            .search-container {{
                width: 300px;
                right: 20px;
            }}
        }}

        @media (max-width: 640px) {{
            h1 {{
                font-size: 36px;
            }}

            h2 {{
                font-size: 28px;
            }}

            h3 {{
                font-size: 22px;
            }}

            .main-container {{
                padding: 30px 20px;
            }}

            .navbar {{
                padding: 0 20px;
            }}

            .navbar-brand {{
                font-size: 20px;
                margin-left: 60px;
            }}

            table {{
                font-size: 14px;
            }}

            th, td {{
                padding: 12px 15px;
            }}

            .search-container {{
                width: calc(100% - 40px);
                right: 20px;
            }}
        }}

        /* 打印样式 */
        @media print {{
            .navbar, .sidebar, .sidebar-toggle, .back-to-top, .search-container, .progress-bar {{
                display: none !important;
            }}

            .main-container {{
                margin: 0 !important;
                padding: 20px !important;
            }}

            body {{
                font-size: 12pt;
                background: white !important;
            }}

            body::before {{
                display: none !important;
            }}

            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}

            table, blockquote, pre {{
                page-break-inside: avoid;
            }}
        }}

        /* 特殊效果 */
        .highlight-card {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            border-radius: 20px;
            margin: 30px 0;
            box-shadow: var(--shadow-lg);
            position: relative;
            overflow: hidden;
        }}

        .highlight-card::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: shimmer 3s linear infinite;
        }}

        @keyframes shimmer {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <!-- 加载动画 -->
    <div class="loader" id="loader">
        <div class="loader-content">
            <div class="moon"></div>
            <div class="loader-text">加载中...</div>
        </div>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar" id="progressBar"></div>

    <!-- 顶部导航 -->
    <nav class="navbar" id="navbar">
        <a href="#" class="navbar-brand">
            Livehouse 12.26
            <span class="navbar-subtitle">执行方案</span>
        </a>
        <div class="navbar-actions">
            <button class="navbar-btn" id="searchBtn" title="搜索">
                <i class="fas fa-search"></i>
            </button>
            <button class="navbar-btn" id="themeBtn" title="切换主题">
                <i class="fas fa-moon"></i>
            </button>
            <button class="navbar-btn" id="printBtn" title="打印">
                <i class="fas fa-print"></i>
            </button>
            <button class="navbar-btn" id="downloadBtn" title="下载">
                <i class="fas fa-download"></i>
            </button>
        </div>
    </nav>

    <!-- 搜索框 -->
    <div class="search-container" id="searchContainer">
        <input type="text" class="search-input" placeholder="搜索方案内容..." id="searchInput">
        <div class="search-results" id="searchResults"></div>
    </div>

    <!-- 侧边栏切换按钮 -->
    <button class="sidebar-toggle" id="sidebarToggle">
        <i class="fas fa-bars"></i>
    </button>

    <!-- 侧边栏 -->
    <aside class="sidebar" id="sidebar">
        <div class="toc-title">项目导航</div>
        <nav class="toc-nav" id="tocNav"></nav>
    </aside>

    <!-- 主内容 -->
    <main class="main-container" id="mainContent">
        {html_content}
    </main>

    <!-- 返回顶部 -->
    <button class="back-to-top" id="backToTop">
        <i class="fas fa-arrow-up"></i>
    </button>

    <script>
        // 初始化
        document.addEventListener('DOMContentLoaded', function() {{
            // 隐藏加载动画
            setTimeout(() => {{
                document.getElementById('loader').classList.add('hidden');
            }}, 800);

            // 生成目录
            generateTOC();

            // 初始化主题
            initTheme();

            // 初始化事件监听
            initEventListeners();

            // 初始化滚动监听
            initScrollListener();

            // 初始化代码复制功能
            initCodeCopy();

            // 添加特殊样式
            addSpecialStyles();
        }});

        // 生成目录
        function generateTOC() {{
            const tocNav = document.getElementById('tocNav');
            const headings = document.querySelectorAll('h2, h3');
            const tocList = document.createElement('ul');
            tocList.className = 'toc-list';

            let currentH2List = null;

            headings.forEach((heading, index) => {{
                const id = heading.id || `heading-${{index}}`;
                heading.id = id;

                const tocItem = document.createElement('li');
                tocItem.className = 'toc-item';

                const tocLink = document.createElement('a');
                tocLink.className = 'toc-link';
                tocLink.href = `#${{id}}`;
                tocLink.textContent = heading.textContent;

                tocLink.addEventListener('click', function(e) {{
                    e.preventDefault();
                    smoothScroll(id);

                    // 更新活动状态
                    document.querySelectorAll('.toc-link').forEach(link => {{
                        link.classList.remove('active');
                    }});
                    this.classList.add('active');
                }});

                tocItem.appendChild(tocLink);

                if (heading.tagName === 'H2') {{
                    tocList.appendChild(tocItem);
                    currentH2List = document.createElement('ul');
                    currentH2List.className = 'toc-list';
                    tocItem.appendChild(currentH2List);
                }} else if (heading.tagName === 'H3' && currentH2List) {{
                    currentH2List.appendChild(tocItem);
                }}
            }});

            tocNav.appendChild(tocList);
        }}

        // 平滑滚动
        function smoothScroll(targetId) {{
            const target = document.getElementById(targetId);
            if (target) {{
                const targetPosition = target.offsetTop - 100;
                window.scrollTo({{
                    top: targetPosition,
                    behavior: 'smooth'
                }});
            }}
        }}

        // 初始化主题
        function initTheme() {{
            const savedTheme = localStorage.getItem('livehouse-theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            updateThemeIcon(savedTheme);
        }}

        // 更新主题图标
        function updateThemeIcon(theme) {{
            const themeBtn = document.getElementById('themeBtn');
            const icon = themeBtn.querySelector('i');
            if (theme === 'dark') {{
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            }} else {{
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }}
        }}

        // 初始化事件监听
        function initEventListeners() {{
            // 主题切换
            document.getElementById('themeBtn').addEventListener('click', function() {{
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('livehouse-theme', newTheme);
                updateThemeIcon(newTheme);
            }});

            // 侧边栏切换
            const sidebarToggle = document.getElementById('sidebarToggle');
            const sidebar = document.getElementById('sidebar');
            const mainContent = document.getElementById('mainContent');

            sidebarToggle.addEventListener('click', function() {{
                sidebar.classList.toggle('active');
                sidebarToggle.classList.toggle('active');
                mainContent.classList.toggle('full-width');
            }});

            // 搜索功能
            const searchBtn = document.getElementById('searchBtn');
            const searchContainer = document.getElementById('searchContainer');
            const searchInput = document.getElementById('searchInput');

            searchBtn.addEventListener('click', function() {{
                searchContainer.classList.toggle('active');
                if (searchContainer.classList.contains('active')) {{
                    searchInput.focus();
                }}
            }});

            // 搜索输入
            searchInput.addEventListener('input', function() {{
                performSearch(this.value);
            }});

            // 点击外部关闭搜索
            document.addEventListener('click', function(e) {{
                if (!searchContainer.contains(e.target) && !searchBtn.contains(e.target)) {{
                    searchContainer.classList.remove('active');
                }}
            }});

            // 打印
            document.getElementById('printBtn').addEventListener('click', function() {{
                window.print();
            }});

            // 下载
            document.getElementById('downloadBtn').addEventListener('click', function() {{
                alert('项目方案文档可通过浏览器"打印 > 保存为PDF"功能下载');
            }});

            // 返回顶部
            document.getElementById('backToTop').addEventListener('click', function() {{
                window.scrollTo({{
                    top: 0,
                    behavior: 'smooth'
                }});
            }});
        }}

        // 初始化滚动监听
        function initScrollListener() {{
            const navbar = document.getElementById('navbar');
            const backToTop = document.getElementById('backToTop');
            const progressBar = document.getElementById('progressBar');
            const headings = document.querySelectorAll('h2, h3');
            const tocLinks = document.querySelectorAll('.toc-link');

            window.addEventListener('scroll', function() {{
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                const scrollProgress = (scrollTop / scrollHeight) * 100;

                // 更新进度条
                progressBar.style.width = scrollProgress + '%';

                // 导航栏样式
                if (scrollTop > 20) {{
                    navbar.classList.add('scrolled');
                }} else {{
                    navbar.classList.remove('scrolled');
                }}

                // 返回顶部按钮
                if (scrollTop > 400) {{
                    backToTop.classList.add('visible');
                }} else {{
                    backToTop.classList.remove('visible');
                }}

                // 更新目录活动状态
                let currentSection = '';
                headings.forEach(heading => {{
                    const rect = heading.getBoundingClientRect();
                    if (rect.top <= 120) {{
                        currentSection = heading.id;
                    }}
                }});

                tocLinks.forEach(link => {{
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${{currentSection}}`) {{
                        link.classList.add('active');
                    }}
                }});
            }});
        }}

        // 初始化代码复制
        function initCodeCopy() {{
            document.querySelectorAll('pre').forEach(pre => {{
                const button = document.createElement('button');
                button.className = 'code-copy-btn';
                button.innerHTML = '<i class="fas fa-copy"></i> 复制';

                button.addEventListener('click', function() {{
                    const code = pre.querySelector('code');
                    const text = code.textContent;

                    navigator.clipboard.writeText(text).then(() => {{
                        button.innerHTML = '<i class="fas fa-check"></i> 已复制';
                        setTimeout(() => {{
                            button.innerHTML = '<i class="fas fa-copy"></i> 复制';
                        }}, 2000);
                    }});
                }});

                pre.appendChild(button);
            }});
        }}

        // 搜索功能
        function performSearch(query) {{
            const searchResults = document.getElementById('searchResults');
            searchResults.innerHTML = '';

            if (query.length < 2) {{
                return;
            }}

            const headings = document.querySelectorAll('h2, h3, h4');
            const results = [];

            headings.forEach(heading => {{
                if (heading.textContent.toLowerCase().includes(query.toLowerCase())) {{
                    results.push({{
                        title: heading.textContent,
                        id: heading.id,
                        level: heading.tagName
                    }});
                }}
            }});

            if (results.length > 0) {{
                results.forEach(result => {{
                    const item = document.createElement('div');
                    item.className = 'search-result-item';
                    item.innerHTML = `<strong>${{result.level}}</strong>: ${{result.title}}`;
                    item.addEventListener('click', function() {{
                        smoothScroll(result.id);
                        document.getElementById('searchContainer').classList.remove('active');
                    }});
                    searchResults.appendChild(item);
                }});
            }} else {{
                searchResults.innerHTML = '<div class="search-result-item">没有找到相关内容</div>';
            }}
        }}

        // 添加特殊样式
        function addSpecialStyles() {{
            // 为执行摘要添加特殊样式
            const summarySection = document.querySelector('h2[id*="执行摘要"], h2[id*="摘要"]');
            if (summarySection) {{
                const nextElement = summarySection.nextElementSibling;
                if (nextElement && nextElement.tagName === 'P') {{
                    nextElement.classList.add('highlight-card');
                }}
            }}
        }}

        // 键盘快捷键
        document.addEventListener('keydown', function(e) {{
            // Ctrl/Cmd + K 打开搜索
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
                e.preventDefault();
                document.getElementById('searchBtn').click();
            }}

            // Escape 关闭搜索
            if (e.key === 'Escape') {{
                document.getElementById('searchContainer').classList.remove('active');
            }}

            // Ctrl/Cmd + D 切换主题
            if ((e.ctrlKey || e.metaKey) && e.key === 'd') {{
                e.preventDefault();
                document.getElementById('themeBtn').click();
            }}
        }});
    </script>
</body>
</html>
"""

    # 写入HTML文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ Livehouse交互式HTML文件已生成：{html_file}")
    print("   🌙 月光主题特色：")
    print("   - 🌟 星空背景动画")
    print("   - 🌙 月亮加载动画")
    print("   - 🎨 紫色渐变主题")
    print("   - 🌓 深色/浅色主题切换")
    print("   - 📱 响应式设计")
    print("   - 🔍 实时搜索功能")
    print("   - 📑 可折叠的侧边栏目录")
    print("   - ⬆️ 返回顶部按钮")
    print("   - 📊 阅读进度条")
    print("   - 📋 代码一键复制")
    print("   - ⌨️ 键盘快捷键支持（Ctrl+K搜索，Ctrl+D切换主题）")
    print("   - 💫 流光溢彩的视觉效果")

if __name__ == "__main__":
    # 输入和输出文件路径
    markdown_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/Livehouse_12.26_执行方案_2025-09-16.md"
    html_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/Livehouse_12.26_执行方案_互动版_2025-09-16.html"

    # 创建交互式HTML
    create_livehouse_interactive_html(markdown_file, html_file)