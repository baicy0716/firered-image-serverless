import requests
import base64
import json
import time
from PIL import Image
from io import BytesIO

# 创建简单的测试图片
def create_test_image(width=512, height=512, color=(100, 150, 200)):
    """创建测试图片"""
    img = Image.new('RGB', (width, height), color)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

# API 端点
API_URL = "https://api.runpod.ai/v2/q3p5ssmpl99maw/run"

print("Creating test images...")
person_img = create_test_image(color=(100, 150, 200))
garment_img = create_test_image(color=(200, 100, 50))

payload = {
    "input": {
        "type": "edit-batch",
        "images": [person_img, garment_img],
        "prompt": "换装，穿上新衣服",
        "model_name": "HY-WU",
        "num_inference_steps": 20,
        "cfg_scale": 4.0,
        "seed": 42
    }
}

print("Sending request...")
print(f"Payload size: {len(json.dumps(payload)) / 1024 / 1024:.2f} MB")

try:
    response = requests.post(API_URL, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
