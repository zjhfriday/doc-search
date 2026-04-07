import request from './request'
import type { Material, PagedList, SearchResponse } from './types'

export const materialApi = {
  /** 素材列表 */
  list(params: Record<string, any>): Promise<PagedList<Material>> {
    return request.get('/materials', { params })
  },

  /** 素材详情 */
  detail(id: number): Promise<Material> {
    return request.get(`/materials/${id}`)
  },

  /** 更新素材 */
  update(id: number, data: Record<string, any>): Promise<Material> {
    return request.put(`/materials/${id}`, data)
  },

  /** 删除素材 */
  delete(id: number): Promise<void> {
    return request.delete(`/materials/${id}`)
  },

  /** 审核通过 */
  approve(id: number): Promise<void> {
    return request.post(`/materials/${id}/approve`)
  },

  /** 审核驳回 */
  reject(id: number): Promise<void> {
    return request.post(`/materials/${id}/reject`)
  },

  /** 文本/语义检索 */
  search(data: Record<string, any>): Promise<SearchResponse> {
    return request.post('/search', data)
  },

  /** 以图搜图 */
  searchByImage(file: File, params?: Record<string, any>): Promise<SearchResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (params) {
      Object.entries(params).forEach(([k, v]) => formData.append(k, String(v)))
    }
    return request.post('/search/by-image', formData)
  },

  /** 人脸检索 */
  searchByFace(file: File, params?: Record<string, any>): Promise<SearchResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (params) {
      Object.entries(params).forEach(([k, v]) => formData.append(k, String(v)))
    }
    return request.post('/search/by-face', formData)
  },

  /** 单文件上传 */
  uploadSingle(file: File, meta?: Record<string, any>): Promise<any> {
    const formData = new FormData()
    formData.append('file', file)
    if (meta) {
      Object.entries(meta).forEach(([k, v]) => {
        if (v !== undefined && v !== null) formData.append(k, String(v))
      })
    }
    return request.post('/upload/single', formData)
  },

  /** 批量上传 */
  uploadBatch(files: File[], meta?: Record<string, any>): Promise<any> {
    const formData = new FormData()
    files.forEach((f) => formData.append('files', f))
    if (meta) {
      Object.entries(meta).forEach(([k, v]) => {
        if (v !== undefined && v !== null) formData.append(k, String(v))
      })
    }
    return request.post('/upload/batch', formData)
  },
}
