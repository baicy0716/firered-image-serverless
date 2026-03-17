#!/bin/bash

# 🚀 FireRed-Image-Edit Runpod Serverless 快速部署脚本
# Quick deployment script for Runpod Serverless

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查前置条件
check_prerequisites() {
    print_header "检查前置条件"

    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        exit 1
    fi
    print_success "Docker 已安装: $(docker --version)"

    # 检查 Docker 登录
    if ! docker info &> /dev/null; then
        print_error "Docker 未登录，请运行: docker login"
        exit 1
    fi
    print_success "Docker 已登录"

    # 检查必要文件
    local required_files=("Dockerfile.serverless" "runpod_handler.py" "requirements.txt")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "文件不存在: $file"
            exit 1
        fi
    done
    print_success "所有必要文件已存在"
}

# 构建镜像
build_image() {
    local username=$1
    local tag=$2

    print_header "构建 Docker 镜像"

    local image_name="firered-image-serverless"
    local full_image_name="${username}/${image_name}:${tag}"

    print_info "构建镜像: $full_image_name"
    docker build -t "$image_name:$tag" -f Dockerfile.serverless .

    if [ $? -ne 0 ]; then
        print_error "镜像构建失败"
        exit 1
    fi
    print_success "镜像构建成功"

    print_info "标记镜像: $full_image_name"
    docker tag "$image_name:$tag" "$full_image_name"

    print_success "镜像已准备好: $full_image_name"
    echo "$full_image_name"
}

# 推送镜像
push_image() {
    local full_image_name=$1

    print_header "推送镜像到 Docker Hub"

    print_info "推送镜像: $full_image_name"
    docker push "$full_image_name"

    if [ $? -ne 0 ]; then
        print_error "镜像推送失败"
        exit 1
    fi
    print_success "镜像推送成功"
}

# 显示部署说明
show_deployment_instructions() {
    local full_image_name=$1

    print_header "部署说明"

    echo ""
    echo -e "${GREEN}镜像已准备好！${NC}"
    echo ""
    echo "现在请按照以下步骤在 Runpod 部署:"
    echo ""
    echo "1️⃣  访问 Runpod 控制台:"
    echo "   https://www.runpod.io/console/serverless/endpoints"
    echo ""
    echo "2️⃣  点击 'Create Endpoint'"
    echo ""
    echo "3️⃣  选择 'Custom Image'"
    echo ""
    echo "4️⃣  输入镜像 URL:"
    echo -e "   ${YELLOW}$full_image_name${NC}"
    echo ""
    echo "5️⃣  配置资源:"
    echo "   - GPU: 1x A100 或 1x RTX 4090"
    echo "   - 容器磁盘: 50 GB"
    echo "   - 卷大小: 100 GB"
    echo ""
    echo "6️⃣  配置环境变量:"
    echo "   - HF_HOME = /workspace/huggingface_cache"
    echo "   - TMPDIR = /workspace/tmp"
    echo "   - TORCH_HOME = /workspace/torch_cache"
    echo ""
    echo "7️⃣  设置处理器:"
    echo "   - Handler: runpod_handler.handler"
    echo ""
    echo "8️⃣  点击 'Deploy' 并等待完成"
    echo ""
    echo "9️⃣  获取 Endpoint ID 并保存"
    echo ""
    echo "🔟 测试 API (参考 RUNPOD_DEPLOYMENT_GUIDE.md)"
    echo ""
}

# 主函数
main() {
    print_header "🚀 FireRed-Image-Edit Runpod Serverless 部署"

    # 检查参数
    if [ $# -lt 2 ]; then
        print_error "用法: $0 <docker-username> <tag>"
        echo ""
        echo "示例:"
        echo "  $0 myusername latest"
        echo "  $0 myusername v1.0"
        exit 1
    fi

    local username=$1
    local tag=$2

    # 检查前置条件
    check_prerequisites

    # 构建镜像
    local full_image_name=$(build_image "$username" "$tag")

    # 询问是否推送
    echo ""
    read -p "是否推送镜像到 Docker Hub? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_image "$full_image_name"
    else
        print_warning "跳过推送步骤"
    fi

    # 显示部署说明
    show_deployment_instructions "$full_image_name"

    print_success "部署准备完成！"
}

# 运行主函数
main "$@"
