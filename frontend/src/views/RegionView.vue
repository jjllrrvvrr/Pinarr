<template>
  <main class="max-w-7xl mx-auto px-4 py-8 pb-20">
    <div class="flex items-center gap-2 mb-6 text-[#8b949e]">
      <router-link to="/" class="hover:text-[#58a6ff]">Accueil</router-link>
      <span>/</span>
      <router-link to="/map" class="hover:text-[#58a6ff]">Carte</router-link>
      <span>/</span>
      <span class="text-white">{{ regionName }}</span>
    </div>

    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-white">
        {{ regionName }}
        <span class="text-[#8b949e] text-lg font-normal">({{ bottles.length }} bouteilles)</span>
      </h1>
    </div>

    <div v-if="bottles.length === 0" class="text-center py-20 text-[#8b949e]">
      <p>Aucune bouteille dans cette région</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="bottle in bottles" :key="bottle.id" 
           class="bg-[#161b22] rounded-md border border-[#30363d] hover:border-[#8b949e] transition-all flex flex-col overflow-hidden cursor-pointer"
           @click="goToBottle(bottle.id)">
        
        <div class="p-4 flex justify-between items-start">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-2">
              <span :class="`w-3 h-3 rounded-full ${getTypeColor(bottle.type)}`"></span>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full border" :class="getTypeColor(bottle.type)">
                {{ bottle.type }}
              </span>
            </div>
            <h3 class="text-base font-semibold text-white truncate">{{ bottle.name }}</h3>
            <p class="text-[#8b949e] text-sm truncate">{{ bottle.domaine }}</p>
          </div>
          <div class="text-right ml-4 flex-shrink-0">
            <div class="text-lg font-bold text-white">{{ bottle.year }}</div>
            <div class="flex items-center justify-end text-[#e3b341] gap-1 mt-1">
              <span class="text-sm font-medium">{{ bottle.rating }}/5</span>
            </div>
          </div>
        </div>

        <div class="px-4 pb-3 space-y-2 flex-grow text-sm">
          <div class="flex items-center text-[#8b949e] gap-2">
            <span class="text-white">{{ bottle.quantity }} en stock</span>
            <span v-if="bottle.price" class="text-[#3fb950]">{{ bottle.price }} €</span>
          </div>
          <div v-if="bottle.cepage" class="text-[#8b949e]">
            {{ bottle.cepage }}
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiRequest } from '../services/api.js'

const route = useRoute()
const router = useRouter()

const API_URL = '/bottles'
const regionName = ref('')
const bottles = ref([])

const getTypeColor = (type) => {
  if (type === 'Rouge') return 'bg-[#f85149]/30 text-[#f85149] border-[#f85149]/50'
  if (type === 'Blanc') return 'bg-[#e3b341]/30 text-[#e3b341] border-[#e3b341]/50'
  if (type === 'Rosé') return 'bg-[#db61a2]/30 text-[#db61a2] border-[#db61a2]/50'
  if (type === 'Champagne') return 'bg-[#a371f7]/30 text-[#a371f7] border-[#a371f7]/50'
  return 'bg-[#30363d] text-[#8b949e] border-[#30363d]'
}

const goToBottle = (id) => {
  router.push(`/wine/${id}`)
}

const fetchBottles = async () => {
  regionName.value = decodeURIComponent(route.params.region)
  try {
    const allBottles = await apiRequest(API_URL)
    bottles.value = allBottles.filter(b => 
      b.region && b.region.toLowerCase() === regionName.value.toLowerCase()
    )
  } catch (e) {
    console.error(e)
  }
}

watch(() => route.params.region, () => {
  fetchBottles()
})

onMounted(() => {
  fetchBottles()
})
</script>