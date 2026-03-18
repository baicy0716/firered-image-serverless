#!/bin/bash

# FireRed ComfyUI 部署脚本

set -e

echo "=========================================="
echo "FireRed ComfyUI 工作流部署"
echo "=========================================="

# 配置
COMFYUI_DIR="/workspace/ComfyUI"
PROJECT_DIR="/home/ihouse/projects/FireRed-Image"
API_PORT=8080

# 检查 ComfyUI 是否存在
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "❌ ComfyUI 目录不存在: $COMFYUI_DIR"
    echo "请先安装 ComfyUI"
    exit 1
fi

echo "✅ ComfyUI 目录已找到"

# 检查工作流文件
if [ ! -f "$PROJECT_DIR/comfyui.json" ]; then
    echo "❌ 工作流文件不存在: $PROJECT_DIR/comfyui.json"
    exit 1
fi

echo "✅ 工作流文件已找到"

# 检查 Python 脚本
if [ ! -f "$PROJECT_DIR/comfyui_api_server.py" ]; then
    echo "❌ API 服务器脚本不存在"
    exit 1
fi

echo "✅ API 服务器脚本已找到"

# 检查并清理端口
echo ""
echo "🔍 检查端口 $API_PORT..."
if lsof -i :$API_PORT > /dev/null 2>&1; then
    echo "⚠️  端口 $API_PORT 已被占用，正在清理..."
    PID=$(lsof -i :$API_PORT | grep LISTEN | awk '{print $2}' | head -1)
    if [ ! -z "$PID" ]; then
        kill -9 $PID 2>/dev/null || true
        echo "✅ 已杀死进程 (PID: $PID)"
    fi
fi

# 启动 ComfyUI（如果未运行）
echo ""
echo "🚀 启动 ComfyUI..."
if ! curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
    echo "ComfyUI 未运行，正在启动..."
    cd "$COMFYUI_DIR"
    python main.py > /tmp/comfyui.log 2>&1 &
    COMFYUI_PID=$!
    echo "✅ ComfyUI 已启动 (PID: $COMFYUI_PID)"

    # 等待 ComfyUI 启动
    echo "⏳ 等待 ComfyUI 启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
            echo "✅ ComfyUI 已就绪"
            break
        fi
        sleep 1
    done
else
    echo "✅ ComfyUI 已在运行"
fi

# 启动 API 服务器
echo ""
echo "🚀 启动 API 服务器..."
cd "$PROJECT_DIR"
python comfyui_api_server.py &
API_PID=$!
echo "✅ API 服务器已启动 (PID: $API_PID)"

# 等待 API 服务器启动
echo "⏳ 等待 API 服务器启动..."
for i in {1..10}; do
    if curl -s http://localhost:$API_PORT > /dev/null 2>&1; then
        echo "✅ API 服务器已就绪"
        break
    fi
    sleep 1
done

echo ""
echo "=========================================="
echo "✅ 部署完成!"
echo "=========================================="
echo ""
echo "📱 访问测试页面: http://localhost:$API_PORT"
echo ""
echo "进程信息:"
echo "  ComfyUI: PID $COMFYUI_PID (http://localhost:8188)"
echo "  API 服务器: PID $API_PID (http://localhost:$API_PORT)"
echo ""
echo "查看日志:"
echo "  ComfyUI: tail -f /tmp/comfyui.log"
echo "  API: 在前台运行"
echo ""
echo "停止服务:"
echo "  kill $COMFYUI_PID $API_PID"
echo ""
echo "=========================================="

# 保持脚本运行
wait
