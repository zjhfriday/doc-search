#!/bin/bash
# Celery Worker 启动脚本
exec celery -A app.celery_app:celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=default,ai_queue \
    --hostname=worker@%h
