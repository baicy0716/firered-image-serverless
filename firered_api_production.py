#!/usr/bin/env python3
"""FireRed-Image-Edit REST API - 完整版本"""

import os
import io
import base64
import torch
import logging
from pathlib import Path
from PIL import Image

# 设置缓存目录
os.environ['HF_HOME'] = '/workspace/huggingface_cache'
os.environ['TMPDIR'] = '/workspace/tmp'
os.environ['TORCH_HOME'] = '/workspace/torch_cache'
os.makedirs('/workspace/huggingface_cache', exist_ok=True)
os.makedirs('/workspace/tmp', exist_ok=True)
os.makedirs('/workspace/torch_cache', exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

pipeline_cache = {}

def get_pipeline(model_name: str = "FireRed-Image-Edit-1.1"):
    """加载模型管道"""
    if model_name in pipeline_cache:
        logger.info(f"Using cached pipeline: {model_name}")
        return pipeline_cache[model_name]

    try:
        logger.info(f"Loading model: {model_name}")

        # 尝试导入 diffusers
        try:
            from diffusers import QwenImageEditPlusPipeline
        except ImportError:
            logger.warning("diffusers not found, installing...")
            os.system("pip install -q diffusers accelerate")
            from diffusers import QwenImageEditPlusPipeline

        model_id = f"FireRedTeam/{model_name}"

        logger.info(f"Loading from: {model_id}")

        # 加载管道
        pipe = QwenImageEditPlusPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )

        logger.info("Moving model to CUDA...")
        pipe.to("cuda")

        pipeline_cache[model_name] = pipe
        logger.info(f"✅ Model loaded successfully: {model_name}")

        return pipe

    except Exception as e:
        logger.error(f"❌ Error loading model: {str(e)}", exc_info=True)
        raise

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
    """编辑图像"""
    try:
        logger.info(f"Processing edit request: prompt={prompt[:50]}...")

        # 读取和验证图像
        image_data = await image.read()
        input_image = Image.open(io.BytesIO(image_data)).convert("RGB")
        logger.info(f"Input image size: {input_image.size}")

        # 验证参数
        if not (1 <= num_inference_steps <= 100):
            raise ValueError("num_inference_steps must be between 1 and 100")
        if not (0.0 <= cfg_scale <= 20.0):
            raise ValueError("cfg_scale must be between 0.0 and 20.0")
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("prompt cannot be empty")

        # 获取管道
        pipe = get_pipeline(model_name)

        logger.info(f"Running inference: steps={num_inference_steps}, cfg={cfg_scale}, seed={seed}")

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
        logger.info(f"Output image size: {output_image.size}")

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
        logger.error(f"Error in /edit: {str(e)}", exc_info=True)
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
    """编辑多张图像（用于多图融合）"""
    try:
        logger.info(f"Processing batch edit: {len(images)} images, prompt={prompt[:50]}...")

        input_images = []
        for idx, img_file in enumerate(images):
            img_data = await img_file.read()
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            input_images.append(img)
            logger.info(f"Image {idx+1} size: {img.size}")

        if len(input_images) == 0:
            raise ValueError("No images provided")

        pipe = get_pipeline(model_name)

        logger.info(f"Running batch inference: {len(input_images)} images")

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
        logger.info(f"Output image size: {output_image.size}")

        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=edited_image.png"}
        )

    except Exception as e:
        logger.error(f"Error in /edit-batch: {str(e)}", exc_info=True)
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
        ],
        "usage_examples": {
            "clothing_change": "person wearing a red dress, professional photo",
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
