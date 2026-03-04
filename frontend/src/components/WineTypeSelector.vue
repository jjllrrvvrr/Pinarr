<template>
  <div class="grid grid-cols-5 gap-2">
    <button
      v-for="type in wineTypes"
      :key="type.value"
      type="button"
      :class="[
        'flex flex-col items-center justify-center p-3 rounded-card border-2 transition-fast',
        modelValue === type.value ? '' : 'border-gh-border hover:border-gh-border-hover bg-gh-bg'
      ]"
      :style="modelValue === type.value ? getSelectedStyle(type.color) : {}"
      @click="selectType(type.value)"
    >
      <span 
        class="text-xs font-medium"
        :style="modelValue === type.value ? { color: `var(--${type.color})` } : {}"
        :class="modelValue === type.value ? '' : 'text-gh-text-secondary'"
      >
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
  'wine-red': '0 0 10px rgba(248, 81, 73, 0.3)',
  'wine-white': '0 0 10px rgba(227, 179, 65, 0.3)',
  'wine-rose': '0 0 10px rgba(219, 97, 162, 0.3)',
  'wine-champagne': '0 0 10px rgba(163, 113, 247, 0.3)',
  'wine-default': '0 0 10px rgba(139, 148, 158, 0.3)'
}

const getSelectedStyle = (color) => {
  return {
    borderColor: `var(--${color})`,
    backgroundColor: `rgba(${getRgbValues(color)}, 0.1)`,
    boxShadow: colorToShadow[color]
  }
}

const getRgbValues = (color) => {
  const rgbMap = {
    'wine-red': '248, 81, 73',
    'wine-white': '227, 179, 65',
    'wine-rose': '219, 97, 162',
    'wine-champagne': '163, 113, 247',
    'wine-default': '139, 148, 158'
  }
  return rgbMap[color] || '139, 148, 158'
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
