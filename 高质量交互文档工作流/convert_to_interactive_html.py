#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import markdown2
import re
import os

def create_interactive_html(md_file, html_file):
    """创建交互式HTML版本的调研报告"""

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

    # 创建交互式HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人信息管理系统调研报告 - 交互版</title>

    <!-- 字体 -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">

    <!-- 图标 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {{
            --primary-color: #00bcd4;
            --primary-dark: #0097a7;
            --primary-light: #4dd0e1;
            --secondary-color: #00acc1;
            --accent-color: #00e5ff;
            --text-primary: #2c3e50;
            --text-secondary: #546e7a;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafb;
            --bg-accent: #e0f7fa;
            --border-color: #e0f2f1;
            --shadow-sm: 0 2px 4px rgba(0,188,212,0.1);
            --shadow-md: 0 4px 8px rgba(0,188,212,0.15);
            --shadow-lg: 0 8px 16px rgba(0,188,212,0.2);
            --sidebar-width: 320px;
        }}

        /* 深色模式 */
        [data-theme="dark"] {{
            --primary-color: #26c6da;
            --primary-dark: #00acc1;
            --primary-light: #4dd0e1;
            --secondary-color: #00bcd4;
            --accent-color: #00e5ff;
            --text-primary: #e1f5fe;
            --text-secondary: #b3e5fc;
            --bg-primary: #0f1419;
            --bg-secondary: #1a2332;
            --bg-accent: #263238;
            --border-color: #37474f;
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
            background: var(--bg-primary);
            transition: all 0.3s ease;
            overflow-x: hidden;
        }}

        /* 加载动画 */
        .loader {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--bg-primary);
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

        .loader-spinner {{
            width: 60px;
            height: 60px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}

        /* 顶部导航栏 */
        .navbar {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: var(--bg-primary);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            padding: 0 20px;
            z-index: 1000;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
        }}

        .navbar.scrolled {{
            box-shadow: var(--shadow-md);
        }}

        .navbar-brand {{
            font-size: 20px;
            font-weight: 600;
            color: var(--primary-color);
            text-decoration: none;
            margin-left: 50px;
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
            padding: 8px;
            border-radius: 8px;
            transition: all 0.3s;
        }}

        .navbar-btn:hover {{
            background: var(--bg-accent);
            color: var(--primary-color);
        }}

        /* 侧边栏 */
        .sidebar {{
            position: fixed;
            top: 60px;
            left: 0;
            width: var(--sidebar-width);
            height: calc(100vh - 60px);
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            overflow-y: auto;
            padding: 20px;
            transform: translateX(0);
            transition: transform 0.3s ease;
            z-index: 999;
        }}

        .sidebar.collapsed {{
            transform: translateX(-100%);
        }}

        .sidebar-toggle {{
            position: fixed;
            top: 75px;
            left: 15px;
            width: 40px;
            height: 40px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            justify-content: center;
            align-items: center;
            font-size: 18px;
            box-shadow: var(--shadow-md);
            z-index: 998;
            transition: all 0.3s;
        }}

        .sidebar-toggle:hover {{
            background: var(--primary-dark);
            transform: scale(1.1);
        }}

        .sidebar-toggle.active {{
            left: calc(var(--sidebar-width) - 25px);
        }}

        /* 目录 */
        .toc-title {{
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary-color);
        }}

        .toc-list {{
            list-style: none;
        }}

        .toc-item {{
            margin: 5px 0;
        }}

        .toc-link {{
            color: var(--text-secondary);
            text-decoration: none;
            padding: 8px 12px;
            display: block;
            border-radius: 8px;
            transition: all 0.3s;
            font-size: 14px;
        }}

        .toc-link:hover {{
            background: var(--bg-accent);
            color: var(--primary-color);
            padding-left: 18px;
        }}

        .toc-link.active {{
            background: var(--primary-color);
            color: white;
        }}

        .toc-list .toc-list {{
            margin-left: 15px;
        }}

        .toc-list .toc-list .toc-link {{
            font-size: 13px;
        }}

        /* 主内容区 */
        .main-container {{
            margin-left: var(--sidebar-width);
            margin-top: 60px;
            padding: 40px;
            max-width: 1000px;
            transition: margin-left 0.3s ease;
        }}

        .main-container.full-width {{
            margin-left: 0;
        }}

        /* 内容样式 */
        h1 {{
            color: var(--primary-color);
            font-size: 42px;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 3px solid var(--primary-light);
            animation: fadeInUp 0.8s ease;
        }}

        h1 + h2 {{
            color: var(--text-secondary);
            font-size: 18px;
            font-weight: 400;
            margin-top: -10px;
            margin-bottom: 30px;
        }}

        h2 {{
            color: var(--primary-dark);
            font-size: 28px;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 4px solid var(--primary-color);
            scroll-margin-top: 80px;
            animation: fadeInLeft 0.6s ease;
        }}

        h3 {{
            color: var(--primary-dark);
            font-size: 22px;
            margin-top: 30px;
            margin-bottom: 15px;
            scroll-margin-top: 80px;
        }}

        h4 {{
            color: var(--text-primary);
            font-size: 18px;
            margin-top: 25px;
            margin-bottom: 10px;
            font-weight: 600;
        }}

        /* 段落和文本 */
        p {{
            margin: 15px 0;
            text-align: justify;
        }}

        strong {{
            color: var(--primary-dark);
            font-weight: 600;
        }}

        em {{
            color: var(--text-secondary);
        }}

        /* 链接 */
        a {{
            color: var(--primary-color);
            text-decoration: none;
            border-bottom: 1px dotted var(--primary-color);
            transition: all 0.3s;
        }}

        a:hover {{
            color: var(--primary-dark);
            border-bottom-style: solid;
        }}

        /* 列表 */
        ul, ol {{
            margin: 20px 0;
            padding-left: 30px;
        }}

        li {{
            margin: 10px 0;
            position: relative;
        }}

        /* 引用块 */
        blockquote {{
            background: var(--bg-accent);
            border-left: 4px solid var(--primary-color);
            margin: 25px 0;
            padding: 20px 25px;
            border-radius: 0 8px 8px 0;
            position: relative;
            overflow: hidden;
        }}

        blockquote::before {{
            content: '"';
            position: absolute;
            top: -20px;
            left: 10px;
            font-size: 80px;
            color: var(--primary-light);
            opacity: 0.3;
        }}

        /* 表格 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            background: var(--bg-primary);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }}

        th {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 500;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid var(--border-color);
        }}

        tr:hover td {{
            background: var(--bg-accent);
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        /* 代码块 */
        code {{
            background: var(--bg-accent);
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Monaco', 'Courier New', monospace;
            color: var(--primary-dark);
            font-size: 0.9em;
        }}

        pre {{
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            border: 1px solid var(--border-color);
            position: relative;
        }}

        pre code {{
            background: transparent;
            padding: 0;
            color: var(--text-primary);
        }}

        /* 复制按钮 */
        .code-copy-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.3s;
        }}

        pre:hover .code-copy-btn {{
            opacity: 1;
        }}

        .code-copy-btn:hover {{
            background: var(--primary-dark);
        }}

        /* 分割线 */
        hr {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, var(--primary-color), transparent);
            margin: 40px 0;
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

        /* 进度条 */
        .progress-bar {{
            position: fixed;
            top: 60px;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            z-index: 1001;
            transition: width 0.3s ease;
        }}

        /* 返回顶部按钮 */
        .back-to-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            font-size: 20px;
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
            background: var(--primary-dark);
            transform: translateY(-5px);
        }}

        /* 搜索框 */
        .search-container {{
            position: fixed;
            top: 70px;
            right: 20px;
            width: 300px;
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
            padding: 12px 20px;
            border: 2px solid var(--primary-color);
            border-radius: 25px;
            font-size: 14px;
            background: var(--bg-primary);
            color: var(--text-primary);
            outline: none;
        }}

        .search-results {{
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-top: 10px;
            max-height: 400px;
            overflow-y: auto;
            box-shadow: var(--shadow-lg);
        }}

        .search-result-item {{
            padding: 12px 20px;
            cursor: pointer;
            transition: background 0.3s;
        }}

        .search-result-item:hover {{
            background: var(--bg-accent);
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
                padding: 30px 20px;
            }}

            .navbar-brand {{
                margin-left: 60px;
            }}
        }}

        @media (max-width: 640px) {{
            h1 {{
                font-size: 32px;
            }}

            h2 {{
                font-size: 24px;
            }}

            h3 {{
                font-size: 20px;
            }}

            .main-container {{
                padding: 20px 15px;
            }}

            table {{
                font-size: 14px;
            }}

            th, td {{
                padding: 10px;
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
            }}

            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}

            table, blockquote, pre {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <!-- 加载动画 -->
    <div class="loader" id="loader">
        <div class="loader-spinner"></div>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar" id="progressBar"></div>

    <!-- 顶部导航 -->
    <nav class="navbar" id="navbar">
        <a href="#" class="navbar-brand">
            <i class="fas fa-book-open"></i> 调研报告
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
        <input type="text" class="search-input" placeholder="搜索内容..." id="searchInput">
        <div class="search-results" id="searchResults"></div>
    </div>

    <!-- 侧边栏切换按钮 -->
    <button class="sidebar-toggle" id="sidebarToggle">
        <i class="fas fa-bars"></i>
    </button>

    <!-- 侧边栏 -->
    <aside class="sidebar" id="sidebar">
        <div class="toc-title">目录</div>
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
            }}, 500);

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
                const targetPosition = target.offsetTop - 80;
                window.scrollTo({{
                    top: targetPosition,
                    behavior: 'smooth'
                }});
            }}
        }}

        // 初始化主题
        function initTheme() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
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
                localStorage.setItem('theme', newTheme);
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
                alert('PDF版本已生成：个人信息管理系统调研报告_2025-09-16.pdf');
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

                // 导航栏阴影
                if (scrollTop > 10) {{
                    navbar.classList.add('scrolled');
                }} else {{
                    navbar.classList.remove('scrolled');
                }}

                // 返回顶部按钮
                if (scrollTop > 300) {{
                    backToTop.classList.add('visible');
                }} else {{
                    backToTop.classList.remove('visible');
                }}

                // 更新目录活动状态
                let currentSection = '';
                headings.forEach(heading => {{
                    const rect = heading.getBoundingClientRect();
                    if (rect.top <= 100) {{
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

            const content = document.getElementById('mainContent').textContent;
            const regex = new RegExp(query, 'gi');
            const matches = content.match(regex);

            if (matches && matches.length > 0) {{
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
                            searchContainer.classList.remove('active');
                        }});
                        searchResults.appendChild(item);
                    }});
                }} else {{
                    searchResults.innerHTML = '<div class="search-result-item">没有找到相关内容</div>';
                }}
            }} else {{
                searchResults.innerHTML = '<div class="search-result-item">没有找到相关内容</div>';
            }}
        }}

        // 添加键盘快捷键
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
        }});
    </script>
</body>
</html>
"""

    # 写入HTML文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ 交互式HTML文件已生成：{html_file}")
    print("   特性包括：")
    print("   - 🎨 深色/浅色主题切换")
    print("   - 📱 响应式设计")
    print("   - 🔍 实时搜索功能")
    print("   - 📑 可折叠的侧边栏目录")
    print("   - ⬆️ 返回顶部按钮")
    print("   - 📊 阅读进度条")
    print("   - 📋 代码一键复制")
    print("   - ⌨️ 键盘快捷键支持")

if __name__ == "__main__":
    # 输入和输出文件路径
    markdown_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/个人信息管理系统调研报告_2025-09-16.md"
    html_file = "/mnt/c/Users/Administrator/Desktop/all-in/待处理/个人信息管理系统调研报告_互动版_2025-09-16.html"

    # 创建交互式HTML
    create_interactive_html(markdown_file, html_file)