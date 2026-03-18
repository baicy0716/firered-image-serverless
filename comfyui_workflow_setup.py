#!/usr/bin/env python3
"""
ComfyUI 工作流配置脚本
将 comfyui.json 工作流部署到 ComfyUI 服务器
"""

import json
import requests
import sys
from pathlib import Path

# ComfyUI 服务器配置
COMFYUI_SERVER = "http://localhost:8188"
WORKFLOW_FILE = "/home/ihouse/projects/FireRed-Image/comfyui.json"

def load_workflow():
    """加载工作流文件"""
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_comfyui_server():
    """检查 ComfyUI 服务器是否运行"""
    try:
        response = requests.get(f"{COMFYUI_SERVER}/system_stats", timeout=5)
        if response.status_code == 200:
            print("✅ ComfyUI 服务器已连接")
            return True
    except Exception as e:
        print(f"❌ 无法连接到 ComfyUI 服务器: {e}")
        return False

def get_available_models():
    """获取可用的模型列表"""
    try:
        response = requests.get(f"{COMFYUI_SERVER}/api/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print("\n📦 可用模型:")
            for model_type, model_list in models.items():
                print(f"  {model_type}: {len(model_list)} 个模型")
                for model in model_list[:3]:  # 只显示前3个
                    print(f"    - {model}")
            return models
    except Exception as e:
        print(f"❌ 获取模型列表失败: {e}")
    return None

def validate_workflow(workflow):
    """验证工作流配置"""
    print("\n🔍 验证工作流配置...")

    required_nodes = {
        115: "CLIPLoader",
        116: "VAELoader",
        128: "UNETLoader",
        117: "TextEncodeQwenImageEditPlus",
        118: "TextEncodeQwenImageEditPlus",
        130: "KSampler",
        126: "VAEDecode",
        9: "SaveImage"
    }

    nodes = {node['id']: node['type'] for node in workflow['nodes']}

    missing = []
    for node_id, expected_type in required_nodes.items():
        if node_id not in nodes:
            missing.append(f"Node {node_id} ({expected_type})")
        elif nodes[node_id] != expected_type:
            missing.append(f"Node {node_id}: 期望 {expected_type}, 实际 {nodes[node_id]}")

    if missing:
        print(f"❌ 工作流验证失败:")
        for item in missing:
            print(f"  - {item}")
        return False

    print("✅ 工作流验证成功")
    return True

def main():
    print("=" * 60)
    print("ComfyUI 工作流配置工具")
    print("=" * 60)

    # 检查服务器
    if not check_comfyui_server():
        print("\n请确保 ComfyUI 服务器正在运行:")
        print("  cd /workspace/ComfyUI")
        print("  python main.py")
        sys.exit(1)

    # 加载工作流
    print("\n📂 加载工作流...")
    try:
        workflow = load_workflow()
        print(f"✅ 工作流已加载 ({len(workflow['nodes'])} 个节点)")
    except Exception as e:
        print(f"❌ 加载工作流失败: {e}")
        sys.exit(1)

    # 验证工作流
    if not validate_workflow(workflow):
        sys.exit(1)

    # 获取可用模型
    get_available_models()

    print("\n" + "=" * 60)
    print("✅ 工作流配置完成!")
    print("=" * 60)
    print("\n下一步:")
    print("1. 运行 API 服务器: python comfyui_api_server.py")
    print("2. 打开测试页面: http://localhost:5000")

if __name__ == "__main__":
    main()
