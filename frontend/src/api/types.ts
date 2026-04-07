/** 用户信息 */
export interface UserInfo {
  id: number
  username: string
  display_name?: string
  email?: string
  department?: string
  role: 'super_admin' | 'manager' | 'user' | 'guest'
  is_active: boolean
  last_login_at?: string
  created_at: string
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

/** 标签 */
export interface Tag {
  id: number
  name: string
  category: string
}

/** 素材信息 */
export interface Material {
  id: number
  filename: string
  material_type: 'image' | 'video'
  file_size: number
  thumbnail_path?: string
  width?: number
  height?: number
  duration?: number
  title?: string
  description?: string
  event_name?: string
  event_date?: string
  status: 'pending' | 'processing' | 'approved' | 'rejected' | 'archived'
  security_level: 'public' | 'internal' | 'restricted' | 'confidential'
  quality_score?: number
  is_duplicate: boolean
  ocr_text?: string
  asr_text?: string
  tags: Tag[]
  created_at: string
  updated_at: string
}

/** 分页列表 */
export interface PagedList<T> {
  total: number
  page: number
  page_size: number
  items: T[]
}

/** 检索结果项 */
export interface SearchResultItem {
  material_id: number
  filename: string
  material_type: string
  thumbnail_url?: string
  preview_url?: string
  relevance_score: number
  quality_score?: number
  security_level: string
  event_name?: string
  tags: string[]
  matched_faces: string[]
  timestamp_start?: number
  timestamp_end?: number
  created_at?: string
}

/** 检索响应 */
export interface SearchResponse {
  total: number
  page: number
  page_size: number
  search_type: string
  query?: string
  items: SearchResultItem[]
}

/** 看板数据 */
export interface DashboardOverview {
  total_materials: number
  image_count: number
  video_count: number
  pending_count: number
  processing_count: number
  total_size_bytes: number
  total_size_gb: number
  download_count: number
  user_count: number
}
