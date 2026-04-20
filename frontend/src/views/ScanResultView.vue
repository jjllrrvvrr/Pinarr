<template>
  <main class="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-8 pb-20">
    <div v-if="isLoading" class="text-center py-20 text-[#8b949e]">
      <p>Chargement...</p>
    </div>

    <div v-else-if="error" class="text-center py-20">
      <div class="text-[#f85149] text-xl mb-4">❌</div>
      <p class="text-[#f85149] font-bold text-lg">{{ error }}</p>
      <router-link to="/" class="mt-4 inline-block text-[#58a6ff] hover:underline">
        Retour à l'accueil
      </router-link>
    </div>

    <div v-else-if="physicalBottle" class="space-y-6">
      <!-- Breadcrumb -->
      <div class="flex items-center gap-2 mb-4 sm:mb-6 text-[#8b949e] text-xs sm:text-sm">
        <router-link to="/" class="hover:text-[#58a6ff] truncate">Accueil</router-link>
        <span>/</span>
        <span class="text-white truncate">Bouteille scannée</span>
      </div>

      <!-- Card principale -->
      <div class="bg-[#161b22] rounded-lg sm:rounded-xl border border-[#30363d] overflow-hidden">
        
        <!-- Header avec image et infos -->
        <div class="flex flex-col sm:flex-row">
          <!-- Image à gauche -->
          <div class="w-full sm:w-48 lg:w-64 flex-shrink-0 bg-[#0d1117] border-b sm:border-b-0 sm:border-r border-[#30363d] flex items-center justify-center">
            <div class="p-4 sm:p-6 flex items-center justify-center">
              <div class="relative flex items-center justify-center">
                <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full max-w-[150px] sm:max-w-[180px] max-h-[250px] sm:max-h-[300px] object-contain" />
                <div v-else class="w-32 h-32 sm:w-40 sm:h-40 bg-[#21262d] rounded-lg flex items-center justify-center">
                  <WineBottleIcon :type="bottle.type" :size="80" />
                </div>
              </div>
            </div>
          </div>
          
          <!-- Infos -->
          <div class="flex-1 p-4 sm:p-6">
            <div class="flex flex-wrap items-center gap-x-2 text-xs sm:text-sm text-[#8b949e] mb-2">
              <span class="flex items-center gap-1 text-white">
                <span :class="['w-2 h-2 rounded-full', getTypeBgColor(bottle.type)]"></span>
                {{ bottle.type }}
              </span>
              <span v-if="bottle.year">•</span>
              <span v-if="bottle.year" class="font-mono">{{ bottle.year }}</span>
              <WinePhaseBadge
                v-if="bottle.year"
                :vintage-year="bottle.year"
                :jeunesse-end="bottle.jeunesse_end"
                :maturite-end="bottle.maturite_end"
                :apogee-end="bottle.apogee_end"
              />
            </div>
            
            <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-white leading-tight">{{ bottle.name }}</h1>
            
            <p v-if="bottle.domaine" class="text-[#8b949e] mt-1 text-sm">
              {{ bottle.domaine }}
            </p>

            <!-- Position en cave -->
            <div v-if="position" class="mt-4 p-3 bg-[#0d1117] rounded-lg border border-[#30363d]">
              <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-1">
                <MapPinIcon class="w-4 h-4" />
                Position en cave
              </div>
              <div class="text-white font-medium">
                {{ position.cave_name }} → {{ position.column_name }} → {{ position.row_name }} → {{ position.code }}
              </div>
            </div>

            <div v-else class="mt-4 p-3 bg-[#0d1117] rounded-lg border border-[#30363d]">
              <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-1">
                <MapPinIcon class="w-4 h-4" />
                Emplacement
              </div>
              <div class="text-[#8b949e]">Stock libre (non placé en cave)</div>
            </div>

            <!-- Phases du vin -->
            <div v-if="bottle.year" class="mt-4">
              <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                <ClockIcon class="w-4 h-4" />
                Évolution du vin
              </div>
              <WinePhaseTimeline
                :vintage-year="bottle.year"
                :jeunesse-end="bottle.jeunesse_end"
                :maturite-end="bottle.maturite_end"
                :apogee-end="bottle.apogee_end"
                :editable="false"
                :compact="true"
              />
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="p-4 border-t border-[#30363d] bg-[#0d1117]/50">
          <div v-if="isAuthenticated" class="flex flex-col sm:flex-row gap-3">
            <button 
              @click="removeBottle" 
              :disabled="isProcessing"
              class="flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-white bg-[#f85149] hover:bg-[#da3633] disabled:opacity-50 rounded-lg transition"
            >
              <ArchiveBoxIcon class="w-4 h-4" />
              {{ isProcessing ? 'Traitement...' : 'Retirer de la cave' }}
            </button>

            <button 
              @click="showMoveModal = true"
              :disabled="isProcessing"
              class="flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-[#58a6ff] bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] disabled:opacity-50 rounded-lg transition"
            >
              <ArrowsRightLeftIcon class="w-4 h-4" />
              Déplacer
            </button>

            <router-link 
              :to="`/wine/${bottle.id}`"
              class="flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-[#8b949e] bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] rounded-lg transition"
            >
              <InformationCircleIcon class="w-4 h-4" />
              Voir la fiche complète
            </router-link>
          </div>

          <div v-else class="text-center py-4">
            <p class="text-[#8b949e] mb-3">Connectez-vous pour gérer cette bouteille</p>
            <router-link 
              :to="`/login?redirect=${encodeURIComponent($route.fullPath)}`"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-[#58a6ff] bg-[#21262d] hover:bg-[#30363d] border border-[#58a6ff]/30 rounded-lg transition"
            >
              Se connecter
            </router-link>
          </div>
        </div>
      </div>

      <!-- Détails supplémentaires -->
      <div v-if="bottle.description" class="bg-[#161b22] rounded-lg border border-[#30363d] p-4">
        <h3 class="text-sm font-medium text-[#8b949e] uppercase tracking-wide mb-2">Description</h3>
        <p class="text-white whitespace-pre-wrap">{{ bottle.description }}</p>
      </div>
    </div>

    <!-- Modal de déplacement -->
    <MoveBottleModal
      v-if="showMoveModal"
      :show="showMoveModal"
      :physical-bottle-id="physicalBottle?.id"
      @close="showMoveModal = false"
      @moved="onBottleMoved"
    />
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  MapPinIcon, 
  ArchiveBoxIcon,
  ArrowsRightLeftIcon,
  InformationCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/solid'
import WineBottleIcon from '@/components/WineBottleIcon.vue'
import WinePhaseBadge from '@/components/WinePhaseBadge.vue'
import WinePhaseTimeline from '@/components/WinePhaseTimeline.vue'
import MoveBottleModal from '@/components/MoveBottleModal.vue'
import { QrService } from '../services/qrService.js'
import { apiRequest } from '../services/api.js'
import config from '../config.js'

const route = useRoute()
const router = useRouter()

const isLoading = ref(true)
const error = ref(null)
const physicalBottle = ref(null)
const bottle = ref({})
const position = ref(null)
const isProcessing = ref(false)
const showMoveModal = ref(false)

const isAuthenticated = computed(() => {
  return !!sessionStorage.getItem('auth_token')
})

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  if (path.includes('uploads')) return path
  return `${config.API_BASE_URL}${path}`
}

const getTypeBgColor = (type) => {
  if (type === 'Rouge') return 'bg-[#f85149]'
  if (type === 'Blanc') return 'bg-[#e3b341]'
  if (type === 'Rosé') return 'bg-[#db61a2]'
  if (type === 'Effervescents') return 'bg-[#a371f7]'
  return 'bg-[#8b949e]'
}

const scanQrCode = async () => {
  const qrCode = route.params.qrCode
  if (!qrCode) {
    error.value = 'Code QR manquant'
    isLoading.value = false
    return
  }

  try {
    const data = await QrService.scanQrCode(qrCode)
    physicalBottle.value = data
    bottle.value = data.bottle || {}
    position.value = data.position || null
  } catch (e) {
    console.error('Erreur scan QR:', e)
    error.value = 'Code QR invalide ou bouteille non trouvée'
  } finally {
    isLoading.value = false
  }
}

const removeBottle = async () => {
  if (!confirm('Retirer cette bouteille de la cave ?')) return
  
  isProcessing.value = true
  try {
    await QrService.removeBottle(physicalBottle.value.id)
    alert('Bouteille retirée avec succès')
    router.push('/')
  } catch (e) {
    console.error('Erreur retrait:', e)
    alert('Erreur lors du retrait: ' + e.message)
  } finally {
    isProcessing.value = false
  }
}

const onBottleMoved = () => {
  showMoveModal.value = false
  // Recharger les données
  scanQrCode()
}

onMounted(() => {
  scanQrCode()
})
</script>
