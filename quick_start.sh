#!/bin/bash
# 快速启动脚本 - 一键启动 Serverless

set -e

echo "=========================================="
echo "FireRed ComfyUI Serverless 快速启动"
echo "=========================================="

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: ./quick_start.sh [init|start|stop|logs]"
    echo ""
    echo "命令:"
    echo "  init   - 初始化环境（首次运行）"
    echo "  start  - 启动服务"
    echo "  stop   - 停止服务"
    echo "  logs   - 查看日志"
    exit 1
fi

COMMAND=$1

case $COMMAND in
    init)
        echo "初始化环境..."
        chmod +x runpod_serverless_init.sh
        ./runpod_serverless_init.sh
        ;;
    start)
        echo "启动服务..."
        chmod +x runpod_serverless_init.sh
        nohup ./runpod_serverless_init.sh > /tmp/serverless.log 2>&1 &
        echo "✅ 服务已启动"
        echo "查看日志: tail -f /tmp/serverless.log"
        ;;
    stop)
        echo "停止服务..."
        pkill -f "python3 main.py" || true
        pkill -f "runpod_serverless_handler.py" || true
        echo "✅ 服务已停止"
        ;;
    logs)
        echo "查看日志..."
        tail -f /tmp/serverless.log
        ;;
    *)
        echo "未知命令: $COMMAND"
        exit 1
        ;;
esac
