<template>
  <div class="grid grid-cols-5 gap-2">
    <button
      v-for="type in wineTypes"
      :key="type.value"
      type="button"
      :class="[
        'flex flex-col items-center justify-center p-3 rounded-card border-2 transition-fast',
        modelValue === type.value
          ? `border-${type.color} bg-${type.color}/10 ${colorToShadow[type.color]}`
          : 'border-gh-border hover:border-gh-border-hover bg-gh-bg'
      ]"
      @click="selectType(type.value)"
    >
      <span class="w-4 h-4 rounded-full" :class="`bg-${type.color}`"></span>
      <span :class="[
        'text-xs font-medium',
        modelValue === type.value ? `text-${type.color}` : 'text-gh-text-secondary'
      ]">
        {{ type.label }}
      </span>
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    default: 'Rouge'
  }
})

const emit = defineEmits(['update:modelValue'])

const colorToShadow = {
  'wine-red': 'shadow-glow-red',
  'wine-white': 'shadow-glow-yellow',
  'wine-rose': 'shadow-glow-pink',
  'wine-champagne': 'shadow-glow-purple',
  'wine-default': 'shadow-glow-gray'
}

const wineTypes = [
  { value: 'Rouge', label: 'Rouge', color: 'wine-red' },
  { value: 'Blanc', label: 'Blanc', color: 'wine-white' },
  { value: 'Rosé', label: 'Rosé', color: 'wine-rose' },
  { value: 'Champagne', label: 'Champagne', color: 'wine-champagne' },
  { value: 'Spiritueux', label: 'Spirit', color: 'wine-default' }
]

const selectType = (value) => {
  emit('update:modelValue', value)
}
</script>