# 🚀 FireRed ComfyUI Serverless 完整部署包

## 📦 项目内容

这是一个完整的 Serverless 部署包，包含：

- ✅ ComfyUI 工作流配置
- ✅ RunPod Serverless Handler
- ✅ Docker 镜像定义
- ✅ 模型自动下载脚本
- ✅ 一键启动脚本
- ✅ 完整的部署文档

## 🎯 快速开始

### 本地测试（5 分钟）

```bash
# 1. 克隆项目
git clone https://github.com/baicy0716/firered-image-serverless.git
cd firered-image-serverless

# 2. 初始化（首次运行）
./quick_start.sh init

# 3. 启动服务
./quick_start.sh start

# 4. 查看日志
./quick_start.sh logs
```

### RunPod 部署（10 分钟）

```bash
# 在 RunPod 终端执行
cd /workspace
git clone https://github.com/baicy0716/firered-image-serverless.git
cd firered-image-serverless
chmod +x runpod_serverless_init.sh
./runpod_serverless_init.sh
```

### Docker 部署

```bash
# 构建镜像
docker build -f Dockerfile.serverless -t firered-comfyui:latest .

# 运行容器
docker run --gpus all -p 8188:8188 -p 8080:8080 firered-comfyui:latest
```

## 📋 文件说明

| 文件 | 说明 |
|------|------|
| `runpod_serverless_init.sh` | 初始化脚本，自动安装依赖和下载模型 |
| `runpod_serverless_handler.py` | Serverless Handler，处理 RunPod 请求 |
| `Dockerfile.serverless` | Docker 镜像定义，包含所有依赖 |
| `comfyui.json` | ComfyUI 工作流配置 |
| `download_models.py` | 模型下载脚本 |
| `quick_start.sh` | 快速启动脚本 |
| `SERVERLESS_DEPLOYMENT.md` | 详细部署文档 |
| `COMFYUI_DEPLOYMENT.md` | ComfyUI 部署文档 |

## 🔌 API 使用

### 请求示例

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

- **prompt**: 编辑提示词（必需）
- **steps**: 推理步数，1-100（默认 40）
- **cfg**: CFG 强度，0-20（默认 4.0）
- **seed**: 随机种子（默认 43）
- **use_lora**: 是否使用加速 LoRA（默认 true）
- **images**: 输入图片（base64 编码）

## 🎨 工作流说明

工作流包含以下节点：

1. **模型加载**
   - CLIPLoader: 文本编码器（Qwen 7B）
   - VAELoader: 图像编码器
   - UNETLoader: 扩散模型
   - LoraLoaderModelOnly: 加速 LoRA

2. **图像处理**
   - LoadImage: 加载输入图片
   - FluxKontextImageScale: 缩放图片
   - VAEEncode: 编码为潜在空间

3. **文本编码**
   - TextEncodeQwenImageEditPlus: 编码提示词和图片

4. **采样**
   - KSampler: 执行扩散采样

5. **输出**
   - VAEDecode: 解码为图片
   - SaveImage: 保存输出

## 📊 性能指标

| 配置 | 步数 | 时间 | 质量 |
|------|------|------|------|
| 快速 | 20 | 30-60s | ⭐⭐⭐ |
| 标准 | 40 | 60-120s | ⭐⭐⭐⭐ |
| 高质量 | 60-100 | 120-300s | ⭐⭐⭐⭐⭐ |

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

## 🐳 Docker 镜像

### 镜像大小
- 基础镜像: ~5GB
- 模型: ~20GB
- 总计: ~25GB

### 构建时间
- 首次构建: 30-60 分钟
- 后续构建: 5-10 分钟（使用缓存）

## 📝 日志位置

- ComfyUI: `/tmp/comfyui.log`
- Serverless: `/tmp/serverless.log`
- API: `/tmp/api_server.log`

## 🚨 故障排除

### 问题：模型加载失败
```bash
# 手动下载模型
python3 download_models.py

# 检查模型文件
ls -lh /workspace/runpod-slim/ComfyUI/models/*/
```

### 问题：处理超时
- 减少 steps 参数
- 启用 use_lora
- 检查 GPU 显存

### 问题：内存不足
- 使用更小的 GPU
- 减少并发数
- 启用 use_lora

## 📚 相关文档

- [Serverless 部署指南](./SERVERLESS_DEPLOYMENT.md)
- [ComfyUI 部署指南](./COMFYUI_DEPLOYMENT.md)
- [工作流说明](./comfyui.json)

## 🔗 相关链接

- [GitHub 仓库](https://github.com/baicy0716/firered-image-serverless)
- [RunPod 官网](https://www.runpod.io/)
- [ComfyUI 官网](https://github.com/comfyanonymous/ComfyUI)
- [FireRed 模型](https://huggingface.co/FireRedTeam)

## 📄 许可证

MIT License

## 👨‍💻 开发者

- 项目维护者: baicy0716
- 最后更新: 2026-03-18

## 💬 反馈

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**快速命令参考：**

```bash
# 初始化
./quick_start.sh init

# 启动
./quick_start.sh start

# 停止
./quick_start.sh stop

# 查看日志
./quick_start.sh logs

# 构建 Docker 镜像
docker build -f Dockerfile.serverless -t firered-comfyui:latest .

# 运行 Docker 容器
docker run --gpus all -p 8188:8188 -p 8080:8080 firered-comfyui:latest
```
