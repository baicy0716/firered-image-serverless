# Docker 部署指南 - FireRed-Image-Edit API

## 📦 Docker 镜像构建

### 1. 构建 REST API 镜像（用于常规部署）

```bash
cd /home/ihouse/projects/FireRed-Image

# 构建镜像
docker build -t firered-image-api:latest -f Dockerfile .

# 标记镜像（用于推送到 Docker Hub）
docker tag firered-image-api:latest your-username/firered-image-api:latest

# 推送到 Docker Hub
docker push your-username/firered-image-api:latest
```

### 2. 构建 Runpod Serverless 镜像

```bash
# 构建 Serverless 镜像
docker build -t firered-image-serverless:latest -f Dockerfile.serverless .

# 标记镜像
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest

# 推送到 Docker Hub
docker push your-username/firered-image-serverless:latest
```

---

## 🚀 本地测试

### 使用 Docker Compose

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f firered-api

# 测试 API
curl http://localhost:8080/health

# 停止服务
docker-compose down
```

### 手动运行 Docker 容器

```bash
# 运行 REST API 容器
docker run --gpus all -p 8080:8080 \
  -v $(pwd)/cache:/workspace/huggingface_cache \
  -v $(pwd)/tmp:/workspace/tmp \
  firered-image-api:latest

# 测试
curl http://localhost:8080/health
```

---

## 🌐 Runpod Serverless 部署

### 方法 1: 使用 Runpod Web UI

1. **登录 Runpod**
   - 访问 https://www.runpod.io/
   - 登录你的账户

2. **创建新的 Serverless Endpoint**
   - 点击 "Serverless" → "Create Endpoint"
   - 选择 "Custom Image"

3. **配置镜像**
   - 输入镜像 URL: `your-username/firered-image-serverless:latest`
   - 设置 GPU: 1x A100 或 RTX 4090
   - 设置容器磁盘: 50GB
   - 设置卷大小: 100GB

4. **配置环境变量**
   ```
   HF_HOME=/workspace/huggingface_cache
   TMPDIR=/workspace/tmp
   TORCH_HOME=/workspace/torch_cache
   ```

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成

### 方法 2: 使用 Runpod CLI

```bash
# 安装 Runpod CLI
pip install runpod-cli

# 登录
runpod login

# 部署
runpod endpoint create \
  --name "FireRed-Image-Edit" \
  --image "your-username/firered-image-serverless:latest" \
  --gpu-count 1 \
  --container-disk-gb 50 \
  --volume-gb 100
```

### 方法 3: 使用配置文件

```bash
# 使用 runpod_config.json 部署
runpod endpoint create --config runpod_config.json
```

---

## 📝 使用 Runpod Serverless API

### 单图编辑

```python
import requests
import base64
import json

# 读取图像
with open('person.png', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode()

# 准备请求
payload = {
    "type": "edit",
    "image": image_base64,
    "prompt": "person wearing a beautiful red dress, professional photo",
    "num_inference_steps": 30,
    "cfg_scale": 4.0,
    "seed": 49
}

# 发送请求到 Runpod Endpoint
endpoint_url = "https://api.runpod.io/v2/{endpoint_id}/run"
headers = {"Content-Type": "application/json"}

response = requests.post(endpoint_url, json=payload, headers=headers)
job_id = response.json()["id"]

# 轮询结果
import time
while True:
    status_url = f"https://api.runpod.io/v2/{endpoint_id}/status/{job_id}"
    status = requests.get(status_url).json()

    if status["status"] == "COMPLETED":
        result = status["output"]

        # 保存结果
        image_data = base64.b64decode(result["image"])
        with open('result.png', 'wb') as f:
            f.write(image_data)

        print("✅ 编辑完成!")
        break
    elif status["status"] == "FAILED":
        print(f"❌ 失败: {status['error']}")
        break

    time.sleep(2)
```

### 多图融合

```python
import requests
import base64

# 读取多张图像
images_base64 = []
for img_path in ['person.png', 'dress.png']:
    with open(img_path, 'rb') as f:
        images_base64.append(base64.b64encode(f.read()).decode())

# 准备请求
payload = {
    "type": "edit-batch",
    "images": images_base64,
    "prompt": "merge person with dress seamlessly",
    "num_inference_steps": 30
}

# 发送请求
response = requests.post(endpoint_url, json=payload, headers=headers)
# ... 轮询结果
```

---

## 🔧 Docker 镜像优化

### 减小镜像大小

```bash
# 使用多阶段构建
docker build -t firered-image-api:slim -f Dockerfile.slim .

# 查看镜像大小
docker images | grep firered
```

### 预加载模型

创建 `Dockerfile.with-models`:

```dockerfile
FROM firered-image-api:latest

# 预加载模型
RUN python3 << 'EOF'
import os
os.environ['HF_HOME'] = '/workspace/huggingface_cache'

from diffusers import QwenImageEditPlusPipeline
import torch

print("Preloading model...")
pipe = QwenImageEditPlusPipeline.from_pretrained(
    "FireRedTeam/FireRed-Image-Edit-1.1",
    torch_dtype=torch.bfloat16,
)
print("✅ Model preloaded!")
EOF
```

构建：
```bash
docker build -t firered-image-api:with-models -f Dockerfile.with-models .
```

---

## 📊 性能优化

### GPU 选择

| GPU | 推荐用途 | 成本 |
|-----|---------|------|
| RTX 4090 | 高性能，快速推理 | 高 |
| A100 | 企业级，稳定性好 | 很高 |
| RTX 3090 | 平衡性能和成本 | 中 |
| RTX 4080 | 经济型 | 低 |

### 推理优化

```python
# 使用 bfloat16 加速
torch_dtype=torch.bfloat16

# 启用 xFormers 优化
pipe.enable_xformers_memory_efficient_attention()

# 启用 attention slicing
pipe.enable_attention_slicing()
```

---

## 🐛 故障排除

### 镜像构建失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker build --no-cache -t firered-image-api:latest -f Dockerfile .
```

### 容器启动失败

```bash
# 查看日志
docker logs container_id

# 交互式运行
docker run -it --gpus all firered-image-api:latest /bin/bash
```

### Runpod 部署超时

- 增加容器磁盘大小
- 使用预加载模型的镜像
- 检查网络连接

---

## 📋 文件清单

| 文件 | 说明 |
|------|------|
| `Dockerfile` | REST API 镜像 |
| `Dockerfile.serverless` | Runpod Serverless 镜像 |
| `docker-compose.yml` | 本地测试配置 |
| `runpod_handler.py` | Runpod 处理器 |
| `runpod_config.json` | Runpod 配置 |
| `firered_api_final.py` | REST API 脚本 |

---

## 🚀 快速部署命令

### 本地测试
```bash
docker-compose up -d
curl http://localhost:8080/health
```

### 构建并推送
```bash
docker build -t your-username/firered-image-api:latest -f Dockerfile .
docker push your-username/firered-image-api:latest
```

### Runpod 部署
```bash
runpod endpoint create \
  --name "FireRed-Image-Edit" \
  --image "your-username/firered-image-serverless:latest" \
  --gpu-count 1 \
  --container-disk-gb 50
```

---

## 📞 支持

- 镜像仓库: Docker Hub
- 文档: `/home/ihouse/projects/FireRed-Image/`
- API 文档: `API_USAGE.md`
