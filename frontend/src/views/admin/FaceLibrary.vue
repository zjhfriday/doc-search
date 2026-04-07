<template>
  <div>
    <h2>人脸库管理</h2>
    <el-card style="margin-top: 20px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>已录入人脸</span>
          <el-button type="primary" size="small">添加人脸</el-button>
        </div>
      </template>
      <el-table :data="faces" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="person_name" label="姓名" width="120" />
        <el-table-column prop="person_title" label="职务" />
        <el-table-column prop="department" label="部门" width="120" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="添加时间" width="170" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" size="small" @click="deleteFace(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const loading = ref(false)
const faces = ref<any[]>([])

async function deleteFace(id: number) {
  // TODO: 删除人脸
}

onMounted(async () => {
  loading.value = true
  // TODO: 加载人脸库列表
  loading.value = false
})
</script>
