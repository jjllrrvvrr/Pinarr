<template>
  <div class="flex items-center gap-1">
    <button
      v-for="star in 5"
      :key="star"
      type="button"
      class="p-1 transition-fast hover:scale-110 focus:outline-none"
      @click="setRating(star)"
      @mouseenter="hoverRating = star"
      @mouseleave="hoverRating = 0"
    >
      <StarIcon
        :filled="star <= (hoverRating || modelValue)"
        :class="[
          'w-6 h-6',
          star <= (hoverRating || modelValue) ? 'text-gh-accent-gold' : 'text-gh-border'
        ]"
      />
    </button>
    
    <span v-if="modelValue > 0" class="ml-2 text-sm text-gh-text-secondary">
      {{ modelValue }}/5
    </span>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import StarIcon from './icons/StarIcon.vue'

const props = defineProps({
  modelValue: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

const hoverRating = ref(0)

const setRating = (rating) => {
  emit('update:modelValue', rating)
}
</script>