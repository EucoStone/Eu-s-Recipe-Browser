import { defineStore } from 'pinia'

import {
  calculateRecipe,
  searchRecipes,
  splitFilesIntoBatches,
  uploadRecipeFiles,
  uploadTranslationFiles,
  type CalculateResponse,
  type InventoryItem,
  type RecipeSearchItem,
  type UploadSummary
} from '../api/recipes'

export const useRecipeStore = defineStore('recipe', {
  state: () => ({
    uploadProgress: 0,
    uploadSummary: null as UploadSummary | null,
    searchResults: [] as RecipeSearchItem[],
    selectedRecipeId: null as string | null,
    calculation: null as CalculateResponse | null,
    loading: false,
    message: '',
    error: ''
  }),
  actions: {
    async upload(files: File[]) {
      this.loading = true
      this.error = ''
      this.message = ''
      this.uploadProgress = 0
      try {
        const batches = splitFilesIntoBatches(files, 20)
        const totals: UploadSummary = { inserted: 0, updated: 0, skipped: 0, total_seen: 0 }
        const failedBatches: number[] = []
        let processedFiles = 0

        for (const [index, batch] of batches.entries()) {
          try {
            const response = await uploadRecipeFiles(batch)
            totals.inserted += response.data.summary.inserted
            totals.updated += response.data.summary.updated
            totals.skipped += response.data.summary.skipped
            totals.total_seen += response.data.summary.total_seen
          } catch (error) {
            failedBatches.push(index + 1)
            if (failedBatches.length === batches.length) throw error
          } finally {
            processedFiles += batch.length
            this.uploadProgress = Math.round((processedFiles / files.length) * 100)
          }
        }

        this.uploadSummary = totals
        this.error = failedBatches.length > 0 ? `有 ${failedBatches.length} 个批次上传失败，已忽略后继续导入。` : ''
        this.message = `已导入 ${totals.inserted} 条，更新 ${totals.updated} 条，跳过 ${totals.skipped} 条。`
      } catch (error: any) {
        this.error = error?.response?.data?.detail ?? '上传失败，请检查后端服务和文件格式。'
      } finally {
        this.loading = false
      }
    },
    async uploadTranslations(files: File[]) {
      this.loading = true
      this.error = ''
      this.message = ''
      try {
        const response = await uploadTranslationFiles(files)
        const summary = response.data.translation_summary
        this.message = `已导入 ${summary?.files ?? files.length} 个翻译文件，读取 ${summary?.entries ?? 0} 条中文名称。`
      } catch (error: any) {
        this.error = error?.response?.data?.detail ?? '中文名称导入失败，请确认文件是 zh_cn.json。'
      } finally {
        this.loading = false
      }
    },
    clearCalculation() {
      this.calculation = null
    },
    async search(query: string) {
      if (!query.trim()) {
        this.searchResults = []
        return
      }
      this.error = ''
      try {
        const response = await searchRecipes(query.trim())
        this.searchResults = response.data.items
      } catch (error: any) {
        this.error = error?.response?.data?.detail ?? '搜索失败。'
      }
    },
    async calculate(targetItem: string, amount: number, inventory: InventoryItem[]) {
      this.loading = true
      this.error = ''
      this.message = ''
      try {
        const response = await calculateRecipe({
          target_item: targetItem,
          amount,
          recipe_id: this.selectedRecipeId,
          inventory
        })
        this.calculation = response.data
      } catch (error: any) {
        this.error = error?.response?.data?.detail ?? '计算失败，请确认目标物品已有导入数据。'
      } finally {
        this.loading = false
      }
    }
  }
})
