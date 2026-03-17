# 🎯 FireRed-Image-Edit Runpod Serverless 部署指南

## 📌 项目概述

**FireRed-Image-Edit** 是一个基于 Qwen 视觉模型的图像编辑 API，支持：
- ✅ 图像换装（改变人物衣服）
- ✅ 风格转换（改变图像风格）
- ✅ 多图融合（融合多张图像）
- ❌ 视频生成（需要集成 Runway/Pika）

---

## 🚀 快速开始（3 步）

### 第 1 步：构建并推送镜像（10 分钟）

```bash
cd /home/ihouse/projects/FireRed-Image

# 使用快速部署脚本
bash deploy-serverless.sh your-docker-username latest

# 或手动构建
docker build -t firered-image-serverless:latest -f Dockerfile.serverless .
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest
docker push your-username/firered-image-serverless:latest
```

### 第 2 步：在 Runpod 创建 Endpoint（10 分钟）

1. 访问 https://www.runpod.io/console/serverless/endpoints
2. 点击 "Create Endpoint"
3. 选择 "Custom Image"
4. 输入镜像 URL: `your-username/firered-image-serverless:latest`
5. 配置资源：
   - GPU: 1x A100 或 1x RTX 4090
   - 容器磁盘: 50 GB
   - 卷大小: 100 GB
6. 配置环境变量：
   - `HF_HOME = /workspace/huggingface_cache`
   - `TMPDIR = /workspace/tmp`
   - `TORCH_HOME = /workspace/torch_cache`
7. 设置处理器: `runpod_handler.handler`
8. 点击 "Deploy"

### 第 3 步：测试 API（5 分钟）

```python
import requests
import base64
import time

ENDPOINT_ID = "your-endpoint-id"
ENDPOINT_URL = f"https://api.runpod.io/v2/{ENDPOINT_ID}/run"

# 读取图像
with open('person.png', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode()

# 发送请求
payload = {
    "type": "edit",
    "image": image_base64,
    "prompt": "person wearing a beautiful red dress",
    "num_inference_steps": 30
}

response = requests.post(ENDPOINT_URL, json=payload)
job_id = response.json()["id"]

# 轮询结果
while True:
    status = requests.get(f"https://api.runpod.io/v2/{ENDPOINT_ID}/status/{job_id}").json()
    if status["status"] == "COMPLETED":
        result = status["output"]
        image_data = base64.b64decode(result["image"])
        with open('result.png', 'wb') as f:
            f.write(image_data)
        break
    time.sleep(2)
```

---

## 📁 项目文件结构

```
/home/ihouse/projects/FireRed-Image/
├── 📄 核心脚本
│   ├── firered_api_final.py          ✅ REST API 主脚本
│   ├── runpod_handler.py             ✅ Runpod Serverless 处理器
│   ├── api_client.py                 ✅ Python 客户端库
│   └── test_api.py                   ✅ API 测试脚本
│
├── 🐳 Docker 配置
│   ├── Dockerfile                    ✅ REST API 镜像
│   ├── Dockerfile.serverless         ✅ Runpod Serverless 镜像
│   ├── docker-compose.yml            ✅ 本地测试配置
│   ├── .dockerignore                 ✅ Docker 忽略文件
│   ├── requirements.txt              ✅ Python 依赖
│   ├── deploy.sh                     ✅ 自动部署脚本
│   └── deploy-serverless.sh          ✅ Serverless 快速部署脚本
│
├── ⚙️ 配置文件
│   └── runpod_config.json            ✅ Runpod 配置
│
└── 📚 文档
    ├── DEPLOYMENT_CHECKLIST.md       ✅ 部署检查清单
    ├── RUNPOD_DEPLOYMENT_GUIDE.md    ✅ 完整部署指南
    ├── QUICK_DEPLOY.md               ✅ 5 分钟快速部署
    ├── MODEL_CAPABILITIES.md         ✅ 模型能力说明
    ├── API_USAGE.md                  ✅ API 使用指南
    ├── QUICK_REFERENCE.md            ✅ 快速参考卡
    ├── PROJECT_SUMMARY.md            ✅ 项目总结
    ├── FILE_MANIFEST.md              ✅ 文件清单
    ├── START_HERE.md                 ✅ 入门指南
    └── README.md                     ✅ 项目说明
```

---

## 🔧 API 端点说明

### 请求格式

所有请求都是 JSON 格式，图像使用 Base64 编码：

```json
{
  "type": "edit",
  "image": "base64_encoded_image",
  "prompt": "person wearing a red dress",
  "num_inference_steps": 30,
  "cfg_scale": 4.0,
  "seed": 49
}
```

### 响应格式

```json
{
  "id": "job_id_123",
  "status": "COMPLETED",
  "output": {
    "image": "base64_encoded_result",
    "prompt": "person wearing a red dress",
    "num_inference_steps": 30,
    "processing_time": 45.2
  }
}
```

### 支持的参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| type | string | 任务类型: "edit" 或 "edit-batch" | 必需 |
| image | string | Base64 编码的图像 | 必需 |
| images | array | Base64 编码的多张图像 | 仅 edit-batch |
| prompt | string | 编辑提示词 | 必需 |
| num_inference_steps | int | 推理步数 (20-50) | 30 |
| cfg_scale | float | 引导尺度 (1.0-20.0) | 4.0 |
| seed | int | 随机种子 | 49 |

---

## 💡 使用场景示例

### 场景 1: 换装
```python
prompt = "person wearing a beautiful red dress, professional photo"
```

### 场景 2: 风格转换
```python
prompt = "oil painting style, impressionist"
```

### 场景 3: 多图融合
```python
payload = {
    "type": "edit-batch",
    "images": [image1_base64, image2_base64],
    "prompt": "merge person with dress seamlessly"
}
```

---

## 📊 性能指标

| 指标 | 值 |
|------|-----|
| 推理时间 (20 步) | 30-60 秒 |
| 推理时间 (30 步) | 45-90 秒 |
| 推理时间 (40 步) | 60-120 秒 |
| GPU 内存 | ~20GB |
| 模型大小 | ~25GB |
| 容器大小 | ~15GB |

---

## 💰 成本估算

| GPU | 价格/小时 | 推理时间 | 单次成本 |
|-----|----------|---------|---------|
| RTX 4090 | $0.44 | 1 分钟 | ~$0.007 |
| A100 | $1.29 | 1 分钟 | ~$0.021 |

**示例**: 每天 100 次请求
- RTX 4090: ~$0.70/天
- A100: ~$2.10/天

---

## 🐛 故障排除

### 问题 1: 镜像推送失败

```bash
# 检查 Docker 登录
docker login

# 重新标记镜像
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest

# 重新推送
docker push your-username/firered-image-serverless:latest
```

### 问题 2: Endpoint 部署超时

- 增加容器磁盘大小 (50GB → 100GB)
- 选择不同的 GPU
- 检查网络连接
- 查看 Runpod 日志

### 问题 3: 模型加载失败

- 检查容器磁盘大小 (至少 50GB)
- 检查卷大小 (至少 100GB)
- 查看 Runpod 日志
- 重新部署 Endpoint

### 问题 4: 请求超时

```python
# 增加超时时间
response = requests.post(
    ENDPOINT_URL,
    json=payload,
    timeout=600  # 10 分钟
)
```

---

## 📚 文档导航

| 文档 | 用途 |
|------|------|
| **START_HERE.md** | 🎯 入门指南（从这里开始） |
| **QUICK_DEPLOY.md** | ⚡ 5 分钟快速部署 |
| **DEPLOYMENT_CHECKLIST.md** | ✅ 部署检查清单 |
| **RUNPOD_DEPLOYMENT_GUIDE.md** | 📖 完整部署指南 |
| **API_USAGE.md** | 🔌 API 使用详解 |
| **MODEL_CAPABILITIES.md** | 🤖 模型能力说明 |
| **QUICK_REFERENCE.md** | 📋 快速参考卡 |
| **PROJECT_SUMMARY.md** | 📊 项目总结 |

---

## 🎯 下一步

1. ✅ 构建 Docker 镜像
2. ✅ 推送到 Docker Hub
3. ✅ 在 Runpod 创建 Endpoint
4. ✅ 测试 API
5. ✅ 集成到你的应用

---

## 📞 获取帮助

- 快速部署: `bash deploy-serverless.sh your-username latest`
- 查看日志: Runpod Dashboard → Endpoint → Logs
- API 文档: `API_USAGE.md`
- 模型说明: `MODEL_CAPABILITIES.md`

---

## ✨ 特性

- ✅ 基于 Qwen 视觉模型
- ✅ 支持图像换装、风格转换、多图融合
- ✅ 完整的 REST API 和 Serverless 支持
- ✅ Docker 容器化部署
- ✅ 自动扩展和负载均衡
- ✅ 详细的错误处理和日志记录
- ✅ 完整的文档和示例代码

---

**准备好了吗？开始部署！** 🚀

```bash
cd /home/ihouse/projects/FireRed-Image
bash deploy-serverless.sh your-docker-username latest
```
