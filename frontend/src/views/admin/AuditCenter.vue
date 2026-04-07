<template>
  <div>
    <h2>素材审核</h2>
    <el-card style="margin-top: 20px">
      <el-table :data="materials" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="filename" label="文件名" show-overflow-tooltip />
        <el-table-column prop="material_type" label="类型" width="80" />
        <el-table-column prop="event_name" label="活动名称" show-overflow-tooltip />
        <el-table-column prop="quality_score" label="质量分" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="success" size="small" @click="approve(row.id)">通过</el-button>
            <el-button type="danger" size="small" @click="reject(row.id)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const materials = ref<any[]>([])

async function approve(id: number) {
  // TODO: await materialApi.approve(id)
  ElMessage.success('已通过')
}

async function reject(id: number) {
  // TODO: await materialApi.reject(id)
  ElMessage.success('已驳回')
}

onMounted(async () => {
  loading.value = true
  // TODO: 加载待审核素材
  loading.value = false
})
</script>
