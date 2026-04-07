<template>
  <el-container class="main-layout">
    <!-- 顶部导航 -->
    <el-header class="top-header">
      <div class="header-left">
        <router-link to="/" class="logo">党群素材智能检索平台</router-link>
      </div>
      <div class="header-right">
        <el-button v-if="userStore.isAdmin" text @click="$router.push('/admin')">
          管理后台
        </el-button>
        <el-dropdown>
          <span class="user-info">
            {{ userStore.user?.display_name || userStore.user?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="userStore.logout(); $router.push('/login')">
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>

    <!-- 内容区 -->
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { ArrowDown } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
}

.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid var(--border-color);
  padding: 0 24px;
  height: var(--header-height);
}

.logo {
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
  text-decoration: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

.main-content {
  background: var(--bg-color);
  overflow-y: auto;
  padding: 0;
}
</style>
