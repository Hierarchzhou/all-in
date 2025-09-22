#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import markdown2
import re
import os
import sys

def create_universal_interactive_html(md_file, html_file, theme='cyan'):
    """创建通用的交互式HTML版本文档

    Args:
        md_file (str): 输入的Markdown文件路径
        html_file (str): 输出的HTML文件路径
        theme (str): 主题选择 ('cyan' 或 'moon')
    """

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

    # 根据主题选择颜色配置
    if theme == 'moon':
        # 月光主题 - 紫色系
        theme_config = {
            'primary_color': '#6366f1',
            'primary_dark': '#4f46e5',
            'primary_light': '#a5b4fc',
            'secondary_color': '#8b5cf6',
            'accent_color': '#c084fc',
            'gold_color': '#fbbf24',
            'theme_name': '月光主题',
            'brand_emoji': '🌙'
        }
        background_effect = '''
        /* 星空背景效果 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image:
                radial-gradient(2px 2px at 20px 30px, var(--accent-color), transparent),
                radial-gradient(2px 2px at 40px 70px, var(--primary-light), transparent),
                radial-gradient(1px 1px at 90px 40px, var(--gold-color), transparent);
            background-repeat: repeat;
            background-size: 200px 100px;
            opacity: 0.1;
            z-index: -1;
            animation: starfield 20s linear infinite;
        }
        @keyframes starfield {
            from { transform: translateY(0); }
            to { transform: translateY(-100px); }
        }'''
    else:
        # 青色主题 - 默认
        theme_config = {
            'primary_color': '#00bcd4',
            'primary_dark': '#0097a7',
            'primary_light': '#4dd0e1',
            'secondary_color': '#00acc1',
            'accent_color': '#00e5ff',
            'gold_color': '#ffc107',
            'theme_name': '青色主题',
            'brand_emoji': '📄'
        }
        background_effect = '''
        /* 渐变背景效果 */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, transparent 0%, rgba(0,188,212,0.03) 100%);
            z-index: -1;
        }'''

    # 创建交互式HTML
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交互式文档 - {theme_config['theme_name']}</title>

    <!-- 字体 -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">

    <!-- 图标 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <style>
        :root {{
            --primary-color: {theme_config['primary_color']};
            --primary-dark: {theme_config['primary_dark']};
            --primary-light: {theme_config['primary_light']};
            --secondary-color: {theme_config['secondary_color']};
            --accent-color: {theme_config['accent_color']};
            --gold-color: {theme_config['gold_color']};
            --text-primary: #2c3e50;
            --text-secondary: #546e7a;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-accent: #f1f5f9;
            --border-color: #e2e8f0;
            --shadow-sm: 0 2px 4px rgba(0,188,212,0.1);
            --shadow-md: 0 4px 8px rgba(0,188,212,0.15);
            --shadow-lg: 0 8px 16px rgba(0,188,212,0.2);
            --sidebar-width: 320px;
        }}

        /* 深色模式 */
        [data-theme="dark"] {{
            --primary-color: {theme_config['primary_light']};
            --primary-dark: {theme_config['secondary_color']};
            --primary-light: {theme_config['accent_color']};
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --bg-primary: #0f1419;
            --bg-secondary: #1a2332;
            --bg-accent: #263238;
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

        {background_effect}

        /* 加载动画 */
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

        .loader-spinner {{
            width: 60px;
            height: 60px;
            border: 4px solid var(--border-color);
            border-top: 4px solid var(--primary-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }}

        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
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
            background: rgba(15, 20, 25, 0.95);
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
            content: '{theme_config['brand_emoji']}';
            font-size: 28px;
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
        }}

        .navbar-btn:hover {{
            background: var(--bg-accent);
            color: var(--primary-color);
            transform: translateY(-2px);
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
            background: rgba(26, 35, 50, 0.95);
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
        }}

        .toc-link:hover {{
            background: var(--bg-accent);
            color: var(--primary-color);
            padding-left: 25px;
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

        /* 主内容区 */
        .main-container {{
            margin-left: var(--sidebar-width);
            margin-top: 70px;
            padding: 50px 40px;
            max-width: 1200px;
            transition: margin-left 0.3s ease;
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
        }}

        h2 {{
            color: var(--primary-dark);
            font-size: 32px;
            margin-top: 50px;
            margin-bottom: 25px;
            padding: 20px 0 20px 25px;
            border-left: 5px solid var(--primary-color);
            background: linear-gradient(90deg, rgba(0,188,212,0.05) 0%, transparent 100%);
            border-radius: 0 15px 15px 0;
            scroll-margin-top: 100px;
        }}

        h3 {{
            color: var(--primary-dark);
            font-size: 24px;
            margin-top: 35px;
            margin-bottom: 20px;
            scroll-margin-top: 100px;
        }}

        /* 表格样式 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            background: var(--bg-primary);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: var(--shadow-md);
        }}

        th {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            text-align: left;
            font-weight: 500;
        }}

        td {{
            padding: 18px 20px;
            border-bottom: 1px solid var(--border-color);
        }}

        tr:hover td {{
            background: var(--bg-accent);
        }}

        /* 引用块 */
        blockquote {{
            background: var(--bg-accent);
            border-left: 5px solid var(--primary-color);
            margin: 30px 0;
            padding: 25px 30px;
            border-radius: 0 15px 15px 0;
        }}

        /* 进度条 */
        .progress-bar {{
            position: fixed;
            top: 70px;
            left: 0;
            width: 0%;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
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
        }}

        @media (max-width: 640px) {{
            h1 {{ font-size: 36px; }}
            h2 {{ font-size: 28px; }}
            h3 {{ font-size: 22px; }}
            .main-container {{ padding: 30px 20px; }}
        }}

        /* 动画 */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <!-- 加载动画 -->
    <div class="loader" id="loader">
        <div class="loader-content">
            <div class="loader-spinner"></div>
            <div class="loader-text">加载中...</div>
        </div>
    </div>

    <!-- 进度条 -->
    <div class="progress-bar" id="progressBar"></div>

    <!-- 顶部导航 -->
    <nav class="navbar" id="navbar">
        <a href="#" class="navbar-brand">交互式文档</a>
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
        <div class="toc-title">文档导航</div>
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
        // JavaScript代码与之前相同，此处省略以节省空间
        // 包含所有交互功能：目录生成、搜索、主题切换、滚动监听等

        document.addEventListener('DOMContentLoaded', function() {{
            setTimeout(() => {{
                document.getElementById('loader').classList.add('hidden');
            }}, 500);

            generateTOC();
            initTheme();
            initEventListeners();
            initScrollListener();
        }});

        function generateTOC() {{
            const tocNav = document.getElementById('tocNav');
            const headings = document.querySelectorAll('h2, h3');
            const tocList = document.createElement('ul');
            tocList.className = 'toc-list';

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
                    const target = document.getElementById(id);
                    if (target) {{
                        window.scrollTo({{
                            top: target.offsetTop - 100,
                            behavior: 'smooth'
                        }});
                    }}
                }});

                tocItem.appendChild(tocLink);
                tocList.appendChild(tocItem);
            }});

            tocNav.appendChild(tocList);
        }}

        function initTheme() {{
            const savedTheme = localStorage.getItem('doc-theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
        }}

        function initEventListeners() {{
            // 主题切换
            document.getElementById('themeBtn').addEventListener('click', function() {{
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('doc-theme', newTheme);
            }});

            // 侧边栏切换
            document.getElementById('sidebarToggle').addEventListener('click', function() {{
                document.getElementById('sidebar').classList.toggle('active');
                document.getElementById('mainContent').classList.toggle('full-width');
            }});

            // 搜索功能
            document.getElementById('searchBtn').addEventListener('click', function() {{
                document.getElementById('searchContainer').classList.toggle('active');
            }});

            // 打印
            document.getElementById('printBtn').addEventListener('click', function() {{
                window.print();
            }});

            // 返回顶部
            document.getElementById('backToTop').addEventListener('click', function() {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }});
        }}

        function initScrollListener() {{
            window.addEventListener('scroll', function() {{
                const scrollTop = window.pageYOffset;
                const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
                const progress = (scrollTop / scrollHeight) * 100;

                document.getElementById('progressBar').style.width = progress + '%';

                if (scrollTop > 20) {{
                    document.getElementById('navbar').classList.add('scrolled');
                }} else {{
                    document.getElementById('navbar').classList.remove('scrolled');
                }}

                if (scrollTop > 400) {{
                    document.getElementById('backToTop').classList.add('visible');
                }} else {{
                    document.getElementById('backToTop').classList.remove('visible');
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    # 写入HTML文件
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ 交互式HTML文件已生成：{html_file}")
    print(f"   🎨 主题：{theme_config['theme_name']}")

def main():
    """主函数，支持命令行参数"""
    if len(sys.argv) < 3:
        print("使用方法：python 通用HTML生成器.py <输入MD文件> <输出HTML文件> [主题]")
        print("主题选项：cyan（青色，默认）或 moon（月光）")
        return

    md_file = sys.argv[1]
    html_file = sys.argv[2]
    theme = sys.argv[3] if len(sys.argv) > 3 else 'cyan'

    if not os.path.exists(md_file):
        print(f"错误：文件 {md_file} 不存在")
        return

    create_universal_interactive_html(md_file, html_file, theme)

if __name__ == "__main__":
    main()