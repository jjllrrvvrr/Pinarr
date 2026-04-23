<template>
  <main class="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-8 pb-20">
    <div v-if="isLoading" class="text-center py-20 text-gh-text-secondary">
      <p>Chargement...</p>
    </div>

    <div v-else-if="error" class="text-center py-20">
      <div class="text-gh-accent-red text-xl mb-4">❌</div>
      <p class="text-gh-accent-red font-bold text-lg">{{ error }}</p>
      <router-link to="/" class="mt-4 inline-block text-gh-accent hover:underline">
        Retour à l'accueil
      </router-link>
    </div>

    <div v-else-if="physicalBottle" class="space-y-6">
      <!-- Breadcrumb (retiré pour passants) -->
      <div class="flex items-center gap-2 mb-4 sm:mb-6 text-gh-text-secondary text-xs sm:text-sm">
        <router-link to="/" class="hover:text-gh-accent truncate">Accueil</router-link>
        <span>/</span>
        <span class="text-gh-text truncate">Bouteille scannée</span>
      </div>

      <!-- Card principale -->
      <div class="bg-gh-surface rounded-lg sm:rounded-xl border border-gh-border overflow-hidden">
        <!-- Header avec image et infos -->
        <div class="flex flex-col sm:flex-row">
          <!-- Image -->
          <div class="w-full sm:w-48 lg:w-64 flex-shrink-0 bg-gh-bg border-b sm:border-b-0 sm:border-r border-gh-border flex items-center justify-center">
            <div class="p-4 sm:p-6 flex items-center justify-center">
              <div class="relative flex items-center justify-center">
                <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full max-w-[150px] sm:max-w-[180px] max-h-[250px] sm:max-h-[300px] object-contain" />
                <div v-else class="w-32 h-32 sm:w-40 sm:h-40 bg-gh-elevated rounded-lg flex items-center justify-center">
                  <WineBottleIcon :type="bottle.type" :size="80" />
                </div>
              </div>
            </div>
          </div>
          <!-- Infos -->
          <div class="flex-1 p-4 sm:p-6">
            <div class="flex flex-wrap items-center gap-x-2 text-xs sm:text-sm text-gh-text-secondary mb-2">
              <span v-if="bottle.type" class="flex items-center gap-1 text-gh-text">
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

            <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gh-text leading-tight">{{ bottle.name }}</h1>
            <p v-if="bottle.domaine" class="text-gh-text-secondary mt-1 text-sm">{{ bottle.domaine }}</p>

            <!-- Status -->
            <div class="mt-3">
              <span v-if="physicalBottle.status === 'in_cellar'"
                    class="inline-flex items-center gap-1.5 text-xs font-medium text-gh-accent-green-text bg-gh-accent-green/20 px-2.5 py-1 rounded-full">
                <span class="w-1.5 h-1.5 rounded-full bg-gh-accent-green"></span>
                En cave
              </span>
              <span v-else
                    class="inline-flex items-center gap-1.5 text-xs font-medium text-gh-accent-red bg-gh-accent-red/20 px-2.5 py-1 rounded-full">
                <span class="w-1.5 h-1.5 rounded-full bg-gh-accent-red"></span>
                Déjà consommée
              </span>
            </div>

            <!-- Position en cave -->
            <div v-if="position" class="mt-4 p-3 bg-gh-bg rounded-lg border border-gh-border">
              <div class="flex items-center gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-1">
                <MapPinIcon class="w-4 h-4" />
                Position en cave
              </div>
              <div class="text-gh-text font-medium text-sm">
                {{ position.cave_name }} → {{ position.column_name }} → {{ position.row_name }} → {{ position.code }}
              </div>
            </div>
            <div v-else class="mt-4 p-3 bg-gh-bg rounded-lg border border-gh-border">
              <div class="flex items-center gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-1">
                <MapPinIcon class="w-4 h-4" />
                Emplacement
              </div>
              <div class="text-gh-text-secondary text-sm">Stock libre (non placé en cave)</div>
            </div>

            <!-- Phases du vin -->
            <div v-if="bottle.year" class="mt-4">
              <div class="flex items-center gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
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

        <!-- Description -->
        <div v-if="bottle.description" class="px-4 sm:px-6 py-3 border-t border-gh-border bg-gh-bg/30">
          <h3 class="text-xs font-medium text-gh-text-secondary uppercase tracking-wide mb-1">Description</h3>
          <p class="text-gh-text text-sm whitespace-pre-wrap">{{ bottle.description }}</p>
        </div>

        <!-- Actions — accessibles à tous (passants) -->
        <div class="p-4 border-t border-gh-border bg-gh-bg/50">
          <div v-if="physicalBottle.status === 'in_cellar'" class="flex flex-col gap-3">
            <button
              @click="showDetail = !showDetail"
              class="flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-gh-accent bg-gh-elevated hover:bg-gh-border border border-gh-border rounded-lg transition"
            >
              <InformationCircleIcon class="w-4 h-4" />
              {{ showDetail ? 'Masquer les détails' : 'Voir les informations' }}
            </button>

            <button
              @click="removeBottle"
              :disabled="isProcessing"
              class="flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium text-white bg-gh-accent-red hover:bg-gh-accent-red disabled:opacity-50 rounded-lg transition"
            >
              <ArchiveBoxIcon class="w-4 h-4" />
              {{ isProcessing ? 'Traitement...' : 'Retirer de la cave' }}
            </button>
          </div>

          <div v-else class="text-center py-4 text-sm text-gh-text-secondary">
            Cette bouteille a été retirée de la cave.
          </div>
        </div>
      </div>

      <!-- Détails étendus (déroulés par le bouton) -->
      <div v-if="showDetail && physicalBottle.status === 'in_cellar'" class="bg-gh-surface rounded-lg border border-gh-border p-4 space-y-3">
        <h3 class="text-sm font-medium text-gh-text-secondary uppercase tracking-wide">Caractéristiques</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
          <div v-if="bottle.cepage"><span class="text-gh-text-secondary">Cépage :</span> <span class="text-gh-text">{{ bottle.cepage }}</span></div>
          <div v-if="bottle.region"><span class="text-gh-text-secondary">Région :</span> <span class="text-gh-text">{{ bottle.region }}</span></div>
          <div v-if="bottle.country"><span class="text-gh-text-secondary">Pays :</span> <span class="text-gh-text">{{ bottle.country }}</span></div>
          <div v-if="bottle.alcohol"><span class="text-gh-text-secondary">Alcool :</span> <span class="text-gh-text">{{ bottle.alcohol }} %</span></div>
          <div v-if="bottle.size"><span class="text-gh-text-secondary">Volume :</span> <span class="text-gh-text">{{ bottle.size }}</span></div>
          <div v-if="bottle.price"><span class="text-gh-text-secondary">Prix :</span> <span class="text-gh-text">{{ bottle.price.toFixed(2) }} €</span></div>
          <div v-if="bottle.rating"><span class="text-gh-text-secondary">Note :</span> <span class="text-gh-text">{{ bottle.rating }} / 5</span></div>
          <div v-if="bottle.buy_link"><a :href="bottle.buy_link" target="_blank" class="text-gh-accent hover:underline">Lien d'achat</a></div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { 
  MapPinIcon, 
  ArchiveBoxIcon,
  InformationCircleIcon,
  ClockIcon
} from '@heroicons/vue/24/solid'
import WineBottleIcon from '@/components/WineBottleIcon.vue'
import WinePhaseBadge from '@/components/WinePhaseBadge.vue'
import WinePhaseTimeline from '@/components/WinePhaseTimeline.vue'
import { QrService } from '../services/qrService.js'
import config from '../config.js'

const route = useRoute()

const isLoading = ref(true)
const error = ref(null)
const physicalBottle = ref(null)
const bottle = ref({})
const position = ref(null)
const isProcessing = ref(false)
const showDetail = ref(false)

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  if (path.includes('uploads')) return path
  return `${config.API_BASE_URL}${path}`
}

import { useWineTypeStyles } from '@/composables/useWineTypeStyles.js'

const { getTypeBgClass } = useWineTypeStyles()

const getTypeBgColor = (type) => {
  return getTypeBgClass(type)
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
    await scanQrCode()   // recharger les données (statut devient "consumed")
  } catch (e) {
    console.error('Erreur retrait:', e)
    alert('Erreur lors du retrait: ' + e.message)
  } finally {
    isProcessing.value = false
  }
}

onMounted(() => {
  scanQrCode()
})
</script>
