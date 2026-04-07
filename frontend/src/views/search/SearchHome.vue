<template>
  <div class="search-home">
    <!-- 搜索主区域 -->
    <div class="search-hero">
      <h1>党群素材智能检索</h1>
      <p>输入关键词、自然语言描述，或上传图片进行检索</p>

      <div class="search-box">
        <el-input
          v-model="searchQuery"
          size="large"
          placeholder="搜索素材... 例如：去年表彰大会 总经理 发言 高清"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </template>
        </el-input>

        <div class="search-actions">
          <el-upload
            :show-file-list="false"
            :before-upload="handleImageSearch"
            accept="image/*"
          >
            <el-button text>以图搜图</el-button>
          </el-upload>
          <el-upload
            :show-file-list="false"
            :before-upload="handleFaceSearch"
            accept="image/*"
          >
            <el-button text>人脸检索</el-button>
          </el-upload>
        </div>
      </div>
    </div>

    <!-- 常用分类入口 -->
    <div class="category-section">
      <h3>快捷分类</h3>
      <div class="category-grid">
        <div
          v-for="cat in categories"
          :key="cat.name"
          class="category-card"
          @click="searchByCategory(cat.name)"
        >
          <el-icon :size="32"><component :is="cat.icon" /></el-icon>
          <span>{{ cat.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, Flag, Briefcase, UserFilled, Star,
} from '@element-plus/icons-vue'
import { useSearchStore } from '@/stores/search'

const router = useRouter()
const searchStore = useSearchStore()
const searchQuery = ref('')

const categories = [
  { name: '党建', label: '党建活动', icon: Flag },
  { name: '会议', label: '会议素材', icon: Briefcase },
  { name: '领导', label: '领导活动', icon: UserFilled },
  { name: '表彰', label: '表彰活动', icon: Star },
]

function handleSearch() {
  if (!searchQuery.value.trim()) return
  searchStore.setQuery(searchQuery.value)
  searchStore.searchType = 'text'
  router.push({ name: 'SearchResult', query: { q: searchQuery.value } })
}

function searchByCategory(category: string) {
  searchStore.setQuery(category)
  searchStore.searchType = 'text'
  router.push({ name: 'SearchResult', query: { q: category } })
}

function handleImageSearch(file: File) {
  searchStore.searchType = 'image'
  router.push({ name: 'SearchResult', query: { type: 'image' } })
  return false // 阻止默认上传
}

function handleFaceSearch(file: File) {
  searchStore.searchType = 'face'
  router.push({ name: 'SearchResult', query: { type: 'face' } })
  return false
}
</script>

<style scoped lang="scss">
.search-home {
  min-height: calc(100vh - var(--header-height));
}

.search-box {
  max-width: 680px;
  margin: 0 auto;
}

.search-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;

  .el-button {
    color: rgba(255, 255, 255, 0.8);

    &:hover {
      color: #fff;
    }
  }
}

.category-section {
  padding: 40px 24px;
  max-width: 800px;
  margin: 0 auto;

  h3 {
    margin-bottom: 20px;
    color: var(--text-primary);
  }
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.category-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--border-color);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border-color: var(--primary-color);
    color: var(--primary-color);
  }

  span {
    font-size: 14px;
  }
}
</style>
