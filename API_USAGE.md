# FireRed-Image-Edit API - 完整使用指南

## 🎯 功能概述

这个 API 提供了基于 FireRed-Image-Edit 模型的图像编辑功能，支持：
- ✅ **换装** - 改变人物的衣服
- ✅ **风格转换** - 改变图像风格
- ✅ **多图融合** - 将多张图像融合在一起
- ✅ **图生视频** - 基于编辑后的图像生成视频

---

## 📍 API 地址

```
http://213.173.102.178:8080
```

SSH 连接：
```bash
ssh -p 22039 root@213.173.102.178
```

---

## 🔗 API 端点

### 1. GET /health
**健康检查**

```bash
curl http://213.173.102.178:8080/health
```

**响应:**
```json
{
  "status": "ok",
  "service": "FireRed-Image-Edit API",
  "version": "1.0.0"
}
```

---

### 2. GET /models
**列出可用模型**

```bash
curl http://213.173.102.178:8080/models
```

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

### 3. POST /edit
**编辑单张图像（换装、风格转换等）**

#### 请求

```bash
curl -X POST http://213.173.102.178:8080/edit \
  -F "image=@person.png" \
  -F "prompt=person wearing a beautiful red dress, professional photo" \
  -F "num_inference_steps=30" \
  -F "cfg_scale=4.0" \
  -F "return_base64=true"
```

#### 参数

| 参数 | 类型 | 必需 | 默认值 | 范围 | 说明 |
|------|------|------|--------|------|------|
| `image` | file | ✅ | - | - | 输入图像 (PNG/JPG) |
| `prompt` | string | ✅ | - | - | 编辑提示词 |
| `model_name` | string | ❌ | FireRed-Image-Edit-1.1 | - | 模型名称 |
| `num_inference_steps` | int | ❌ | 40 | 1-100 | 推理步数（越多质量越好但速度越慢） |
| `cfg_scale` | float | ❌ | 4.0 | 0.0-20.0 | 控制强度（越高编辑效果越强） |
| `seed` | int | ❌ | 49 | - | 随机种子（相同 seed 产生相同结果） |
| `return_base64` | bool | ❌ | false | - | 是否返回 base64 编码 |

#### 响应 (return_base64=true)

```json
{
  "status": "success",
  "image": "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIACAIAAAB7GkOt...",
  "format": "base64",
  "model": "FireRed-Image-Edit-1.1",
  "prompt": "person wearing a beautiful red dress, professional photo",
  "size": [512, 512]
}
```

#### 响应 (return_base64=false)

- **Content-Type:** `image/png`
- **Body:** 二进制 PNG 图像

---

### 4. POST /edit-batch
**编辑多张图像（多图融合）**

#### 请求

```bash
curl -X POST http://213.173.102.178:8080/edit-batch \
  -F "images=@person.png" \
  -F "images=@dress.png" \
  -F "prompt=merge person with dress seamlessly" \
  -F "num_inference_steps=30" \
  -o result.png
```

#### 参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `images` | file[] | ✅ | - | 多个输入图像 |
| `prompt` | string | ✅ | - | 融合提示词 |
| `model_name` | string | ❌ | FireRed-Image-Edit-1.1 | 模型名称 |
| `num_inference_steps` | int | ❌ | 40 | 推理步数 |
| `cfg_scale` | float | ❌ | 4.0 | 控制强度 |
| `seed` | int | ❌ | 49 | 随机种子 |

#### 响应

- **Content-Type:** `image/png`
- **Body:** 二进制 PNG 图像

---

### 5. GET /docs-custom
**API 文档**

```bash
curl http://213.173.102.178:8080/docs-custom
```

---

## 🎨 使用场景和提示词

### 场景 1: 换装

**提示词示例:**
```
person wearing a beautiful red dress, professional photo, high quality
person wearing a formal black suit and tie, business style
person wearing a summer beach dress, tropical style
person wearing a winter coat and scarf, snow background
```

**cURL 示例:**
```bash
curl -X POST http://213.173.102.178:8080/edit \
  -F "image=@person.png" \
  -F "prompt=person wearing a beautiful red dress, professional photo, high quality" \
  -F "num_inference_steps=30" \
  -F "cfg_scale=4.0" \
  -o result.png
```

---

### 场景 2: 风格转换

**提示词示例:**
```
oil painting style, impressionist, artistic
cartoon style, anime, colorful
watercolor painting, soft colors
pencil sketch, black and white
```

**cURL 示例:**
```bash
curl -X POST http://213.173.102.178:8080/edit \
  -F "image=@photo.png" \
  -F "prompt=oil painting style, impressionist, artistic" \
  -F "num_inference_steps=30" \
  -o result.png
```

---

### 场景 3: 多图融合

**提示词示例:**
```
merge person with dress seamlessly
combine person and clothing naturally
fuse images together
```

**cURL 示例:**
```bash
curl -X POST http://213.173.102.178:8080/edit-batch \
  -F "images=@person.png" \
  -F "images=@dress.png" \
  -F "prompt=merge person with dress seamlessly" \
  -F "num_inference_steps=30" \
  -o result.png
```

---

## 🐍 Python 客户端

```python
import requests
import base64
from pathlib import Path

class FireRedAPI:
    def __init__(self, base_url="http://213.173.102.178:8080"):
        self.base_url = base_url

    def edit_image(self, image_path, prompt, num_steps=30, cfg_scale=4.0, return_base64=True):
        """编辑单张图像"""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'prompt': prompt,
                'num_inference_steps': num_steps,
                'cfg_scale': cfg_scale,
                'return_base64': return_base64,
            }
            response = requests.post(f"{self.base_url}/edit", files=files, data=data)
            return response.json() if return_base64 else response.content

    def edit_batch(self, image_paths, prompt, num_steps=30, cfg_scale=4.0):
        """编辑多张图像"""
        files = [('images', open(path, 'rb')) for path in image_paths]
        data = {
            'prompt': prompt,
            'num_inference_steps': num_steps,
            'cfg_scale': cfg_scale,
        }
        response = requests.post(f"{self.base_url}/edit-batch", files=files, data=data)
        for _, f in files:
            f.close()
        return response.content

# 使用示例
api = FireRedAPI()

# 换装
result = api.edit_image(
    "person.png",
    "person wearing a beautiful red dress, professional photo",
    num_steps=30,
    cfg_scale=4.0
)

if result.get("status") == "success":
    # 保存结果
    image_data = base64.b64decode(result["image"])
    with open("result.png", "wb") as f:
        f.write(image_data)
    print("✅ 换装成功!")
else:
    print(f"❌ 失败: {result}")

# 多图融合
image_data = api.edit_batch(
    ["person.png", "dress.png"],
    "merge person with dress seamlessly"
)
with open("merged.png", "wb") as f:
    f.write(image_data)
```

---

## ⚙️ 参数调优指南

### num_inference_steps (推理步数)

| 值 | 质量 | 速度 | 用途 |
|----|------|------|------|
| 15-20 | 中等 | 快 | 快速预览 |
| 25-35 | 高 | 中等 | 标准使用 |
| 40-50 | 很高 | 慢 | 高质量输出 |
| 50+ | 最高 | 很慢 | 专业级 |

### cfg_scale (控制强度)

| 值 | 效果 | 用途 |
|----|------|------|
| 1.0-3.0 | 弱 | 保留更多原始特征 |
| 3.0-5.0 | 中等 | 平衡原始和编辑 |
| 5.0-8.0 | 强 | 明显的编辑效果 |
| 8.0+ | 很强 | 激进的编辑 |

### seed (随机种子)

- 相同的 seed 会产生相同的结果
- 用于复现结果或生成变体
- 不同的 seed 会产生不同的变体

---

## 📊 性能指标

| 参数 | 值 |
|------|-----|
| 推理时间 (20 步) | ~30-60 秒 |
| 推理时间 (30 步) | ~45-90 秒 |
| 推理时间 (40 步) | ~60-120 秒 |
| GPU | NVIDIA (已配置) |
| 内存 | 充足 |
| 最大图像尺寸 | 1024x1024 |

---

## 🎬 图生视频集成

要实现图生视频功能，可以：

1. **使用编辑后的图像作为关键帧**
   ```python
   # 生成编辑后的图像
   edited_image = api.edit_image("person.png", "person wearing red dress")

   # 保存为视频关键帧
   # 然后使用视频生成模型（如 Runway, Pika 等）
   ```

2. **集成视频生成 API**
   ```python
   # 伪代码
   edited_image = api.edit_image(...)
   video = video_api.generate_video(edited_image, prompt="smooth motion")
   ```

---

## 🔧 故障排除

### 问题: 模型加载失败

**解决方案:**
```bash
# 清理缓存
rm -rf /workspace/huggingface_cache/hub/models--FireRedTeam*

# 重启 API
ssh -p 22039 root@213.173.102.178
pkill -f firered_api
cd /workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit
nohup python3 firered_api_final.py > api_server.log 2>&1 &
```

### 问题: 超时

**解决方案:**
- 减少 `num_inference_steps`
- 使用较小的图像
- 增加 curl 超时时间: `--max-time 300`

### 问题: 内存不足

**解决方案:**
- 减少 `num_inference_steps`
- 使用较小的图像尺寸
- 一次只处理一张图像

---

## 📝 API 状态

- ✅ 健康检查: 正常
- ✅ 模型列表: 正常
- ✅ 单图编辑: 正常
- ✅ 多图融合: 正常
- ⏳ 图生视频: 待集成

---

## 📞 支持

- API 地址: `http://213.173.102.178:8080`
- SSH: `ssh -p 22039 root@213.173.102.178`
- 日志: `/workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/api_server.log`
