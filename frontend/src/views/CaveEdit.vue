<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PlusIcon, TrashIcon, ArrowUpIcon, ArrowDownIcon } from '@heroicons/vue/24/outline'
import { apiRequest } from '../services/api.js'

const route = useRoute()
const router = useRouter()

const isNew = computed(() => !route.params.id)
const caveId = computed(() => route.params.id)

const caveName = ref('')
const columns = ref([])
const loading = ref(false)
const saving = ref(false)

const fetchCave = async () => {
  if (isNew.value) return
  loading.value = true
  try {
    const cave = await apiRequest(`/caves/${caveId.value}`)
    caveName.value = cave.name
    columns.value = cave.columns?.map(col => ({
      id: col.id,
      name: col.name,
      order: col.order,
      rows: col.rows?.map(row => ({
        id: row.id,
        name: row.name,
        width: row.width,
        height: row.height,
        order: row.order
      })) || []
    })) || []
  } catch (e) {
    console.error('Erreur:', e)
  } finally {
    loading.value = false
  }
}

const addColumn = () => {
  columns.value.push({
    name: `Colonne ${columns.value.length + 1}`,
    order: columns.value.length,
    rows: []
  })
}

const removeColumn = (colIndex) => {
  columns.value.splice(colIndex, 1)
  columns.value.forEach((col, i) => col.order = i)
}

const addRow = (colIndex) => {
  const col = columns.value[colIndex]
  col.rows.push({
    name: `Étagère ${col.rows.length + 1}`,
    width: 6,
    height: 3,
    order: col.rows.length
  })
}

const removeRow = (colIndex, rowIndex) => {
  columns.value[colIndex].rows.splice(rowIndex, 1)
  columns.value[colIndex].rows.forEach((row, i) => row.order = i)
}

const moveColumnUp = (index) => {
  if (index === 0) return
  const temp = columns.value[index]
  columns.value[index] = columns.value[index - 1]
  columns.value[index - 1] = temp
  columns.value.forEach((col, i) => col.order = i)
}

const moveColumnDown = (index) => {
  if (index === columns.value.length - 1) return
  const temp = columns.value[index]
  columns.value[index] = columns.value[index + 1]
  columns.value[index + 1] = temp
  columns.value.forEach((col, i) => col.order = i)
}

const moveRowUp = (colIndex, rowIndex) => {
  const rows = columns.value[colIndex].rows
  if (rowIndex === 0) return
  const temp = rows[rowIndex]
  rows[rowIndex] = rows[rowIndex - 1]
  rows[rowIndex - 1] = temp
  rows.forEach((row, i) => row.order = i)
}

const moveRowDown = (colIndex, rowIndex) => {
  const rows = columns.value[colIndex].rows
  if (rowIndex === rows.length - 1) return
  const temp = rows[rowIndex]
  rows[rowIndex] = rows[rowIndex + 1]
  rows[rowIndex + 1] = temp
  rows.forEach((row, i) => row.order = i)
}

const saveCave = async () => {
  if (!caveName.value.trim()) {
    alert('Le nom de la cave est obligatoire')
    return
  }

  saving.value = true
  try {
    let savedCaveId = caveId.value

    if (isNew.value) {
      const cave = await apiRequest('/caves/', {
        method: 'POST',
        body: JSON.stringify({ name: caveName.value })
      })
      savedCaveId = cave.id
    } else {
      await apiRequest(`/caves/${savedCaveId}`, {
        method: 'PUT',
        body: JSON.stringify({ name: caveName.value })
      })
    }

    const existingColumnIds = columns.value.filter(c => c.id).map(c => c.id)
    if (!isNew.value) {
      const existingCave = await apiRequest(`/caves/${savedCaveId}`)
      for (const col of existingCave.columns || []) {
        if (!existingColumnIds.includes(col.id)) {
          await apiRequest(`/columns/${col.id}`, { method: 'DELETE' })
        }
      }
    }

    for (const col of columns.value) {
      let savedColId = col.id
      
      if (!col.id) {
        const saved = await apiRequest(`/caves/${savedCaveId}/columns/`, {
          method: 'POST',
          body: JSON.stringify({ name: col.name, order: col.order })
        })
        savedColId = saved.id
      } else {
        await apiRequest(`/columns/${col.id}`, {
          method: 'PUT',
          body: JSON.stringify({ name: col.name, order: col.order })
        })
      }

      const existingRowIds = col.rows.filter(r => r.id).map(r => r.id)
      if (col.id) {
        const caveData = await apiRequest(`/caves/${savedCaveId}`)
        const existingCol = caveData.columns?.find(c => c.id === savedColId)
        if (existingCol?.rows) {
          for (const row of existingCol.rows) {
            if (!existingRowIds.includes(row.id)) {
              await apiRequest(`/rows/${row.id}`, { method: 'DELETE' })
            }
          }
        }
      }

      for (const row of col.rows) {
        if (!row.id) {
          await apiRequest(`/columns/${savedColId}/rows/`, {
            method: 'POST',
            body: JSON.stringify({
              name: row.name,
              width: row.width,
              height: row.height,
              order: row.order
            })
          })
        } else {
          await apiRequest(`/rows/${row.id}`, {
            method: 'PUT',
            body: JSON.stringify({
              name: row.name,
              width: row.width,
              height: row.height,
              order: row.order
            })
          })
        }
      }
    }

    router.push('/caves')
  } catch (e) {
    alert('Erreur: ' + e.message)
  } finally {
    saving.value = false
  }
}

onMounted(fetchCave)
</script>

<template>
  <main class="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-8 pb-20">
    <div class="flex flex-wrap items-center gap-2 mb-4 sm:mb-6 text-[#8b949e] text-xs sm:text-sm">
      <router-link to="/caves" class="hover:text-[#58a6ff]">Caves</router-link>
      <span>/</span>
      <span class="text-white truncate">{{ isNew ? 'Nouvelle cave' : 'Modifier' }}</span>
    </div>

    <div v-if="loading" class="text-center py-12 text-[#8b949e]">Chargement...</div>

    <div v-else class="space-y-4 sm:space-y-6">
      <div class="bg-[#161b22] rounded-md border border-[#30363d] p-3 sm:p-4">
        <label class="block text-xs font-medium text-[#8b949e] mb-1">Nom de la cave *</label>
        <input v-model="caveName" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2 sm:p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="Ma Cave">
      </div>

      <div class="space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h2 class="text-base sm:text-lg font-medium text-white">Colonnes</h2>
          <button @click="addColumn" class="flex items-center justify-center gap-1 text-xs sm:text-sm text-[#58a6ff] hover:text-[#388bfd] transition px-2 py-1.5 sm:px-0 sm:py-0">
            <PlusIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            <span class="sm:hidden">Ajouter</span>
            <span class="hidden sm:inline">Ajouter une colonne</span>
          </button>
        </div>

        <div v-if="columns.length === 0" class="text-center py-8 text-[#8b949e] bg-[#161b22] rounded-md border border-[#30363d]">
          Aucune colonne. Ajoutez une colonne pour commencer.
        </div>

        <div v-for="(col, colIndex) in columns" :key="colIndex" class="bg-[#161b22] rounded-md border border-[#30363d] overflow-hidden">
          <div class="p-2 sm:p-4 border-b border-[#30363d] flex items-center justify-between bg-[#0d1117]/50">
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <div class="flex flex-col gap-1">
                <button @click="moveColumnUp(colIndex)" :disabled="colIndex === 0" class="p-0.5 text-[#8b949e] hover:text-white disabled:opacity-30">
                  <ArrowUpIcon class="w-3 h-3" />
                </button>
                <button @click="moveColumnDown(colIndex)" :disabled="colIndex === columns.length - 1" class="p-0.5 text-[#8b949e] hover:text-white disabled:opacity-30">
                  <ArrowDownIcon class="w-3 h-3" />
                </button>
              </div>
              <input v-model="col.name" class="bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 text-white text-xs sm:text-sm focus:border-[#58a6ff] outline-none flex-1 min-w-0" placeholder="Nom de la colonne">
            </div>
            <button @click="removeColumn(colIndex)" class="p-1.5 text-[#8b949e] hover:text-[#f85149] transition flex-shrink-0">
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>

          <div class="p-2 sm:p-4">
            <div class="flex items-center justify-between mb-3">
              <span class="text-xs sm:text-sm text-[#8b949e]">Étagères ({{ col.rows.length }})</span>
              <button @click="addRow(colIndex)" class="text-xs text-[#58a6ff] hover:underline px-2 py-1">+ Étagère</button>
            </div>

            <div v-if="col.rows.length === 0" class="text-center py-4 text-[#8b949e] text-xs sm:text-sm">
              Aucune étagère
            </div>

            <div v-else class="space-y-2">
              <div v-for="(row, rowIndex) in col.rows" :key="rowIndex" class="flex flex-col sm:flex-row sm:items-center gap-2 p-2 bg-[#0d1117] rounded border border-[#30363d]">
                <div class="flex items-center gap-2 flex-1">
                  <div class="flex flex-col gap-1 flex-shrink-0">
                    <button @click="moveRowUp(colIndex, rowIndex)" :disabled="rowIndex === 0" class="p-0.5 text-[#8b949e] hover:text-white disabled:opacity-30">
                      <ArrowUpIcon class="w-3 h-3" />
                    </button>
                    <button @click="moveRowDown(colIndex, rowIndex)" :disabled="rowIndex === col.rows.length - 1" class="p-0.5 text-[#8b949e] hover:text-white disabled:opacity-30">
                      <ArrowDownIcon class="w-3 h-3" />
                    </button>
                  </div>
                  <input v-model="row.name" class="flex-1 bg-transparent border border-[#30363d] rounded px-2 py-1 text-white text-xs sm:text-sm focus:border-[#58a6ff] outline-none" placeholder="Nom">
                </div>
                <div class="flex items-center gap-2 ml-6 sm:ml-0">
                  <div class="flex items-center gap-1">
                    <input v-model.number="row.width" type="number" min="1" max="20" class="w-10 sm:w-12 bg-transparent border border-[#30363d] rounded px-1 py-1 text-white text-xs text-center focus:border-[#58a6ff] outline-none" title="Largeur (positions par ligne)">
                    <span class="text-[#8b949e] text-xs">×</span>
                    <input v-model.number="row.height" type="number" min="1" max="10" class="w-10 sm:w-12 bg-transparent border border-[#30363d] rounded px-1 py-1 text-white text-xs text-center focus:border-[#58a6ff] outline-none" title="Hauteur (lignes)">
                  </div>
                  <span class="text-[#8b949e] text-xs">{{ row.width * row.height }} pos</span>
                  <button @click="removeRow(colIndex, rowIndex)" class="p-1 text-[#8b949e] hover:text-[#f85149]">
                    <TrashIcon class="w-3 h-3" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row justify-between gap-2 pt-4 border-t border-[#30363d]">
        <router-link to="/caves" class="px-4 py-2 rounded-md text-[#8b949e] hover:bg-[#21262d] transition font-medium border border-[#30363d] text-sm text-center">
          Annuler
        </router-link>
        <button @click="saveCave" :disabled="saving" class="px-4 sm:px-6 py-2 rounded-md bg-[#238636] hover:bg-[#2ea043] text-white font-medium transition text-sm disabled:opacity-50">
          {{ saving ? 'Sauvegarde...' : 'Enregistrer' }}
        </button>
      </div>
    </div>
  </main>
</template>