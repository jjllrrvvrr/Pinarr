<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { PencilIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import WineBottleIcon from '../components/WineBottleIcon.vue'
import BottlePreview from '../components/BottlePreview.vue'
import BottleSidebar from '../components/BottleSidebar.vue'
import { apiRequest } from '../services/api.js'

const route = useRoute()
const router = useRouter()

const emit = defineEmits(['refresh-data'])

const cave = ref(null)
const loading = ref(true)
const selectedColumn = ref(null)
const selectedPosition = ref(null)
const bottles = ref([])

// États pour le drag & drop
const draggedBottle = ref(null)
const dragSourcePosition = ref(null)
const isDragging = ref(false)
const dropConflict = ref(null)
const hoveredDropZone = ref(null)
const draggedFromSidebar = ref(false)

// Hover highlight
const hoveredBottleId = ref(null)
const highlightedPositions = ref([])

// États pour la vignette de preview
const previewBottle = ref(null)
const previewPosition = ref({ x: 0, y: 0 })
const previewShow = ref(false)

const caveId = computed(() => route.params.id)

const fetchCave = async () => {
  loading.value = true
  try {
    cave.value = await apiRequest(`/caves/${caveId.value}`)
    if (cave.value.columns?.length > 0) {
      selectedColumn.value = cave.value.columns[0]
    }
  } catch (e) {
    console.error('Erreur:', e)
  } finally {
    loading.value = false
  }
}

const fetchBottles = async () => {
  try {
    bottles.value = await apiRequest('/bottles/')
  } catch (e) {
    console.error('Erreur:', e)
  }
}

const getBottleAtPosition = (rowId, line, pos) => {
  const row = cave.value?.columns
    ?.flatMap(c => c.rows || [])
    ?.find(r => r.id === rowId)
  
  if (!row) return null
  
  const position = row.positions?.find(p => p.line === line && p.position === pos)
  if (!position || !position.bottle_at_position) return null
  
  return bottles.value.find(b => b.id === position.bottle_at_position.id)
}

const getPositionData = (rowId, line, pos) => {
  const row = cave.value?.columns
    ?.flatMap(c => c.rows || [])
    ?.find(r => r.id === rowId)
  
  if (!row) return null
  
  return row.positions?.find(p => p.line === line && p.position === pos)
}

const selectPosition = (row, line, pos) => {
  const positionData = getPositionData(row.id, line, pos)
  const bottle = getBottleAtPosition(row.id, line, pos)
  
  selectedPosition.value = {
    row,
    line,
    position: pos,
    positionData,
    bottle
  }
}

const clearPosition = async () => {
  if (!selectedPosition.value?.positionData?.id) return
  
  try {
    await apiRequest(`/positions/${selectedPosition.value.positionData.id}/bottle`, {
      method: 'DELETE'
    })
    await fetchCave()
    selectedPosition.value = null
  } catch (e) {
    alert('Erreur: ' + e.message)
  }
}

const availableBottles = computed(() => {
  // Compter les placements actuels par bouteille
  const placementCount = {}
  cave.value?.columns?.forEach(col => {
    col.rows?.forEach(row => {
      row.positions?.forEach(pos => {
        if (pos.bottle_at_position) {
          placementCount[pos.bottle_at_position.id] = (placementCount[pos.bottle_at_position.id] || 0) + 1
        }
      })
    })
  })
  
  // Filtrer : ne montrer que les bouteilles avec places disponibles
  return bottles.value.filter(b => {
    const placedCount = placementCount[b.id] || 0
    return placedCount < b.quantity
  })
})

const assignBottle = async (bottleId) => {
  console.log('Assigning bottle:', bottleId)
  console.log('Selected position:', selectedPosition.value)
  
  if (!selectedPosition.value) {
    console.error('No position selected')
    return
  }
  
  // Si la position n'existe pas encore, on doit d'abord la créer
  let positionId = selectedPosition.value.positionData?.id
  
  if (!positionId) {
    console.log('Position does not exist, creating it first...')
    try {
      const newPosition = await apiRequest(`/rows/${selectedPosition.value.row.id}/positions/`, {
        method: 'POST',
        body: JSON.stringify({
          line: selectedPosition.value.line,
          position: selectedPosition.value.position
        })
      })
      
      console.log('Position created:', newPosition)
      positionId = newPosition.id
    } catch (e) {
      console.error('Error creating position:', e)
      alert('Erreur lors de la création de la position: ' + e.message)
      return
    }
  }
  
  console.log('Assigning bottle to position:', positionId)
  
  try {
    await apiRequest(`/positions/${positionId}`, {
      method: 'PUT',
      body: JSON.stringify({ bottle_id: bottleId })
    })
    
    console.log('Bottle assigned successfully')
    await fetchCave()
    emit('refresh-data')
    selectedPosition.value = null
  } catch (e) {
    console.error('Error assigning bottle:', e)
    alert('Erreur: ' + e.message)
  }
}

// Fonctions pour le drag & drop
const handleDragStart = (event, row, line, pos, bottle) => {
  if (!bottle) return
  
  draggedBottle.value = bottle
  dragSourcePosition.value = {
    row,
    line,
    position: pos,
    positionData: getPositionData(row.id, line, pos)
  }
  isDragging.value = true
  
  // Ajouter une classe pour styliser l'élément draggé
  event.target.classList.add('dragging')
  
  // Configurer les données du drag
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', JSON.stringify({
    bottleId: bottle.id,
    sourceRowId: row.id,
    sourceLine: line,
    sourcePosition: pos
  }))
}

const handleDragEnd = (event) => {
  event.target.classList.remove('dragging')
  isDragging.value = false
  hoveredDropZone.value = null
}

const handleDragOver = (event, row, line, pos) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
  
  const bottleAtTarget = getBottleAtPosition(row.id, line, pos)
  hoveredDropZone.value = {
    rowId: row.id,
    line,
    position: pos,
    hasBottle: !!bottleAtTarget
  }
}

const handleDragLeave = () => {
  hoveredDropZone.value = null
}

const handleDrop = async (event, targetRow, targetLine, targetPos) => {
  event.preventDefault()
  hoveredDropZone.value = null
  
  const data = JSON.parse(event.dataTransfer.getData('text/plain'))
  
  // Drop depuis la sidebar
  if (data.fromSidebar) {
    const bottle = bottles.value.find(b => b.id === data.bottleId)
    if (!bottle) return
    
    const bottleAtTarget = getBottleAtPosition(targetRow.id, targetLine, targetPos)
    
    if (bottleAtTarget) {
      // Conflit avec drop depuis sidebar
      dropConflict.value = {
        source: { bottle, fromSidebar: true },
        target: {
          row: targetRow,
          line: targetLine,
          position: targetPos,
          positionData: getPositionData(targetRow.id, targetLine, targetPos),
          bottle: bottleAtTarget
        },
        draggedBottle: bottle
      }
      return
    }
    
    // Placement simple depuis sidebar
    await placeBottleFromSidebar(bottle, targetRow, targetLine, targetPos)
    return
  }
  
  // Drop depuis la grille (existing logic)
  if (!draggedBottle.value || !dragSourcePosition.value) return
  
  const sourceRowId = dragSourcePosition.value.row.id
  const sourceLine = dragSourcePosition.value.line
  const sourcePos = dragSourcePosition.value.position
  
  if (sourceRowId === targetRow.id && sourceLine === targetLine && sourcePos === targetPos) {
    draggedBottle.value = null
    dragSourcePosition.value = null
    return
  }
  
  const bottleAtTarget = getBottleAtPosition(targetRow.id, targetLine, targetPos)
  
  if (bottleAtTarget) {
    dropConflict.value = {
      source: dragSourcePosition.value,
      target: {
        row: targetRow,
        line: targetLine,
        position: targetPos,
        positionData: getPositionData(targetRow.id, targetLine, targetPos),
        bottle: bottleAtTarget
      },
      draggedBottle: draggedBottle.value
    }
    return
  }
  
  await executeMove(
    dragSourcePosition.value,
    {
      row: targetRow,
      line: targetLine,
      position: targetPos,
      positionData: getPositionData(targetRow.id, targetLine, targetPos)
    }
  )
  
  draggedBottle.value = null
  dragSourcePosition.value = null
}

// Fonction pour déplacer une bouteille localement (Optimistic UI)
const moveBottleLocally = (source, target, bottle) => {
  console.log('=== MOVE BOTTLE LOCALLY ===')
  
  // Trouver et modifier la position source (retirer la bouteille)
  if (source.positionData?.id) {
    cave.value?.columns?.forEach(col => {
      col.rows?.forEach(row => {
        const sourcePos = row.positions?.find(p => p.id === source.positionData.id)
        if (sourcePos) {
          console.log('Clearing source position:', sourcePos.id)
          sourcePos.bottle_at_position = null
          sourcePos.bottle_id = null
        }
      })
    })
  }
  
  // Trouver ou créer la position cible (ajouter la bouteille)
  let targetPos = null
  cave.value?.columns?.forEach(col => {
    col.rows?.forEach(row => {
      if (row.id === target.row.id) {
        targetPos = row.positions?.find(p => p.line === target.line && p.position === target.position)
        if (targetPos) {
          console.log('Found existing target position:', targetPos.id)
          targetPos.bottle_at_position = bottle
          targetPos.bottle_id = bottle.id
        }
      }
    })
  })
  
  return targetPos
}

const executeMove = async (source, target) => {
  console.log('=== EXECUTE MOVE (Optimistic) ===')
  console.log('Source positionData ID:', source.positionData?.id)
  console.log('Target:', { rowId: target.row.id, line: target.line, pos: target.position })
  console.log('Bottle:', draggedBottle.value?.name, 'ID:', draggedBottle.value?.id)
  
  const bottle = draggedBottle.value
  const backupCave = JSON.parse(JSON.stringify(cave.value)) // Backup pour rollback
  
  try {
    // ÉTAPE 1: Mettre à jour l'UI immédiatement (Optimistic)
    console.log('Step 1: Updating UI optimistically...')
    const targetPos = moveBottleLocally(source, target, bottle)
    emit('refresh-data')
    console.log('Step 1 SUCCESS: UI updated')
    
    // ÉTAPE 2: Créer la position cible sur le serveur si nécessaire
    let targetPositionId = targetPos?.id
    
    if (!targetPositionId) {
      console.log('Step 2: Creating new position on server...')
      const newPosition = await apiRequest(`/rows/${target.row.id}/positions/`, {
        method: 'POST',
        body: JSON.stringify({
          line: target.line,
          position: target.position
        })
      })
      
      targetPositionId = newPosition.id
      console.log('Step 2 SUCCESS: New position ID:', targetPositionId)
      
      // Mettre à jour l'ID local
      targetPos.id = targetPositionId
    }
    
    // ÉTAPE 3: Vider la position source sur le serveur (AVANT d'assigner la cible)
    // Cela évite l'erreur "Quantité maximale atteinte" car la bouteille n'est plus comptée
    if (source.positionData?.id && source.positionData.id !== targetPositionId) {
      console.log('Step 3: Clearing source position on server...')
      await apiRequest(`/positions/${source.positionData.id}`, {
        method: 'PUT',
        body: JSON.stringify({ bottle_id: null })
      })
      console.log('Step 3 SUCCESS: Source cleared')
    }
    
    // ÉTAPE 4: Assigner la bouteille sur le serveur (APRÈS avoir vidé la source)
    console.log('Step 4: Assigning bottle on server...')
    await apiRequest(`/positions/${targetPositionId}`, {
      method: 'PUT',
      body: JSON.stringify({ bottle_id: bottle.id })
    })
    console.log('Step 4 SUCCESS: Bottle assigned on server')
    
    console.log('=== MOVE COMPLETED SUCCESSFULLY ===')
    
  } catch (e) {
    console.error('=== MOVE FAILED - ROLLING BACK ===', e)
    // ROLLBACK: Restaurer l'état précédent
    cave.value = backupCave
    alert('Erreur lors du déplacement: ' + e.message)
  }
}

const handleTrashDrop = async () => {
  if (!draggedBottle.value || !dragSourcePosition.value?.positionData?.id) return
  
  try {
    await apiRequest(`/positions/${dragSourcePosition.value.positionData.id}/bottle`, {
      method: 'DELETE'
    })
    await fetchCave()
    emit('refresh-data')
  } catch (e) {
    console.error('Error removing bottle:', e)
    alert('Erreur lors de la suppression: ' + e.message)
  }
  
  draggedBottle.value = null
  dragSourcePosition.value = null
  hoveredDropZone.value = null
}

const resolveConflict = async (action) => {
  if (!dropConflict.value) return
  
  const { source, target, draggedBottle } = dropConflict.value
  
  try {
    if (action === 'swap') {
      // Échanger les bouteilles
      // 1. Créer position temporaire pour la bouteille cible si besoin
      let tempPositionId = null
      
      // 2. Déplacer la bouteille source vers la cible
      await executeMove(source, target)
      
      // 3. Déplacer la bouteille cible vers la source
      const targetBottle = target.bottle
      draggedBottle.value = targetBottle
      dragSourcePosition.value = target
      
      const newTarget = {
        row: source.row,
        line: source.line,
        position: source.position,
        positionData: source.positionData
      }
      
      await executeMove(target, newTarget)
      
    } else if (action === 'replace') {
      // Remplacer - vider l'ancienne position et mettre la nouvelle
      if (target.positionData?.id) {
        await apiRequest(`/positions/${target.positionData.id}`, {
          method: 'PUT',
          body: JSON.stringify({ bottle_id: null })
        })
      }
      await executeMove(source, target)
      
    } else if (action === 'cancel') {
      // Annuler - ne rien faire
    }
  } catch (e) {
    console.error('Error resolving conflict:', e)
    alert('Erreur: ' + e.message)
  }
  
  dropConflict.value = null
  draggedBottle.value = null
  dragSourcePosition.value = null
}

// Fonctions pour la vignette de preview
const showPreview = (event, bottle) => {
  previewBottle.value = bottle
  previewShow.value = true
  updatePreviewPosition(event)
}

const hidePreview = () => {
  previewShow.value = false
  previewBottle.value = null
}

const updatePreviewPosition = (event) => {
  // Position en bas de la souris avec offset de 20px
  const x = event.clientX
  const y = event.clientY + 20
  
  // Vérifier les bords de l'écran
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  const previewWidth = 200
  const previewHeight = 150
  
  let finalX = x
  let finalY = y
  
  // Ajuster si dépasse à droite
  if (x + previewWidth > windowWidth) {
    finalX = x - previewWidth
  }
  
  // Ajuster si dépasse en bas
  if (y + previewHeight > windowHeight) {
    finalY = event.clientY - previewHeight - 10
  }
  
  previewPosition.value = { x: finalX, y: finalY }
}

onMounted(() => {
  fetchCave()
  fetchBottles()
})

// Fonctions pour la sidebar
const onHoverBottle = (bottleId) => {
  hoveredBottleId.value = bottleId
  if (bottleId) {
    highlightedPositions.value = getPositionsForBottleInCave(bottleId)
  } else {
    highlightedPositions.value = []
  }
}

const getPositionsForBottleInCave = (bottleId) => {
  const positions = []
  cave.value?.columns?.forEach(col => {
    col.rows?.forEach(row => {
      row.positions?.forEach(pos => {
        if (pos.bottle_at_position?.id === bottleId) {
          positions.push({
            rowId: row.id,
            line: pos.line,
            position: pos.position,
            positionId: pos.id
          })
        }
      })
    })
  })
  return positions
}

const isHighlighted = (rowId, line, pos) => {
  return highlightedPositions.value.some(p => 
    p.rowId === rowId && p.line === line && p.position === pos
  )
}

const onDragStartFromSidebar = (bottle, isFromSidebar) => {
  draggedFromSidebar.value = isFromSidebar
  draggedBottle.value = bottle
  dragSourcePosition.value = null
  isDragging.value = true
}

const onDragEndFromSidebar = () => {
  draggedFromSidebar.value = false
  isDragging.value = false
  hoveredDropZone.value = null
}

const removeBottleFromPosition = async (positionId) => {
  try {
    await apiRequest(`/positions/${positionId}/bottle`, {
      method: 'DELETE'
    })
    await fetchCave()
    emit('refresh-data')
  } catch (e) {
    console.error('Error removing bottle:', e)
  }
}

const placeBottleFromSidebar = async (bottle, targetRow, targetLine, targetPos) => {
  try {
    // Créer la position si elle n'existe pas
    let positionId = getPositionData(targetRow.id, targetLine, targetPos)?.id
    
    if (!positionId) {
      const newPosition = await apiRequest(`/rows/${targetRow.id}/positions/`, {
        method: 'POST',
        body: JSON.stringify({
          line: targetLine,
          position: targetPos
        })
      })
      positionId = newPosition.id
    }
    
    // Assigner la bouteille
    await apiRequest(`/positions/${positionId}`, {
      method: 'PUT',
      body: JSON.stringify({ bottle_id: bottle.id })
    })
    
    await fetchCave()
    emit('refresh-data')
  } catch (e) {
    console.error('Error placing bottle:', e)
  }
}
</script>

<template>
  <main class="max-w-6xl mx-auto px-4 py-8 pb-20">
    <div class="flex items-center gap-2 mb-6 text-[#8b949e] text-sm">
      <router-link to="/caves" class="hover:text-[#58a6ff]">Caves</router-link>
      <span>/</span>
      <span class="text-white">{{ cave?.name || 'Chargement...' }}</span>
    </div>

    <div v-if="loading" class="text-center py-12 text-[#8b949e]">Chargement...</div>

    <div v-else-if="!cave" class="text-center py-12 text-[#8b949e]">Cave non trouvée</div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6">
      <!-- GAUCHE: Grille de la cave -->
      <div class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-bold text-white">{{ cave.name }}</h1>
            <p class="text-sm text-[#8b949e]">{{ cave.columns?.length || 0 }} colonne(s)</p>
          </div>
          <router-link :to="`/caves/${cave.id}/edit`" class="flex items-center gap-2 px-3 py-2 text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded-md transition text-sm">
            <PencilIcon class="w-4 h-4" />
            Modifier
          </router-link>
        </div>

        <div v-if="cave.columns?.length > 1" class="flex gap-2 overflow-x-auto pb-2">
          <button
            v-for="col in cave.columns"
            :key="col.id"
            @click="selectedColumn = col"
            :class="['px-4 py-2 rounded-md text-sm font-medium transition whitespace-nowrap', selectedColumn?.id === col.id ? 'bg-[#238636] text-white' : 'bg-[#21262d] text-[#8b949e] hover:bg-[#30363d]']"
          >
            {{ col.name }}
          </button>
        </div>

        <div v-if="selectedColumn" class="space-y-6">
          <div v-for="row in selectedColumn.rows" :key="row.id" class="bg-[#161b22] rounded-md border border-[#30363d] overflow-hidden">
            <div class="px-4 py-2 border-b border-[#30363d] bg-[#0d1117]/50 flex items-center justify-between">
              <span class="text-sm font-medium text-white">{{ row.name }}</span>
              <span class="text-xs text-[#8b949e]">{{ row.width }}×{{ row.height }}</span>
            </div>
            
            <div class="p-4 overflow-x-auto">
              <div class="flex gap-1 mb-1">
                <div class="w-8 flex-shrink-0"></div>
                <div v-for="pos in row.width" :key="pos" class="w-16 text-center text-xs text-[#8b949e]">
                  {{ pos }}
                </div>
              </div>
              
              <div v-for="line in row.height" :key="line" class="flex gap-1 items-center mb-1">
                <div class="w-8 flex-shrink-0 text-xs text-[#8b949e] text-center">L{{ row.height - line + 1 }}</div>
                <div
                  v-for="pos in row.width"
                  :key="pos"
                  @click="selectPosition(row, row.height - line + 1, pos)"
                  @dragover.prevent="(e) => handleDragOver(e, row, row.height - line + 1, pos)"
                  @dragleave="handleDragLeave"
                  @drop="(e) => handleDrop(e, row, row.height - line + 1, pos)"
                  :class="[
                    'w-16 h-16 rounded border flex items-center justify-center cursor-pointer transition relative',
                    getBottleAtPosition(row.id, row.height - line + 1, pos)
                      ? 'bg-[#238636]/20 border-[#238636]'
                      : 'bg-[#0d1117] border-[#30363d]',
                    isHighlighted(row.id, row.height - line + 1, pos)
                      ? 'ring-2 ring-[#58a6ff] bg-[#58a6ff]/30 scale-105 z-10'
                      : '',
                    hoveredDropZone?.rowId === row.id && hoveredDropZone?.line === (row.height - line + 1) && hoveredDropZone?.position === pos
                      ? hoveredDropZone.hasBottle
                        ? 'ring-2 ring-[#f0883e] bg-[#f0883e]/20'
                        : 'ring-2 ring-[#58a6ff] bg-[#58a6ff]/20'
                      : ''
                  ]"
                >
                <div
                  v-if="getBottleAtPosition(row.id, row.height - line + 1, pos)"
                  class="text-center w-full h-full flex items-center justify-center"
                  draggable="true"
                  @dragstart="(e) => handleDragStart(e, row, row.height - line + 1, pos, getBottleAtPosition(row.id, row.height - line + 1, pos))"
                  @dragend="handleDragEnd"
                  @mouseenter="(e) => showPreview(e, getBottleAtPosition(row.id, row.height - line + 1, pos))"
                  @mouseleave="hidePreview"
                  @mousemove="updatePreviewPosition"
                  :class="{ 'opacity-50': draggedBottle?.id === getBottleAtPosition(row.id, row.height - line + 1, pos).id }"
                >
                  <div class="flex flex-col items-center">
                    <WineBottleIcon :type="getBottleAtPosition(row.id, row.height - line + 1, pos).type" class="w-6 h-10" />
                    <div class="text-[10px] text-white truncate px-1 max-w-full">
                      {{ getBottleAtPosition(row.id, row.height - line + 1, pos).name?.substring(0, 8) }}
                    </div>
                  </div>
                </div>
                <div v-else class="text-[#30363d] text-xs">+</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="cave.columns?.length === 0" class="text-center py-12 text-[#8b949e] bg-[#161b22] rounded-md border border-[#30363d]">
        Cette cave n'a pas encore de colonnes.
        <router-link :to="`/caves/${cave.id}/edit`" class="text-[#58a6ff] hover:underline">Modifier la cave</router-link>
      </div>
    </div>

    <!-- DROITE: Sidebar des bouteilles -->
    <div>
      <BottleSidebar
        :bottles="bottles"
        :cave="cave"
        :hovered-bottle-id="hoveredBottleId"
        :is-dragging="isDragging"
        @hover-bottle="onHoverBottle"
        @drag-start="onDragStartFromSidebar"
        @drag-end="onDragEndFromSidebar"
        @remove-bottle="removeBottleFromPosition"
      />
    </div>
  </div>

    <div v-if="selectedPosition" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="selectedPosition = null">
      <div class="bg-[#161b22] rounded-md w-full max-w-md border border-[#30363d]">
        <div class="p-4 border-b border-[#30363d] flex items-center justify-between">
          <div>
            <h3 class="font-medium text-white">Position {{ selectedPosition.row?.name }} - L{{ selectedPosition.line }}/{{ selectedPosition.position }}</h3>
          </div>
          <button @click="selectedPosition = null" class="text-[#8b949e] hover:text-white">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <div class="p-4">
          <div v-if="selectedPosition.bottle" class="mb-4">
            <div class="text-sm text-[#8b949e] mb-2">Bouteille assignée:</div>
            <router-link
              :to="`/wine/${selectedPosition.bottle.id}`"
              class="flex items-center gap-3 p-3 bg-[#0d1117] rounded-md border border-[#30363d] hover:border-[#58a6ff] transition"
            >
              <WineBottleIcon :type="selectedPosition.bottle.type" class="w-8 h-12" />
              <div>
                <div class="font-medium text-white">{{ selectedPosition.bottle.name }}</div>
                <div class="text-xs text-[#8b949e]">{{ selectedPosition.bottle.year }} · {{ selectedPosition.bottle.type }}</div>
              </div>
            </router-link>
            <button
              @click="clearPosition"
              class="w-full mt-3 px-4 py-2 bg-[#f85149]/20 text-[#f85149] rounded-md text-sm hover:bg-[#f85149]/30 transition"
            >
              Retirer la bouteille
            </button>
          </div>

          <div v-else>
            <div class="text-sm text-[#8b949e] mb-2">Assigner une bouteille:</div>
            <div class="max-h-64 overflow-y-auto space-y-1">
              <button
                v-for="bottle in availableBottles"
                :key="bottle.id"
                @click="assignBottle(bottle.id)"
                class="w-full flex items-center gap-3 p-2 bg-[#0d1117] rounded border border-[#30363d] hover:border-[#58a6ff] transition text-left"
              >
                <WineBottleIcon :type="bottle.type" class="w-6 h-8" />
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-white truncate">{{ bottle.name }}</div>
                  <div class="text-xs text-[#8b949e]">{{ bottle.year }}</div>
                </div>
                <div class="text-xs text-[#8b949e]">×{{ bottle.quantity }}</div>
              </button>
              <div v-if="availableBottles.length === 0" class="text-center py-4 text-[#8b949e]">
                Aucune bouteille disponible
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Zone Poubelle -->
    <div
      v-if="isDragging"
      class="fixed bottom-6 right-6 z-50"
      @dragover.prevent="hoveredDropZone = { isTrash: true }"
      @dragleave="hoveredDropZone = null"
      @drop.prevent="handleTrashDrop"
    >
      <div
        :class="[
          'w-20 h-20 rounded-full border-2 flex items-center justify-center transition-all duration-200',
          hoveredDropZone?.isTrash
            ? 'bg-[#f85149]/30 border-[#f85149] scale-110'
            : 'bg-[#161b22]/90 border-[#30363d] hover:border-[#f85149]/50'
        ]"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          :class="['w-8 h-8 transition-colors', hoveredDropZone?.isTrash ? 'text-[#f85149]' : 'text-[#8b949e]']"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </div>
      <div class="text-center text-xs text-[#8b949e] mt-2" v-if="hoveredDropZone?.isTrash">
        Déposer pour retirer
      </div>
    </div>

    <!-- Popup de résolution de conflit -->
    <div
      v-if="dropConflict"
      class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[60] flex items-center justify-center p-4"
      @click.self="resolveConflict('cancel')"
    >
      <div class="bg-[#161b22] rounded-md w-full max-w-md border border-[#30363d]">
        <div class="p-4 border-b border-[#30363d]">
          <h3 class="font-medium text-white">Position occupée</h3>
          <p class="text-sm text-[#8b949e] mt-1">
            Une bouteille est déjà présente à cet emplacement. Que souhaitez-vous faire ?
          </p>
        </div>

        <div class="p-4 space-y-4">
          <!-- Informations sur les bouteilles -->
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-[#0d1117] rounded border border-[#30363d] p-3">
              <div class="text-xs text-[#8b949e] mb-2">À déplacer :</div>
              <div class="flex items-center gap-2">
                <WineBottleIcon :type="dropConflict.draggedBottle.type" class="w-6 h-8" />
                <div class="min-w-0">
                  <div class="text-sm text-white truncate">{{ dropConflict.draggedBottle.name }}</div>
                  <div class="text-xs text-[#8b949e]">{{ dropConflict.draggedBottle.year }}</div>
                </div>
              </div>
            </div>

            <div class="bg-[#0d1117] rounded border border-[#30363d] p-3">
              <div class="text-xs text-[#8b949e] mb-2">Actuellement :</div>
              <div class="flex items-center gap-2">
                <WineBottleIcon :type="dropConflict.target.bottle.type" class="w-6 h-8" />
                <div class="min-w-0">
                  <div class="text-sm text-white truncate">{{ dropConflict.target.bottle.name }}</div>
                  <div class="text-xs text-[#8b949e]">{{ dropConflict.target.bottle.year }}</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Boutons d'action -->
          <div class="space-y-2">
            <button
              @click="resolveConflict('swap')"
              class="w-full px-4 py-2 bg-[#58a6ff]/20 text-[#58a6ff] rounded-md text-sm hover:bg-[#58a6ff]/30 transition flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              Échanger les positions
            </button>

            <button
              @click="resolveConflict('replace')"
              class="w-full px-4 py-2 bg-[#f0883e]/20 text-[#f0883e] rounded-md text-sm hover:bg-[#f0883e]/30 transition flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Remplacer (retirer l'ancienne)
            </button>

            <button
              @click="resolveConflict('cancel')"
              class="w-full px-4 py-2 text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded-md text-sm transition"
            >
              Annuler
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Vignette de preview -->
    <BottlePreview
      :bottle="previewBottle"
      :show="previewShow"
      :position="previewPosition"
    />
  </main>
</template>