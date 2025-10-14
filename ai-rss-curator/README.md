# 🤖 AI-RSS Curator

> AI驱动的RSS内容策展系统 - 实现你的"AI分身"概念

## 🚀 快速开始

\`\`\`bash
# 1. 启动服务
docker-compose up -d

# 2. 配置API
vim config.yaml  # 填入 ANTHROPIC_API_KEY

# 3. 运行
pip install -r requirements.txt
python rss_ai_processor.py
\`\`\`

## 📊 访问

- **Miniflux**: http://localhost:8080 (admin/changeme123)
- **RSSHub**: http://localhost:1200

## ✨ 特性

- AI自动评分 (0-100分)
- 只保存高价值内容 (≥70分)
- 完全本地化部署
- 基于 Claude Sonnet 4.5

详细文档见: `../GITHUB_RSS_SEARCH_REPORT.md`
