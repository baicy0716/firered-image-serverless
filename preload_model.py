import os
os.environ['HF_HOME'] = '/workspace/huggingface_cache'
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
