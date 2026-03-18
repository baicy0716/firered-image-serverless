# FireRed ComfyUI Serverless 部署指南

## 📦 快速部署

### 方式 1：使用 Docker（推荐）

```bash
# 构建镜像
docker build -f Dockerfile.serverless -t firered-comfyui:latest .

# 运行容器
docker run --gpus all -p 8188:8188 -p 8080:8080 firered-comfyui:latest
```

### 方式 2：RunPod 部署

1. **创建 RunPod Pod**
   - 选择 GPU：RTX 4090 或 A100
   - 选择镜像：`pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime`

2. **在 RunPod 终端执行**
   ```bash
   cd /workspace
   git clone https://github.com/baicy0716/firered-image-serverless.git
   cd firered-image-serverless
   chmod +x runpod_serverless_init.sh
   ./runpod_serverless_init.sh
   ```

3. **使用 Serverless API**
   ```bash
   curl -X POST https://api.runpod.io/v2/<endpoint_id>/run \
     -H "Content-Type: application/json" \
     -d '{
       "input": {
         "prompt": "把模特换成穿着红色连衣裙",
         "steps": 40,
         "cfg": 4.0,
         "seed": 43,
         "use_lora": true,
         "images": {
           "image1": "base64_encoded_image1",
           "image2": "base64_encoded_image2",
           "image3": "base64_encoded_image3"
         }
       }
     }'
   ```

## 🔧 API 请求格式

### 请求参数

```json
{
  "input": {
    "prompt": "编辑提示词（必需）",
    "steps": 40,
    "cfg": 4.0,
    "seed": 43,
    "use_lora": true,
    "images": {
      "image1": "base64_encoded_image",
      "image2": "base64_encoded_image",
      "image3": "base64_encoded_image"
    }
  }
}
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | string | "" | 编辑提示词 |
| steps | int | 40 | 推理步数（1-100） |
| cfg | float | 4.0 | CFG 强度（0-20） |
| seed | int | 43 | 随机种子 |
| use_lora | bool | true | 是否使用加速 LoRA |
| images | object | {} | 输入图片（base64） |

### 响应格式

```json
{
  "status": "success",
  "prompt_id": "xxx-xxx-xxx",
  "images": [
    "http://localhost:8188/view?filename=xxx&type=output"
  ],
  "output": {
    "9": {
      "images": [
        {
          "filename": "xxx.png",
          "subfolder": "Firered_image_edit_1.0/00000",
          "type": "output"
        }
      ]
    }
  }
}
```

## 📊 性能参数建议

### 快速模式（推荐）
- steps: 20
- cfg: 1-2
- use_lora: true
- 预计时间: 30-60 秒

### 标准模式
- steps: 40
- cfg: 4
- use_lora: true
- 预计时间: 60-120 秒

### 高质量模式
- steps: 60-100
- cfg: 4-7
- use_lora: false
- 预计时间: 120-300 秒

## 🐳 Docker 镜像构建

### 本地构建

```bash
docker build -f Dockerfile.serverless -t firered-comfyui:latest .
```

### 推送到 Docker Hub

```bash
docker tag firered-comfyui:latest <your-username>/firered-comfyui:latest
docker push <your-username>/firered-comfyui:latest
```

### 推送到 RunPod

1. 在 RunPod 创建私有镜像
2. 上传 Dockerfile
3. 构建镜像
4. 创建 Serverless Endpoint

## 📝 文件说明

| 文件 | 说明 |
|------|------|
| `runpod_serverless_init.sh` | 初始化脚本 |
| `runpod_serverless_handler.py` | Serverless Handler |
| `Dockerfile.serverless` | Docker 镜像定义 |
| `comfyui.json` | ComfyUI 工作流 |
| `download_models.py` | 模型下载脚本 |

## 🚀 部署到 RunPod Serverless

### 步骤 1：创建 Docker 镜像

```bash
# 在本地或 RunPod 上构建
docker build -f Dockerfile.serverless -t firered-comfyui:latest .

# 标记镜像
docker tag firered-comfyui:latest <registry>/firered-comfyui:latest

# 推送到镜像仓库
docker push <registry>/firered-comfyui:latest
```

### 步骤 2：在 RunPod 创建 Serverless Endpoint

1. 登录 RunPod
2. 进入 Serverless 页面
3. 创建新 Endpoint
4. 选择镜像：`<registry>/firered-comfyui:latest`
5. 配置：
   - GPU：RTX 4090 或 A100
   - 最大并发：1-4
   - 超时：3600 秒

### 步骤 3：测试 API

```bash
# 获取 Endpoint ID
ENDPOINT_ID="your-endpoint-id"
API_KEY="your-api-key"

# 提交请求
curl -X POST https://api.runpod.io/v2/$ENDPOINT_ID/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d '{
    "input": {
      "prompt": "把模特换成穿着蓝色连衣裙",
      "steps": 20,
      "cfg": 4.0,
      "seed": 42,
      "use_lora": true,
      "images": {
        "image1": "...",
        "image2": "...",
        "image3": "..."
      }
    }
  }'
```

## 💾 模型缓存

模型会在首次运行时下载并缓存到容器中。为了加快部署速度，可以：

1. **预构建镜像时下载模型**
   - Dockerfile 中已包含 `RUN python3 download_models.py`

2. **使用持久化存储**
   - 在 RunPod 中配置 Volume 挂载模型目录

## 🔍 故障排除

### 问题：模型下载失败

**解决方案：**
```bash
# 手动下载模型
python3 download_models.py

# 检查模型文件
ls -lh /workspace/runpod-slim/ComfyUI/models/*/
```

### 问题：ComfyUI 启动失败

**解决方案：**
```bash
# 查看日志
tail -f /tmp/comfyui.log

# 重启 ComfyUI
pkill -f "python3 main.py"
cd /workspace/runpod-slim/ComfyUI
python3 main.py --listen 0.0.0.0 --port 8188
```

### 问题：处理超时

**解决方案：**
- 减少 steps 参数
- 启用 use_lora
- 检查 GPU 显存

## 📞 支持

如有问题，请查看日志或联系开发者。

## 许可证

MIT License
