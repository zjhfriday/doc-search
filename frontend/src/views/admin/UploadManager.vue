<template>
  <div>
    <h2>上传管理</h2>
    <el-card style="margin-top: 20px">
      <el-upload
        drag
        multiple
        action=""
        :auto-upload="false"
        :on-change="handleFileChange"
        accept="image/*,video/*"
      >
        <el-icon :size="48" style="color: #999"><Upload /></el-icon>
        <div>将文件拖到此处，或点击上传</div>
        <div style="color: #999; font-size: 12px; margin-top: 4px">
          支持图片(jpg/png/bmp等)和视频(mp4/avi/mov等)格式
        </div>
      </el-upload>

      <el-form style="margin-top: 20px; max-width: 500px" label-width="100px">
        <el-form-item label="活动名称">
          <el-input v-model="uploadMeta.eventName" placeholder="例如：2024年度表彰大会" />
        </el-form-item>
        <el-form-item label="密级">
          <el-select v-model="uploadMeta.securityLevel">
            <el-option label="公开" value="public" />
            <el-option label="内部" value="internal" />
            <el-option label="受限" value="restricted" />
            <el-option label="涉密" value="confidential" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="uploading" @click="handleUpload">
            开始上传
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Upload } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const uploading = ref(false)
const fileList = ref<File[]>([])
const uploadMeta = reactive({
  eventName: '',
  securityLevel: 'internal',
})

function handleFileChange(file: any) {
  fileList.value.push(file.raw)
}

async function handleUpload() {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  uploading.value = true
  // TODO: await materialApi.uploadBatch(fileList.value, uploadMeta)
  ElMessage.success('上传完成')
  uploading.value = false
}
</script>
