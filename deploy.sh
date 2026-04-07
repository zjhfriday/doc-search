#!/bin/bash
# ==============================================================
# 党群素材智能检索平台 - 一键部署脚本
# 用法: bash deploy.sh
# ==============================================================
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} 党群素材智能检索平台 - 部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[错误] 未安装 Docker，请先安装 Docker${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}[错误] 未安装 Docker Compose，请先安装${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Docker 环境检查通过${NC}"

# 2. 环境变量
if [ ! -f .env ]; then
    echo -e "${YELLOW}[!] .env 文件不存在，从模板创建...${NC}"
    cp .env.example .env

    # 自动生成随机密码
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    PG_PASSWORD=$(openssl rand -hex 16)
    MINIO_SECRET=$(openssl rand -hex 16)
    RABBIT_PASS=$(openssl rand -hex 16)

    sed -i "s/请替换为随机字符串-至少32位/${SECRET_KEY}/" .env
    sed -i "s/JWT_SECRET_KEY=请替换为随机字符串-至少32位/JWT_SECRET_KEY=${JWT_SECRET}/" .env
    sed -i "s/POSTGRES_PASSWORD=请替换为强密码/POSTGRES_PASSWORD=${PG_PASSWORD}/" .env
    sed -i "s/MINIO_SECRET_KEY=请替换为强密码/MINIO_SECRET_KEY=${MINIO_SECRET}/" .env
    sed -i "s/RABBITMQ_DEFAULT_PASS=请替换为强密码/RABBITMQ_DEFAULT_PASS=${RABBIT_PASS}/" .env
    sed -i "s|CELERY_BROKER_URL=amqp://admin:请替换为强密码@|CELERY_BROKER_URL=amqp://admin:${RABBIT_PASS}@|" .env

    echo -e "${GREEN}[✓] .env 已创建并自动生成密码${NC}"
    echo -e "${YELLOW}[!] 请检查 .env 文件确认配置正确${NC}"
fi

# 3. 创建必要目录
mkdir -p backend/models

# 4. 构建镜像
echo -e "${GREEN}[...] 构建 Docker 镜像...${NC}"
docker compose build --parallel

echo -e "${GREEN}[✓] 镜像构建完成${NC}"

# 5. 启动基础设施
echo -e "${GREEN}[...] 启动基础设施服务...${NC}"
docker compose up -d postgres redis rabbitmq minio elasticsearch etcd

echo -e "${YELLOW}[...] 等待基础设施就绪 (30秒)...${NC}"
sleep 30

# 6. 启动 Milvus
echo -e "${GREEN}[...] 启动 Milvus...${NC}"
docker compose up -d milvus

echo -e "${YELLOW}[...] 等待 Milvus 就绪 (20秒)...${NC}"
sleep 20

# 7. 启动应用层
echo -e "${GREEN}[...] 启动应用服务...${NC}"
docker compose up -d backend celery-worker celery-beat frontend

# 8. 检查状态
echo -e "${YELLOW}[...] 等待服务启动 (15秒)...${NC}"
sleep 15

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} 部署完成！服务状态：${NC}"
echo -e "${GREEN}========================================${NC}"
docker compose ps

echo ""
echo -e "${GREEN}访问地址：${NC}"
echo -e "  前端界面:     http://$(hostname -I | awk '{print $1}')"
echo -e "  后端 API:     http://$(hostname -I | awk '{print $1}'):8000"
echo -e "  API 文档:     http://$(hostname -I | awk '{print $1}'):8000/docs"
echo -e "  MinIO 控制台: http://$(hostname -I | awk '{print $1}'):9001"
echo -e "  RabbitMQ:     http://$(hostname -I | awk '{print $1}'):15672"
echo ""
