<template>
  <div class="w-full">
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-gh-text-secondary mb-1">
      {{ label }}
      <span v-if="required" class="text-gh-accent-red">*</span>
    </label>
    
    <div class="relative">
      <div v-if="$slots.prefix || prefixIcon" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <slot name="prefix">
          <component :is="prefixIcon" v-if="prefixIcon" class="h-5 w-5 text-gh-text-muted" />
        </slot>
      </div>
      
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :class="inputClasses"
        @input="$emit('update:modelValue', $event.target.value)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      />
      
      <div v-if="$slots.suffix || suffixIcon || loading" class="absolute inset-y-0 right-0 pr-3 flex items-center">
        <slot name="suffix">
          <svg v-if="loading" class="animate-spin h-5 w-5 text-gh-text-muted" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
          </svg>
          <component :is="suffixIcon" v-else-if="suffixIcon" class="h-5 w-5 text-gh-text-muted" />
        </slot>
      </div>
    </div>    
    
    <p v-if="error" class="mt-1 text-sm text-gh-accent-red">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-sm text-gh-text-muted">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  prefixIcon: {
    type: [Object, Function],
    default: null
  },
  suffixIcon: {
    type: [Object, Function],
    default: null
  },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'error', 'success'].includes(v)
  }
})

defineEmits(['update:modelValue', 'blur', 'focus'])

const inputId = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const inputClasses = computed(() => {
  const base = 'block w-full rounded-button text-gh-text placeholder-gh-text-muted focus:outline-none focus:ring-1 focus:border-gh-accent transition-fast disabled:opacity-50 disabled:cursor-not-allowed'
  
  const sizes = {
    sm: 'pl-3 pr-3 py-1.5 text-xs',
    md: 'pl-4 pr-4 py-2 text-sm',
    lg: 'pl-4 pr-4 py-3 text-base'
  }
  
  const sizesWithIcons = {
    sm: 'pl-9 pr-3 py-1.5 text-xs',
    md: 'pl-10 pr-10 py-2 text-sm',
    lg: 'pl-11 pr-11 py-3 text-base'
  }
  
  const variants = {
    default: 'bg-gh-bg border border-gh-border focus:ring-gh-accent',
    error: 'bg-gh-bg border border-gh-accent-red focus:ring-gh-accent-red focus:border-gh-accent-red',
    success: 'bg-gh-bg border border-gh-accent-green focus:ring-gh-accent-green focus:border-gh-accent-green'
  }
  
  const hasPrefix = props.prefixIcon || props.$slots?.prefix
  const hasSuffix = props.suffixIcon || props.loading || props.$slots?.suffix
  
  let sizeClasses = sizes[props.size]
  if (hasPrefix || hasSuffix) {
    sizeClasses = sizesWithIcons[props.size]
  }
  
  return `${base} ${sizeClasses} ${variants[props.variant]}`
})
</script>