# 🎨 FireRed ComfyUI Serverless

AI 驱动的智能图像编辑系统 - 基于 ComfyUI 和 FireRed 模型的 Serverless 部署方案

## 📋 项目概述

这是一个完整的 Serverless 部署包，用于在 RunPod、Docker 或本地环境中快速部署 FireRed 图像编辑工作流。

**核心功能：**
- 🎭 智能换装 - 将人物图片中的衣服替换为指定的衣服
- 🖼️ 多图融合 - 支持同时处理人物、衣服、配饰等多张图片
- ⚡ 快速推理 - 使用 LoRA 加速，8 步即可生成高质量结果
- 🔄 异步处理 - 支持 Serverless 异步请求
- 📦 开箱即用 - 一键部署，自动下载模型

## 🚀 快速开始

### 方式 1：本地运行（推荐用于测试）

```bash
# 1. 克隆项目
git clone https://github.com/baicy0716/firered-image-serverless.git
cd firered-image-serverless

# 2. 初始化环境
./quick_start.sh init

# 3. 启动服务
./quick_start.sh start

# 4. 查看日志
./quick_start.sh logs
```

### 方式 2：RunPod 部署（推荐用于生产）

```bash
# 在 RunPod 终端执行
cd /workspace
git clone https://github.com/baicy0716/firered-image-serverless.git
cd firered-image-serverless
chmod +x runpod_serverless_init.sh
./runpod_serverless_init.sh
```

### 方式 3：Docker 部署

```bash
# 构建镜像
docker build -f Dockerfile.serverless -t firered-comfyui:latest .

# 运行容器
docker run --gpus all -p 8188:8188 -p 8080:8080 firered-comfyui:latest
```

## 📁 项目结构

```
firered-image-serverless/
├── comfyui.json                      # ComfyUI 工作流配置
├── runpod_serverless_init.sh         # 初始化脚本（自动安装依赖和模型）
├── runpod_serverless_handler.py      # Serverless Handler（处理 RunPod 请求）
├── Dockerfile.serverless             # Docker 镜像定义
├── download_models.py                # 模型下载脚本
├── quick_start.sh                    # 快速启动脚本
├── requirements_api.txt              # Python 依赖
├── README.md                         # 本文件
├── SERVERLESS_DEPLOYMENT.md          # 详细部署文档
├── COMFYUI_DEPLOYMENT.md             # ComfyUI 工作流说明
└── .github/workflows/                # CI/CD 配置
```

## 🔌 API 使用

### 请求格式

```bash
curl -X POST https://api.runpod.io/v2/<endpoint_id>/run \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "把模特换成穿着红色连衣裙，搭配黑色高跟鞋",
      "steps": 20,
      "cfg": 4.0,
      "seed": 42,
      "use_lora": true,
      "images": {
        "image1": "base64_encoded_person_image",
        "image2": "base64_encoded_garment_image",
        "image3": "base64_encoded_accessory_image"
      }
    }
  }'
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| prompt | string | "" | 编辑提示词（必需） |
| steps | int | 40 | 推理步数（1-100） |
| cfg | float | 4.0 | CFG 强度（0-20） |
| seed | int | 43 | 随机种子 |
| use_lora | bool | true | 是否使用加速 LoRA |
| images | object | {} | 输入图片（base64 编码） |

### 响应格式

```json
{
  "status": "success",
  "prompt_id": "xxx-xxx-xxx",
  "images": [
    "http://localhost:8188/view?filename=xxx&type=output"
  ]
}
```

## 📊 工作流说明

工作流包含以下主要步骤：

1. **模型加载** - 加载 CLIP、VAE、UNET 和 LoRA 模型
2. **图像处理** - 加载和缩放输入图片
3. **文本编码** - 将提示词和图片编码为条件向量
4. **扩散采样** - 执行图像生成
5. **输出解码** - 将结果解码为图片

详见 [COMFYUI_DEPLOYMENT.md](./COMFYUI_DEPLOYMENT.md)

## 🎯 性能指标

| 配置 | 步数 | 时间 | 质量 | 用途 |
|------|------|------|------|------|
| 快速 | 20 | 30-60s | ⭐⭐⭐ | 测试 |
| 标准 | 40 | 60-120s | ⭐⭐⭐⭐ | 生产 |
| 高质量 | 60-100 | 120-300s | ⭐⭐⭐⭐⭐ | 精细化 |

## 📦 模型信息

工作流使用以下模型：

| 模型 | 大小 | 用途 |
|------|------|------|
| qwen2.5vl-7b-bf16.safetensors | ~7GB | 文本和图像编码 |
| qwen_image_vae.safetensors | ~2GB | 图像编码/解码 |
| FireRed-Image-Edit-1.1-transformer.safetensors | ~10GB | 扩散模型 |
| FireRed-Image-Edit-1.0-Lightning-8steps-v1.1.safetensors | ~100MB | 加速 LoRA |

**总大小：** ~20GB

## 🔧 配置调整

### 快速模式（推荐用于测试）
```json
{
  "steps": 20,
  "cfg": 1-2,
  "use_lora": true
}
```

### 标准模式（推荐用于生产）
```json
{
  "steps": 40,
  "cfg": 4,
  "use_lora": true
}
```

### 高质量模式
```json
{
  "steps": 60-100,
  "cfg": 4-7,
  "use_lora": false
}
```

## 📝 快速命令参考

```bash
# 初始化环境
./quick_start.sh init

# 启动服务
./quick_start.sh start

# 停止服务
./quick_start.sh stop

# 查看日志
./quick_start.sh logs

# 构建 Docker 镜像
docker build -f Dockerfile.serverless -t firered-comfyui:latest .

# 运行 Docker 容器
docker run --gpus all -p 8188:8188 -p 8080:8080 firered-comfyui:latest
```

## 🐳 Docker 镜像

### 镜像大小
- 基础镜像：~5GB
- 模型：~20GB
- 总计：~25GB

### 构建时间
- 首次构建：30-60 分钟
- 后续构建：5-10 分钟（使用缓存）

## 📚 详细文档

- [Serverless 部署指南](./SERVERLESS_DEPLOYMENT.md) - 详细的部署步骤和配置
- [ComfyUI 工作流说明](./COMFYUI_DEPLOYMENT.md) - 工作流节点和参数详解

## 🚨 故障排除

### 问题：模型加载失败

```bash
# 手动下载模型
python3 download_models.py

# 检查模型文件
ls -lh /workspace/runpod-slim/ComfyUI/models/*/
```

### 问题：处理超时

- 减少 `steps` 参数
- 启用 `use_lora`
- 检查 GPU 显存

### 问题：内存不足

- 使用更小的 GPU
- 减少并发数
- 启用 `use_lora`

## 📞 支持

如有问题，请：
1. 查看详细文档
2. 检查日志文件
3. 提交 Issue

## 📄 许可证

MIT License

## 🔗 相关链接

- [GitHub 仓库](https://github.com/baicy0716/firered-image-serverless)
- [RunPod 官网](https://www.runpod.io/)
- [ComfyUI 官网](https://github.com/comfyanonymous/ComfyUI)
- [FireRed 模型](https://huggingface.co/FireRedTeam)

## 👨‍💻 开发者

- 项目维护者：baicy0716
- 最后更新：2026-03-18

---

**立即开始：** `./quick_start.sh init`
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
