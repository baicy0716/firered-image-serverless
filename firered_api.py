#!/usr/bin/env python3
"""FireRed-Image-Edit REST API Server."""

import os
import io
import base64
import torch
from pathlib import Path
from PIL import Image

# 设置缓存目录到 /workspace
os.environ['HF_HOME'] = '/workspace/huggingface_cache'
os.environ['TMPDIR'] = '/workspace/tmp'
os.environ['TORCH_HOME'] = '/workspace/torch_cache'
os.makedirs('/workspace/huggingface_cache', exist_ok=True)
os.makedirs('/workspace/tmp', exist_ok=True)
os.makedirs('/workspace/torch_cache', exist_ok=True)

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

try:
    from diffusers import QwenImageEditPlusPipeline
except ImportError:
    os.system("pip install -q diffusers accelerate")
    from diffusers import QwenImageEditPlusPipeline

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
    if model_name not in pipeline_cache:
        print(f"Loading model: {model_name}")
        model_id = f"FireRedTeam/{model_name}"
        pipe = QwenImageEditPlusPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
        )
        pipe.to("cuda")
        pipeline_cache[model_name] = pipe
    return pipeline_cache[model_name]

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
    try:
        image_data = await image.read()
        input_image = Image.open(io.BytesIO(image_data)).convert("RGB")

        if not (1 <= num_inference_steps <= 100):
            raise ValueError("num_inference_steps must be between 1 and 100")
        if not (0.0 <= cfg_scale <= 20.0):
            raise ValueError("cfg_scale must be between 0.0 and 20.0")
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError("prompt cannot be empty")

        pipe = get_pipeline(model_name)
        print(f"Processing image with prompt: {prompt[:100]}...")

        with torch.inference_mode():
            result = pipe(
                image=[input_image],
                prompt=prompt,
                generator=torch.Generator(device="cuda").manual_seed(seed),
                true_cfg_scale=cfg_scale,
                negative_prompt=" ",
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=1,
            )

        output_image = result.images[0]

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
    try:
        input_images = []
        for img_file in images:
            img_data = await img_file.read()
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            input_images.append(img)

        if len(input_images) == 0:
            raise ValueError("No images provided")

        pipe = get_pipeline(model_name)
        print(f"Processing {len(input_images)} images with prompt: {prompt[:100]}...")

        with torch.inference_mode():
            result = pipe(
                image=input_images,
                prompt=prompt,
                generator=torch.Generator(device="cuda").manual_seed(seed),
                true_cfg_scale=cfg_scale,
                negative_prompt=" ",
                num_inference_steps=num_inference_steps,
                num_images_per_prompt=1,
            )

        output_image = result.images[0]

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
