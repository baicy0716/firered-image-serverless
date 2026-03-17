# ⚡ Runpod Serverless 快速部署清单

## 🎯 5 分钟快速部署

### ✅ 第 1 步：构建镜像 (2 分钟)

```bash
cd /home/ihouse/projects/FireRed-Image

# 构建 Serverless 镜像
docker build -t firered-image-serverless:latest -f Dockerfile.serverless .

# 标记镜像
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest
```

### ✅ 第 2 步：推送镜像 (3 分钟)

```bash
# 登录 Docker Hub
docker login

# 推送镜像
docker push your-username/firered-image-serverless:latest

# 等待完成...
```

### ✅ 第 3 步：在 Runpod 部署 (5 分钟)

1. 访问 https://www.runpod.io/
2. 登录账户
3. 点击 "Serverless" → "Endpoints"
4. 点击 "Create Endpoint"
5. 选择 "Custom Image"
6. 输入: `your-username/firered-image-serverless:latest`
7. GPU: 选择 "1x A100" 或 "1x RTX 4090"
8. 容器磁盘: 50 GB
9. 卷大小: 100 GB
10. 点击 "Deploy"
11. 等待部署完成，复制 Endpoint ID

---

## 🧪 测试 (1 分钟)

```python
import requests
import base64
import time

ENDPOINT_ID = "your-endpoint-id"  # 替换为你的 ID
ENDPOINT_URL = f"https://api.runpod.io/v2/{ENDPOINT_ID}/run"

# 读取图像
with open('person.png', 'rb') as f:
    image_base64 = base64.b64encode(f.read()).decode()

# 发送请求
payload = {
    "type": "edit",
    "image": image_base64,
    "prompt": "person wearing a red dress",
    "num_inference_steps": 30
}

response = requests.post(ENDPOINT_URL, json=payload)
job_id = response.json()["id"]

# 等待结果
while True:
    status = requests.get(f"{ENDPOINT_URL.replace('/run', '/status')}/{job_id}").json()
    if status["status"] == "COMPLETED":
        result = status["output"]
        image_data = base64.b64decode(result["image"])
        with open('result.png', 'wb') as f:
            f.write(image_data)
        print("✅ 完成!")
        break
    time.sleep(2)
```

---

## 📋 部署前检查

- [ ] Docker 已安装: `docker --version`
- [ ] Docker Hub 账户已创建: https://hub.docker.com/
- [ ] Runpod 账户已创建: https://www.runpod.io/
- [ ] 有测试图像: `person.png`

---

## 🚨 常见错误

### 错误 1: "镜像不存在"
```bash
# 检查镜像是否推送成功
docker push your-username/firered-image-serverless:latest
```

### 错误 2: "部署超时"
```
解决: 增加容器磁盘到 100GB
```

### 错误 3: "模型加载失败"
```
解决: 检查卷大小是否 >= 100GB
```

---

## 💡 提示

1. **第一次部署会比较慢** (5-10 分钟)
   - 需要下载模型 (~25GB)
   - 之后会快很多

2. **成本优化**
   - 使用 RTX 4090 比 A100 便宜
   - 不用时删除 Endpoint

3. **性能优化**
   - 减少 `num_inference_steps` 加快速度
   - 增加 `num_inference_steps` 提高质量

---

## 📞 获取帮助

- 完整指南: `RUNPOD_DEPLOYMENT_GUIDE.md`
- API 文档: `API_USAGE.md`
- 模型说明: `MODEL_CAPABILITIES.md`

---

**准备好了吗？开始部署！** 🚀
