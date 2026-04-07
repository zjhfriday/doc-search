<template>
  <el-container class="admin-layout">
    <!-- 顶部导航 -->
    <el-header class="top-header">
      <div class="header-left">
        <router-link to="/admin" class="logo">素材管理后台</router-link>
      </div>
      <div class="header-right">
        <el-button text @click="$router.push('/')">回到检索</el-button>
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

    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="220px" class="sidebar">
        <el-menu :default-active="$route.path" router>
          <el-menu-item index="/admin">
            <el-icon><DataBoard /></el-icon>
            <span>数据看板</span>
          </el-menu-item>
          <el-menu-item index="/admin/upload">
            <el-icon><Upload /></el-icon>
            <span>上传管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/audit">
            <el-icon><Checked /></el-icon>
            <span>素材审核</span>
          </el-menu-item>
          <el-menu-item index="/admin/dedup">
            <el-icon><CopyDocument /></el-icon>
            <span>查重管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/face-library">
            <el-icon><Avatar /></el-icon>
            <span>人脸库</span>
          </el-menu-item>
          <el-menu-item index="/admin/logs">
            <el-icon><Document /></el-icon>
            <span>操作日志</span>
          </el-menu-item>

          <el-sub-menu v-if="userStore.user?.role === 'super_admin'" index="/system">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/system/users">用户管理</el-menu-item>
            <el-menu-item index="/system/roles">角色权限</el-menu-item>
            <el-menu-item index="/system/config">系统配置</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 内容区 -->
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import {
  ArrowDown, DataBoard, Upload, Checked,
  CopyDocument, Avatar, Document, Setting,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
</script>

<style scoped lang="scss">
.admin-layout {
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

.sidebar {
  background: #fff;
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
}

.admin-main {
  background: var(--bg-color);
  padding: 20px;
}
</style>
