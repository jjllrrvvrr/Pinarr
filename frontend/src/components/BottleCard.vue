<template>
  <div
    :class="[
      'bg-gh-surface border border-gh-border rounded-md transition-all cursor-pointer group',
      archived ? 'opacity-50 hover:opacity-70' : 'hover:border-gh-accent',
      viewMode === 'grid' ? 'max-h-[300px] flex' : 'flex items-center'
    ]"
    @click="goToDetail"
  >
    <template v-if="viewMode === 'grid'">
      <div class="w-16 sm:w-20 lg:w-24 h-[100px] sm:h-[120px] lg:h-[149px] flex-shrink-0 bg-gh-card-image flex items-center justify-center overflow-hidden rounded-l-md border-r border-gh-border relative">
        <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full h-[80px] sm:h-[100px] lg:h-[120px] object-contain" />
        <WineBottleIcon v-else :type="bottle.type" :size="48" class="sm:w-[60px]" />
        <span v-if="archived" class="absolute top-1 left-1 bg-gh-accent-red text-gh-text-inverse text-[8px] px-1 rounded">Épuisé</span>
      </div>

      <div class="flex-1 flex flex-col min-w-0">
        <div class="flex-1 p-2 sm:p-2.5 border-b border-gh-border flex flex-col justify-center gap-0.5">
          <div class="flex items-center justify-between">
            <span class="inline-flex items-center gap-1 sm:gap-1.5">
              <span :class="['w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full', getTypeDotClass(bottle.type)]"></span>
              <span class="text-xs text-gh-text font-medium">{{ bottle.type }}</span>
            </span>
            <div class="flex items-center gap-1 sm:gap-2 text-xs text-gh-text-secondary">
              <span v-if="bottle.cepage" @click.stop="$emit('filter', 'cepage', bottle.cepage)" 
                    class="truncate max-w-[50px] sm:max-w-[70px] hover:text-gh-accent-red cursor-pointer transition">{{ bottle.cepage }}</span>
              <span class="font-mono text-gh-text hover:text-gh-accent cursor-pointer transition" @click.stop="$emit('filter', 'year', bottle.year)">{{ bottle.year }}</span>
              <WinePhaseBadge
                v-if="bottle.year"
                :vintage-year="bottle.year"
                :jeunesse-end="bottle.jeunesse_end"
                :maturite-end="bottle.maturite_end"
                :apogee-end="bottle.apogee_end"
              />
            </div>
          </div>
          <h3 class="text-gh-text font-semibold truncate group-hover:text-gh-accent transition text-xs sm:text-sm leading-tight">{{ bottle.name }}</h3>
          <p v-if="bottle.domaine" @click.stop="$emit('filter', 'domaine', bottle.domaine)" 
             class="text-gh-text-secondary text-[10px] sm:text-xs truncate hover:text-gh-accent-gold cursor-pointer transition">{{ bottle.domaine }}</p>
          <p v-else class="text-gh-text-secondary text-[10px] sm:text-xs truncate">—</p>
          <div v-if="bottle.location" class="flex items-center gap-1 text-[10px] sm:text-xs text-gh-text-secondary mt-1">
            <MapPinIcon class="w-2.5 h-2.5 sm:w-3 sm:h-3 flex-shrink-0" />
            <span class="truncate">{{ bottle.location }}</span>
          </div>
        </div>

        <div class="px-2 sm:px-2.5 py-1.5 sm:py-2 flex items-center gap-1 sm:gap-2">
          <div class="flex flex-wrap gap-0.5 sm:gap-1 flex-1 min-w-0">
            <span v-for="tag in bottle.tags?.split(',').slice(0,2)" :key="tag"
                  @click.stop="$emit('filter', 'tag', tag.trim())"
                  class="text-[8px] sm:text-[10px] px-1 sm:px-1.5 py-0.5 rounded text-gh-text-secondary bg-gh-bg hover:text-gh-accent-pink transition cursor-pointer truncate">
              {{ tag.trim() }}
            </span>
          </div>

           <div class="flex items-center gap-1" @click.stop>
            <button @click="decrement" 
                    class="w-8 h-8 sm:w-5 sm:h-5 flex items-center justify-center text-gh-text-secondary hover:text-gh-text hover:bg-gh-elevated rounded text-sm sm:text-xs transition">−</button>
            <span class="w-4 sm:w-4 text-center text-gh-text font-bold text-sm sm:text-xs">{{ bottle.quantity }}</span>
            <button @click="increment" 
                    class="w-8 h-8 sm:w-5 sm:h-5 flex items-center justify-center text-gh-text-secondary hover:text-gh-text hover:bg-gh-elevated rounded text-sm sm:text-xs transition">+</button>
          </div>

          <div class="flex flex-col items-end">
            <span v-if="bottle.price" class="text-gh-accent-green-text font-bold text-xs">{{ bottle.price }}€</span>
            <span v-if="bottle.rating" class="flex items-center gap-0.5 text-gh-accent-gold text-[10px] sm:text-[10px]">
              <StarSolid class="w-2 h-2 sm:w-2.5 sm:h-2.5" /> {{ bottle.rating }}/5
            </span>
          </div>
        </div>

        <div class="px-2 sm:px-2.5 py-1 sm:py-1.5 border-t border-gh-border flex items-center justify-between bg-gh-bg opacity-0 group-hover:opacity-100 transition" @click.stop>
          <div class="flex items-center gap-1 sm:gap-2">
            <router-link :to="`/edit/${bottle.id}`" class="text-[8px] sm:text-[10px] text-gh-accent hover:underline" @click.stop>Modifier</router-link>
            <button @click="deleteBottle" class="text-[8px] sm:text-[10px] text-gh-text-secondary hover:text-gh-accent-red transition flex items-center gap-1" title="Supprimer">
              <TrashIcon class="w-3 h-3 sm:w-3.5 sm:h-3.5" />
            </button>
          </div>
          <button v-if="!archived" @click="archive" class="text-[8px] sm:text-[10px] text-gh-accent-red hover:underline">Archiver</button>
          <button v-else @click="restore" class="text-[8px] sm:text-[10px] text-gh-accent-green-text hover:underline">Restaurer</button>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="w-10 sm:w-12 h-10 sm:h-12 flex-shrink-0 bg-gh-card-image flex items-center justify-center overflow-hidden rounded-l relative">
        <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full h-full object-cover" />
        <WineBottleIcon v-else :type="bottle.type" :size="20" class="sm:w-6" />
        <span v-if="archived" class="absolute top-0 left-0 bg-gh-accent-red text-gh-text-inverse text-[6px] px-0.5 rounded-br">0</span>
      </div>
      <div class="flex-1 min-w-0 px-2 sm:px-3">
        <div class="flex items-center gap-1 sm:gap-2">
          <span class="text-gh-text font-medium truncate group-hover:text-gh-accent transition text-sm sm:text-base">{{ bottle.name }}</span>
          <span @click.stop="$emit('filter', 'year', bottle.year)" class="text-gh-text-secondary text-xs font-mono hover:text-gh-accent cursor-pointer">{{ bottle.year }}</span>
        </div>
        <div class="flex items-center gap-2 sm:gap-3 text-xs text-gh-text-secondary">
          <span v-if="bottle.domaine" @click.stop="$emit('filter', 'domaine', bottle.domaine)" class="hover:text-gh-accent-gold cursor-pointer truncate">{{ bottle.domaine }}</span>
          <span v-else>—</span>
          <span v-if="bottle.location" class="hidden sm:inline">→ {{ bottle.location }}</span>
        </div>
      </div>
      <div class="flex items-center gap-1 sm:gap-3 pr-2 sm:pr-3" @click.stop>
        <div class="flex items-center gap-1">
          <button @click="decrement" class="w-8 h-8 sm:w-5 sm:h-5 flex items-center justify-center text-gh-text-secondary hover:text-gh-text transition text-sm sm:text-xs">−</button>
          <span class="w-4 text-center text-gh-text font-mono text-sm sm:text-sm">{{ bottle.quantity }}</span>
          <button @click="increment" class="w-8 h-8 sm:w-5 sm:h-5 flex items-center justify-center text-gh-text-secondary hover:text-gh-text transition text-sm sm:text-xs">+</button>
        </div>
        <span v-if="bottle.price" class="text-gh-accent-green-text text-xs sm:text-sm font-mono">{{ bottle.price }}€</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { MapPinIcon, StarIcon as StarSolid, TrashIcon } from '@heroicons/vue/24/solid'
import WineBottleIcon from '@/components/WineBottleIcon.vue'
import WinePhaseBadge from '@/components/WinePhaseBadge.vue'
import { useWineTypeStyles } from '@/composables/useWineTypeStyles.js'
import config from '../config.js'

const { getTypeDotClass } = useWineTypeStyles()

const props = defineProps({
  bottle: {
    type: Object,
    required: true
  },
  viewMode: {
    type: String,
    default: 'grid',
    validator: (value) => ['grid', 'list'].includes(value)
  },
  archived: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['filter', 'update-quantity', 'archive', 'restore', 'delete'])
const router = useRouter()

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  // Les uploads sont servis directement depuis /uploads/ (pas sous /api/v1)
  if (path.includes('uploads')) return path
  return `${config.API_BASE_URL}${path}`
}

const goToDetail = () => {
  router.push(`/wine/${props.bottle.id}`)
}

const increment = () => {
  emit('update-quantity', props.bottle.id, props.bottle.quantity + 1)
}

const decrement = () => {
  const newQty = props.bottle.quantity - 1
  if (newQty < 0) return
  emit('update-quantity', props.bottle.id, newQty)
}

const archive = () => {
  emit('archive', props.bottle.id)
}

const restore = () => {
  emit('restore', props.bottle.id)
}

const deleteBottle = () => {
  if (confirm(`Supprimer "${props.bottle.name}" ?`)) {
    emit('delete', props.bottle.id)
  }
}
</script>
