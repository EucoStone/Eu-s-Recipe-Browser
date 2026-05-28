<script setup lang="ts">
import { ref, watch } from 'vue'

import type { InventoryItem, RecipeSearchItem } from '../api/recipes'
import { useRecipeStore } from '../stores/recipeStore'

const store = useRecipeStore()
const targetItem = ref('')
const amount = ref(1)
const inventoryText = ref('')
let searchTimer: number | undefined

watch(targetItem, (value) => {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => {
    store.search(value)
  }, 250)
})

function selectRecipe(recipe: RecipeSearchItem) {
  targetItem.value = recipe.outputs[0] ?? ''
  store.selectedRecipeId = recipe.recipe_id
}

function parseInventory(): InventoryItem[] {
  return inventoryText.value
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const [itemId, amountValue] = line.split(/[,\s]+/)
      return {
        item_id: itemId,
        amount: Number(amountValue || 0)
      }
    })
    .filter((entry) => entry.item_id && Number.isFinite(entry.amount))
}

async function calculate() {
  if (!targetItem.value.trim()) return
  await store.calculate(targetItem.value.trim(), amount.value, parseInventory())
}
</script>

<template>
  <section class="panel">
    <div class="panel-header">
      <div>
        <h2>配方计算</h2>
        <p>输入物品名称或 ID，选择匹配的配方后生成合成树与基础材料清单。</p>
      </div>
    </div>

    <div class="query-grid">
      <label>
        <span>目标物品</span>
        <input v-model="targetItem" placeholder="Pattern Provider 或 ae2:pattern_provider" />
      </label>
      <label>
        <span>数量</span>
        <input v-model.number="amount" min="1" type="number" />
      </label>
      <button :disabled="store.loading || !targetItem.trim()" @click="calculate">计算</button>
    </div>

    <div v-if="store.searchResults.length" class="search-results">
      <button
        v-for="recipe in store.searchResults"
        :key="recipe.recipe_id"
        :class="{ active: store.selectedRecipeId === recipe.recipe_id }"
        @click="selectRecipe(recipe)"
      >
        <strong>{{ recipe.output_labels.join(', ') || recipe.outputs.join(', ') }}</strong>
        <span>{{ recipe.outputs.join(', ') }}</span>
        <span>{{ recipe.type }} · {{ recipe.source_file || recipe.recipe_id }}</span>
      </button>
    </div>

    <label class="inventory">
      <span>已有库存，可选。每行格式：物品ID 数量</span>
      <textarea v-model="inventoryText" rows="5" placeholder="minecraft:oak_planks 32"></textarea>
    </label>
  </section>
</template>
