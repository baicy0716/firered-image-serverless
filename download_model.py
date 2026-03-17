#!/usr/bin/env python3
"""Download FireRed-Image-Edit model from HuggingFace."""

import os
import sys
from pathlib import Path

# Add ComfyUI to path
comfyui_path = Path("/workspace/runpod-slim/ComfyUI")
sys.path.insert(0, str(comfyui_path))

try:
    from diffusers import QwenImageEditPlusPipeline
    import torch

    print("🔄 Downloading FireRed-Image-Edit-1.1 model...")
    print("This may take a few minutes...")

    model_id = "FireRedTeam/FireRed-Image-Edit-1.1"

    # Download to HuggingFace cache
    pipe = QwenImageEditPlusPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
    )

    print("✅ Model downloaded successfully!")
    print(f"Model location: {pipe.model_card_data}")

except Exception as e:
    print(f"❌ Error downloading model: {e}")
    sys.exit(1)
