<template>
  <span
    class="w-3 h-3 rounded-full flex-shrink-0"
    :class="badgeClass"
    :title="type"
  />
</template>

<script setup>
import { computed } from 'vue'
import { useWineColors } from '../composables/useWineColors.js'

const props = defineProps({
  type: {
    type: String,
    default: 'default'
  },
  size: {
    type: String,
    default: 'sm',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  }
})

const { getTypeBgColor } = useWineColors()

const badgeClass = computed(() => {
  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  }
  
  return `${sizeClasses[props.size]} ${getTypeBgColor(props.type)}`
})
</script>