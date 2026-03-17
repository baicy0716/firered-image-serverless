#!/usr/bin/env python3
"""快速测试 FireRed-Image API"""

import requests
import json
import sys
from pathlib import Path

def test_api(base_url: str = "http://localhost:8080"):
    """测试 API 端点"""

    print("=" * 60)
    print("FireRed-Image API 快速测试")
    print("=" * 60)

    # 1. 健康检查
    print("\n✅ 测试 1: 健康检查")
    try:
        resp = requests.get(f"{base_url}/health", timeout=5)
        print(f"   状态码: {resp.status_code}")
        print(f"   响应: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

    # 2. 列出模型
    print("\n✅ 测试 2: 列出模型")
    try:
        resp = requests.get(f"{base_url}/models", timeout=5)
        print(f"   状态码: {resp.status_code}")
        print(f"   响应: {json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

    # 3. 自定义文档
    print("\n✅ 测试 3: 自定义文档")
    try:
        resp = requests.get(f"{base_url}/docs-custom", timeout=5)
        print(f"   状态码: {resp.status_code}")
        data = resp.json()
        print(f"   服务: {data.get('service')}")
        print(f"   版本: {data.get('version')}")
        print(f"   端点数: {len(data.get('endpoints', {}))}")
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ 所有基础测试通过!")
    print("=" * 60)
    print("\n下一步:")
    print("1. 准备一张图像文件")
    print("2. 运行: python3 api_client.py")
    print("3. 或使用 curl 测试:")
    print(f"   curl -X POST {base_url}/edit \\")
    print("     -F 'image=@image.png' \\")
    print("     -F 'prompt=a beautiful portrait' \\")
    print("     -o result.png")

    return True

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    success = test_api(base_url)
    sys.exit(0 if success else 1)
