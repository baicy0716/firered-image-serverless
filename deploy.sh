#!/bin/bash

# FireRed-Image-Edit Docker 部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}FireRed-Image-Edit Docker 部署${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker 已安装${NC}"

# 获取参数
IMAGE_NAME="${1:-firered-image-api}"
IMAGE_TAG="${2:-latest}"
REGISTRY="${3:-}"

# 完整镜像名称
if [ -z "$REGISTRY" ]; then
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
else
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
fi

echo -e "${YELLOW}镜像名称: ${FULL_IMAGE_NAME}${NC}"

# 选择构建类型
echo ""
echo "选择构建类型:"
echo "1) REST API (Dockerfile)"
echo "2) Runpod Serverless (Dockerfile.serverless)"
echo "3) 两者都构建"
read -p "请选择 (1-3): " BUILD_TYPE

case $BUILD_TYPE in
    1)
        echo -e "${YELLOW}构建 REST API 镜像...${NC}"
        docker build -t "${FULL_IMAGE_NAME}" -f Dockerfile .
        echo -e "${GREEN}✅ REST API 镜像构建完成${NC}"
        ;;
    2)
        echo -e "${YELLOW}构建 Runpod Serverless 镜像...${NC}"
        docker build -t "${FULL_IMAGE_NAME}-serverless" -f Dockerfile.serverless .
        echo -e "${GREEN}✅ Serverless 镜像构建完成${NC}"
        ;;
    3)
        echo -e "${YELLOW}构建 REST API 镜像...${NC}"
        docker build -t "${FULL_IMAGE_NAME}" -f Dockerfile .
        echo -e "${GREEN}✅ REST API 镜像构建完成${NC}"

        echo -e "${YELLOW}构建 Runpod Serverless 镜像...${NC}"
        docker build -t "${FULL_IMAGE_NAME}-serverless" -f Dockerfile.serverless .
        echo -e "${GREEN}✅ Serverless 镜像构建完成${NC}"
        ;;
    *)
        echo -e "${RED}❌ 无效选择${NC}"
        exit 1
        ;;
esac

# 显示镜像信息
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}镜像构建完成${NC}"
echo -e "${GREEN}========================================${NC}"
docker images | grep "${IMAGE_NAME}"

# 询问是否推送
echo ""
if [ ! -z "$REGISTRY" ]; then
    read -p "是否推送到 Docker Hub? (y/n): " PUSH_CHOICE
    if [ "$PUSH_CHOICE" = "y" ]; then
        echo -e "${YELLOW}推送镜像...${NC}"
        docker push "${FULL_IMAGE_NAME}"
        if [ "$BUILD_TYPE" = "2" ] || [ "$BUILD_TYPE" = "3" ]; then
            docker push "${FULL_IMAGE_NAME}-serverless"
        fi
        echo -e "${GREEN}✅ 镜像推送完成${NC}"
    fi
fi

# 询问是否本地测试
echo ""
read -p "是否进行本地测试? (y/n): " TEST_CHOICE
if [ "$TEST_CHOICE" = "y" ]; then
    echo -e "${YELLOW}启动本地测试...${NC}"
    docker-compose up -d
    sleep 5
    echo -e "${YELLOW}测试 API...${NC}"
    curl http://localhost:8080/health || echo -e "${RED}❌ API 未响应${NC}"
    echo ""
    echo -e "${GREEN}✅ 本地测试启动完成${NC}"
    echo -e "${YELLOW}查看日志: docker-compose logs -f${NC}"
    echo -e "${YELLOW}停止服务: docker-compose down${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"

# 显示后续步骤
echo ""
echo "后续步骤:"
echo "1. REST API 部署:"
echo "   docker run --gpus all -p 8080:8080 ${FULL_IMAGE_NAME}"
echo ""
echo "2. Runpod Serverless 部署:"
echo "   - 访问 https://www.runpod.io/"
echo "   - 创建新 Endpoint"
echo "   - 使用镜像: ${FULL_IMAGE_NAME}-serverless"
echo ""
echo "3. 查看文档:"
echo "   - DOCKER_DEPLOYMENT.md"
echo "   - API_USAGE.md"
