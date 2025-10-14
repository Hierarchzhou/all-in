#!/bin/bash
# 终极证明：在后台运行看进程

echo "=== 启动3个并行任务 ==="
echo "运行 python3 prove_parallel.py 并在另一个终端运行："
echo "  watch -n 0.5 'ps aux | grep \"claude --print\" | grep -v grep'"
echo ""
echo "你会看到同时有3个 'claude --print' 进程在运行！"
echo ""
echo "按 Ctrl+C 停止监控"
echo ""

# 在后台运行并监控进程
python3 prove_parallel.py &
PID=$!

sleep 2  # 等待启动

echo "=== 当前运行的 Claude 进程 ==="
ps aux | grep "claude --print" | grep -v grep | head -5 || echo "进程已完成"

wait $PID
