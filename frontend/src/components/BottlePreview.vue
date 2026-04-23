<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-150"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div
        v-if="show && bottle"
        class="fixed z-50 bg-gh-surface border border-gh-border rounded-lg shadow-2xl p-3 w-[200px] pointer-events-none"
        :style="{ left: position.x + 'px', top: position.y + 'px' }"
      >
        <div class="w-full h-[100px] bg-gh-bg rounded-md overflow-hidden flex items-center justify-center mb-2">
          <img
            v-if="bottle.image_path"
            :src="getImageUrl(bottle.image_path)"
            :alt="bottle.name"
            class="w-full h-full object-contain"
          />
          <WineBottleIcon v-else :type="bottle.type" :size="50" />
        </div>
        <div class="text-gh-text font-medium text-sm truncate leading-tight">{{ bottle.name }}</div>
        <div class="text-gh-text-secondary text-xs mt-1 flex items-center gap-2">
          <span>{{ bottle.year }}</span>
          <span v-if="bottle.rating" class="flex items-center gap-1 text-gh-accent-gold">
            <StarIcon class="w-3 h-3" /> {{ bottle.rating }}/5
          </span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { StarIcon } from '@heroicons/vue/24/solid'
import WineBottleIcon from './WineBottleIcon.vue'
import config from '../config.js'

const props = defineProps({
  bottle: Object,
  show: Boolean,
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
})

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  // Les uploads sont servis directement depuis /uploads/ (pas sous /api/v1)
  if (path.includes('uploads')) return path
  return `${config.API_BASE_URL}${path}`
}
</script>
