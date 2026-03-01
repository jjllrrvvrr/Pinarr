<template>
  <div class="bg-[#161b22] rounded-md border border-[#30363d] flex flex-col h-[600px] lg:h-auto lg:max-h-[calc(100vh-200px)]">
    <!-- Drop zone for removing -->
    <div 
      v-if="isDragging"
      class="p-3 m-3 border-2 border-dashed border-[#f85149] rounded text-center text-[#f85149] bg-[#f85149]/10"
      @dragover.prevent
      @drop="onDropToUnplace"
    >
      <TrashIcon class="w-5 h-5 mx-auto mb-1" />
      <span class="text-xs">Déposer ici pour retirer de la cave</span>
    </div>
    
    <!-- Header -->
    <div class="p-4 border-b border-[#30363d]">
      <h3 class="text-sm font-medium text-white mb-3">Bouteilles</h3>
      <div class="relative">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="Rechercher..."
          class="w-full bg-[#0d1117] border border-[#30363d] rounded px-3 py-2 text-sm text-white placeholder-[#8b949e] focus:border-[#58a6ff] focus:outline-none"
        />
        <MagnifyingGlassIcon class="w-4 h-4 text-[#8b949e] absolute right-3 top-2.5" />
      </div>
    </div>
    
    <!-- List -->
    <div class="flex-1 overflow-y-auto p-2 space-y-1">
      <div 
        v-for="bottle in sortedBottles" 
        :key="bottle.id"
        class="group flex items-center gap-3 p-2 rounded hover:bg-[#21262d] cursor-pointer transition border border-transparent"
        :class="{'bg-[#21262d]/50': isPlaced(bottle), 'border-[#58a6ff]/30': isHovered(bottle)}"
        @mouseenter="onHover(bottle)"
        @mouseleave="onLeave"
        draggable="true"
        @dragstart="onDragStart($event, bottle)"
        @dragend="onDragEnd"
      >
        <!-- Status indicator -->
        <div class="flex-shrink-0 w-2 h-2 rounded-full" 
             :class="isPlaced(bottle) ? 'bg-[#3fb950]' : 'bg-[#8b949e]'">
        </div>
        
        <!-- Bottle info -->
        <div class="flex-1 min-w-0">
          <div class="text-sm text-white font-medium truncate">{{ bottle.name }}</div>
          <div class="text-xs text-[#8b949e] flex items-center gap-2">
            <span>{{ bottle.year }} • {{ bottle.type }}</span>
            <span v-if="getPlacementCount(bottle) > 0" class="text-[#3fb950] bg-[#3fb950]/10 px-1.5 py-0.5 rounded">
              x{{ getPlacementCount(bottle) }}
            </span>
          </div>
        </div>
        
        <!-- Drag handle -->
        <svg class="w-4 h-4 text-[#484f58] opacity-0 group-hover:opacity-100 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M8 9h8M8 15h8M8 12h8" />
        </svg>
      </div>
      
      <!-- Empty state -->
      <div v-if="sortedBottles.length === 0" class="text-center py-8 text-[#8b949e]">
        <p class="text-sm">Aucune bouteille trouvée</p>
      </div>
    </div>
    
    <!-- Footer stats -->
    <div class="p-3 border-t border-[#30363d] text-xs text-[#8b949e] flex justify-between">
      <span>{{ placedCount }} placées</span>
      <span>{{ unplacedCount }} à placer</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { MagnifyingGlassIcon, TrashIcon } from '@heroicons/vue/24/solid'

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
  },
  isDragging: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'hover-bottle',
  'drag-start',
  'drag-end',
  'remove-bottle'
])

const searchQuery = ref('')

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
  // Sort: unplaced first, then alphabetically
  return [...filteredBottles.value].sort((a, b) => {
    const aPlaced = isPlaced(a)
    const bPlaced = isPlaced(b)
    
    if (aPlaced !== bPlaced) {
      return aPlaced ? 1 : -1 // Unplaced first
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
const isPlaced = (bottle) => getPlacementCount(bottle) > 0

const isHovered = (bottle) => props.hoveredBottleId === bottle.id

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

const onDragStart = (event, bottle) => {
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', JSON.stringify({
    bottleId: bottle.id,
    fromSidebar: true
  }))
  emit('drag-start', bottle, true)
}

const onDragEnd = () => {
  emit('drag-end')
}

const onDropToUnplace = (event) => {
  event.preventDefault()
  const data = JSON.parse(event.dataTransfer.getData('text/plain'))
  if (data && !data.fromSidebar && data.positionId) {
    emit('remove-bottle', data.positionId)
  }
}
</script>