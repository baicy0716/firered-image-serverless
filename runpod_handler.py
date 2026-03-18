#!/usr/bin/env python3
"""
Runpod Serverless Handler for FireRed-Image-Edit API
处理 Runpod 的异步请求
"""

import os
import io
import base64
import json
import torch
import logging
from pathlib import Path
from PIL import Image
from typing import Any

# 禁用 brotli 编码以避免兼容性问题
os.environ['PYTHONHTTPSVERIFY'] = '0'

# 设置缓存目录
os.environ['HF_HOME'] = '/workspace/huggingface_cache'
os.environ['TMPDIR'] = '/workspace/tmp'
os.environ['TORCH_HOME'] = '/workspace/torch_cache'

# 禁用 brotli 自动解压以避免兼容性问题
os.environ['REQUESTS_CA_BUNDLE'] = ''

# 在导入 requests 之前设置
import urllib3
urllib3.disable_warnings()

# 禁用 brotli 编码
try:
    import brotli
    # 移除 brotli 编码器
    from urllib3.util.request import SKIP_HEADER, SKIP_COOKIE
    import urllib3.util.request as req_module
    if hasattr(req_module, 'SUPPORTED_DECODERS'):
        if 'br' in req_module.SUPPORTED_DECODERS:
            del req_module.SUPPORTED_DECODERS['br']
except:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局模型缓存
pipeline_cache = {}

def load_model(model_name: str = "FireRed-Image-Edit-1.1"):
    """加载模型"""
    if model_name in pipeline_cache:
        logger.info(f"Using cached model: {model_name}")
        return pipeline_cache[model_name]

    try:
        logger.info(f"Loading model: {model_name}")
        logger.info(f"Model path: FireRedTeam/{model_name}")

        from diffusers import QwenImageEditPlusPipeline

        logger.info("Downloading model from HuggingFace...")
        pipe = QwenImageEditPlusPipeline.from_pretrained(
            f"FireRedTeam/{model_name}",
            torch_dtype=torch.bfloat16,
        )
        logger.info("Model downloaded successfully")

        logger.info("Moving model to CUDA...")
        pipe.to("cuda")
        logger.info("Model moved to CUDA")

        pipeline_cache[model_name] = pipe
        logger.info(f"✅ Model loaded: {model_name}")

        return pipe

    except Exception as e:
        error_msg = f"Error loading model: {str(e)}"
        logger.error(f"❌ {error_msg}", exc_info=True)

        # 提供更详细的错误信息
        if "404" in str(e) or "not found" in str(e).lower():
            logger.error(f"Model not found: FireRedTeam/{model_name}")
            logger.error("Available models: FireRed-Image-Edit-1.1")

        raise

def edit_image_handler(job):
    """处理图像编辑请求"""
    try:
        job_input = job["input"]

        # 获取参数
        image_base64 = job_input.get("image")
        prompt = job_input.get("prompt")
        model_name = job_input.get("model_name", "FireRed-Image-Edit-1.1")
        num_inference_steps = int(job_input.get("num_inference_steps", 40))
        cfg_scale = float(job_input.get("cfg_scale", 4.0))
        seed = int(job_input.get("seed", 49))

        if not image_base64:
            return {"error": "image parameter is required"}
        if not prompt:
            return {"error": "prompt parameter is required"}

        logger.info(f"Processing: prompt={prompt[:50]}...")

        # 解码图像
        image_data = base64.b64decode(image_base64)
        input_image = Image.open(io.BytesIO(image_data)).convert("RGB")
        logger.info(f"Input image size: {input_image.size}")

        # 验证参数
        if not (1 <= num_inference_steps <= 100):
            return {"error": "num_inference_steps must be between 1 and 100"}
        if not (0.0 <= cfg_scale <= 20.0):
            return {"error": "cfg_scale must be between 0.0 and 20.0"}

        # 加载模型
        pipe = load_model(model_name)

        logger.info(f"Running inference: steps={num_inference_steps}, cfg={cfg_scale}")

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

        # 编码输出
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        output_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "status": "success",
            "image": output_base64,
            "format": "base64",
            "model": model_name,
            "prompt": prompt,
            "size": list(output_image.size),
        }

    except Exception as e:
        logger.error(f"Error in edit_image_handler: {str(e)}", exc_info=True)
        return {"error": str(e)}

def edit_batch_handler(job):
    """处理多图融合请求"""
    try:
        job_input = job["input"]

        # 获取参数
        images_base64 = job_input.get("images", [])
        prompt = job_input.get("prompt")
        model_name = job_input.get("model_name", "FireRed-Image-Edit-1.1")
        num_inference_steps = int(job_input.get("num_inference_steps", 40))
        cfg_scale = float(job_input.get("cfg_scale", 4.0))
        seed = int(job_input.get("seed", 49))

        if not images_base64:
            return {"error": "images parameter is required"}
        if not prompt:
            return {"error": "prompt parameter is required"}

        logger.info(f"Processing batch: {len(images_base64)} images, prompt={prompt[:50]}...")

        # 解码所有图像
        input_images = []
        for idx, img_base64 in enumerate(images_base64):
            image_data = base64.b64decode(img_base64)
            img = Image.open(io.BytesIO(image_data)).convert("RGB")
            input_images.append(img)
            logger.info(f"Image {idx+1} size: {img.size}")

        # 加载模型
        pipe = load_model(model_name)

        logger.info(f"Running batch inference: {len(input_images)} images")

        # 运行推理
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

        # 编码输出
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        output_base64 = base64.b64encode(buffer.getvalue()).decode()

        return {
            "status": "success",
            "image": output_base64,
            "format": "base64",
            "model": model_name,
            "prompt": prompt,
            "size": list(output_image.size),
        }

    except Exception as e:
        logger.error(f"Error in edit_batch_handler: {str(e)}", exc_info=True)
        return {"error": str(e)}

def handler(job):
    """主处理函数"""
    job_type = job["input"].get("type", "edit")

    if job_type == "edit":
        return edit_image_handler(job)
    elif job_type == "edit-batch":
        return edit_batch_handler(job)
    else:
        return {"error": f"Unknown job type: {job_type}"}

if __name__ == "__main__":
    import runpod

    logger.info("Starting Runpod Serverless Handler...")
    runpod.serverless.start({"handler": handler})
