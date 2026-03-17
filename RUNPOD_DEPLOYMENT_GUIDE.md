# 🚀 Runpod Serverless 部署完整步骤

## 📋 部署前准备

### 1. 准备 Docker Hub 账户
```bash
# 如果没有账户，访问 https://hub.docker.com/ 注册

# 登录 Docker
docker login
# 输入用户名和密码
```

### 2. 检查 Docker 安装
```bash
docker --version
docker ps
```

---

## 🔨 第一步：构建 Docker 镜像

### 方法 A: 使用自动脚本（推荐）

```bash
cd /home/ihouse/projects/FireRed-Image

# 运行部署脚本
bash deploy.sh your-docker-username latest

# 按照提示选择：
# 1) REST API (Dockerfile)
# 2) Runpod Serverless (Dockerfile.serverless)
# 3) 两者都构建  ← 选择这个
```

### 方法 B: 手动构建

```bash
cd /home/ihouse/projects/FireRed-Image

# 构建 Serverless 镜像
docker build -t firered-image-serverless:latest -f Dockerfile.serverless .

# 标记镜像（用你的 Docker Hub 用户名替换 your-username）
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest

# 查看镜像
docker images | grep firered
```

---

## 📤 第二步：推送镜像到 Docker Hub

```bash
# 推送 Serverless 镜像
docker push your-username/firered-image-serverless:latest

# 等待上传完成（可能需要 5-10 分钟）
# 你会看到类似的输出：
# Pushing your-username/firered-image-serverless:latest
# Pushed 123.45 MB
```

### 验证上传成功
```bash
# 访问 https://hub.docker.com/
# 登录后查看你的镜像库
# 应该能看到 firered-image-serverless
```

---

## 🌐 第三步：在 Runpod 创建 Endpoint

### 方法 A: 使用 Web UI（推荐新手）

#### 1. 登录 Runpod
```
访问: https://www.runpod.io/
点击 "Sign In" 登录
```

#### 2. 进入 Serverless 页面
```
左侧菜单 → "Serverless" → "Endpoints"
```

#### 3. 创建新 Endpoint
```
点击 "Create Endpoint" 按钮
```

#### 4. 选择镜像
```
选择 "Custom Image"
输入镜像 URL: your-username/firered-image-serverless:latest
```

#### 5. 配置资源
```
GPU: 选择 "1x A100" 或 "1x RTX 4090"
  - A100: 更稳定，更贵
  - RTX 4090: 性能好，便宜一点

容器磁盘: 50 GB
卷大小: 100 GB
```

#### 6. 配置环境变量
```
点击 "Add Environment Variable"

添加以下变量:
1. HF_HOME = /workspace/huggingface_cache
2. TMPDIR = /workspace/tmp
3. TORCH_HOME = /workspace/torch_cache
```

#### 7. 配置处理器
```
Handler: runpod_handler.handler
```

#### 8. 部署
```
点击 "Deploy" 按钮
等待部署完成（通常 5-10 分钟）
```

#### 9. 获取 Endpoint ID
```
部署完成后，你会看到 Endpoint ID
例如: abc123def456
保存这个 ID，后面会用到
```

---

### 方法 B: 使用 Runpod CLI

#### 1. 安装 CLI
```bash
pip install runpod-cli
```

#### 2. 登录
```bash
runpod login
# 输入你的 Runpod API Key
# 获取方式: https://www.runpod.io/console/user/settings
```

#### 3. 部署
```bash
runpod endpoint create \
  --name "FireRed-Image-Edit" \
  --image "your-username/firered-image-serverless:latest" \
  --gpu-count 1 \
  --gpu-type "A100" \
  --container-disk-gb 50 \
  --volume-gb 100
```

#### 4. 查看部署状态
```bash
runpod endpoint list
```

---

## ✅ 第四步：测试 Endpoint

### 1. 获取 Endpoint URL
```
在 Runpod Dashboard 中找到你的 Endpoint
复制 Endpoint URL，格式如下:
https://api.runpod.io/v2/{endpoint_id}/run
```

### 2. 测试单图编辑

#### 使用 Python
```python
import requests
import base64
import time
import json

# 配置
ENDPOINT_ID = "your-endpoint-id"  # 替换为你的 Endpoint ID
ENDPOINT_URL = f"https://api.runpod.io/v2/{ENDPOINT_ID}/run"

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

print("📤 发送请求...")
response = requests.post(ENDPOINT_URL, json=payload)
job_id = response.json()["id"]
print(f"✅ 任务已提交，Job ID: {job_id}")

# 轮询结果
print("⏳ 等待处理...")
while True:
    status_url = f"https://api.runpod.io/v2/{ENDPOINT_ID}/status/{job_id}"
    status = requests.get(status_url).json()

    print(f"状态: {status['status']}")

    if status["status"] == "COMPLETED":
        result = status["output"]
        print("✅ 处理完成!")

        # 保存结果
        image_data = base64.b64decode(result["image"])
        with open('result.png', 'wb') as f:
            f.write(image_data)

        print(f"✅ 结果已保存: result.png")
        print(f"📊 信息: {json.dumps({k:v for k,v in result.items() if k != 'image'}, indent=2)}")
        break

    elif status["status"] == "FAILED":
        print(f"❌ 处理失败: {status.get('error', 'Unknown error')}")
        break

    time.sleep(2)
```

#### 使用 cURL
```bash
# 1. 发送请求
curl -X POST https://api.runpod.io/v2/{endpoint_id}/run \
  -H "Content-Type: application/json" \
  -d '{
    "type": "edit",
    "image": "base64_encoded_image_here",
    "prompt": "person wearing a red dress",
    "num_inference_steps": 30
  }' > job.json

# 2. 获取 Job ID
JOB_ID=$(jq -r '.id' job.json)
echo "Job ID: $JOB_ID"

# 3. 轮询状态
while true; do
  curl -s https://api.runpod.io/v2/{endpoint_id}/status/$JOB_ID | jq .
  sleep 2
done
```

### 3. 测试多图融合

```python
import requests
import base64
import time

ENDPOINT_ID = "your-endpoint-id"
ENDPOINT_URL = f"https://api.runpod.io/v2/{ENDPOINT_ID}/run"

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

print("📤 发送多图融合请求...")
response = requests.post(ENDPOINT_URL, json=payload)
job_id = response.json()["id"]

# 轮询结果
while True:
    status_url = f"https://api.runpod.io/v2/{ENDPOINT_ID}/status/{job_id}"
    status = requests.get(status_url).json()

    if status["status"] == "COMPLETED":
        result = status["output"]
        image_data = base64.b64decode(result["image"])
        with open('merged.png', 'wb') as f:
            f.write(image_data)
        print("✅ 融合完成: merged.png")
        break

    time.sleep(2)
```

---

## 🔍 第五步：监控和管理

### 查看 Endpoint 状态
```bash
# 使用 CLI
runpod endpoint list

# 或访问 Web UI
# https://www.runpod.io/console/serverless/endpoints
```

### 查看日志
```bash
# 在 Runpod Dashboard 中
# 点击 Endpoint → "Logs"
```

### 调整配置
```bash
# 增加副本数（自动扩展）
runpod endpoint update {endpoint_id} --replicas 2

# 更改 GPU
runpod endpoint update {endpoint_id} --gpu-type "RTX4090"
```

### 删除 Endpoint
```bash
# 停止使用时删除以节省成本
runpod endpoint delete {endpoint_id}
```

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

## 🐛 常见问题

### Q1: 镜像上传失败
```bash
# 检查 Docker 登录
docker login

# 重新标记镜像
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest

# 重新推送
docker push your-username/firered-image-serverless:latest
```

### Q2: Endpoint 部署超时
```
解决方案:
1. 增加容器磁盘大小 (50GB → 100GB)
2. 选择不同的 GPU
3. 检查网络连接
4. 查看 Runpod 日志
```

### Q3: 请求超时
```python
# 增加超时时间
response = requests.post(
    ENDPOINT_URL,
    json=payload,
    timeout=600  # 10 分钟
)
```

### Q4: 模型加载失败
```
解决方案:
1. 检查容器磁盘大小 (至少 50GB)
2. 检查卷大小 (至少 100GB)
3. 查看 Runpod 日志
4. 重新部署 Endpoint
```

---

## 📊 完整工作流示例

```python
#!/usr/bin/env python3
"""完整的 Runpod Serverless 工作流"""

import requests
import base64
import time
import sys

class RunpodFireRedClient:
    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id
        self.base_url = f"https://api.runpod.io/v2/{endpoint_id}"

    def edit_image(self, image_path, prompt, num_steps=30):
        """编辑图像"""
        # 读取图像
        with open(image_path, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode()

        # 发送请求
        payload = {
            "type": "edit",
            "image": image_base64,
            "prompt": prompt,
            "num_inference_steps": num_steps
        }

        print(f"📤 发送请求: {prompt[:50]}...")
        response = requests.post(f"{self.base_url}/run", json=payload)
        job_id = response.json()["id"]
        print(f"✅ Job ID: {job_id}")

        # 轮询结果
        return self._wait_for_result(job_id)

    def _wait_for_result(self, job_id, max_wait=600):
        """等待结果"""
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait:
                print(f"❌ 超时 ({max_wait}s)")
                return None

            status = requests.get(f"{self.base_url}/status/{job_id}").json()

            if status["status"] == "COMPLETED":
                print("✅ 处理完成!")
                return status["output"]

            elif status["status"] == "FAILED":
                print(f"❌ 失败: {status.get('error')}")
                return None

            print(f"⏳ 处理中... ({int(elapsed)}s)")
            time.sleep(2)

# 使用
if __name__ == "__main__":
    # 配置
    ENDPOINT_ID = "your-endpoint-id"  # 替换为你的 Endpoint ID

    # 创建客户端
    client = RunpodFireRedClient(ENDPOINT_ID)

    # 编辑图像
    result = client.edit_image(
        "person.png",
        "person wearing a beautiful red dress, professional photo",
        num_steps=30
    )

    if result:
        # 保存结果
        image_data = base64.b64decode(result["image"])
        with open("result.png", "wb") as f:
            f.write(image_data)
        print("✅ 结果已保存: result.png")
```

---

## ✅ 部署检查清单

- [ ] Docker 已安装
- [ ] Docker Hub 账户已创建
- [ ] 镜像已构建
- [ ] 镜像已推送到 Docker Hub
- [ ] Runpod 账户已创建
- [ ] Endpoint 已部署
- [ ] 环境变量已配置
- [ ] 测试请求成功
- [ ] 结果已保存

---

## 🎉 部署完成！

现在你可以：
1. ✅ 通过 Runpod Serverless 调用 API
2. ✅ 进行图像换装
3. ✅ 进行多图融合
4. ✅ 自动扩展处理请求

**下一步**: 集成到你的应用中！

---

**需要帮助？** 查看 `DOCKER_DEPLOYMENT.md` 或 `API_USAGE.md`
