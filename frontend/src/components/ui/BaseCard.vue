<template>
  <div :class="cardClasses">
    <div v-if="$slots.header || title" class="px-4 py-3 border-b border-gh-border flex items-center justify-between">
      <div class="flex items-center gap-2 flex-1">
        <slot name="icon" />
        <h3 v-if="title" class="font-semibold text-gh-text">{{ title }}</h3>
        <slot name="header" />
      </div>
      <slot name="actions" />
    </div>
    
    <div :class="bodyClasses">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="px-4 py-3 border-t border-gh-border bg-gh-surface/50">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'elevated', 'outlined', 'flat'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  title: {
    type: String,
    default: ''
  },
  hoverable: {
    type: Boolean,
    default: false
  },
  clickable: {
    type: Boolean,
    default: false
  }
})

const cardClasses = computed(() => {
  const base = 'bg-gh-surface border border-gh-border overflow-hidden transition-fast'
  
  const variants = {
    default: 'rounded-card',
    elevated: 'rounded-card shadow-md',
    outlined: 'rounded-card border-2',
    flat: 'rounded-card shadow-none'
  }
  
  const states = props.clickable ? 'cursor-pointer hover:border-gh-border-hover' : ''
  const hover = props.hoverable ? 'hover:shadow-glow-blue hover:border-gh-accent' : ''
  
  return `${base} ${variants[props.variant]} ${states} ${hover}`
})

const bodyClasses = computed(() => {
  const sizes = {
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6'
  }
  
  return `${sizes[props.size]} h-full`
})
</script>