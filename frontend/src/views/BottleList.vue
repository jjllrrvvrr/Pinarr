<template>
  <main class="max-w-7xl mx-auto px-4 pt-4 pb-20">
    <div class="flex items-center gap-3 mb-4">
      <div class="relative flex-1">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8b949e]" />
        <input v-model="searchQuery" type="text" placeholder="Rechercher un vin..." 
               class="w-full bg-[#0d1117] border border-[#30363d] rounded-md py-1.5 pl-9 pr-4 text-white placeholder-[#8b949e] focus:outline-none focus:border-[#58a6ff] focus:ring-1 focus:ring-[#58a6ff] text-sm">
      </div>
      <div class="flex items-center gap-1 border border-[#30363d] rounded-md p-0.5">
        <button @click="viewMode = 'grid'" :class="['p-1.5 rounded transition', viewMode === 'grid' ? 'bg-[#21262d] text-white' : 'text-[#8b949e] hover:text-white']">
          <Squares2X2Icon class="w-4 h-4" />
        </button>
        <button @click="viewMode = 'list'" :class="['p-1.5 rounded transition', viewMode === 'list' ? 'bg-[#21262d] text-white' : 'text-[#8b949e] hover:text-white']">
          <ListBulletIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- MODE RECHERCHE ACTIVE -->
    <template v-if="searchQuery.trim()">
      <!-- Section: En cave -->
      <div v-if="inStockSearchResults.length > 0" class="mb-8">
        <h2 class="text-sm font-semibold text-[#3fb950] mb-4 flex items-center gap-2 px-1">
          <span class="w-2 h-2 rounded-full bg-[#3fb950]"></span>
          En cave ({{ inStockSearchResults.length }} résultat{{ inStockSearchResults.length > 1 ? 's' : '' }})
        </h2>
        <div :class="viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-2'">
          <BottleCard 
            v-for="bottle in inStockSearchResults" 
            :key="bottle.id"
            :bottle="bottle"
            :view-mode="viewMode"
            :archived="false"
            @navigate="goToBottle"
            @filter="setFilter"
            @update-quantity="updateQty"
            @delete="deleteBottle"
          />
        </div>
      </div>

      <!-- Section: Dans l'historique -->
      <div v-if="archivedSearchResults.length > 0" class="mb-8">
        <h2 class="text-sm font-semibold text-[#8b949e] mb-4 flex items-center gap-2 px-1">
          <ArchiveBoxIcon class="w-4 h-4" />
          Dans l'historique ({{ archivedSearchResults.length }} résultat{{ archivedSearchResults.length > 1 ? 's' : '' }})
        </h2>
        <div :class="viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-2'" class="opacity-60">
          <BottleCard 
            v-for="bottle in archivedSearchResults" 
            :key="bottle.id"
            :bottle="bottle"
            :view-mode="viewMode"
            :archived="true"
            @navigate="goToBottle"
            @filter="setFilter"
            @update-quantity="updateQty"
            @delete="deleteBottle"
          />
        </div>
      </div>

      <!-- Aucun résultat -->
      <div v-if="inStockSearchResults.length === 0 && archivedSearchResults.length === 0" class="text-center py-20">
        <div class="text-[#8b949e] text-sm mb-2">Aucune bouteille trouvée pour "{{ searchQuery }}"</div>
        <div class="text-[#8b949e] text-xs">Essayez avec un autre terme de recherche</div>
      </div>
    </template>

    <!-- MODE NORMAL (sans recherche) -->
    <template v-else>
      <div class="flex items-center gap-2 mb-4">
        <button @click="showHistory = false" 
                :class="['px-3 py-1 rounded-md text-xs font-medium transition', !showHistory ? 'bg-[#238636] text-white' : 'bg-[#21262d] text-[#8b949e] hover:text-white']">
          En cave ({{ inStockCount }})
        </button>
        <button @click="showHistory = true" 
                :class="['px-3 py-1 rounded-md text-xs font-medium transition', showHistory ? 'bg-[#f85149] text-white' : 'bg-[#21262d] text-[#8b949e] hover:text-white']">
          Historique ({{ archivedCount }})
        </button>
      </div>

      <div v-if="hasActiveFilters" class="mb-4 flex flex-wrap items-center gap-2">
        <span class="text-[#8b949e] text-xs">Filtres:</span>
        <button v-if="filters.cepage" @click="clearFilter('cepage')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[#f85149]/20 text-[#f85149] border border-[#f85149]/30 hover:bg-[#f85149]/30 transition">
          Cépage: {{ filters.cepage }} ×
        </button>
        <button v-if="filters.region" @click="clearFilter('region')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[#a371f7]/20 text-[#a371f7] border border-[#a371f7]/30 hover:bg-[#a371f7]/30 transition">
          Région: {{ filters.region }} ×
        </button>
        <button v-if="filters.year" @click="clearFilter('year')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[#58a6ff]/20 text-[#58a6ff] border border-[#58a6ff]/30 hover:bg-[#58a6ff]/30 transition">
          Année: {{ filters.year }} ×
        </button>
        <button v-if="filters.domaine" @click="clearFilter('domaine')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[#e3b341]/20 text-[#e3b341] border border-[#e3b341]/30 hover:bg-[#e3b341]/30 transition">
          Domaine: {{ filters.domaine }} ×
        </button>
        <button v-if="filters.country" @click="clearFilter('country')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[#3fb950]/20 text-[#3fb950] border border-[#3fb950]/30 hover:bg-[#3fb950]/30 transition">
          Pays: {{ filters.country }} ×
        </button>
        <button v-if="filters.tag" @click="clearFilter('tag')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-[#db61a2]/20 text-[#db61a2] border border-[#db61a2]/30 hover:bg-[#db61a2]/30 transition">
          Tag: {{ filters.tag }} ×
        </button>
        <button @click="clearAllFilters" class="text-xs text-[#8b949e] hover:text-white underline ml-2">
          Effacer tout
        </button>
      </div>

      <div v-if="visibleBottles.length === 0" class="text-center py-20 border border-[#30363d] rounded-md bg-[#0d1117]">
        <div class="text-[#8b949e] text-sm">{{ showHistory ? 'Aucune bouteille dans l\'historique' : 'Aucune bouteille en cave' }}</div>
      </div>

      <div v-else :class="viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-2'">
        <BottleCard 
          v-for="bottle in visibleBottles" 
          :key="bottle.id"
          :bottle="bottle"
          :view-mode="viewMode"
          :archived="bottle.quantity === 0"
          @navigate="goToBottle"
          @filter="setFilter"
          @update-quantity="updateQty"
          @delete="deleteBottle"
        />
      </div>
    </template>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  MagnifyingGlassIcon, ArchiveBoxIcon,
  Squares2X2Icon, ListBulletIcon
} from '@heroicons/vue/24/solid'
import BottleCard from '@/components/BottleCard.vue'

const route = useRoute()
const router = useRouter()

const props = defineProps({
  bottles: Array,
  storageLocations: Array,
  shelves: Array
})
const emit = defineEmits(['edit-bottle', 'delete-bottle', 'show-qr', 'update-quantity'])

const searchQuery = ref('')
const viewMode = ref('grid')
const showHistory = ref(false)

const filters = ref({
  cepage: null,
  region: null,
  year: null,
  domaine: null,
  country: null,
  tag: null
})

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(v => v !== null)
})

const setFilter = (key, value) => {
  if (filters.value[key] === value) {
    filters.value[key] = null
  } else {
    filters.value[key] = value
  }
  updateUrl()
}

const clearFilter = (key) => {
  filters.value[key] = null
  updateUrl()
}

const clearAllFilters = () => {
  Object.keys(filters.value).forEach(key => {
    filters.value[key] = null
  })
  updateUrl()
}

const updateUrl = () => {
  const query = {}
  Object.entries(filters.value).forEach(([key, value]) => {
    if (value) query[key] = value
  })
  router.replace({ path: '/', query })
}

const goToBottle = (id) => {
  router.push(`/wine/${id}`)
}

const updateQty = (id, qty) => {
  if (qty < 0) return
  emit('update-quantity', id, qty)
}

const deleteBottle = (id) => {
  emit('delete-bottle', id)
}

const normalize = (text) => {
  if (!text) return ''
  return text.toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const filteredBottles = computed(() => {
  let result = props.bottles
  
  if (filters.value.cepage) {
    result = result.filter(b => normalize(b.cepage).includes(normalize(filters.value.cepage)))
  }
  if (filters.value.region) {
    result = result.filter(b => normalize(b.region).includes(normalize(filters.value.region)))
  }
  if (filters.value.year) {
    result = result.filter(b => String(b.year) === String(filters.value.year))
  }
  if (filters.value.domaine) {
    result = result.filter(b => normalize(b.domaine).includes(normalize(filters.value.domaine)))
  }
  if (filters.value.country) {
    result = result.filter(b => normalize(b.country).includes(normalize(filters.value.country)))
  }
  if (filters.value.tag) {
    result = result.filter(b => 
      b.tags && b.tags.split(',').map(t => t.trim().toLowerCase()).includes(filters.value.tag.toLowerCase())
    )
  }
  
  const s = normalize(searchQuery.value)
  if (s) {
    result = result.filter(b => 
      normalize(b.name).includes(s) || 
      normalize(b.domaine).includes(s) ||
      normalize(b.region).includes(s) ||
      normalize(b.location).includes(s) ||
      normalize(b.country).includes(s) ||
      normalize(b.cepage).includes(s)
    )
  }
  
  return result
})

const visibleBottles = computed(() => {
  if (showHistory.value) {
    return filteredBottles.value.filter(b => b.quantity === 0)
  }
  return filteredBottles.value.filter(b => b.quantity > 0)
})

// Nouvelles computed properties pour la recherche séparée
const inStockSearchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  return filteredBottles.value.filter(b => b.quantity > 0)
})

const archivedSearchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  return filteredBottles.value.filter(b => b.quantity === 0)
})

const inStockCount = computed(() => filteredBottles.value.filter(b => b.quantity > 0).length)
const archivedCount = computed(() => filteredBottles.value.filter(b => b.quantity === 0).length)

const loadFiltersFromUrl = () => {
  const query = route.query
  filters.value = {
    cepage: query.cepage || null,
    region: query.region || null,
    year: query.year || null,
    domaine: query.domaine || null,
    country: query.country || null,
    tag: query.tag || null
  }
}

onMounted(() => {
  loadFiltersFromUrl()
})

watch(() => route.query, () => {
  loadFiltersFromUrl()
}, { deep: true })
</script>
