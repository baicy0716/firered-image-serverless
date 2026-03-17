# FireRed-Image-Edit API 使用指南

## 概述

FireRed-Image-Edit 是一个基于 Qwen 的图像编辑模型，通过 FastAPI 暴露 REST API 接口。支持单图编辑和多图融合。

## 快速开始

### 1. 启动 API 服务

在 runpod 服务器上：

```bash
cd /workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit
python3 firered_rest_api.py
```

服务将在 `http://localhost:8080` 启动

### 2. 检查健康状态

```bash
curl http://localhost:8080/health
```

响应：
```json
{
  "status": "ok",
  "service": "FireRed-Image-Edit API",
  "version": "1.0.0"
}
```

### 3. 编辑图像

```bash
curl -X POST http://localhost:8080/edit \
  -F "image=@/path/to/image.png" \
  -F "prompt=a beautiful portrait with warm lighting" \
  -F "num_inference_steps=30" \
  -o result.png
```

## API 端点详解

### GET /health
健康检查端点

**响应:**
```json
{
  "status": "ok",
  "service": "FireRed-Image-Edit API",
  "version": "1.0.0"
}
```

---

### GET /models
列出可用模型

**响应:**
```json
{
  "models": [
    "FireRed-Image-Edit-1.1",
    "FireRed-Image-Edit-1.0"
  ]
}
```

---

### POST /edit
编辑单张图像

**请求参数:**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| image | file | ✅ | - | 输入图像 (PNG/JPG) |
| prompt | string | ✅ | - | 编辑提示词 |
| model_name | string | ❌ | FireRed-Image-Edit-1.1 | 使用的模型 |
| num_inference_steps | int | ❌ | 40 | 推理步数 (1-100) |
| cfg_scale | float | ❌ | 4.0 | 控制强度 (0.0-20.0) |
| seed | int | ❌ | 49 | 随机种子 |
| return_base64 | bool | ❌ | false | 是否返回 base64 编码 |

**响应 (return_base64=false):**
- Content-Type: `image/png`
- Body: 二进制 PNG 图像

**响应 (return_base64=true):**
```json
{
  "status": "success",
  "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "format": "base64",
  "model": "FireRed-Image-Edit-1.1",
  "prompt": "a beautiful portrait"
}
```

---

### POST /edit-batch
编辑多张图像（用于多图融合）

**请求参数:**

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| images | file[] | ✅ | - | 多个输入图像 |
| prompt | string | ✅ | - | 编辑提示词 |
| model_name | string | ❌ | FireRed-Image-Edit-1.1 | 使用的模型 |
| num_inference_steps | int | ❌ | 40 | 推理步数 (1-100) |
| cfg_scale | float | ❌ | 4.0 | 控制强度 (0.0-20.0) |
| seed | int | ❌ | 49 | 随机种子 |

**响应:**
- Content-Type: `image/png`
- Body: 二进制 PNG 图像

---

### GET /docs-custom
自定义 API 文档

**响应:**
```json
{
  "service": "FireRed-Image-Edit API",
  "version": "1.0.0",
  "endpoints": {
    "GET /health": "Health check",
    "GET /models": "List available models",
    "POST /edit": "Edit a single image",
    "POST /edit-batch": "Edit multiple images"
  },
  "models": [
    "FireRed-Image-Edit-1.1 (Latest, optimized for portrait consistency)",
    "FireRed-Image-Edit-1.0 (Base model)"
  ]
}
```

## 使用示例

### Python 客户端

```python
from api_client import FireRedImageAPI

# 初始化客户端
client = FireRedImageAPI("http://localhost:8080")

# 编辑图像
result = client.edit_image(
    image_path="/path/to/image.png",
    prompt="a beautiful portrait with professional makeup",
    num_inference_steps=30,
    cfg_scale=4.0,
    return_base64=True
)

if result.get("status") == "success":
    print(f"✅ 编辑成功: {result['image'][:50]}...")
else:
    print(f"❌ 编辑失败: {result['message']}")
```

### cURL 示例

**单图编辑 (返回 PNG):**
```bash
curl -X POST http://localhost:8080/edit \
  -F "image=@portrait.png" \
  -F "prompt=a beautiful portrait with warm lighting" \
  -F "num_inference_steps=30" \
  -F "cfg_scale=4.0" \
  -o result.png
```

**单图编辑 (返回 base64):**
```bash
curl -X POST http://localhost:8080/edit \
  -F "image=@portrait.png" \
  -F "prompt=a beautiful portrait" \
  -F "return_base64=true" | jq .image
```

**多图融合:**
```bash
curl -X POST http://localhost:8080/edit-batch \
  -F "images=@image1.png" \
  -F "images=@image2.png" \
  -F "prompt=merge these images seamlessly" \
  -o merged.png
```

## 参数调优指南

### num_inference_steps
- **范围:** 1-100
- **默认:** 40
- **说明:** 推理步数越多，质量越好但速度越慢
- **建议:** 20-50 为最佳平衡

### cfg_scale
- **范围:** 0.0-20.0
- **默认:** 4.0
- **说明:** 控制提示词的影响强度
- **建议:**
  - 3.0-5.0: 保留更多原始图像特征
  - 5.0-8.0: 平衡原始和编辑效果
  - 8.0+: 更强的编辑效果

### seed
- **范围:** 任意整数
- **默认:** 49
- **说明:** 控制随机性，相同 seed 产生相同结果
- **建议:** 用于复现结果

## 常见问题

### Q: 如何获得最佳编辑效果？
A:
1. 使用清晰、高质量的输入图像
2. 编写详细的提示词（如 "a beautiful portrait with warm lighting and professional makeup"）
3. 调整 `num_inference_steps` (30-50) 和 `cfg_scale` (4.0-6.0)
4. 尝试不同的 seed 值

### Q: 支持哪些图像格式？
A: PNG 和 JPG 格式

### Q: 处理时间多长？
A: 取决于 `num_inference_steps`，通常 20-50 步需要 30-120 秒

### Q: 可以编辑多少张图像？
A: `/edit-batch` 支持任意数量，但受 GPU 内存限制

## 远程访问

### 通过 SSH 隧道访问

```bash
ssh -L 8080:localhost:8080 -p 34597 root@213.173.102.178
```

然后访问 `http://localhost:8080`

### 直接远程访问

```bash
curl http://213.173.102.178:8080/health
```

## 故障排除

### 错误: "No space left on device"
- 检查磁盘空间: `df -h`
- 清理缓存: `rm -rf ~/.cache/huggingface/*`

### 错误: "Address already in use"
- 查找占用端口的进程: `lsof -i :8080`
- 杀死进程: `kill <PID>`

### 错误: "Model not found"
- 确保模型已下载: `python3 download_model.py`
- 检查 HuggingFace 缓存: `ls ~/.cache/huggingface/hub/`

## 文件位置

- **API 脚本:** `/workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/firered_rest_api.py`
- **日志文件:** `/workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/api_server.log`
- **模型缓存:** `~/.cache/huggingface/hub/`
- **Python 客户端:** `./api_client.py`

## 许可证

FireRed-Image-Edit 由 FireRed Team 开发
