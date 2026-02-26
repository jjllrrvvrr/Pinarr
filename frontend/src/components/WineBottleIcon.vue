<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, default: 'Rouge' },
  size: { type: Number, default: 24 }
})

const wineColor = computed(() => {
  const colors = {
    'Rouge': '#722f37',
    'Blanc': '#c9a227',
    'Rosé': '#e8a0a0',
    'Champagne': '#d4af37',
    'Spiritueux': '#6b7280'
  }
  return colors[props.type] || '#6b7280'
})
</script>

<template>
  <svg :width="size" :height="size * 2" viewBox="0 0 24 48" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="1" width="8" height="5" rx="1.5" fill="#6b4423"/>
    <rect x="9" y="6" width="6" height="8" :fill="wineColor"/>
    <path d="M6 14 h12 v28 a4 4 0 0 1 -4 4 h-4 a4 4 0 0 1 -4 -4 z" :fill="wineColor"/>
    <rect x="8" y="16" width="2" height="26" fill="rgba(255,255,255,0.1)" rx="1"/>
  </svg>
</template>