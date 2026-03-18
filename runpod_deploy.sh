#!/bin/bash
# 一键部署脚本 - 在 RunPod 机器上运行

set -e

echo "=========================================="
echo "FireRed ComfyUI 一键部署"
echo "=========================================="

# 1. 克隆项目
echo ""
echo "📦 克隆项目..."
cd /workspace
if [ -d "firered-image-serverless" ]; then
    echo "项目已存在，更新中..."
    cd firered-image-serverless
    git pull
else
    git clone https://github.com/baicy0716/firered-image-serverless.git
    cd firered-image-serverless
fi

echo "✅ 项目已就绪"

# 2. 安装依赖
echo ""
echo "📦 安装依赖..."
pip install -q tqdm requests Flask==2.3.3 Werkzeug==2.3.7 2>/dev/null || pip install -q --no-deps tqdm requests Flask Werkzeug
echo "✅ 依赖已安装"

# 3. 下载模型
echo ""
echo "📥 下载模型..."
python download_models.py

# 4. 清理端口
echo ""
echo "🔍 清理端口 8080..."
lsof -i :8080 | grep LISTEN | awk '{print $2}' | xargs -r kill -9 2>/dev/null || true

# 5. 启动 ComfyUI（如果未运行）
echo ""
echo "🚀 检查 ComfyUI..."
if ! curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
    echo "启动 ComfyUI..."
    cd /workspace/ComfyUI
    nohup python main.py > /tmp/comfyui.log 2>&1 &
    echo "等待 ComfyUI 启动..."
    sleep 10
fi

# 6. 启动 API 服务器
echo ""
echo "🚀 启动 API 服务器..."
cd /workspace/firered-image-serverless
nohup python comfyui_api_server.py > /tmp/api_server.log 2>&1 &
API_PID=$!

sleep 3

echo ""
echo "=========================================="
echo "✅ 部署完成!"
echo "=========================================="
echo ""
echo "服务信息:"
echo "  ComfyUI: http://localhost:8188"
echo "  API 服务器: http://localhost:8080"
echo ""
echo "查看日志:"
echo "  tail -f /tmp/comfyui.log"
echo "  tail -f /tmp/api_server.log"
echo ""
echo "访问测试页面:"
echo "  需要端口转发: ssh -L 8080:localhost:8080 <your-runpod>"
echo "  然后访问: http://localhost:8080"
echo ""
echo "=========================================="
