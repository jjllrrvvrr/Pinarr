<template>
  <button
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="$emit('click', $event)"
  >
    <span v-if="loading" class="inline-flex items-center">
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
      </svg>
      Chargement...
    </span>
    <span v-else class="inline-flex items-center gap-2">
      <slot name="icon-left" />
      <slot>{{ label }}</slot>
      <slot name="icon-right" />
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'danger', 'ghost', 'link'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  type: {
    type: String,
    default: 'button'
  },
  label: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center justify-center font-medium rounded-button transition-fast focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gh-bg focus:ring-gh-accent'
  
  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }
  
  const variants = {
    primary: 'bg-gh-accent-green text-white hover:bg-gh-accent-green-hover focus:ring-gh-accent-green',
    secondary: 'bg-gh-surface border border-gh-border text-gh-text-secondary hover:text-gh-text hover:border-gh-border-hover hover:bg-gh-elevated',
    danger: 'bg-transparent text-gh-accent-red border border-gh-border hover:bg-gh-accent-red/10 hover:border-gh-accent-red',
    ghost: 'bg-transparent text-gh-text-secondary hover:text-gh-text hover:bg-gh-elevated',
    link: 'bg-transparent text-gh-accent hover:text-gh-accent underline-offset-2 hover:underline p-0'
  }
  
  const states = props.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
  const width = props.fullWidth ? 'w-full' : ''
  
  return `${base} ${sizes[props.size]} ${variants[props.variant]} ${states} ${width}`
})
</script>