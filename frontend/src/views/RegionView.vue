<template>
  <main class="max-w-7xl mx-auto px-4 py-8 pb-20">
    <div class="flex items-center gap-2 mb-6 text-gh-text-secondary">
      <router-link to="/" class="hover:text-gh-accent">Accueil</router-link>
      <span>/</span>
      <router-link to="/map" class="hover:text-gh-accent">Carte</router-link>
      <span>/</span>
      <span class="text-gh-text">{{ regionName }}</span>
    </div>

    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-gh-text">
        {{ regionName }}
        <span class="text-gh-text-secondary text-lg font-normal">({{ bottles.length }} bouteilles)</span>
      </h1>
    </div>

    <div v-if="bottles.length === 0" class="text-center py-20 text-gh-text-secondary">
      <p>Aucune bouteille dans cette région</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="bottle in bottles" :key="bottle.id" 
           class="bg-gh-surface rounded-md border border-gh-border hover:border-gh-border-hover transition-all flex flex-col overflow-hidden cursor-pointer"
           @click="goToBottle(bottle.id)">
        
        <div class="p-4 flex justify-between items-start">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-2">
              <span :class="`w-3 h-3 rounded-full ${getTypeColor(bottle.type)}`"></span>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full border" :class="getTypeColor(bottle.type)">
                {{ bottle.type }}
              </span>
            </div>
            <h3 class="text-base font-semibold text-gh-text truncate">{{ bottle.name }}</h3>
            <p class="text-gh-text-secondary text-sm truncate">{{ bottle.domaine }}</p>
          </div>
          <div class="text-right ml-4 flex-shrink-0">
            <div class="text-lg font-bold text-gh-text">{{ bottle.year }}</div>
            <div class="flex items-center justify-end text-gh-accent-gold gap-1 mt-1">
              <span class="text-sm font-medium">{{ bottle.rating }}/5</span>
            </div>
          </div>
        </div>

        <div class="px-4 pb-3 space-y-2 flex-grow text-sm">
          <div class="flex items-center text-gh-text-secondary gap-2">
            <span class="text-gh-text">{{ bottle.quantity }} en stock</span>
            <span v-if="bottle.price" class="text-gh-accent-green-text">{{ bottle.price }} €</span>
          </div>
          <div v-if="bottle.cepage" class="text-gh-text-secondary">
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

import { useWineTypeStyles } from '@/composables/useWineTypeStyles.js'

const { getTypeBadgeClass } = useWineTypeStyles()

const getTypeColor = (type) => {
  return getTypeBadgeClass(type)
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