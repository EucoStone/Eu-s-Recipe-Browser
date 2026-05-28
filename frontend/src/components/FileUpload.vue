<script setup lang="ts">
import { computed, ref } from 'vue'

import { useRecipeStore } from '../stores/recipeStore'

const store = useRecipeStore()
const selectedFiles = ref<File[]>([])

const jsonFiles = computed(() => selectedFiles.value.filter((file) => file.name.endsWith('.json')))
const selectedLabel = computed(() => {
  if (jsonFiles.value.length === 0) return '选择 recipes 文件夹或多个 JSON 文件'
  if (jsonFiles.value.length === 1) return jsonFiles.value[0].webkitRelativePath || jsonFiles.value[0].name
  return `已选择 ${jsonFiles.value.length} 个 JSON 文件`
})

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  selectedFiles.value = Array.from(target.files ?? [])
}

async function submit() {
  if (jsonFiles.value.length === 0) return
  await store.upload(jsonFiles.value)
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>导入 KubeJS 配方</h2>
        <p>
          在游戏内执行 <code>/kubejs export</code>，然后选择
          <code>local/kubejs/export/recipes</code> 文件夹，或一次选择其中的多个 JSON 文件。
        </p>
        <p class="hint">
          不要使用 <code>/kubejs export recipes</code>。当前导出结构通常会按 mod 和配方类型分成多级文件夹。
        </p>
      </div>
    </div>

    <div class="upload-row">
      <label class="file-picker">
        <input
          type="file"
          accept=".json,application/json"
          multiple
          webkitdirectory
          directory
          @change="onFileChange"
        />
        <span>{{ selectedLabel }}</span>
      </label>
      <button :disabled="jsonFiles.length === 0 || store.loading" @click="submit">
        上传并解析
      </button>
    </div>

    <div v-if="jsonFiles.length > 0" class="file-count">
      将上传 {{ jsonFiles.length }} 个 JSON 文件。
    </div>

    <div v-if="store.uploadProgress > 0" class="progress">
      <div :style="{ width: `${store.uploadProgress}%` }" />
    </div>
  </section>
</template>
