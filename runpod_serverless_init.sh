#!/bin/bash
# RunPod Serverless Handler 启动脚本

set -e

echo "=========================================="
echo "FireRed ComfyUI Serverless 初始化"
echo "=========================================="

# 配置
COMFYUI_PATH="/workspace/runpod-slim/ComfyUI"
PROJECT_PATH="/workspace/firered-image-serverless"
MODELS_PATH="$COMFYUI_PATH/models"

# 1. 检查 ComfyUI
echo ""
echo "✅ 检查 ComfyUI..."
if [ ! -d "$COMFYUI_PATH" ]; then
    echo "❌ ComfyUI 不存在，正在安装..."
    cd /workspace
    git clone https://github.com/comfyanonymous/ComfyUI.git runpod-slim/ComfyUI
    cd $COMFYUI_PATH
    pip install -q -r requirements.txt
fi

# 2. 检查项目
echo "✅ 检查项目..."
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ 项目不存在，正在克隆..."
    cd /workspace
    git clone https://github.com/baicy0716/firered-image-serverless.git
fi

# 3. 下载模型
echo ""
echo "📥 检查模型..."
cd $PROJECT_PATH

# 检查模型是否存在
MODELS_NEEDED=(
    "$MODELS_PATH/diffusion_models/FireRed-Image-Edit-1.1-transformer.safetensors"
    "$MODELS_PATH/loras/FireRed-Image-Edit-1.0-Lightning-8steps-v1.1.safetensors"
    "$MODELS_PATH/text_encoders/qwen2.5vl-7b-bf16.safetensors"
    "$MODELS_PATH/vae/qwen_image_vae.safetensors"
)

NEED_DOWNLOAD=false
for model in "${MODELS_NEEDED[@]}"; do
    if [ ! -f "$model" ]; then
        NEED_DOWNLOAD=true
        break
    fi
done

if [ "$NEED_DOWNLOAD" = true ]; then
    echo "下载缺失的模型..."
    python3 download_models.py
else
    echo "✅ 所有模型已就绪"
fi

# 4. 启动 ComfyUI
echo ""
echo "🚀 启动 ComfyUI..."
cd $COMFYUI_PATH
nohup python3 main.py --listen 0.0.0.0 --port 8188 > /tmp/comfyui.log 2>&1 &
COMFYUI_PID=$!
echo "ComfyUI PID: $COMFYUI_PID"

# 等待 ComfyUI 启动
echo "⏳ 等待 ComfyUI 启动..."
for i in {1..30}; do
    if curl -s http://localhost:8188/system_stats > /dev/null 2>&1; then
        echo "✅ ComfyUI 已就绪"
        break
    fi
    sleep 1
done

# 5. 启动 Serverless Handler
echo ""
echo "🚀 启动 Serverless Handler..."
cd $PROJECT_PATH
python3 runpod_serverless_handler.py

echo ""
echo "=========================================="
echo "✅ Serverless 已启动"
echo "=========================================="
