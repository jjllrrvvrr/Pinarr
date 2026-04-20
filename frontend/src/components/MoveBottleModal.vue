<template>
  <div v-if="show" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-[#161b22] rounded-xl border border-[#30363d] max-w-md w-full p-6">
      <h3 class="text-lg font-bold text-white mb-4">Déplacer la bouteille</h3>
      
      <div v-if="isLoading" class="text-center py-4 text-[#8b949e]">
        Chargement des caves...
      </div>
      
      <div v-else class="space-y-4">
        <div>
          <label class="block text-sm text-[#8b949e] mb-2">Nouvelle position</label>
          <div class="space-y-2">
            <select v-model="selectedCave" @change="onCaveChange" class="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-2.5 text-white">
              <option :value="null">Choisir une cave...</option>
              <option v-for="cave in caves" :key="cave.id" :value="cave.id">{{ cave.name }}</option>
            </select>
            
            <select v-model="selectedColumn" @change="onColumnChange" :disabled="!selectedCave" class="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-2.5 text-white disabled:opacity-50">
              <option :value="null">Choisir une colonne...</option>
              <option v-for="col in columns" :key="col.id" :value="col.id">{{ col.name }}</option>
            </select>
            
            <select v-model="selectedRow" @change="onRowChange" :disabled="!selectedColumn" class="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-2.5 text-white disabled:opacity-50">
              <option :value="null">Choisir une rangée...</option>
              <option v-for="row in rows" :key="row.id" :value="row.id">{{ row.name }}</option>
            </select>
            
            <select v-model="selectedPosition" :disabled="!selectedRow" class="w-full bg-[#0d1117] border border-[#30363d] rounded-lg p-2.5 text-white disabled:opacity-50">
              <option :value="null">Choisir une position...</option>
              <option v-for="pos in positions" :key="pos.id" :value="pos.id" :disabled="pos.occupied">
                L{{ pos.line }}/P{{ pos.position }} {{ pos.occupied ? '(occupée)' : '' }}
              </option>
            </select>
          </div>
        </div>

        <div class="flex gap-3 pt-2">
          <button 
            @click="moveBottle" 
            :disabled="!selectedPosition || isProcessing"
            class="flex-1 py-2.5 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white rounded-lg transition"
          >
            {{ isProcessing ? 'Déplacement...' : 'Déplacer' }}
          </button>
          
          <button 
            @click="$emit('close')"
            class="px-4 py-2.5 text-[#8b949e] hover:text-white bg-[#21262d] hover:bg-[#30363d] rounded-lg transition"
          >
            Annuler
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiRequest } from '../services/api.js'
import { QrService } from '../services/qrService.js'

const props = defineProps({
  show: Boolean,
  physicalBottleId: Number
})

const emit = defineEmits(['close', 'moved'])

const isLoading = ref(true)
const isProcessing = ref(false)
const caves = ref([])
const columns = ref([])
const rows = ref([])
const positions = ref([])

const selectedCave = ref(null)
const selectedColumn = ref(null)
const selectedRow = ref(null)
const selectedPosition = ref(null)

const loadCaves = async () => {
  try {
    caves.value = await apiRequest('/caves')
  } catch (e) {
    console.error('Erreur chargement caves:', e)
  } finally {
    isLoading.value = false
  }
}

const onCaveChange = async () => {
  selectedColumn.value = null
  selectedRow.value = null
  selectedPosition.value = null
  columns.value = []
  rows.value = []
  positions.value = []
  
  if (!selectedCave.value) return
  
  const cave = caves.value.find(c => c.id === selectedCave.value)
  if (cave) {
    columns.value = cave.columns || []
  }
}

const onColumnChange = async () => {
  selectedRow.value = null
  selectedPosition.value = null
  rows.value = []
  positions.value = []
  
  if (!selectedColumn.value) return
  
  const column = columns.value.find(c => c.id === selectedColumn.value)
  if (column) {
    rows.value = column.rows || []
  }
}

const onRowChange = async () => {
  selectedPosition.value = null
  positions.value = []
  
  if (!selectedRow.value) return
  
  try {
    const rowPositions = await apiRequest(`/rows/${selectedRow.value}/positions`)
    positions.value = rowPositions
  } catch (e) {
    console.error('Erreur chargement positions:', e)
  }
}

const moveBottle = async () => {
  if (!selectedPosition.value) return
  
  isProcessing.value = true
  try {
    await QrService.moveBottle(props.physicalBottleId, selectedPosition.value)
    emit('moved')
  } catch (e) {
    console.error('Erreur déplacement:', e)
    alert('Erreur lors du déplacement: ' + e.message)
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  loadCaves()
})
</script>
