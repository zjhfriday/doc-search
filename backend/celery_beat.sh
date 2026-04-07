#!/bin/bash
# Celery Beat 定时任务启动脚本
exec celery -A app.celery_app:celery_app beat \
    --loglevel=info \
    --schedule=/tmp/celerybeat-schedule
