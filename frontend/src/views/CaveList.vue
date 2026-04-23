<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { PlusIcon, PencilIcon, EyeIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { apiRequest } from '../services/api.js'

const router = useRouter()
const API_URL = '/caves'

const caves = ref([])
const loading = ref(true)

const fetchCaves = async () => {
  loading.value = true
  try {
    caves.value = await apiRequest(API_URL)
  } catch (e) {
    console.error('Erreur:', e)
  } finally {
    loading.value = false
  }
}

const deleteCave = async (id) => {
  if (!confirm('Supprimer cette cave et toutes ses données ?')) return
  try {
    await apiRequest(`${API_URL}/${id}`, { method: 'DELETE' })
    fetchCaves()
  } catch (e) {
    alert('Erreur: ' + e.message)
  }
}

const getTotalPositions = (cave) => {
  let total = 0
  cave.columns?.forEach(col => {
    col.rows?.forEach(row => {
      total += (row.width || 0) * (row.height || 0)
    })
  })
  return total
}

const getOccupiedPositions = (cave) => {
  let occupied = 0
  cave.columns?.forEach(col => {
    col.rows?.forEach(row => {
      occupied += row.positions?.filter(p => p.physical_bottle_id).length || 0
    })
  })
  return occupied
}

onMounted(fetchCaves)
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 py-8 pb-20">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-xl font-bold text-gh-text">Mes Caves</h1>
        <p class="text-sm text-gh-text-secondary">Gérez vos espaces de stockage</p>
      </div>
      <router-link to="/caves/new" class="flex items-center gap-2 bg-gh-accent-green hover:bg-gh-accent-green-hover text-white px-4 py-2 rounded-md font-medium transition text-sm">
        <PlusIcon class="w-5 h-5" />
        <span>Nouvelle cave</span>
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-12 text-gh-text-secondary">Chargement...</div>

    <div v-else-if="caves.length === 0" class="text-center py-12">
      <div class="text-gh-text-secondary mb-4">Aucune cave configurée</div>
      <router-link to="/caves/new" class="text-gh-accent hover:underline">Créer ma première cave</router-link>
    </div>

    <div v-else class="space-y-4">
      <div v-for="cave in caves" :key="cave.id" class="bg-gh-surface rounded-md border border-gh-border overflow-hidden">
        <div class="p-4 flex items-center justify-between hover:bg-gh-elevated/30 transition">
          <router-link :to="`/caves/${cave.id}`" class="flex-1 group cursor-pointer">
            <h2 class="text-lg font-medium text-gh-text group-hover:text-gh-accent transition-colors duration-200 ease-in-out">{{ cave.name }}</h2>
            <p class="text-sm text-gh-text-secondary group-hover:text-gh-text-secondary">
              {{ cave.columns?.length || 0 }} colonne(s) · 
              {{ getTotalPositions(cave) }} positions · 
              {{ getOccupiedPositions(cave) }} occupées
            </p>
          </router-link>
          <div class="flex gap-2">
            <router-link :to="`/caves/${cave.id}`" class="p-2 text-gh-text-secondary hover:text-gh-text hover:bg-gh-elevated rounded-md transition" title="Voir">
              <EyeIcon class="w-5 h-5" />
            </router-link>
            <router-link :to="`/caves/${cave.id}/edit`" class="p-2 text-gh-text-secondary hover:text-gh-accent hover:bg-gh-elevated rounded-md transition" title="Modifier">
              <PencilIcon class="w-5 h-5" />
            </router-link>
            <button @click="deleteCave(cave.id)" class="p-2 text-gh-text-secondary hover:text-gh-accent-red hover:bg-gh-elevated rounded-md transition" title="Supprimer">
              <TrashIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div class="border-t border-gh-border px-4 py-3 bg-gh-bg/50">
          <div class="flex flex-wrap gap-4 text-xs">
            <div v-for="col in cave.columns" :key="col.id" class="text-gh-text-secondary">
              <span class="text-gh-text font-medium">{{ col.name }}</span>
              <span class="ml-1">({{ col.rows?.length || 0 }} étagères)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>