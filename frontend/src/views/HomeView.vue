<script setup lang="ts">
import FileUpload from '../components/FileUpload.vue'
import RecipeSearch from '../components/RecipeSearch.vue'
import ResultViewer from '../components/ResultViewer.vue'
import TranslationUpload from '../components/TranslationUpload.vue'
import { useRecipeStore } from '../stores/recipeStore'

const store = useRecipeStore()
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <div>
        <h1>RecipeBrowser</h1>
        <p>Minecraft KubeJS 导出配方浏览与材料计算工具</p>
      </div>
      <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">API 文档</a>
    </header>

    <div v-if="store.message" class="notice success">{{ store.message }}</div>
    <div v-if="store.error" class="notice error">{{ store.error }}</div>

    <div class="workspace">
      <aside class="left-column">
        <FileUpload />
        <TranslationUpload />
        <RecipeSearch />
      </aside>
      <section class="right-column">
        <ResultViewer v-if="store.calculation" />
        <div v-else class="panel placeholder-panel">
          <h2>合成树</h2>
          <p>选择一个配方后，这里会显示合成树与基础材料清单。</p>
        </div>
      </section>
    </div>
  </main>
</template>
