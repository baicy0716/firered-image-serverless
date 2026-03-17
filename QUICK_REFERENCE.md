# 🎯 FireRed-Image-Edit API - 快速参考

## 📍 API 地址
```
http://213.173.102.178:8080
```

## 🔗 快速命令

### 换装
```bash
curl -X POST http://213.173.102.178:8080/edit \
  -F "image=@person.png" \
  -F "prompt=person wearing a beautiful red dress, professional photo" \
  -F "num_inference_steps=30" \
  -F "return_base64=true" | jq .image | base64 -d > result.png
```

### 风格转换
```bash
curl -X POST http://213.173.102.178:8080/edit \
  -F "image=@photo.png" \
  -F "prompt=oil painting style, impressionist" \
  -F "num_inference_steps=30" \
  -o result.png
```

### 多图融合
```bash
curl -X POST http://213.173.102.178:8080/edit-batch \
  -F "images=@person.png" \
  -F "images=@dress.png" \
  -F "prompt=merge person with dress seamlessly" \
  -o result.png
```

## 📋 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `image` | 输入图像 | `@person.png` |
| `prompt` | 编辑提示词 | `"person wearing red dress"` |
| `num_inference_steps` | 推理步数 (1-100) | `30` |
| `cfg_scale` | 控制强度 (0.0-20.0) | `4.0` |
| `seed` | 随机种子 | `49` |
| `return_base64` | 返回 base64 | `true/false` |

## 🎨 提示词示例

### 换装
- `person wearing a beautiful red dress, professional photo`
- `person wearing a formal black suit and tie`
- `person wearing a summer beach dress`
- `person wearing a winter coat and scarf`

### 风格
- `oil painting style, impressionist`
- `cartoon style, anime`
- `watercolor painting`
- `pencil sketch, black and white`

### 融合
- `merge person with dress seamlessly`
- `combine images naturally`
- `fuse images together`

## ⚡ 性能

| 步数 | 时间 |
|------|------|
| 15-20 | 30-60 秒 |
| 25-35 | 45-90 秒 |
| 40-50 | 60-120 秒 |

## 🐍 Python 快速示例

```python
import requests
import base64

def edit_image(image_path, prompt):
    with open(image_path, 'rb') as f:
        response = requests.post(
            "http://213.173.102.178:8080/edit",
            files={'image': f},
            data={
                'prompt': prompt,
                'num_inference_steps': 30,
                'return_base64': True
            }
        )

    result = response.json()
    if result['status'] == 'success':
        image_data = base64.b64decode(result['image'])
        with open('result.png', 'wb') as f:
            f.write(image_data)
        return 'result.png'
    return None

# 使用
edit_image('person.png', 'person wearing a red dress')
```

## 🔍 检查状态

```bash
# 健康检查
curl http://213.173.102.178:8080/health

# 列出模型
curl http://213.173.102.178:8080/models

# API 文档
curl http://213.173.102.178:8080/docs-custom
```

## 🚀 启动/停止 API

```bash
# SSH 连接
ssh -p 22039 root@213.173.102.178

# 查看日志
tail -f /workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit/api_server.log

# 重启 API
pkill -f firered_api_final
cd /workspace/runpod-slim/ComfyUI/custom_nodes/FireRed-Image-Edit
nohup python3 firered_api_final.py > api_server.log 2>&1 &
```

## 📊 响应格式

### 成功 (return_base64=true)
```json
{
  "status": "success",
  "image": "iVBORw0KGgoAAAANSUhEUgAAAgAAAA...",
  "format": "base64",
  "model": "FireRed-Image-Edit-1.1",
  "prompt": "person wearing a red dress",
  "size": [512, 512]
}
```

### 成功 (return_base64=false)
- Content-Type: `image/png`
- Body: 二进制 PNG 数据

### 错误
```json
{
  "detail": "错误信息"
}
```

## 💡 提示

1. **快速预览**: 使用 15-20 步快速查看效果
2. **高质量**: 使用 40-50 步获得最佳质量
3. **复现结果**: 使用相同的 seed 值
4. **调整强度**: cfg_scale 越高编辑效果越强
5. **详细提示词**: 提示词越详细效果越好

---

完整文档: `/home/ihouse/projects/FireRed-Image/API_USAGE.md`
