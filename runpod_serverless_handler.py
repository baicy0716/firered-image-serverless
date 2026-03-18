#!/usr/bin/env python3
"""
RunPod Serverless Handler for FireRed ComfyUI
处理 RunPod 的异步请求
"""

import json
import requests
import base64
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ComfyUI 配置
COMFYUI_SERVER = "http://localhost:8188"
WORKFLOW_FILE = "/workspace/firered-image-serverless/comfyui.json"

def load_workflow():
    """加载工作流"""
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def submit_workflow(workflow):
    """提交工作流到 ComfyUI"""
    try:
        response = requests.post(
            f"{COMFYUI_SERVER}/prompt",
            json={"prompt": workflow},
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get('prompt_id'), None
        else:
            return None, f"提交失败: {response.text}"
    except Exception as e:
        return None, str(e)

def get_workflow_status(prompt_id):
    """获取工作流状态"""
    try:
        response = requests.get(
            f"{COMFYUI_SERVER}/history/{prompt_id}",
            timeout=10
        )
        if response.status_code == 200:
            history = response.json()
            if prompt_id in history:
                return history[prompt_id]
        return None
    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        return None

def handler(job):
    """
    RunPod Serverless Handler

    输入格式:
    {
        "input": {
            "prompt": "编辑提示词",
            "steps": 40,
            "cfg": 4.0,
            "seed": 43,
            "use_lora": true,
            "images": {
                "image1": "base64_encoded_image",
                "image2": "base64_encoded_image",
                "image3": "base64_encoded_image"
            }
        }
    }
    """
    try:
        job_input = job.get("input", {})

        # 获取参数
        prompt = job_input.get("prompt", "")
        steps = int(job_input.get("steps", 40))
        cfg = float(job_input.get("cfg", 4.0))
        seed = int(job_input.get("seed", 43))
        use_lora = job_input.get("use_lora", True)
        images = job_input.get("images", {})

        logger.info(f"处理请求: prompt={prompt[:50]}..., steps={steps}, cfg={cfg}")

        # 加载工作流
        workflow = load_workflow()

        # 更新工作流参数
        for node in workflow['nodes']:
            # 更新提示词
            if node['type'] == 'TextEncodeQwenImageEditPlus' and node.get('title') == 'TextEncodeQwenImageEditPlus (Positive)':
                node['widgets_values'][0] = prompt

            # 更新步数
            elif node['id'] == 155:  # Steps
                node['widgets_values'][0] = steps

            # 更新 CFG
            elif node['id'] == 162:  # CFG
                node['widgets_values'][0] = cfg

            # 更新 LoRA 步数
            elif node['id'] == 156:  # LoRA-Steps
                node['widgets_values'][0] = 8 if use_lora else steps

            # 更新是否使用 LoRA
            elif node['id'] == 153:  # 是否使用加速 LoRA
                node['widgets_values'][0] = use_lora

            # 更新种子
            elif node['id'] == 130:  # KSampler
                node['widgets_values'][0] = seed

        # 上传图片
        logger.info("上传图片...")
        for image_key, image_data in images.items():
            try:
                # 解码 base64
                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = image_data

                files = {'image': (f'{image_key}.png', image_bytes, 'image/png')}
                response = requests.post(
                    f"{COMFYUI_SERVER}/upload/image",
                    files=files,
                    timeout=30
                )
                if response.status_code != 200:
                    logger.warning(f"图片上传失败: {image_key}")
            except Exception as e:
                logger.warning(f"上传 {image_key} 失败: {e}")

        # 提交工作流
        logger.info("提交工作流...")
        prompt_id, error = submit_workflow(workflow)

        if error:
            return {"error": error}

        logger.info(f"工作流已提交: {prompt_id}")

        # 轮询获取结果
        logger.info("等待处理完成...")
        max_wait = 3600  # 1 小时超时
        start_time = time.time()

        while time.time() - start_time < max_wait:
            history = get_workflow_status(prompt_id)

            if history and 'outputs' in history:
                logger.info("处理完成!")

                # 提取输出
                outputs = history['outputs']
                result_images = []

                for node_id, output in outputs.items():
                    if 'images' in output:
                        for img_info in output['images']:
                            # 获取图片 URL
                            img_url = f"{COMFYUI_SERVER}/view?filename={img_info['filename']}&subfolder={img_info.get('subfolder', '')}&type=output"
                            result_images.append(img_url)

                return {
                    "status": "success",
                    "prompt_id": prompt_id,
                    "images": result_images,
                    "output": outputs
                }

            time.sleep(5)

        return {"error": "处理超时"}

    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        return {"error": str(e)}


if __name__ == "__main__":
    import runpod

    logger.info("启动 RunPod Serverless Handler...")
    runpod.serverless.start({"handler": handler})
