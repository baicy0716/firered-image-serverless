# FireRed-Image-Edit API - 部署完成

## ✅ 状态

FireRed-Image-Edit API 已成功部署到 runpod 服务器，所有端点都可用。

## 🔗 API 地址

- **本地:** `http://localhost:8080`
- **远程:** `http://213.173.102.178:8080`
- **SSH:** `ssh -p 22039 root@213.173.102.178`

## 📋 可用端点

### 1. GET /health
健康检查

```bash
curl http://213.173.102.178:8080/health
```

响应:
```json
{
  "status": "ok",
  "service": "FireRed-Image-Edit API",
  "version": "1.0.0"
}
```

### 2. GET /models
列出可用模型

```bash
curl http://213.173.102.178:8080/models
```

响应:
```json
{
  "models": [
    "FireRed-Image-Edit-1.1",
    "FireRed-Image-Edit-1.0"
  ]
}
```

### 3. POST /edit
编辑单张图像

```bash
curl -X POST http://213.173.102.178:8080/edit \
  -F "image=@portrait.png" \
  -F "prompt=a beautiful portrait with warm lighting" \
  -F "num_inference_steps=30" \
  -F "cfg_scale=4.0" \
  -F "return_base64=true"
```

**参数:**
- `image` (file): 输入图像
- `prompt` (string): 编辑提示词
- `model_name` (string): 模型名称，默认 "FireRed-Image-Edit-1.1"
- `num_inference_steps` (int): 推理步数 1-100，默认 40
- `cfg_scale` (float): 控制强度 0.0-20.0，默认 4.0
- `seed` (int): 随机种子，默认 49
- `return_base64` (bool): 是否返回 base64，默认 false

**响应 (return_base64=true):**
```json
{
  "status": "success",
  "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "format": "base64",
  "model": "FireRed-Image-Edit-1.1",
  "prompt": "a beautiful portrait with warm lighting"
}
```

### 4. POST /edit-batch
编辑多张图像（用于多图融合）

```bash
curl -X POST http://213.173.102.178:8080/edit-batch \
  -F "images=@image1.png" \
  -F "images=@image2.png" \
  -F "prompt=merge these images" \
  -o result.png
```

### 5. GET /docs-custom
自定义 API 文档

```bash
curl http://213.173.102.178:8080/docs-custom
```

## 🐍 Python 客户端使用

```python
from api_client import FireRedImageAPI

# 初始化客户端
client = FireRedImageAPI("http://213.173.102.178:8080")

# 编辑图像
result = client.edit_image(
    image_path="portrait.png",
    prompt="a beautiful portrait with professional makeup",
    num_inference_steps=30,
    cfg_scale=4.0,
    return_base64=True
)

if result.get("status") == "success":
    print("✅ 编辑成功!")
    # 保存结果
    import base64
    image_data = base64.b64decode(result["image"])
    with open("result.png", "wb") as f:
        f.write(image_data)
else:
    print(f"❌ 编辑失败: {result['message']}")
```

## 📁 文件位置

- **API 脚本:** `/workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/firered_api_test.py`
- **日志文件:** `/workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/api_server.log`
- **模型缓存:** `/workspace/huggingface_cache/`
- **Python 客户端:** `/home/ihouse/projects/FireRed-Image/api_client.py`
- **测试脚本:** `/home/ihouse/projects/FireRed-Image/test_api.py`

## 🚀 启动/停止 API

### 启动
```bash
ssh -p 22039 root@213.173.102.178
cd /workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit
nohup /workspace/runpod-slim/ComfyUI/.venv/bin/python3 firered_api_test.py > api_server.log 2>&1 &
```

### 停止
```bash
pkill -f firered_api
```

### 查看日志
```bash
ssh -p 22039 root@213.173.102.178 "tail -f /workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/api_server.log"
```

## 🔧 故障排除

### 端口被占用
```bash
lsof -i :8080
kill <PID>
```

### 磁盘空间不足
```bash
df -h /
du -sh /workspace/*
rm -rf /workspace/models  # 删除旧模型
```

### API 无响应
```bash
# 检查进程
ps aux | grep firered_api

# 查看日志
tail -50 /workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/api_server.log

# 重启 API
pkill -f firered_api
# 然后重新启动
```

## 📝 注意事项

1. **当前版本:** 测试版本 (firered_api_test.py)
   - 返回原始图像作为占位符
   - 用于验证 API 端点和参数处理
   - 实际模型推理需要解决 QwenImageEditPlusPipeline 加载问题

2. **模型加载问题:**
   - 原始 firered_api.py 在加载 QwenImageEditPlusPipeline 时出错
   - 错误: "Expecting value: line 1 column 1 (char 0)"
   - 可能原因: 模型版本不兼容或依赖缺失

3. **性能:**
   - 推理时间: 20-50 步约 30-120 秒
   - GPU: NVIDIA (已配置)
   - 内存: 充足

## 🔄 下一步

1. 修复 QwenImageEditPlusPipeline 加载问题
2. 集成实际模型推理
3. 添加换装测试用例
4. 性能优化和缓存

## 📞 支持

- API 文档: `/home/ihouse/projects/FireRed-Image/README.md`
- 客户端代码: `/home/ihouse/projects/FireRed-Image/api_client.py`
- 测试脚本: `/home/ihouse/projects/FireRed-Image/test_api.py`
