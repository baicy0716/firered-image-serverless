import requests
import base64
import json
import time
from pathlib import Path

# API 端点
API_URL = "https://api.runpod.ai/v2/q3p5ssmpl99maw/run"

# 测试图片 URL（使用公开的示例图片）
person_url = "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400"
garment_url = "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=400"

def download_and_encode_image(url):
    """下载图片并转换为 base64"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def test_api():
    """测试 API"""
    print("Downloading images...")
    person_b64 = download_and_encode_image(person_url)
    garment_b64 = download_and_encode_image(garment_url)
    
    if not person_b64 or not garment_b64:
        print("Failed to download images")
        return
    
    # 准备请求
    payload = {
        "input": {
            "type": "edit-batch",
            "images": [person_b64, garment_b64],
            "prompt": "换装，穿上新衣服",
            "model_name": "HY-WU",
            "num_inference_steps": 30,
            "cfg_scale": 4.0,
            "seed": 42
        }
    }
    
    print("Sending request to API...")
    print(f"API URL: {API_URL}")
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nRequest ID: {result.get('id')}")
            print(f"Status: {result.get('status')}")
            
            # 如果是异步，等待结果
            if result.get('status') == 'QUEUED':
                request_id = result.get('id')
                print(f"\nWaiting for result (request ID: {request_id})...")
                
                # 轮询获取结果
                for i in range(60):  # 最多等待 5 分钟
                    time.sleep(5)
                    status_url = f"https://api.runpod.ai/v2/q3p5ssmpl99maw/status/{request_id}"
                    status_response = requests.get(status_url, timeout=10)
                    status_data = status_response.json()
                    
                    print(f"Attempt {i+1}: Status = {status_data.get('status')}")
                    
                    if status_data.get('status') == 'COMPLETED':
                        print(f"\nResult: {json.dumps(status_data.get('output'), indent=2)}")
                        break
                    elif status_data.get('status') == 'FAILED':
                        print(f"Error: {status_data.get('output')}")
                        break
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
