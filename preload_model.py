import os
import sys

# 设置缓存目录
os.environ['HF_HOME'] = '/workspace/huggingface_cache'
os.environ['TMPDIR'] = '/workspace/tmp'
os.environ['TORCH_HOME'] = '/workspace/torch_cache'

# 禁用 brotli 自动解压以避免兼容性问题
os.environ['REQUESTS_CA_BUNDLE'] = ''

try:
    from diffusers import QwenImageEditPlusPipeline
    import torch
    print("Downloading model...")
    QwenImageEditPlusPipeline.from_pretrained(
        'FireRedTeam/FireRed-Image-Edit-1.1',
        torch_dtype=torch.bfloat16
    )
    print("Model downloaded successfully")
except Exception as e:
    print(f"Warning: Could not pre-download model: {e}")
    print("Model will be downloaded on first request")
    sys.exit(0)
