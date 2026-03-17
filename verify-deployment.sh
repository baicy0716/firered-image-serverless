#!/bin/bash

# 🔍 FireRed-Image-Edit 部署前验证脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 检查文件
check_files() {
    print_header "检查项目文件"

    local files=(
        "Dockerfile.serverless"
        "runpod_handler.py"
        "requirements.txt"
        "firered_api_final.py"
        "api_client.py"
        "test_api.py"
        "docker-compose.yml"
        ".dockerignore"
        "deploy.sh"
        "deploy-serverless.sh"
    )

    local missing=0
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_success "文件存在: $file"
        else
            print_error "文件缺失: $file"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "所有核心文件已存在"
    else
        print_error "缺失 $missing 个文件"
        return 1
    fi
}

# 检查文档
check_docs() {
    print_header "检查文档文件"

    local docs=(
        "START_HERE.md"
        "QUICK_DEPLOY.md"
        "DEPLOYMENT_GUIDE.md"
        "DEPLOYMENT_CHECKLIST.md"
        "RUNPOD_DEPLOYMENT_GUIDE.md"
        "API_USAGE.md"
        "MODEL_CAPABILITIES.md"
        "QUICK_REFERENCE.md"
        "PROJECT_SUMMARY.md"
        "FILE_MANIFEST.md"
        "FINAL_SUMMARY.md"
    )

    local missing=0
    for doc in "${docs[@]}"; do
        if [ -f "$doc" ]; then
            print_success "文档存在: $doc"
        else
            print_warning "文档缺失: $doc"
            missing=$((missing + 1))
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "所有文档已完成"
    else
        print_warning "缺失 $missing 个文档"
    fi
}

# 检查 Docker 配置
check_docker_config() {
    print_header "检查 Docker 配置"

    # 检查 Dockerfile.serverless
    if grep -q "FROM nvidia/cuda" Dockerfile.serverless; then
        print_success "Dockerfile.serverless 配置正确"
    else
        print_error "Dockerfile.serverless 配置错误"
        return 1
    fi

    # 检查 requirements.txt
    if grep -q "runpod" requirements.txt; then
        print_success "requirements.txt 包含 runpod"
    else
        print_error "requirements.txt 缺少 runpod"
        return 1
    fi

    # 检查 runpod_handler.py
    if grep -q "def handler" runpod_handler.py; then
        print_success "runpod_handler.py 包含 handler 函数"
    else
        print_error "runpod_handler.py 缺少 handler 函数"
        return 1
    fi
}

# 检查 Python 语法
check_python_syntax() {
    print_header "检查 Python 语法"

    local python_files=(
        "runpod_handler.py"
        "firered_api_final.py"
        "api_client.py"
        "test_api.py"
    )

    for file in "${python_files[@]}"; do
        if python3 -m py_compile "$file" 2>/dev/null; then
            print_success "Python 语法正确: $file"
        else
            print_error "Python 语法错误: $file"
            return 1
        fi
    done
}

# 检查脚本权限
check_script_permissions() {
    print_header "检查脚本权限"

    local scripts=(
        "deploy.sh"
        "deploy-serverless.sh"
    )

    for script in "${scripts[@]}"; do
        if [ -x "$script" ]; then
            print_success "脚本可执行: $script"
        else
            print_warning "脚本不可执行: $script，正在修复..."
            chmod +x "$script"
            print_success "已修复: $script"
        fi
    done
}

# 生成部署报告
generate_report() {
    print_header "部署准备报告"

    echo ""
    echo "📊 项目统计:"
    echo "  - Python 脚本: $(ls -1 *.py 2>/dev/null | wc -l) 个"
    echo "  - Docker 配置: $(ls -1 Dockerfile* 2>/dev/null | wc -l) 个"
    echo "  - 文档文件: $(ls -1 *.md 2>/dev/null | wc -l) 个"
    echo "  - 部署脚本: $(ls -1 *deploy*.sh 2>/dev/null | wc -l) 个"
    echo ""

    echo "📁 项目大小:"
    du -sh . | awk '{print "  - 总大小: " $1}'
    echo ""

    echo "🚀 部署命令:"
    echo "  bash deploy-serverless.sh your-docker-username latest"
    echo ""

    echo "📚 推荐阅读顺序:"
    echo "  1. START_HERE.md"
    echo "  2. QUICK_DEPLOY.md"
    echo "  3. DEPLOYMENT_GUIDE.md"
    echo "  4. API_USAGE.md"
    echo ""
}

# 主函数
main() {
    print_header "🔍 FireRed-Image-Edit 部署前验证"

    check_files || exit 1
    check_docs
    check_docker_config || exit 1
    check_python_syntax || exit 1
    check_script_permissions
    generate_report

    print_header "✅ 验证完成"
    echo ""
    echo -e "${GREEN}所有检查已通过！项目已准备好部署。${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 阅读 START_HERE.md"
    echo "  2. 运行: bash deploy-serverless.sh your-username latest"
    echo "  3. 在 Runpod 创建 Endpoint"
    echo "  4. 测试 API"
    echo ""
}

main
