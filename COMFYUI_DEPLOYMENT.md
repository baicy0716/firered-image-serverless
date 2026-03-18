# FireRed ComfyUI 工作流部署指南

## 概述

这是一个基于 ComfyUI 的图像编辑系统，使用 FireRed-Image-Edit 模型进行智能换装。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   测试页面 (Web UI)                      │
│              http://localhost:8080                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              API 服务器 (Flask)                          │
│         comfyui_api_server.py (端口 8080)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              ComfyUI 服务器                              │
│         http://localhost:8188                           │
└─────────────────────────────────────────────────────────┘
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements_api.txt
```

### 2. 启动服务

#### 方式一：使用启动脚本（推荐）

```bash
chmod +x deploy_comfyui.sh
./deploy_comfyui.sh
```

#### 方式二：手动启动

**启动 ComfyUI：**
```bash
cd /workspace/ComfyUI
python main.py
```

**启动 API 服务器（新终端）：**
```bash
cd /home/ihouse/projects/FireRed-Image
python comfyui_api_server.py
```

### 3. 访问测试页面

打开浏览器访问：http://localhost:8080

## 使用说明

### 测试页面功能

1. **上传图片**
   - 👤 人物图片：上传包含人物的图片
   - 👗 衣服图片：上传衣服或配饰的图片

2. **编辑提示词**
   - 输入详细的编辑指令，例如：
     - "把模特换成穿着红色连衣裙，搭配黑色高跟鞋"
     - "穿上蓝色牛仔裤和白色T恤"

3. **参数设置**
   - 推理步数：1-100（默认 40）
   - CFG 强度：0-20（默认 4）
   - 随机种子：用于复现结果
   - 使用加速 LoRA：勾选以加快处理速度

4. **处理结果**
   - 实时显示处理状态
   - 完成后显示输出图片

## API 端点

### 1. 处理图像

**请求：**
```
POST /api/process
Content-Type: multipart/form-data

参数：
- person_image: 人物图片文件
- garment_image: 衣服图片文件
- prompt: 编辑提示词
```

**响应：**
```json
{
  "task_id": "uuid",
  "prompt_id": "comfyui_prompt_id",
  "status": "processing"
}
```

### 2. 获取任务状态

**请求：**
```
GET /api/status/<task_id>
```

**响应：**
```json
{
  "task_id": "uuid",
  "status": "processing" | "completed"
}
```

### 3. 获取处理结果

**请求：**
```
GET /api/result/<task_id>
```

**响应：**
```json
{
  "task_id": "uuid",
  "status": "completed",
  "images": ["image_url_1", "image_url_2", ...]
}
```

## 工作流说明

### 节点组成

1. **模型加载**
   - CLIPLoader：加载文本编码器
   - VAELoader：加载 VAE 编码器
   - UNETLoader：加载扩散模型

2. **提示词编码**
   - TextEncodeQwenImageEditPlus：将文本和图片转换为条件向量

3. **图像处理**
   - LoadImage：加载输入图片
   - FluxKontextImageScale：缩放图片
   - VAEEncode：将图片编码为潜在空间

4. **采样**
   - KSampler：执行扩散采样
   - ModelSamplingAuraFlow：模型采样配置

5. **输出**
   - VAEDecode：将潜在空间解码为图片
   - SaveImage：保存输出图片

### 参数说明

- **Steps**：推理步数，越多质量越好但速度越慢
- **CFG Scale**：条件自由引导强度，控制对提示词的遵循程度
- **Seed**：随机种子，相同种子会产生相同结果
- **LoRA**：加速 LoRA，可以减少推理步数

## 故障排除

### 问题 1：无法连接到 ComfyUI

**症状：** API 服务器启动失败，提示无法连接到 ComfyUI

**解决方案：**
1. 确保 ComfyUI 已启动：`curl http://localhost:8188/system_stats`
2. 检查 ComfyUI 日志：`tail -f /tmp/comfyui.log`
3. 重启 ComfyUI

### 问题 2：端口被占用

**症状：** 启动脚本失败，提示端口已被占用

**解决方案：**
```bash
# 查看占用端口的进程
lsof -i :8080

# 杀死进程
kill -9 <PID>
```

### 问题 3：模型加载失败

**症状：** 处理请求时提示模型加载失败

**解决方案：**
1. 检查模型文件是否存在
2. 查看 ComfyUI 日志了解具体错误
3. 确保有足够的磁盘空间和内存

### 问题 4：处理超时

**症状：** 处理请求超过 10 分钟仍未完成

**解决方案：**
1. 减少推理步数
2. 检查 GPU 是否正常工作
3. 查看 ComfyUI 日志了解具体错误

## 性能优化

### 1. 使用加速 LoRA

勾选"使用加速 LoRA"可以显著加快处理速度，推荐设置：
- Steps: 8-20
- CFG: 1-4

### 2. 调整推理步数

- 快速预览：20-30 步
- 标准质量：40-50 步
- 高质量：60-100 步

### 3. 批量处理

可以修改 API 服务器支持批量处理多个请求。

## 文件说明

- `comfyui.json`：工作流配置文件
- `comfyui_api_server.py`：API 服务器
- `comfyui_workflow_setup.py`：工作流验证脚本
- `deploy_comfyui.sh`：一键部署脚本
- `requirements_api.txt`：Python 依赖

## 常见问题

**Q: 支持哪些图片格式？**
A: 支持 PNG、JPG、JPEG、WebP 等常见格式

**Q: 最大文件大小是多少？**
A: 默认 50MB，可在 API 服务器中修改

**Q: 可以自定义工作流吗？**
A: 可以，修改 `comfyui.json` 文件后重启服务

**Q: 如何保存处理历史？**
A: 可以修改 API 服务器添加数据库支持

## 许可证

MIT License

## 支持

如有问题，请查看日志或联系开发者。
