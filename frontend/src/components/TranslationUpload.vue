<script setup lang="ts">
import { computed, ref } from 'vue'

import { useRecipeStore } from '../stores/recipeStore'

const store = useRecipeStore()
const selectedFiles = ref<File[]>([])

const jsonFiles = computed(() => selectedFiles.value.filter((file) => file.name.endsWith('.json')))
const selectedLabel = computed(() => {
  if (jsonFiles.value.length === 0) return '选择一个或多个 zh_cn.json 文件'
  if (jsonFiles.value.length === 1) return jsonFiles.value[0].webkitRelativePath || jsonFiles.value[0].name
  return `已选择 ${jsonFiles.value.length} 个翻译文件`
})

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  selectedFiles.value = Array.from(target.files ?? [])
}

async function submit() {
  if (jsonFiles.value.length === 0) return
  await store.uploadTranslations(jsonFiles.value)
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>导入中文名称</h2>
        <p>
          可选导入模组或资源包中的 <code>zh_cn.json</code>。
          导入后，搜索结果和合成树会优先显示中文名称。
        </p>
        <p class="hint">
          常见路径：<code>assets/&lt;modid&gt;/lang/zh_cn.json</code>。
          你可以一次选择多个翻译文件，后导入的内容会覆盖先导入的同名键。
        </p>
      </div>
    </div>

    <div class="upload-row">
      <label class="file-picker">
        <input type="file" accept=".json,application/json" multiple @change="onFileChange" />
        <span>{{ selectedLabel }}</span>
      </label>
      <button :disabled="jsonFiles.length === 0 || store.loading" @click="submit">
        上传中文名
      </button>
    </div>

    <div v-if="jsonFiles.length > 0" class="file-count">
      将导入 {{ jsonFiles.length }} 个翻译文件。
    </div>
  </section>
</template>
