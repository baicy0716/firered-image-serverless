# 🚀 START HERE - 开始部署

## 👋 欢迎！

你已经获得了完整的 **FireRed-Image-Edit** 项目，包括：
- ✅ 图像换装 API
- ✅ Docker 容器化
- ✅ Runpod Serverless 配置
- ✅ 完整文档

---

## ⚡ 3 步快速开始

### 1️⃣ 构建 Docker 镜像 (2 分钟)

```bash
cd /home/ihouse/projects/FireRed-Image

# 构建 Serverless 镜像
docker build -t firered-image-serverless:latest -f Dockerfile.serverless .

# 标记镜像
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest
```

### 2️⃣ 推送到 Docker Hub (3 分钟)

```bash
# 登录
docker login

# 推送
docker push your-username/firered-image-serverless:latest
```

### 3️⃣ 在 Runpod 部署 (5 分钟)

1. 访问 https://www.runpod.io/
2. 登录 → Serverless → Create Endpoint
3. 选择 "Custom Image"
4. 输入: `your-username/firered-image-serverless:latest`
5. GPU: 1x A100 或 RTX 4090
6. 容器磁盘: 50GB
7. 卷大小: 100GB
8. 点击 Deploy

**完成！** 🎉

---

## 📚 文档导航

### 🎯 快速参考
- **QUICK_DEPLOY.md** - 5 分钟快速部署清单
- **QUICK_REFERENCE.md** - API 快速参考卡

### 📖 详细指南
- **RUNPOD_DEPLOYMENT_GUIDE.md** - Runpod 部署完整步骤
- **DOCKER_DEPLOYMENT.md** - Docker 部署详细指南
- **API_USAGE.md** - 完整 API 使用指南

### 🤖 模型信息
- **MODEL_CAPABILITIES.md** - 模型能力详解
- **PROJECT_SUMMARY.md** - 项目完成总结

### 📋 其他
- **FILE_MANIFEST.md** - 文件清单
- **README.md** - 项目说明

---

## 🎯 你想做什么？

### 我想快速部署到 Runpod
👉 阅读: **QUICK_DEPLOY.md**

### 我想了解详细的部署步骤
👉 阅读: **RUNPOD_DEPLOYMENT_GUIDE.md**

### 我想了解 API 如何使用
👉 阅读: **API_USAGE.md**

### 我想了解模型能力
👉 阅读: **MODEL_CAPABILITIES.md**

### 我想本地测试
👉 运行: `docker-compose up -d`

---

## 🔑 关键信息

### 当前部署 (REST API)
```
地址: http://213.173.102.178:8080
状态: ✅ 运行中
```

### 项目文件
```
位置: /home/ihouse/projects/FireRed-Image/
文件: 20+ 个（脚本、Docker、文档）
```

### 模型信息
- **基于**: Qwen (千问)
- **能力**: 图像编辑、换装、风格转换、多图融合
- **不支持**: 视频生成（需要额外集成）

---

## 💡 快速提示

1. **第一次部署会比较慢** (5-10 分钟)
   - 需要下载模型 (~25GB)

2. **成本优化**
   - RTX 4090: $0.44/小时
   - A100: $1.29/小时

3. **性能调优**
   - 减少 `num_inference_steps` 加快速度
   - 增加 `num_inference_steps` 提高质量

---

## ✅ 部署检查清单

- [ ] Docker 已安装
- [ ] Docker Hub 账户已创建
- [ ] 镜像已构建
- [ ] 镜像已推送
- [ ] Runpod 账户已创建
- [ ] Endpoint 已部署
- [ ] 测试请求成功

---

## 🚀 现在就开始！

### 选择你的路径：

**快速部署** (推荐)
```bash
# 1. 构建
docker build -t firered-image-serverless:latest -f Dockerfile.serverless .

# 2. 标记
docker tag firered-image-serverless:latest your-username/firered-image-serverless:latest

# 3. 推送
docker push your-username/firered-image-serverless:latest

# 4. 在 Runpod 部署
# 访问 https://www.runpod.io/
```

**本地测试**
```bash
docker-compose up -d
curl http://localhost:8080/health
```

---

## 📞 需要帮助？

1. 查看 **QUICK_DEPLOY.md** 快速部署
2. 查看 **RUNPOD_DEPLOYMENT_GUIDE.md** 详细步骤
3. 查看 **API_USAGE.md** API 文档
4. 查看 **MODEL_CAPABILITIES.md** 模型说明

---

**准备好了吗？** 🚀

👉 下一步: 阅读 **QUICK_DEPLOY.md** 或 **RUNPOD_DEPLOYMENT_GUIDE.md**
