<template>
  <main class="max-w-7xl mx-auto px-4 pt-4 pb-20">
    <div class="flex items-center gap-3 mb-4">
      <div class="relative flex-1">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gh-text-secondary" />
        <input v-model="searchQuery" type="text" placeholder="Rechercher un vin..." 
               class="w-full bg-gh-bg border border-gh-border rounded-md py-1.5 pl-9 pr-4 text-gh-text placeholder-gh-text-secondary focus:outline-none focus:border-gh-accent focus:ring-1 focus:ring-gh-accent text-sm">
      </div>
      <div class="flex items-center gap-1 border border-gh-border rounded-md p-0.5">
        <button @click="viewMode = 'grid'" :class="['p-1.5 rounded transition', viewMode === 'grid' ? 'bg-gh-elevated text-gh-text' : 'text-gh-text-secondary hover:text-gh-text']">
          <Squares2X2Icon class="w-4 h-4" />
        </button>
        <button @click="viewMode = 'list'" :class="['p-1.5 rounded transition', viewMode === 'list' ? 'bg-gh-elevated text-gh-text' : 'text-gh-text-secondary hover:text-gh-text']">
          <ListBulletIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- MODE RECHERCHE ACTIVE -->
    <template v-if="searchQuery.trim()">
      <!-- Section: En cave -->
      <div v-if="inStockSearchResults.length > 0" class="mb-8">
        <h2 class="text-sm font-semibold text-gh-accent-green-text mb-4 flex items-center gap-2 px-1">
          <span class="w-2 h-2 rounded-full bg-gh-accent-green"></span>
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
        <h2 class="text-sm font-semibold text-gh-text-secondary mb-4 flex items-center gap-2 px-1">
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
        <div class="text-gh-text-secondary text-sm mb-2">Aucune bouteille trouvée pour "{{ searchQuery }}"</div>
        <div class="text-gh-text-secondary text-xs">Essayez avec un autre terme de recherche</div>
      </div>
    </template>

    <!-- MODE NORMAL (sans recherche) -->
    <template v-else>
      <div class="flex flex-col sm:flex-row sm:flex-wrap sm:items-center sm:justify-between gap-3 mb-4">
        <div class="flex items-center gap-2">
          <button @click="showHistory = false" 
                  :class="['px-3 py-1 rounded-md text-xs font-medium transition', !showHistory ? 'bg-gh-accent-green text-white' : 'bg-gh-elevated text-gh-text-secondary hover:text-gh-text']">
            En cave ({{ inStockCount }})
          </button>
          <button @click="showHistory = true" 
                  :class="['px-3 py-1 rounded-md text-xs font-medium transition', showHistory ? 'bg-gh-accent-red text-white' : 'bg-gh-elevated text-gh-text-secondary hover:text-gh-text']">
            Historique ({{ archivedCount }})
          </button>
        </div>
        
        <!-- Boutons de filtres Couleur et Évolution -->
        <div class="flex items-center gap-2 overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 snap-x scrollbar-hide">
          <div class="flex items-center gap-1 flex-shrink-0">
            <button
              v-for="color in colorOptions"
              :key="color.value"
              @click="setFilter('color', color.value)"
              :class="[
                'px-2 py-1 rounded-md text-xs font-medium transition border',
                filters.color === color.value
                  ? `${color.color} text-white border-transparent`
                  : 'bg-gh-elevated text-gh-text-secondary border-gh-border hover:text-gh-text'
              ]"
            >
              {{ color.label }}
            </button>
          </div>
          
          <span class="text-gh-border mx-2">|</span>
          
          <!-- Filtre Évolution -->
          <div class="flex items-center gap-1">
            <button
              v-for="phase in phaseOptions"
              :key="phase.value"
              @click="setFilter('phase', phase.value)"
              :class="[
                'px-2 py-1 rounded-md text-xs font-medium transition border',
                filters.phase === phase.value
                  ? `${phase.color} text-white border-transparent`
                  : 'bg-gh-elevated text-gh-text-secondary border-gh-border hover:text-gh-text'
              ]"
            >
              {{ phase.label }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="hasTextFilters" class="mb-4 flex flex-wrap items-center gap-2">
        <span class="text-gh-text-secondary text-xs">Filtres:</span>
        <button v-if="filters.cepage" @click="clearFilter('cepage')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gh-accent-red/20 text-gh-accent-red border border-gh-accent-red/30 hover:bg-gh-accent-red/30 transition">
          Cépage: {{ filters.cepage }} ×
        </button>
        <button v-if="filters.region" @click="clearFilter('region')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gh-accent-purple/20 text-gh-accent-purple border border-gh-accent-purple/30 hover:bg-gh-accent-purple/30 transition">
          Région: {{ filters.region }} ×
        </button>
        <button v-if="filters.year" @click="clearFilter('year')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gh-accent/20 text-gh-accent border border-gh-accent/30 hover:bg-gh-accent/30 transition">
          Millésime: {{ filters.year }} ×
        </button>
        <button v-if="filters.domaine" @click="clearFilter('domaine')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gh-accent-gold/20 text-gh-accent-gold border border-gh-accent-gold/30 hover:bg-gh-accent-gold/30 transition">
          Domaine: {{ filters.domaine }} ×
        </button>
        <button v-if="filters.country" @click="clearFilter('country')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gh-accent-green/20 text-gh-accent-green-text border border-gh-accent-green/30 hover:bg-gh-accent-green/30 transition">
          Pays: {{ filters.country }} ×
        </button>
        <button v-if="filters.tag" @click="clearFilter('tag')" 
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs bg-gh-accent-pink/20 text-gh-accent-pink border border-gh-accent-pink/30 hover:bg-gh-accent-pink/30 transition">
          Tag: {{ filters.tag }} ×
        </button>
        <button @click="clearAllFilters" class="text-xs text-gh-text-secondary hover:text-gh-text underline ml-2">
          Effacer tout
        </button>
      </div>

      <div v-if="visibleBottles.length === 0" class="text-center py-20 border border-gh-border rounded-md bg-gh-bg">
        <div class="text-gh-text-secondary text-sm">{{ showHistory ? 'Aucune bouteille dans l\'historique' : 'Aucune bouteille en cave' }}</div>
      </div>

      <div v-else :class="viewMode === 'grid' ? 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-2'">
        <BottleCard 
          v-for="bottle in visibleBottles" 
          :key="bottle.id"
          :bottle="bottle"
          :view-mode="viewMode"
          :archived="(bottle.physical_bottles?.length || 0) === 0"
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
const emit = defineEmits(['edit-bottle', 'delete-bottle', 'show-qr', 'update-quantity', 'refresh-data'])

const searchQuery = ref('')
const viewMode = ref('grid')
const showHistory = ref(false)

const filters = ref({
  cepage: null,
  region: null,
  year: null,
  domaine: null,
  country: null,
  tag: null,
  color: null,
  phase: null
})

const hasActiveFilters = computed(() => {
  return Object.values(filters.value).some(v => v !== null)
})

const hasTextFilters = computed(() => {
  return filters.value.cepage || filters.value.region || filters.value.year || 
         filters.value.domaine || filters.value.country || filters.value.tag
})

// Constantes pour les filtres couleur et évolution
const colorOptions = [
  { value: 'RED', label: 'Rouge', color: 'bg-[var(--wine-red)]', text: 'text-[var(--wine-red)]' },
  { value: 'WHITE', label: 'Blanc', color: 'bg-[var(--wine-white)]', text: 'text-[var(--wine-white)]' },
  { value: 'ROSE', label: 'Rosé', color: 'bg-[var(--wine-rose)]', text: 'text-[var(--wine-rose)]' },
  { value: 'EFFERVESCENT', label: 'Efferv.', color: 'bg-[var(--wine-champagne)]', text: 'text-[var(--wine-champagne)]' },
  { value: 'OTHER', label: 'Autre', color: 'bg-[var(--wine-default)]', text: 'text-[var(--wine-default)]' }
]

const phaseOptions = [
  { value: 'JEUNESSE', label: 'Jeunesse', color: 'bg-[var(--phase-jeunesse)]', text: 'text-[var(--phase-jeunesse)]' },
  { value: 'MATURITE', label: 'Maturité', color: 'bg-[var(--phase-maturite)]', text: 'text-[var(--phase-maturite)]' },
  { value: 'APOGEE', label: 'Apogée', color: 'bg-[var(--phase-apogee)]', text: 'text-[var(--phase-apogee)]' },
  { value: 'DECLIN', label: 'Déclin', color: 'bg-[var(--phase-declin)]', text: 'text-[var(--phase-declin)]' }
]

const getColorLabel = (value) => colorOptions.find(c => c.value === value)?.label || value
const getPhaseLabel = (value) => phaseOptions.find(p => p.value === value)?.label || value

const getBottlePhase = (bottle) => {
  if (!bottle.jeunesse_end && !bottle.maturite_end && !bottle.apogee_end) return null
  if (!bottle.year) return null
  
  const currentYear = new Date().getFullYear()
  const jeunesseEnd = bottle.jeunesse_end || bottle.year + 1
  const maturiteEnd = bottle.maturite_end || bottle.year + 4
  const apogeeEnd = bottle.apogee_end || bottle.year + 9
  
  if (currentYear <= jeunesseEnd) return 'JEUNESSE'
  if (currentYear <= maturiteEnd) return 'MATURITE'
  if (currentYear <= apogeeEnd) return 'APOGEE'
  return 'DECLIN'
}

const getBottleColor = (bottle) => {
  const type = (bottle.type || '').toLowerCase()
  if (type.includes('rouge')) return 'RED'
  if (type.includes('blanc')) return 'WHITE'
  if (type.includes('rosé') || type.includes('rose')) return 'ROSE'
  if (type.includes('champagne') || type.includes('crémant') || type.includes('effervescent')) return 'EFFERVESCENT'
  return 'OTHER'
}

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
  // Rafraîchir les données parent (App.vue fetchBottles)
  emit('refresh-data')
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
  
  // Filtre par couleur
  if (filters.value.color) {
    result = result.filter(b => getBottleColor(b) === filters.value.color)
  }
  
  // Filtre par phase d'évolution
  if (filters.value.phase) {
    result = result.filter(b => getBottlePhase(b) === filters.value.phase)
  }
  
  const s = normalize(searchQuery.value)
  if (s) {
    result = result.filter(b => 
      normalize(b.name).includes(s) || 
      normalize(b.domaine).includes(s) ||
      normalize(b.region).includes(s) ||
      normalize(b.country).includes(s) ||
      normalize(b.cepage).includes(s)
    )
  }
  
  return result
})

const visibleBottles = computed(() => {
  if (showHistory.value) {
    return filteredBottles.value.filter(b => (b.cellar_quantity || 0) === 0 && (b.physical_bottles?.length || 0) > 0)
  }
  return filteredBottles.value.filter(b => (b.cellar_quantity || 0) > 0)
})

// Nouvelles computed properties pour la recherche séparée
const inStockSearchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  return filteredBottles.value.filter(b => (b.cellar_quantity || 0) > 0)
})

const archivedSearchResults = computed(() => {
  if (!searchQuery.value.trim()) return []
  return filteredBottles.value.filter(b => (b.cellar_quantity || 0) === 0 && (b.physical_bottles?.length || 0) > 0)
})

const inStockCount = computed(() => filteredBottles.value.filter(b => (b.cellar_quantity || 0) > 0).length)
const archivedCount = computed(() => filteredBottles.value.filter(b => (b.cellar_quantity || 0) === 0 && (b.physical_bottles?.length || 0) > 0).length)

const loadFiltersFromUrl = () => {
  const query = route.query
  filters.value = {
    cepage: query.cepage || null,
    region: query.region || null,
    year: query.year || null,
    domaine: query.domaine || null,
    country: query.country || null,
    tag: query.tag || null,
    color: query.color || null,
    phase: query.phase || null
  }
}

onMounted(() => {
  loadFiltersFromUrl()
})

watch(() => route.query, () => {
  loadFiltersFromUrl()
}, { deep: true })
</script>
