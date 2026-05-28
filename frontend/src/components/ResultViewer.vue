<script setup lang="ts">
import { useRecipeStore } from '../stores/recipeStore'
import TreeNode from './TreeNode.vue'

const store = useRecipeStore()
</script>

<template>
  <section v-if="store.calculation" class="results">
    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>合成树</h2>
          <p>{{ store.calculation.target_label || store.calculation.target_item }} x{{ store.calculation.amount }}</p>
        </div>
        <button class="ghost-button" @click="store.clearCalculation()">关闭</button>
      </div>
      <ul class="tree">
        <TreeNode :node="store.calculation.tree" />
      </ul>
      <p v-if="store.calculation.unresolved_cycles.length" class="warning">
        检测到可能的循环配方：{{ store.calculation.unresolved_cycles.join(', ') }}
      </p>
    </div>

    <div class="panel">
      <div class="panel-header">
        <div>
          <h2>基础材料总表</h2>
          <p>已扣除输入的库存数量。</p>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>物品</th>
            <th>需求</th>
            <th>已有</th>
            <th>缺口</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="material in store.calculation.materials" :key="material.item_id">
            <td>
              <div>{{ material.item_label || material.item_id }}</div>
              <small>{{ material.item_id }}</small>
            </td>
            <td>{{ material.amount_needed }}</td>
            <td>{{ material.amount_available }}</td>
            <td>{{ material.amount_shortage }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
