<script setup lang="ts">
import type { TreeNode } from '../api/recipes'

defineOptions({
  name: 'TreeNode'
})

defineProps<{
  node: TreeNode
}>()
</script>

<template>
  <li>
    <div class="tree-node" :class="{ base: node.is_base }">
      <span class="item">
        <span class="label">{{ node.item_label || node.item_id }}</span>
        <span class="id">{{ node.item_id }}</span>
      </span>
      <span class="meta">
        x{{ node.amount }}<span v-if="node.craft_count"> x {{ node.craft_count }}</span>
      </span>
    </div>
    <ul v-if="node.children.length">
      <TreeNode
        v-for="child in node.children"
        :key="`${child.item_id}-${child.amount}-${child.recipe_id}`"
        :node="child"
      />
    </ul>
  </li>
</template>
