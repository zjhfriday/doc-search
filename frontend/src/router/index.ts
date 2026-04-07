import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  // ── 登录 ──────────────────────────────────────────────────
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },

  // ── 检索门户（普通用户主入口） ─────────────────────────────
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    children: [
      {
        path: '',
        name: 'SearchHome',
        component: () => import('@/views/search/SearchHome.vue'),
        meta: { title: '素材检索' },
      },
      {
        path: 'search/result',
        name: 'SearchResult',
        component: () => import('@/views/search/SearchResult.vue'),
        meta: { title: '检索结果' },
      },
      {
        path: 'material/:id',
        name: 'MaterialDetail',
        component: () => import('@/views/search/MaterialDetail.vue'),
        meta: { title: '素材详情' },
      },
    ],
  },

  // ── 管理后台（管理员） ────────────────────────────────────
  {
    path: '/admin',
    component: () => import('@/views/AdminLayout.vue'),
    meta: { requiresRole: ['super_admin', 'manager'] },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '数据看板' },
      },
      {
        path: 'upload',
        name: 'UploadManager',
        component: () => import('@/views/admin/UploadManager.vue'),
        meta: { title: '上传管理' },
      },
      {
        path: 'audit',
        name: 'AuditCenter',
        component: () => import('@/views/admin/AuditCenter.vue'),
        meta: { title: '素材审核' },
      },
      {
        path: 'dedup',
        name: 'DedupManager',
        component: () => import('@/views/admin/DedupManager.vue'),
        meta: { title: '查重管理' },
      },
      {
        path: 'logs',
        name: 'LogQuery',
        component: () => import('@/views/admin/LogQuery.vue'),
        meta: { title: '操作日志' },
      },
      {
        path: 'face-library',
        name: 'FaceLibrary',
        component: () => import('@/views/admin/FaceLibrary.vue'),
        meta: { title: '人脸库管理' },
      },
    ],
  },

  // ── 系统管理（超级管理员） ─────────────────────────────────
  {
    path: '/system',
    component: () => import('@/views/AdminLayout.vue'),
    meta: { requiresRole: ['super_admin'] },
    children: [
      {
        path: 'users',
        name: 'UserManage',
        component: () => import('@/views/system/UserManage.vue'),
        meta: { title: '用户管理' },
      },
      {
        path: 'roles',
        name: 'RoleManage',
        component: () => import('@/views/system/RoleManage.vue'),
        meta: { title: '角色权限' },
      },
      {
        path: 'config',
        name: 'SystemConfig',
        component: () => import('@/views/system/SystemConfig.vue'),
        meta: { title: '系统配置' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()

  // 不需要认证的页面
  if (to.meta.requiresAuth === false) {
    next()
    return
  }

  // 检查登录状态
  if (!userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  // 检查角色权限
  const requiredRoles = to.meta.requiresRole as string[] | undefined
  if (requiredRoles && !requiredRoles.includes(userStore.user?.role || '')) {
    next({ name: 'SearchHome' })
    return
  }

  next()
})

export default router
