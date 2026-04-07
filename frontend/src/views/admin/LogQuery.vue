<template>
  <div>
    <h2>操作日志</h2>
    <el-card style="margin-top: 20px">
      <el-table :data="logs" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="操作人" width="120" />
        <el-table-column prop="action" label="操作类型" width="100" />
        <el-table-column prop="resource_type" label="资源类型" width="100" />
        <el-table-column prop="resource_id" label="资源ID" width="80" />
        <el-table-column prop="detail" label="操作详情" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP" width="130" />
        <el-table-column prop="created_at" label="操作时间" width="170" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const logs = ref<any[]>([])

onMounted(async () => {
  loading.value = true
  // TODO: 加载审计日志
  loading.value = false
})
</script>
