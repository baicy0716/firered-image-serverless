# 🎨 FireRed-Image-Edit - Docker 部署完整指南

## 📦 项目概述

FireRed-Image-Edit 是一个基于 Qwen 的图像编辑 API，支持：
- ✅ **换装** - 改变人物衣服
- ✅ **风格转换** - 改变图像风格
- ✅ **多图融合** - 融合多张图像
- ✅ **图生视频** - 基于编辑图像生成视频

支持两种部署方式：
- 🚀 **REST API** - 常规 HTTP 服务
- 🌐 **Runpod Serverless** - 无服务器异步处理

---

## 🚀 快速开始

### 1. 构建 Docker 镜像

```bash
cd /home/ihouse/projects/FireRed-Image

# 使用部署脚本（推荐）
bash deploy.sh your-username latest

# 或手动构建
docker build -t firered-image-api:latest -f Dockerfile .
```

### 2. 本地测试

```bash
# 使用 Docker Compose
docker-compose up -d

# 测试 API
curl http://localhost:8080/health

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 推送到 Docker Hub

```bash
# 登录 Docker Hub
docker login

# 标记镜像
docker tag firered-image-api:latest your-username/firered-image-api:latest

# 推送
docker push your-username/firered-image-api:latest
```

---

## 🌐 Runpod Serverless 部署

### 方法 1: Web UI 部署（推荐）

1. **登录 Runpod**
   - 访问 https://www.runpod.io/
   - 登录账户

2. **创建 Serverless Endpoint**
   - 点击 "Serverless" → "Create Endpoint"
   - 选择 "Custom Image"

3. **配置镜像**
   ```
   镜像: your-username/firered-image-serverless:latest
   GPU: 1x A100 或 RTX 4090
   容器磁盘: 50GB
   卷大小: 100GB
   ```

4. **环境变量**
   ```
   HF_HOME=/workspace/huggingface_cache
   TMPDIR=/workspace/tmp
   TORCH_HOME=/workspace/torch_cache
   ```

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成

### 方法 2: CLI 部署

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

---

## 📝 API 使用

### REST API 示例

```bash
# 换装
curl -X POST http://localhost:8080/edit \
  -F "image=@person.png" \
  -F "prompt=person wearing a red dress" \
  -F "num_inference_steps=30" \
  -o result.png

# 多图融合
curl -X POST http://localhost:8080/edit-batch \
  -F "images=@person.png" \
  -F "images=@dress.png" \
  -F "prompt=merge seamlessly" \
  -o result.png
```

### Runpod Serverless 示例

```python
import requests
import base64
import time

# 读取图像
with open('person.png', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode()

# 准备请求
payload = {
    "type": "edit",
    "image": image_base64,
    "prompt": "person wearing a red dress",
    "num_inference_steps": 30
}

# 发送请求
endpoint_url = "https://api.runpod.io/v2/{endpoint_id}/run"
response = requests.post(endpoint_url, json=payload)
job_id = response.json()["id"]

# 轮询结果
while True:
    status_url = f"https://api.runpod.io/v2/{endpoint_id}/status/{job_id}"
    status = requests.get(status_url).json()

    if status["status"] == "COMPLETED":
        result = status["output"]
        image_data = base64.b64decode(result["image"])
        with open('result.png', 'wb') as f:
            f.write(image_data)
        break

    time.sleep(2)
```

---

## 📁 项目结构

```
FireRed-Image/
├── Dockerfile                 # REST API 镜像
├── Dockerfile.serverless      # Runpod Serverless 镜像
├── docker-compose.yml         # 本地测试配置
├── deploy.sh                  # 部署脚本
├── requirements.txt           # Python 依赖
├── .dockerignore             # Docker 忽略文件
├── firered_api_final.py       # REST API 脚本
├── runpod_handler.py          # Runpod 处理器
├── runpod_config.json         # Runpod 配置
├── API_USAGE.md              # API 使用指南
├── QUICK_REFERENCE.md        # 快速参考
├── DOCKER_DEPLOYMENT.md      # Docker 部署指南
└── README.md                 # 本文件
```

---

## 🔧 Docker 镜像详解

### REST API 镜像 (Dockerfile)

- **基础镜像**: `nvidia/cuda:12.1.0-runtime-ubuntu22.04`
- **Python**: 3.12
- **框架**: FastAPI + Uvicorn
- **端口**: 8080
- **用途**: 常规 HTTP 服务

### Serverless 镜像 (Dockerfile.serverless)

- **基础镜像**: `nvidia/cuda:12.1.0-runtime-ubuntu22.04`
- **Python**: 3.12
- **框架**: Runpod SDK
- **用途**: 无服务器异步处理

---

## 📊 性能指标

| 指标 | 值 |
|------|-----|
| 推理时间 (20 步) | 30-60 秒 |
| 推理时间 (30 步) | 45-90 秒 |
| 推理时间 (40 步) | 60-120 秒 |
| GPU 内存 | ~20GB |
| 容器磁盘 | 50GB |
| 卷大小 | 100GB |

---

## 🎯 推荐配置

### 开发环境
```
GPU: RTX 4090
容器磁盘: 50GB
卷大小: 50GB
```

### 生产环境
```
GPU: A100 或 RTX 4090
容器磁盘: 100GB
卷大小: 200GB
副本数: 2-3
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

## 📚 文档

- **API_USAGE.md** - 完整 API 使用指南
- **QUICK_REFERENCE.md** - 快速参考卡
- **DOCKER_DEPLOYMENT.md** - Docker 部署详细指南
- **DEPLOYMENT.md** - 原始部署说明

---

## 🔐 安全建议

1. **使用私有镜像仓库**
   ```bash
   docker tag firered-image-api:latest registry.example.com/firered-image-api:latest
   docker push registry.example.com/firered-image-api:latest
   ```

2. **设置资源限制**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '4'
         memory: 32G
   ```

3. **使用环境变量管理敏感信息**
   ```bash
   docker run -e HF_TOKEN=your_token ...
   ```

---

## 📞 支持

- **项目目录**: `/home/ihouse/projects/FireRed-Image/`
- **API 地址**: `http://213.173.102.178:8080` (当前部署)
- **Runpod**: https://www.runpod.io/

---

## 📝 更新日志

### v1.0.0 (2026-03-17)
- ✅ 初始版本
- ✅ REST API 支持
- ✅ Runpod Serverless 支持
- ✅ Docker 部署配置
- ✅ 完整文档

---

## 📄 许可证

FireRed-Image-Edit 由 FireRed Team 开发

---

## 🚀 快速命令参考

```bash
# 构建
bash deploy.sh your-username latest

# 本地测试
docker-compose up -d

# 推送
docker push your-username/firered-image-api:latest

# Runpod 部署
runpod endpoint create --name "FireRed-Image-Edit" \
  --image "your-username/firered-image-serverless:latest" \
  --gpu-count 1 --container-disk-gb 50
```

---

**准备好了吗？开始部署吧！** 🚀
