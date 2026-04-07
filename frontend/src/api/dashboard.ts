import request from './request'
import type { DashboardOverview } from './types'

export const dashboardApi = {
  overview(): Promise<DashboardOverview> {
    return request.get('/dashboard/overview')
  },

  storage(): Promise<any> {
    return request.get('/dashboard/storage')
  },
}
