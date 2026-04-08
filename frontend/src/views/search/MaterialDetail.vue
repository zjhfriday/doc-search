<template>
  <div class="material-detail page-container">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>素材详情</template>
    </el-page-header>

    <div class="detail-content" v-loading="loading">
      <el-row :gutter="24" style="margin-top: 20px">
        <!-- 左侧预览 -->
        <el-col :span="14">
          <el-card>
            <div class="preview-area">
              <!-- TODO: 根据类型显示图片/视频播放器 -->
              <div class="preview-placeholder flex-center">
                素材预览区域
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧信息 -->
        <el-col :span="10">
          <el-card>
            <template #header>基本信息</template>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="文件名">{{ material?.filename }}</el-descriptions-item>
              <el-descriptions-item label="类型">{{ material?.material_type }}</el-descriptions-item>
              <el-descriptions-item label="大小">{{ formatSize(material?.file_size) }}</el-descriptions-item>
              <el-descriptions-item label="分辨率" v-if="material?.width">
                {{ material?.width }} x {{ material?.height }}
              </el-descriptions-item>
              <el-descriptions-item label="时长" v-if="material?.duration">
                {{ (material?.duration / 60).toFixed(1) }} 分钟
              </el-descriptions-item>
              <el-descriptions-item label="活动名称">{{ material?.event_name || '-' }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="statusType(material?.status)">{{ material?.status }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="密级">
                <el-tag :type="securityType(material?.security_level)">{{ material?.security_level }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="质量评分">{{ material?.quality_score?.toFixed(1) || '-' }}</el-descriptions-item>
              <el-descriptions-item label="上传时间">{{ material?.created_at }}</el-descriptions-item>
            </el-descriptions>
          </el-card>

          <!-- 标签 -->
          <el-card style="margin-top: 16px" v-if="material?.tags?.length">
            <template #header>标签</template>
            <div class="tag-list">
              <el-tag v-for="tag in material?.tags" :key="tag.id" style="margin: 4px">
                {{ tag.name }}
              </el-tag>
            </div>
          </el-card>

          <!-- OCR / ASR 文本 -->
          <el-card style="margin-top: 16px" v-if="material?.ocr_text || material?.asr_text">
            <template #header>提取文本</template>
            <div v-if="material?.ocr_text">
              <h5>OCR 文字</h5>
              <p class="extracted-text">{{ material.ocr_text }}</p>
            </div>
            <div v-if="material?.asr_text" style="margin-top: 12px">
              <h5>语音转写</h5>
              <p class="extracted-text">{{ material.asr_text }}</p>
            </div>
          </el-card>

          <!-- 操作按钮 -->
          <div class="action-buttons" style="margin-top: 16px">
            <el-button type="primary" size="large">下载素材</el-button>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import type { Material } from '@/api/types'

const route = useRoute()
const loading = ref(false)
const material = ref<Material | null>(null)

function formatSize(bytes?: number): string {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function statusType(status?: string) {
  const map: Record<string, string> = {
    approved: 'success', pending: 'warning', processing: 'info',
    rejected: 'danger', archived: 'info',
  }
  return (map[status || ''] || 'info') as any
}

function securityType(level?: string) {
  const map: Record<string, string> = {
    public: 'success', internal: '', restricted: 'warning', confidential: 'danger',
  }
  return (map[level || ''] || '') as any
}

onMounted(async () => {
  const id = Number(route.params.id)
  loading.value = true
  console.log('Loading material:', id)
  // TODO: const data = await materialApi.detail(id)
  // material.value = data
  loading.value = false
})
</script>

<style scoped lang="scss">
.preview-area {
  min-height: 400px;
}

.preview-placeholder {
  width: 100%;
  height: 400px;
  background: #f0f0f0;
  border-radius: 4px;
  color: #999;
}

.extracted-text {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
  max-height: 200px;
  overflow-y: auto;
  background: #f9f9f9;
  padding: 8px;
  border-radius: 4px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}
</style>
