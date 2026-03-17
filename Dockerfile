FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-pip \
    git \
    wget \
    curl \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置 Python 路径
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/workspace/huggingface_cache
ENV TMPDIR=/workspace/tmp
ENV TORCH_HOME=/workspace/torch_cache

# 创建缓存目录
RUN mkdir -p /workspace/huggingface_cache /workspace/tmp /workspace/torch_cache

# 安装 Python 依赖
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-multipart==0.0.6 \
    torch==2.1.0 \
    torchvision==0.16.0 \
    torchaudio==2.1.0 \
    diffusers==0.24.0 \
    transformers==4.35.0 \
    accelerate==0.24.0 \
    pillow==10.1.0 \
    numpy==1.24.3 \
    requests==2.31.0

# 复制 API 脚本
COPY firered_api_final.py /app/

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动 API
CMD ["python3", "-m", "uvicorn", "firered_api_final:app", "--host", "0.0.0.0", "--port", "8080"]
