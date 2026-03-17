#!/usr/bin/env python3
"""FireRed-Image-Edit REST API - 简化版本用于测试"""

import os
import io
import base64
from pathlib import Path
from PIL import Image

os.environ['HF_HOME'] = '/workspace/huggingface_cache'
os.environ['TMPDIR'] = '/workspace/tmp'

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
    """编辑图像 - 测试版本"""
    try:
        image_data = await image.read()
        input_image = Image.open(io.BytesIO(image_data)).convert("RGB")

        if not (1 <= num_inference_steps <= 100):
            raise ValueError("num_inference_steps must be between 1 and 100")
        if not (0.0 <= cfg_scale <= 20.0):
            raise ValueError("cfg_scale must be between 0.0 and 20.0")
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("prompt cannot be empty")

        print(f"Processing image with prompt: {prompt[:100]}...")
        print(f"Model: {model_name}, Steps: {num_inference_steps}, CFG: {cfg_scale}")

        # 模拟处理 - 返回原始图像
        output_image = input_image

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
                "note": "This is a test response - actual model processing not yet available"
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
        print(f"Error: {str(e)}")
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
    """编辑多张图像"""
    try:
        input_images = []
        for img_file in images:
            img_data = await img_file.read()
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            input_images.append(img)

        if len(input_images) == 0:
            raise ValueError("No images provided")

        print(f"Processing {len(input_images)} images with prompt: {prompt[:100]}...")

        # 返回第一张图像
        output_image = input_images[0]

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=edited_image.png"}
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/docs-custom")
async def custom_docs():
    return {
        "service": "FireRed-Image-Edit API",
        "version": "1.0.0",
        "endpoints": {
            "GET /health": "Health check",
            "GET /models": "List available models",
            "POST /edit": "Edit a single image",
            "POST /edit-batch": "Edit multiple images",
        },
        "models": [
            "FireRed-Image-Edit-1.1 (Latest, optimized for portrait consistency)",
            "FireRed-Image-Edit-1.0 (Base model)"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
