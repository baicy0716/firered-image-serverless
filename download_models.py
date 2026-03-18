#!/usr/bin/env python3
"""
下载 FireRed-Image-Edit 模型到 ComfyUI
"""

import os
import requests
from pathlib import Path
from tqdm import tqdm

# ComfyUI 模型目录
COMFYUI_BASE = "/workspace/runpod-slim/ComfyUI"
MODELS = {
    "diffusion_models": [
        {
            "name": "FireRed-Image-Edit-1.1-transformer.safetensors",
            "url": "https://huggingface.co/FireRedTeam/FireRed-Image-Edit-1.1-ComfyUI/resolve/main/FireRed-Image-Edit-1.1-transformer.safetensors"
        }
    ],
    "loras": [
        {
            "name": "FireRed-Image-Edit-1.0-Lightning-8steps-v1.1.safetensors",
            "url": "https://huggingface.co/FireRedTeam/FireRed-Image-Edit-1.0-ComfyUI/resolve/main/FireRed-Image-Edit-1.0-Lightning-8steps-v1.1.safetensors"
        }
    ],
    "text_encoders": [
        {
            "name": "qwen2.5vl-7b-bf16.safetensors",
            "url": "https://huggingface.co/FireRedTeam/FireRed-Image-Edit-1.0-ComfyUI/resolve/main/qwen2.5vl-7b-bf16.safetensors"
        }
    ],
    "vae": [
        {
            "name": "qwen_image_vae.safetensors",
            "url": "https://huggingface.co/FireRedTeam/FireRed-Image-Edit-1.0-ComfyUI/resolve/main/qwen_image_vae.safetensors"
        }
    ]
}

def download_file(url, dest_path):
    """下载文件并显示进度"""
    if os.path.exists(dest_path):
        print(f"✅ 文件已存在: {dest_path}")
        return True

    print(f"📥 下载: {os.path.basename(dest_path)}")
    print(f"   URL: {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        with open(dest_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

        print(f"✅ 下载完成: {dest_path}")
        return True

    except Exception as e:
        print(f"❌ 下载失败: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False

def main():
    print("=" * 60)
    print("FireRed-Image-Edit 模型下载工具")
    print("=" * 60)

    # 检查 ComfyUI 目录
    if not os.path.exists(COMFYUI_BASE):
        print(f"❌ ComfyUI 目录不存在: {COMFYUI_BASE}")
        return

    print(f"✅ ComfyUI 目录: {COMFYUI_BASE}\n")

    # 下载所有模型
    success_count = 0
    total_count = 0

    for model_type, models in MODELS.items():
        print(f"\n📦 {model_type}")
        print("-" * 60)

        model_dir = os.path.join(COMFYUI_BASE, "models", model_type)

        for model in models:
            total_count += 1
            dest_path = os.path.join(model_dir, model["name"])

            if download_file(model["url"], dest_path):
                success_count += 1

            print()

    print("=" * 60)
    print(f"下载完成: {success_count}/{total_count} 成功")
    print("=" * 60)

    if success_count == total_count:
        print("\n✅ 所有模型已就绪!")
        print("\n下一步:")
        print("1. 在 ComfyUI 中加载工作流: comfyui.json")
        print("2. 或启动 API 服务器: python comfyui_api_server.py")
    else:
        print("\n⚠️  部分模型下载失败，请检查网络连接")

if __name__ == "__main__":
    main()
