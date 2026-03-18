# 🎨 FireRed ComfyUI Serverless

FireRed 图像编辑模型的快速免编排部署包 - 基于 ComfyUI 的一键启动方案

## 📋 项目概述

这是一个完整的 Serverless 部署包，用于快速部署 FireRed 智能图像编辑工作流。支持本地、Docker、RunPod 等多种部署方式。

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

### 方式 2：Docker 部署

```bash
# 构建镜像
docker build -f Dockerfile.serverless -t firered-comfyui:latest .

# 运行容器（需要 GPU 支持）
docker run --gpus all -p 8188:8188 -p 8080:8080 firered-comfyui:latest
```

### 方式 3：Serverless 部署（RunPod/其他平台）

```bash
# 在 Serverless 环境中执行
git clone https://github.com/baicy0716/firered-image-serverless.git
cd firered-image-serverless
chmod +x runpod_serverless_init.sh
./runpod_serverless_init.sh
```

## 📁 项目结构

```
firered-image-serverless/
├── comfyui.json                      # ComfyUI 工作流配置
├── runpod_serverless_init.sh         # 初始化脚本（自动安装依赖和模型）
├── runpod_serverless_handler.py      # Serverless Handler
├── Dockerfile.serverless             # Docker 镜像定义
├── download_models.py                # 模型下载脚本
├── quick_start.sh                    # 快速启动脚本
├── requirements_api.txt              # Python 依赖
├── README.md                         # 本文件
├── COMFYUI_DEPLOYMENT.md             # 工作流详细说明
└── .github/workflows/                # CI/CD 配置
```

## 🔌 API 使用

### 请求格式

```bash
curl -X POST http://localhost:8080/process \
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
        "image2": "base64_encoded_garment_image"
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
    "base64_encoded_output_image"
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

工作流使用以下模型（总大小约 20GB）：

| 模型 | 大小 | 用途 |
|------|------|------|
| qwen2.5vl-7b-bf16.safetensors | ~7GB | 文本和图像编码 |
| qwen_image_vae.safetensors | ~2GB | 图像编码/解码 |
| FireRed-Image-Edit-1.1-transformer.safetensors | ~10GB | 扩散模型 |
| FireRed-Image-Edit-1.0-Lightning-8steps-v1.1.safetensors | ~100MB | 加速 LoRA |

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

## 🚨 故障排除

### 问题：模型加载失败

```bash
# 手动下载模型
python3 download_models.py
```

### 问题：处理超时

- 减少 `steps` 参数
- 启用 `use_lora`
- 检查 GPU 显存

### 问题：内存不足

- 使用更大的 GPU
- 减少并发数
- 启用 `use_lora`

### 问题：磁盘空间不足

- 检查磁盘空间：`df -h`
- 清理缓存：`rm -rf ~/.cache/huggingface/*`

## 📚 详细文档

- [ComfyUI 工作流说明](./COMFYUI_DEPLOYMENT.md) - 工作流节点和参数详解

## 🔗 相关链接

- [GitHub 仓库](https://github.com/baicy0716/firered-image-serverless)
- [ComfyUI 官网](https://github.com/comfyanonymous/ComfyUI)
- [FireRed 模型](https://huggingface.co/FireRedTeam)

## 📄 许可证

MIT License

## 👨‍💻 开发者

- 项目维护者：baicy0716
- 最后更新：2026-03-18

---

**立即开始：** `./quick_start.sh init`
