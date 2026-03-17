#!/usr/bin/env python3
"""FireRed-Image-Edit REST API - 通过 ComfyUI 节点"""

import os
import io
import base64
import json
import sys
from pathlib import Path
from PIL import Image

os.environ['HF_HOME'] = '/workspace/huggingface_cache'
os.environ['TMPDIR'] = '/workspace/tmp'

# 添加 ComfyUI 到路径
comfyui_path = Path("/workspace/runpod-slim/ComfyUI")
sys.path.insert(0, str(comfyui_path))

try:
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    os.system("pip install -q fastapi uvicorn python-multipart")
    from fastapi import FastAPI, UploadFile, File, Form, HTTPException
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn

app = FastAPI(title="FireRed-Image-Edit API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "FireRed-Image-Edit API",
        "version": "1.0.0"
    }

@app.get("/models")
async def list_models():
    return {
        "models": [
            "FireRed-Image-Edit-1.1",
            "FireRed-Image-Edit-1.0"
        ]
    }

@app.post("/edit")
async def edit_image(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    model_name: str = Form(default="FireRed-Image-Edit-1.1"),
    num_inference_steps: int = Form(default=40),
    cfg_scale: float = Form(default=4.0),
    seed: int = Form(default=49),
    return_base64: bool = Form(default=False),
):
    """编辑图像 - 换装功能"""
    try:
        print(f"Processing edit request: prompt={prompt[:50]}...")

        # 读取图像
        image_data = await image.read()
        input_image = Image.open(io.BytesIO(image_data)).convert("RGB")
        print(f"Input image size: {input_image.size}")

        # 验证参数
        if not (1 <= num_inference_steps <= 100):
            raise ValueError("num_inference_steps must be between 1 and 100")
        if not (0.0 <= cfg_scale <= 20.0):
            raise ValueError("cfg_scale must be between 0.0 and 20.0")
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("prompt cannot be empty")

        print(f"Model: {model_name}, Steps: {num_inference_steps}, CFG: {cfg_scale}, Seed: {seed}")

        # 尝试使用 ComfyUI 的 QwenImageEdit 节点
        try:
            import torch
            from nodes import QwenImageEditPlusPipeline

            print("Loading QwenImageEditPlusPipeline from ComfyUI nodes...")

            # 创建管道
            pipe = QwenImageEditPlusPipeline.from_pretrained(
                f"FireRedTeam/{model_name}",
                torch_dtype=torch.bfloat16,
            )
            pipe.to("cuda")

            # 运行推理
            with torch.inference_mode():
                result = pipe(
                    image=[input_image],
                    prompt=prompt,
                    generator=torch.Generator(device="cuda").manual_seed(seed),
                    true_cfg_scale=cfg_scale,
                    negative_prompt="",
                    num_inference_steps=num_inference_steps,
                    num_images_per_prompt=1,
                )

            output_image = result.images[0]
            print(f"Output image size: {output_image.size}")

        except Exception as e:
            print(f"ComfyUI node loading failed: {e}")
            print("Falling back to direct diffusers loading...")

            # 备选方案：直接使用 diffusers
            import torch
            from diffusers import QwenImageEditPlusPipeline

            pipe = QwenImageEditPlusPipeline.from_pretrained(
                f"FireRedTeam/{model_name}",
                torch_dtype=torch.bfloat16,
            )
            pipe.to("cuda")

            with torch.inference_mode():
                result = pipe(
                    image=[input_image],
                    prompt=prompt,
                    generator=torch.Generator(device="cuda").manual_seed(seed),
                    true_cfg_scale=cfg_scale,
                    negative_prompt="",
                    num_inference_steps=num_inference_steps,
                    num_images_per_prompt=1,
                )

            output_image = result.images[0]
            print(f"Output image size: {output_image.size}")

        # 返回响应
        if return_base64:
            buffer = io.BytesIO()
            output_image.save(buffer, format="PNG")
            buffer.seek(0)
            base64_str = base64.b64encode(buffer.getvalue()).decode()
            return JSONResponse({
                "status": "success",
                "image": base64_str,
                "format": "base64",
                "model": model_name,
                "prompt": prompt,
                "size": list(output_image.size),
            })
        else:
            buffer = io.BytesIO()
            output_image.save(buffer, format="PNG")
            buffer.seek(0)
            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="image/png",
                headers={"Content-Disposition": "attachment; filename=edited_image.png"}
            )

    except Exception as e:
        print(f"Error in /edit: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/edit-batch")
async def edit_batch(
    images: list[UploadFile] = File(...),
    prompt: str = Form(...),
    model_name: str = Form(default="FireRed-Image-Edit-1.1"),
    num_inference_steps: int = Form(default=40),
    cfg_scale: float = Form(default=4.0),
    seed: int = Form(default=49),
):
    """编辑多张图像（多图融合）"""
    try:
        print(f"Processing batch edit: {len(images)} images, prompt={prompt[:50]}...")

        input_images = []
        for idx, img_file in enumerate(images):
            img_data = await img_file.read()
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            input_images.append(img)
            print(f"Image {idx+1} size: {img.size}")

        if len(input_images) == 0:
            raise ValueError("No images provided")

        import torch
        from diffusers import QwenImageEditPlusPipeline

        pipe = QwenImageEditPlusPipeline.from_pretrained(
            f"FireRedTeam/{model_name}",
            torch_dtype=torch.bfloat16,
        )
        pipe.to("cuda")

        print(f"Running batch inference: {len(input_images)} images")

        with torch.inference_mode():
            result = pipe(
                image=input_images,
                prompt=prompt,
                generator=torch.Generator(device="cuda").manual_seed(seed),
                true_cfg_scale=cfg_scale,
                negative_prompt="",
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=1,
            )

        output_image = result.images[0]
        print(f"Output image size: {output_image.size}")

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=edited_image.png"}
        )

    except Exception as e:
        print(f"Error in /edit-batch: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/docs-custom")
async def custom_docs():
    return {
        "service": "FireRed-Image-Edit API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /models": "List available models",
            "POST /edit": "Edit a single image (clothing change, style transfer, etc)",
            "POST /edit-batch": "Edit multiple images (multi-image fusion)",
        },
        "models": [
            "FireRed-Image-Edit-1.1 (Latest, optimized for portrait consistency)",
            "FireRed-Image-Edit-1.0 (Base model)"
        ],
        "usage_examples": {
            "clothing_change": "person wearing a beautiful red dress, professional photo",
            "style_transfer": "oil painting style, impressionist",
            "multi_image_fusion": "merge person with clothing seamlessly"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
