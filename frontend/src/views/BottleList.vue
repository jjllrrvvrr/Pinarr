<template>
  <main class="max-w-7xl mx-auto px-4 pb-20">
    <div class="flex items-center gap-3 mb-4">
      <div class="relative flex-1">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8b949e]" />
        <input v-model="searchQuery" type="text" placeholder="Rechercher un vin..." 
               class="w-full bg-[#0d1117] border border-[#30363d] rounded-md py-2 pl-9 pr-4 text-white placeholder-[#8b949e] focus:outline-none focus:border-[#58a6ff] focus:ring-1 focus:ring-[#58a6ff] text-sm">
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
      <div v-for="bottle in visibleBottles" :key="bottle.id" 
           :class="[
             'bg-[#161b22] border border-[#30363d] rounded-md transition-all cursor-pointer group',
             bottle.quantity === 0 ? 'opacity-50 hover:opacity-70' : 'hover:border-[#58a6ff]',
             viewMode === 'grid' ? 'max-h-[250px] flex' : 'flex items-center'
           ]"
           @click="goToBottle(bottle.id)">
        
        <template v-if="viewMode === 'grid'">
          <div class="w-24 flex-shrink-0 bg-[#0d1117] flex items-center justify-center overflow-hidden rounded-l-md border-r border-[#30363d] relative">
            <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full h-full object-contain" />
            <WineBottleIcon v-else :type="bottle.type" :size="48" />
            <span v-if="bottle.quantity === 0" class="absolute top-1 left-1 bg-[#f85149] text-white text-[8px] px-1 rounded">Épuisé</span>
          </div>
          
          <div class="flex-1 flex flex-col min-w-0">
            <div class="flex-1 p-2.5 border-b border-[#30363d] flex flex-col justify-center gap-0.5">
              <div class="flex items-center justify-between">
                <span class="inline-flex items-center gap-1.5">
                  <span :class="['w-2 h-2 rounded-full', getTypeDot(bottle.type)]"></span>
                  <span class="text-xs text-white font-medium">{{ bottle.type }}</span>
                </span>
                <div class="flex items-center gap-2 text-xs text-[#8b949e]">
                  <span v-if="bottle.cepage" @click.stop="setFilter('cepage', bottle.cepage)" 
                        class="truncate max-w-[70px] hover:text-[#f85149] cursor-pointer transition">{{ bottle.cepage }}</span>
                  <span class="font-mono text-white hover:text-[#58a6ff] cursor-pointer transition" @click.stop="setFilter('year', bottle.year)">{{ bottle.year }}</span>
                </div>
              </div>
              <h3 class="text-white font-semibold truncate group-hover:text-[#58a6ff] transition text-sm leading-tight">{{ bottle.name }}</h3>
              <p v-if="bottle.domaine" @click.stop="setFilter('domaine', bottle.domaine)" 
                 class="text-[#8b949e] text-xs truncate hover:text-[#e3b341] cursor-pointer transition">{{ bottle.domaine }}</p>
              <p v-else class="text-[#8b949e] text-xs truncate">—</p>
              <div v-if="bottle.location" class="flex items-center gap-1 text-xs text-[#8b949e] mt-1">
                <MapPinIcon class="w-3 h-3 flex-shrink-0" />
                <span class="truncate">{{ bottle.location }}</span>
              </div>
            </div>
            
            <div class="px-2.5 py-2 flex items-center gap-2">
              <div class="flex flex-wrap gap-1 flex-1 min-w-0">
                <span v-for="tag in bottle.tags?.split(',').slice(0,2)" :key="tag"
                      @click.stop="setFilter('tag', tag.trim())"
                      class="text-[10px] px-1.5 py-0.5 rounded text-[#8b949e] bg-[#21262d] hover:text-[#db61a2] transition cursor-pointer truncate">
                  {{ tag.trim() }}
                </span>
              </div>

              <div class="flex items-center gap-1" @click.stop>
                <button @click="updateQty(bottle.id, bottle.quantity - 1)" 
                        class="w-5 h-5 flex items-center justify-center text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded text-xs transition">−</button>
                <span class="w-4 text-center text-white font-bold text-xs">{{ bottle.quantity }}</span>
                <button @click="updateQty(bottle.id, bottle.quantity + 1)" 
                        class="w-5 h-5 flex items-center justify-center text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded text-xs transition">+</button>
              </div>

              <div class="flex flex-col items-end">
                <span v-if="bottle.price" class="text-[#3fb950] font-bold text-xs">{{ bottle.price }}€</span>
                <span v-if="bottle.rating" class="flex items-center gap-0.5 text-[#e3b341] text-[10px]">
                  <StarSolid class="w-2.5 h-2.5" /> {{ bottle.rating }}/5
                </span>
              </div>
            </div>

            <div class="px-2.5 py-1.5 border-t border-[#30363d] flex items-center justify-between bg-[#0d1117] opacity-0 group-hover:opacity-100 transition" @click.stop>
              <router-link :to="`/edit/${bottle.id}`" class="text-[10px] text-[#58a6ff] hover:underline">Modifier</router-link>
              <button v-if="bottle.quantity > 0" @click="archiveBottle(bottle.id)" class="text-[10px] text-[#f85149] hover:underline">Archiver</button>
              <button v-else @click="updateQty(bottle.id, 1)" class="text-[10px] text-[#3fb950] hover:underline">Restaurer</button>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="w-12 h-12 flex-shrink-0 bg-[#0d1117] flex items-center justify-center overflow-hidden rounded-l relative">
            <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full h-full object-cover" />
            <WineBottleIcon v-else :type="bottle.type" :size="24" />
            <span v-if="bottle.quantity === 0" class="absolute top-0 left-0 bg-[#f85149] text-white text-[6px] px-0.5 rounded-br">0</span>
          </div>
          <div class="flex-1 min-w-0 px-3">
            <div class="flex items-center gap-2">
              <span class="text-white font-medium truncate group-hover:text-[#58a6ff] transition">{{ bottle.name }}</span>
              <span @click.stop="setFilter('year', bottle.year)" class="text-[#8b949e] text-xs font-mono hover:text-[#58a6ff] cursor-pointer">{{ bottle.year }}</span>
            </div>
            <div class="flex items-center gap-3 text-xs text-[#8b949e]">
              <span v-if="bottle.domaine" @click.stop="setFilter('domaine', bottle.domaine)" class="hover:text-[#e3b341] cursor-pointer">{{ bottle.domaine }}</span>
              <span v-else>—</span>
              <span v-if="bottle.location">→ {{ bottle.location }}</span>
            </div>
          </div>
          <div class="flex items-center gap-3 pr-3" @click.stop>
            <div class="flex items-center gap-1">
              <button @click="updateQty(bottle.id, bottle.quantity - 1)" class="w-5 h-5 flex items-center justify-center text-[#8b949e] hover:text-white transition text-xs">−</button>
              <span class="w-5 text-center text-white font-mono text-sm">{{ bottle.quantity }}</span>
              <button @click="updateQty(bottle.id, bottle.quantity + 1)" class="w-5 h-5 flex items-center justify-center text-[#8b949e] hover:text-white transition text-xs">+</button>
            </div>
            <span v-if="bottle.price" class="text-[#3fb950] text-sm font-mono">{{ bottle.price }}€</span>
          </div>
        </template>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  MagnifyingGlassIcon, MapPinIcon, StarIcon as StarSolid,
  Squares2X2Icon, ListBulletIcon
} from '@heroicons/vue/24/solid'
import WineBottleIcon from '@/components/WineBottleIcon.vue'

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

const archiveBottle = (id) => {
  emit('update-quantity', id, 0)
}

const getTypeDot = (type) => {
  if (type === 'Rouge') return 'bg-[#f85149]'
  if (type === 'Blanc') return 'bg-[#e3b341]'
  if (type === 'Rosé') return 'bg-[#db61a2]'
  if (type === 'Champagne') return 'bg-[#a371f7]'
  return 'bg-[#8b949e]'
}

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  return `http://127.0.0.1:8000${path}`
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
    return filteredBottles.value
  }
  return filteredBottles.value.filter(b => b.quantity > 0)
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