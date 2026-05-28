import { apiClient } from './client'

export interface RecipeSearchItem {
  recipe_id: string
  type: string
  outputs: string[]
  output_labels: string[]
  output_count: number
  source_file?: string | null
}

export interface UploadSummary {
  inserted: number
  updated: number
  skipped: number
  total_seen: number
}

export interface UploadResponse {
  filenames: string[]
  translation_files?: string[]
  translation_summary?: {
    entries: number
    files: number
    labels_refreshed: number
  }
  failed_files?: string[]
  summary: UploadSummary
}

export interface InventoryItem {
  item_id: string
  amount: number
}

export interface TreeNode {
  item_id: string
  item_label?: string | null
  amount: number
  recipe_id?: string | null
  craft_count: number
  children: TreeNode[]
  is_base: boolean
}

export interface MaterialItem {
  item_id: string
  item_label?: string | null
  amount_needed: number
  amount_available: number
  amount_shortage: number
}

export interface CalculateResponse {
  target_item: string
  target_label?: string | null
  amount: number
  tree: TreeNode
  materials: MaterialItem[]
  unresolved_cycles: string[]
}

export function uploadRecipeFiles(files: File[], onProgress?: (percent: number) => void) {
  const formData = new FormData()
  for (const file of files) {
    const relativePath = file.webkitRelativePath || file.name
    formData.append('files', file, relativePath)
  }
  return apiClient.post<UploadResponse>('/upload', formData, {
    onUploadProgress(event) {
      if (!event.total || !onProgress) return
      onProgress(Math.round((event.loaded / event.total) * 100))
    }
  })
}

export function uploadTranslationFiles(files: File[], onProgress?: (percent: number) => void) {
  const formData = new FormData()
  for (const file of files) {
    formData.append('files', file, file.webkitRelativePath || file.name)
  }
  return apiClient.post<UploadResponse>('/upload', formData, {
    onUploadProgress(event) {
      if (!event.total || !onProgress) return
      onProgress(Math.round((event.loaded / event.total) * 100))
    }
  })
}

export function splitFilesIntoBatches(files: File[], batchSize: number) {
  const batches: File[][] = []
  for (let index = 0; index < files.length; index += batchSize) {
    batches.push(files.slice(index, index + batchSize))
  }
  return batches
}

export function searchRecipes(query: string, limit = 20) {
  return apiClient.get<{ items: RecipeSearchItem[] }>('/recipes/search', {
    params: { query, limit }
  })
}

export function calculateRecipe(payload: {
  target_item: string
  amount: number
  recipe_id?: string | null
  inventory: InventoryItem[]
}) {
  return apiClient.post<CalculateResponse>('/calculate', payload)
}
