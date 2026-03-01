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
      occupied += row.positions?.filter(p => p.bottle_id).length || 0
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
        <h1 class="text-xl font-bold text-white">Mes Caves</h1>
        <p class="text-sm text-[#8b949e]">Gérez vos espaces de stockage</p>
      </div>
      <router-link to="/caves/new" class="flex items-center gap-2 bg-[#238636] hover:bg-[#2ea043] text-white px-4 py-2 rounded-md font-medium transition text-sm">
        <PlusIcon class="w-5 h-5" />
        <span>Nouvelle cave</span>
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-12 text-[#8b949e]">Chargement...</div>

    <div v-else-if="caves.length === 0" class="text-center py-12">
      <div class="text-[#8b949e] mb-4">Aucune cave configurée</div>
      <router-link to="/caves/new" class="text-[#58a6ff] hover:underline">Créer ma première cave</router-link>
    </div>

    <div v-else class="space-y-4">
      <div v-for="cave in caves" :key="cave.id" class="bg-[#161b22] rounded-md border border-[#30363d] overflow-hidden">
        <div class="p-4 flex items-center justify-between hover:bg-[#21262d]/30 transition">
          <router-link :to="`/caves/${cave.id}`" class="flex-1 group cursor-pointer">
            <h2 class="text-lg font-medium text-white group-hover:text-[#58a6ff] transition-colors duration-200 ease-in-out">{{ cave.name }}</h2>
            <p class="text-sm text-[#8b949e] group-hover:text-[#8b949e]">
              {{ cave.columns?.length || 0 }} colonne(s) · 
              {{ getTotalPositions(cave) }} positions · 
              {{ getOccupiedPositions(cave) }} occupées
            </p>
          </router-link>
          <div class="flex gap-2">
            <router-link :to="`/caves/${cave.id}`" class="p-2 text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded-md transition" title="Voir">
              <EyeIcon class="w-5 h-5" />
            </router-link>
            <router-link :to="`/caves/${cave.id}/edit`" class="p-2 text-[#8b949e] hover:text-[#58a6ff] hover:bg-[#21262d] rounded-md transition" title="Modifier">
              <PencilIcon class="w-5 h-5" />
            </router-link>
            <button @click="deleteCave(cave.id)" class="p-2 text-[#8b949e] hover:text-[#f85149] hover:bg-[#21262d] rounded-md transition" title="Supprimer">
              <TrashIcon class="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div class="border-t border-[#30363d] px-4 py-3 bg-[#0d1117]/50">
          <div class="flex flex-wrap gap-4 text-xs">
            <div v-for="col in cave.columns" :key="col.id" class="text-[#8b949e]">
              <span class="text-white font-medium">{{ col.name }}</span>
              <span class="ml-1">({{ col.rows?.length || 0 }} étagères)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>