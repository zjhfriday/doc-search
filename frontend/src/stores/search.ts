import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface SearchFilters {
  materialType?: string
  eventName?: string
  dateFrom?: string
  dateTo?: string
  personName?: string
  scene?: string
  minQuality?: number
  securityLevel?: string
  excludeDuplicates: boolean
}

export const useSearchStore = defineStore('search', () => {
  const query = ref('')
  const searchType = ref<'text' | 'image' | 'face' | 'video_frame'>('text')
  const filters = ref<SearchFilters>({
    excludeDuplicates: true,
  })
  const results = ref<any[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)

  function setQuery(q: string) {
    query.value = q
    page.value = 1
  }

  function resetFilters() {
    filters.value = { excludeDuplicates: true }
    page.value = 1
  }

  return {
    query, searchType, filters, results, total,
    page, pageSize, loading,
    setQuery, resetFilters,
  }
})
