<template>
  <div class="search-result-page">
    <el-container>
      <!-- 左侧筛选栏 -->
      <el-aside width="260px" class="filter-aside">
        <h4>筛选条件</h4>

        <el-form label-position="top" size="small">
          <el-form-item label="素材类型">
            <el-select v-model="filters.materialType" clearable placeholder="全部">
              <el-option label="图片" value="image" />
              <el-option label="视频" value="video" />
            </el-select>
          </el-form-item>

          <el-form-item label="时间范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="人物">
            <el-input v-model="filters.personName" placeholder="人物姓名" clearable />
          </el-form-item>

          <el-form-item label="活动名称">
            <el-input v-model="filters.eventName" placeholder="活动名称" clearable />
          </el-form-item>

          <el-form-item label="最低质量分">
            <el-slider v-model="filters.minQuality" :max="100" :step="10" show-input />
          </el-form-item>

          <el-form-item>
            <el-checkbox v-model="filters.excludeDuplicates">排除重复素材</el-checkbox>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="doSearch" style="width: 100%">应用筛选</el-button>
            <el-button @click="resetFilters" style="width: 100%; margin-top: 8px">重置</el-button>
          </el-form-item>
        </el-form>
      </el-aside>

      <!-- 右侧结果区 -->
      <el-main class="result-main">
        <!-- 搜索框 -->
        <div class="result-header">
          <el-input
            v-model="searchQuery"
            placeholder="继续搜索..."
            clearable
            @keyup.enter="doSearch"
          >
            <template #append>
              <el-button @click="doSearch"><el-icon><Search /></el-icon></el-button>
            </template>
          </el-input>
          <span class="result-count" v-if="total > 0">共 {{ total }} 条结果</span>
        </div>

        <!-- 结果列表 (瀑布流占位) -->
        <div v-loading="loading" class="result-grid">
          <div
            v-for="item in results"
            :key="item.material_id"
            class="material-card"
            @click="goDetail(item.material_id)"
          >
            <div class="card-thumb">
              <img v-if="item.thumbnail_url" :src="item.thumbnail_url" :alt="item.filename" />
              <div v-else class="thumb-placeholder">{{ item.material_type === 'video' ? '视频' : '图片' }}</div>
              <el-tag v-if="item.material_type === 'video'" class="type-tag" size="small" type="danger">视频</el-tag>
            </div>
            <div class="card-info">
              <div class="card-title ellipsis">{{ item.filename }}</div>
              <div class="card-meta">
                <span v-if="item.event_name">{{ item.event_name }}</span>
                <span v-if="item.quality_score">{{ item.quality_score.toFixed(0) }}分</span>
              </div>
              <div class="card-tags" v-if="item.tags.length">
                <el-tag v-for="tag in item.tags.slice(0, 3)" :key="tag" size="small" type="info">{{ tag }}</el-tag>
              </div>
            </div>
          </div>

          <el-empty v-if="!loading && results.length === 0" description="暂无搜索结果" />
        </div>

        <!-- 分页 -->
        <el-pagination
          v-if="total > 0"
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          :page-sizes="[20, 40, 60]"
          @change="doSearch"
          style="margin-top: 20px; justify-content: center"
        />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const searchQuery = ref((route.query.q as string) || '')
const loading = ref(false)
const results = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const dateRange = ref<string[]>([])

const filters = reactive({
  materialType: undefined as string | undefined,
  personName: '',
  eventName: '',
  minQuality: 0,
  excludeDuplicates: true,
})

function doSearch() {
  loading.value = true
  // TODO: 调用 materialApi.search()
  setTimeout(() => {
    loading.value = false
  }, 500)
}

function resetFilters() {
  filters.materialType = undefined
  filters.personName = ''
  filters.eventName = ''
  filters.minQuality = 0
  filters.excludeDuplicates = true
  dateRange.value = []
}

function goDetail(id: number) {
  router.push({ name: 'MaterialDetail', params: { id } })
}

onMounted(() => {
  if (searchQuery.value) {
    doSearch()
  }
})
</script>

<style scoped lang="scss">
.search-result-page {
  height: calc(100vh - var(--header-height));
}

.filter-aside {
  background: #fff;
  padding: 20px;
  border-right: 1px solid var(--border-color);
  overflow-y: auto;

  h4 {
    margin-bottom: 16px;
  }
}

.result-main {
  padding: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;

  .el-input {
    max-width: 500px;
  }

  .result-count {
    color: var(--text-secondary);
    font-size: 13px;
    white-space: nowrap;
  }
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  min-height: 300px;
}

.material-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid var(--border-color);
  transition: all 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
}

.card-thumb {
  position: relative;
  width: 100%;
  height: 160px;
  background: #f0f0f0;
  overflow: hidden;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .thumb-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    font-size: 14px;
  }

  .type-tag {
    position: absolute;
    top: 8px;
    right: 8px;
  }
}

.card-info {
  padding: 10px;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
}

.card-meta {
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  gap: 8px;
  margin-bottom: 6px;
}

.card-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
</style>
