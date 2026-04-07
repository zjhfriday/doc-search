<template>
  <div class="dashboard">
    <h2>数据看板</h2>

    <!-- 概览卡片 -->
    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :span="6" v-for="card in overviewCards" :key="card.label">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>素材类型分布</template>
          <div class="chart-placeholder flex-center">图表占位 - ECharts 饼图</div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>存储使用情况</template>
          <div class="chart-placeholder flex-center">图表占位 - ECharts 柱状图</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const overviewCards = ref([
  { label: '素材总数', value: '-' },
  { label: '图片数量', value: '-' },
  { label: '视频数量', value: '-' },
  { label: '存储总量', value: '-' },
])

onMounted(async () => {
  // TODO: const data = await dashboardApi.overview()
  // 更新 overviewCards
})
</script>

<style scoped lang="scss">
.stat-card {
  text-align: center;
  .stat-value { font-size: 28px; font-weight: bold; color: var(--primary-color); }
  .stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 4px; }
}
.chart-placeholder {
  height: 300px; background: #f9f9f9; border-radius: 4px; color: #999;
}
</style>
