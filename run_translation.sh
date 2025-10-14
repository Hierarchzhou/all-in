#!/bin/bash
# 音频翻译执行脚本

export ANTHROPIC_API_KEY='sk-ant-oat01-yv1TBMa7EZXd1sEwWQD9qG1PP1iJXBIrtx6eQMnTE6PInrgpX1E9CEHsXJn91-qYOlX45DrIUQy3zjcvExANCt6HXcY6FAA'
export ANTHROPIC_BASE_URL='https://code.newcli.com/claude'

echo "🚀 开始音频翻译..."
echo "📁 音频文件: /mnt/c/Users/Administrator/Downloads/de353095889897a34f1d1d5d32920a2a.mp3"
echo ""

/mnt/c/Users/Administrator/Desktop/all-in/venv/bin/python \
  /mnt/c/Users/Administrator/Desktop/all-in/audio_translator.py \
  '/mnt/c/Users/Administrator/Downloads/de353095889897a34f1d1d5d32920a2a.mp3'
