<template>
  <BaseCard variant="flat" class="h-[600px] lg:h-auto lg:max-h-[calc(100vh-200px)] flex flex-col">
    
    <!-- Header avec recherche -->
    <template #header>
      <div class="w-full">
        <BaseInput
          v-model="searchQuery"
          type="text"
          placeholder="Rechercher une bouteille..."
          size="md"
        >
          <template #suffix>
            <MagnifyingGlassIcon class="h-5 w-5 text-gh-text-muted" />
          </template>
        </BaseInput>
      </div>
    </template>
    
    <!-- Liste des bouteilles -->
    <div class="flex-1 overflow-y-auto space-y-3 min-h-0">
      <div
        v-for="bottle in sortedBottles"
        :key="bottle.id"
        class="bg-gh-bg border border-gh-border rounded-card p-3 transition-fast cursor-pointer hover:border-gh-border-hover"
        @mouseenter="onHover(bottle)"
        @mouseleave="onLeave"
        @click="goToBottle(bottle.id)"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <WineTypeBadge :type="bottle.type" />
            <span class="text-gh-text font-medium text-truncate">{{ bottle.name }}</span>
          </div>
          <span class="text-gh-text-secondary text-sm flex-shrink-0">{{ bottle.year }}</span>
        </div>
        
        <div class="text-sm text-gh-text-secondary mt-1 ml-5">
          {{ bottle.quantity }} en stock
          <span v-if="getPlacementCount(bottle) > 0" class="text-gh-accent-green-text">
            • {{ getPlacementCount(bottle) }} placée(s)
          </span>
        </div>
      </div>
      
      <!-- Empty state -->
      <div v-if="sortedBottles.length === 0" class="text-center py-8 text-gh-text-secondary">
        <p class="text-sm">Aucune bouteille trouvée</p>
      </div>
    </div>
    
    <!-- Footer stats -->
    <template #footer>
      <div class="flex justify-between text-xs text-gh-text-secondary">
        <span>{{ placedCount }} placées</span>
        <span>{{ unplacedCount }} à placer</span>
      </div>
    </template>
  </BaseCard>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/solid'
import BaseCard from './ui/BaseCard.vue'
import BaseInput from './ui/BaseInput.vue'
import WineTypeBadge from './WineTypeBadge.vue'
import { useWineColors } from '../composables/useWineColors.js'

const props = defineProps({
  bottles: {
    type: Array,
    default: () => []
  },
  cave: {
    type: Object,
    default: null
  },
  hoveredBottleId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['hover-bottle'])

const router = useRouter()
const searchQuery = ref('')
const { getTypeBadgeClasses } = useWineColors()

// Computed
const filteredBottles = computed(() => {
  if (!searchQuery.value) return props.bottles
  
  const query = searchQuery.value.toLowerCase()
  return props.bottles.filter(b => 
    b.name.toLowerCase().includes(query) ||
    (b.domaine && b.domaine.toLowerCase().includes(query)) ||
    b.year?.toString().includes(query)
  )
})

const sortedBottles = computed(() => {
  return [...filteredBottles.value].sort((a, b) => {
    const aPlaced = getPlacementCount(a) > 0
    const bPlaced = getPlacementCount(b) > 0
    
    if (aPlaced !== bPlaced) {
      return aPlaced ? 1 : -1
    }
    
    return a.name.localeCompare(b.name)
  })
})

const placedCount = computed(() => {
  return props.bottles.filter(b => getPlacementCount(b) > 0).length
})

const unplacedCount = computed(() => {
  return props.bottles.filter(b => getPlacementCount(b) === 0).length
})

// Methods
const getPlacementCount = (bottle) => {
  if (!props.cave) return 0
  
  let count = 0
  props.cave.columns?.forEach(col => {
    col.rows?.forEach(row => {
      row.positions?.forEach(pos => {
        if (pos.bottle_at_position?.id === bottle.id) {
          count++
        }
      })
    })
  })
  return count
}

const onHover = (bottle) => {
  emit('hover-bottle', bottle.id)
}

const onLeave = () => {
  emit('hover-bottle', null)
}

const goToBottle = (id) => {
  router.push(`/wine/${id}`)
}
</script>