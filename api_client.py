#!/usr/bin/env python3
"""
FireRed-Image-Edit API 测试和使用指南
"""

import os
import sys
import io
import base64
import json
from pathlib import Path
from typing import Optional
from PIL import Image
import requests

# API 配置
API_BASE_URL = "http://localhost:8080"
REMOTE_API_URL = "http://213.173.102.178:8080"  # 远程服务器


class FireRedImageAPI:
    """FireRed-Image-Edit API 客户端"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def health_check(self) -> dict:
        """检查 API 健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_models(self) -> dict:
        """列出可用模型"""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def edit_image(
        self,
        image_path: str,
        prompt: str,
        model_name: str = "FireRed-Image-Edit-1.1",
        num_inference_steps: int = 40,
        cfg_scale: float = 4.0,
        seed: int = 49,
        return_base64: bool = False,
    ) -> dict:
        """编辑单张图像"""
        try:
            with open(image_path, "rb") as f:
                files = {"image": f}
                data = {
                    "prompt": prompt,
                    "model_name": model_name,
                    "num_inference_steps": num_inference_steps,
                    "cfg_scale": cfg_scale,
                    "seed": seed,
                    "return_base64": return_base64,
                }

                response = requests.post(
                    f"{self.base_url}/edit",
                    files=files,
                    data=data,
                    timeout=300,
                )

                if response.status_code == 200:
                    if return_base64:
                        return response.json()
                    else:
                        # 保存二进制图像
                        return {
                            "status": "success",
                            "image_data": response.content,
                            "content_type": response.headers.get("content-type"),
                        }
                else:
                    return {
                        "status": "error",
                        "code": response.status_code,
                        "message": response.text,
                    }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def edit_batch(
        self,
        image_paths: list,
        prompt: str,
        model_name: str = "FireRed-Image-Edit-1.1",
        num_inference_steps: int = 40,
        cfg_scale: float = 4.0,
        seed: int = 49,
    ) -> dict:
        """编辑多张图像（用于多图融合）"""
        try:
            files = [("images", open(path, "rb")) for path in image_paths]
            data = {
                "prompt": prompt,
                "model_name": model_name,
                "num_inference_steps": num_inference_steps,
                "cfg_scale": cfg_scale,
                "seed": seed,
            }

            response = requests.post(
                f"{self.base_url}/edit-batch",
                files=files,
                data=data,
                timeout=300,
            )

            # 关闭所有文件
            for _, f in files:
                f.close()

            if response.status_code == 200:
                return {
                    "status": "success",
                    "image_data": response.content,
                    "content_type": response.headers.get("content-type"),
                }
            else:
                return {
                    "status": "error",
                    "code": response.status_code,
                    "message": response.text,
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}


def create_test_image(width: int = 512, height: int = 512) -> str:
    """创建测试图像"""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    test_path = "/tmp/test_image.png"
    img.save(test_path)
    return test_path


def main():
    """主函数 - 演示 API 使用"""
    print("=" * 60)
    print("FireRed-Image-Edit API 使用指南")
    print("=" * 60)

    # 初始化客户端
    client = FireRedImageAPI(API_BASE_URL)

    # 1. 健康检查
    print("\n1️⃣  健康检查...")
    health = client.health_check()
    print(json.dumps(health, indent=2, ensure_ascii=False))

    # 2. 列出模型
    print("\n2️⃣  可用模型...")
    models = client.list_models()
    print(json.dumps(models, indent=2, ensure_ascii=False))

    # 3. 编辑图像
    print("\n3️⃣  编辑图像...")
    test_image = create_test_image()
    print(f"✅ 测试图像已创建: {test_image}")

    result = client.edit_image(
        image_path=test_image,
        prompt="a beautiful portrait with warm lighting and professional makeup",
        num_inference_steps=20,
        cfg_scale=4.0,
        return_base64=True,
    )

    if result.get("status") == "success":
        print("✅ 图像编辑成功!")
        print(f"   - 模型: {result.get('model')}")
        print(f"   - 提示词: {result.get('prompt')}")
        print(f"   - 图像大小: {len(result.get('image', ''))} 字节")

        # 保存结果
        if "image" in result:
            output_path = "/tmp/edited_image.png"
            image_data = base64.b64decode(result["image"])
            with open(output_path, "wb") as f:
                f.write(image_data)
            print(f"   - 已保存到: {output_path}")
    else:
        print(f"❌ 编辑失败: {result.get('message')}")

    print("\n" + "=" * 60)
    print("API 端点说明:")
    print("=" * 60)
    print("""
GET /health
  - 健康检查
  - 返回: {"status": "ok", "service": "...", "version": "..."}

GET /models
  - 列出可用模型
  - 返回: {"models": ["FireRed-Image-Edit-1.1", ...]}

POST /edit
  - 编辑单张图像
  - 参数:
    * image (file): 输入图像
    * prompt (string): 编辑提示词
    * model_name (string): 模型名称，默认 "FireRed-Image-Edit-1.1"
    * num_inference_steps (int): 推理步数，1-100，默认 40
    * cfg_scale (float): 控制强度，0.0-20.0，默认 4.0
    * seed (int): 随机种子，默认 49
    * return_base64 (bool): 是否返回 base64，默认 false
  - 返回: 编辑后的图像 (PNG) 或 JSON (base64)

POST /edit-batch
  - 编辑多张图像（用于多图融合）
  - 参数: 同 /edit，但 images 为多个文件
  - 返回: 融合后的图像 (PNG)

GET /docs-custom
  - 自定义文档
  - 返回: API 文档 JSON
    """)

    print("\n" + "=" * 60)
    print("使用示例 (curl):")
    print("=" * 60)
    print("""
# 1. 健康检查
curl http://localhost:8080/health

# 2. 编辑图像 (返回 PNG)
curl -X POST http://localhost:8080/edit \\
  -F "image=@/path/to/image.png" \\
  -F "prompt=a beautiful portrait" \\
  -F "num_inference_steps=30" \\
  -o result.png

# 3. 编辑图像 (返回 base64)
curl -X POST http://localhost:8080/edit \\
  -F "image=@/path/to/image.png" \\
  -F "prompt=a beautiful portrait" \\
  -F "return_base64=true" | jq .image

# 4. 编辑多张图像
curl -X POST http://localhost:8080/edit-batch \\
  -F "images=@image1.png" \\
  -F "images=@image2.png" \\
  -F "prompt=merge these images" \\
  -o result.png
    """)


if __name__ == "__main__":
    main()
