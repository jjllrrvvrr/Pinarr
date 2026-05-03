<template>
  <main class="max-w-7xl mx-auto px-3 sm:px-4 py-4 sm:py-8 pb-20">
    <div v-if="bottle">
      <!-- Breadcrumb -->
      <div class="flex items-center gap-2 mb-4 sm:mb-6 text-gh-text-secondary text-xs sm:text-sm">
        <router-link to="/" class="hover:text-gh-accent truncate">Accueil</router-link>
        <span>/</span>
        <span class="text-gh-text truncate">{{ bottle.name }}</span>
      </div>

      <!-- Card principale -->
      <div class="bg-gh-surface rounded-lg sm:rounded-xl border border-gh-border overflow-hidden">
        
        <!-- SECTION HAUT : Image + Header + Caractéristiques (2 colonnes sur sm+) -->
        <div class="flex flex-col sm:flex-row">
          <!-- Image à gauche -->
          <div class="w-full sm:w-48 lg:w-64 flex-shrink-0 bg-gh-card-image border-b sm:border-b-0 sm:border-r border-gh-border flex items-center justify-center">
            <div class="sm:sticky sm:top-0 p-4 sm:p-6 flex items-center justify-center w-full h-full min-h-[150px] sm:min-h-[250px] lg:min-h-[500px]">
              <div class="relative flex items-center justify-center w-full h-full">
                <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full h-full max-w-[150px] sm:max-w-[180px] lg:max-w-[200px] max-h-[250px] sm:max-h-[300px] lg:max-h-[350px] object-contain" />
                <WineBottleIcon v-else :type="bottle.type" :size="100" class="sm:w-[120px] lg:w-[140px]" />
                <span v-if="bottle.quantity === 0" class="absolute top-0 left-0 bg-gh-accent-red text-gh-text text-xs px-2 sm:px-3 py-0.5 sm:py-1 rounded-full font-medium">Épuisé</span>
              </div>
            </div>
          </div>
          
          <!-- Contenu droite : Header + Caractéristiques -->
          <div class="flex-1">
            <!-- Header Info - Layout compact -->
            <div class="p-3 sm:p-4 border-b border-gh-border">
              <!-- Ligne 1 : Tags -->
              <div class="flex flex-wrap items-center gap-x-2 text-xs sm:text-sm text-gh-text-secondary mb-2">
                <span class="flex items-center gap-1 sm:gap-1.5 text-gh-text">
                  <span :class="['w-1.5 sm:w-2 h-1.5 sm:h-2 rounded-full', getTypeBgColor(bottle.type)]"></span>
                  {{ bottle.type }}
                </span>
                <span v-if="bottle.year" class="text-gh-text-secondary">•</span>
                <span v-if="bottle.year" @click="goToFilter('year', bottle.year)" 
                      class="hover:text-gh-accent cursor-pointer transition font-mono">
                  {{ bottle.year }}
                </span>
                <!-- Badge phase -->
              <WinePhaseBadge
                v-if="bottle.year"
                :vintage-year="bottle.year"
                :jeunesse-end="bottle.jeunesse_end"
                :maturite-end="bottle.maturite_end"
                :apogee-end="bottle.apogee_end"
              />
                <span v-if="bottle.cepage" class="text-gh-text-secondary">•</span>
                <span v-if="bottle.cepage" @click="goToFilter('cepage', bottle.cepage)" 
                      class="hover:text-gh-accent-red cursor-pointer transition">
                  {{ bottle.cepage }}
                </span>
              </div>
              
              <!-- Ligne 2 : Nom -->
              <h1 class="text-xl sm:text-2xl lg:text-3xl font-bold text-gh-text leading-tight">{{ bottle.name }}</h1>
              
              <!-- Ligne 3 : Domaine + Note -->
              <div class="flex flex-wrap items-center gap-x-2 sm:gap-x-4 mt-1">
                <p v-if="bottle.domaine" @click="goToFilter('domaine', bottle.domaine)" 
                   class="text-gh-text-secondary hover:text-gh-accent-gold cursor-pointer transition text-sm">
                  {{ bottle.domaine }}
                </p>
                <div v-if="bottle.rating" class="flex items-center gap-1 text-gh-accent-gold">
                  <StarIconSolid class="w-3 h-3 sm:w-4 sm:h-4" />
                  <span class="font-bold">{{ bottle.rating }}</span>
                  <span class="text-gh-text-secondary text-xs">/5</span>
                </div>
              </div>
            </div>

            <!-- Section ORIGINE & CARACTÉRISTIQUES -->
            <div class="p-3 sm:p-6">
              <h2 class="text-xs uppercase tracking-wider text-gh-text-secondary mb-3 sm:mb-4 font-medium flex items-center gap-2">
                <InfoTagIconSVG class="w-4 h-4" />
                Origine & Caractéristiques
              </h2>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                <!-- Origine -->
                <div v-if="bottle.country || bottle.region" class="bg-gh-bg rounded-lg p-3 sm:p-4 border border-gh-border">
                  <div class="flex items-center gap-1.5 sm:gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
                    <FlagIconSVG class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    Origine
                  </div>
                  <div class="text-gh-text font-medium text-sm">
                    <span v-if="bottle.country" @click="goToFilter('country', bottle.country)" class="hover:text-gh-accent-green-text cursor-pointer transition">{{ bottle.country }}</span>
                    <span v-if="bottle.country && bottle.region" class="text-gh-text-secondary"> - </span>
                    <span v-if="bottle.region" @click="goToFilter('region', bottle.region)" class="hover:text-gh-accent-purple cursor-pointer transition">{{ bottle.region }}</span>
                  </div>
                </div>

                <!-- Cépage -->
                <div v-if="bottle.cepage" class="bg-gh-bg rounded-lg p-3 sm:p-4 border border-gh-border">
                  <div class="flex items-center gap-1.5 sm:gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
                    <GrapeIconSVG class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    Cépage
                  </div>
                  <div @click="goToFilter('cepage', bottle.cepage)" class="text-gh-text font-medium text-sm hover:text-gh-accent-red cursor-pointer transition">{{ bottle.cepage }}</div>
                </div>

                <!-- Alcool -->
                <div v-if="bottle.alcohol" class="bg-gh-bg rounded-lg p-3 sm:p-4 border border-gh-border">
                  <div class="flex items-center gap-1.5 sm:gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
                    <BeakerIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    Alcool
                  </div>
                  <div class="text-gh-text font-medium text-base sm:text-lg">{{ bottle.alcohol }}%</div>
                </div>

                <!-- Contenance -->
                <div v-if="bottle.size" class="bg-gh-bg rounded-lg p-3 sm:p-4 border border-gh-border">
                  <div class="flex items-center gap-1.5 sm:gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
                    <RulerIconSVG class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                    Contenance
                  </div>
                  <div class="text-gh-text font-medium text-base sm:text-lg">{{ bottle.size }}</div>
                </div>

                <!-- NOTE: Les positions sont affichées dans le tableau des bouteilles physiques ci-dessous -->
              </div>
            </div>
          </div>
        </div>

        <!-- SECTION BAS : Stats, Description, Tags, Actions (pleine largeur) -->
        
        <!-- Section STATS RAPIDES -->
        <div class="p-3 sm:p-6 border-t border-gh-border bg-gh-bg/30">
          <h2 class="text-xs uppercase tracking-wider text-gh-text-secondary mb-3 sm:mb-4 font-medium flex items-center gap-2">
            <ChartBarIcon class="w-4 h-4" />
            Stats rapides
          </h2>
          
          <div class="grid gap-2 sm:gap-4" style="grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));">
            <!-- Quantité en cave -->
            <div class="bg-gh-surface rounded-xl p-4 border border-gh-border text-center">
              <div class="flex items-center justify-center gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
                <QuantityIconSVG class="w-4 h-4" />
                En cave
              </div>
              <div class="text-gh-text text-2xl font-bold">{{ cellarCount }}</div>
              <div class="text-gh-text-secondary text-xs mt-1">bouteilles</div>
            </div>

            <!-- Prix -->
            <div v-if="bottle.price" class="bg-gh-surface rounded-xl p-4 border border-gh-border text-center">
              <div class="flex items-center justify-center gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
                <CurrencyDollarIcon class="w-4 h-4" />
                Prix
              </div>
              <div class="text-gh-accent-green-text text-2xl font-bold">{{ bottle.price }} €</div>
            </div>

            <!-- Millésime -->
            <div v-if="bottle.year" class="bg-gh-surface rounded-xl p-4 border border-gh-border text-center">
              <div class="flex items-center justify-center gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-2">
                <CalendarIcon class="w-4 h-4" />
                Millésime
              </div>
              <div class="text-gh-text text-2xl font-bold">{{ bottle.year }}</div>
            </div>

          </div>

          <!-- Timeline des phases - sur sa propre ligne -->
          <div v-if="bottle.year" class="mt-6 bg-gh-surface rounded-xl p-4 border border-gh-border">
            <div class="flex items-center gap-2 text-gh-text-secondary text-xs uppercase tracking-wide mb-3">
              <ClockIcon class="w-4 h-4" />
              Évolution
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

        <!-- Bouteilles physiques (tableau compact) -->
        <div v-if="activePhysicalBottles.length > 0" class="p-3 sm:p-6 border-t border-gh-border">
          <div class="flex items-center justify-between mb-3 sm:mb-4">
            <h2 class="text-xs uppercase tracking-wider text-gh-text-secondary font-medium flex items-center gap-2">
              <QrCodeIcon class="w-4 h-4" />
              Bouteilles physiques ({{ activePhysicalBottles.length }})
            </h2>
            <button
              v-if="activePhysicalBottles.length > 0"
              @click="downloadAllLabels"
              :disabled="isDownloadingLabels"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-gh-accent bg-gh-elevated hover:bg-gh-border border border-gh-border rounded-md transition disabled:opacity-40"
              title="Télécharger toutes les étiquettes (ZIP)"
            >
              <ArchiveBoxIcon v-if="!isDownloadingLabels" class="w-3.5 h-3.5" />
              <span v-else class="w-3.5 h-3.5 inline-block animate-spin rounded-full border-2 border-current border-t-transparent"></span>
              {{ isDownloadingLabels ? 'Génération…' : 'Télécharger toutes' }}
            </button>
          </div>
          <div class="overflow-x-auto border border-gh-border rounded-lg">
            <table class="min-w-[500px] w-full text-sm text-left">
              <thead class="bg-gh-bg text-xs uppercase text-gh-text-secondary">
                <tr>
                  <th class="px-3 py-2.5">Position</th>
                  <th class="px-3 py-2.5">Acquis.</th>
                  <th class="px-3 py-2.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gh-border bg-gh-surface">
                <tr
                  v-for="pb in activePhysicalBottles"
                  :key="pb.id"
                  class="hover:bg-gh-bg/40 transition"
                >
                  <td class="px-3 py-2.5">
                    <div class="flex flex-col gap-0.5">
                      <button
                        v-if="pb.cave_name"
                        @click="goToCaveFromPhysicalBottle(pb)"
                        class="inline-flex items-center gap-1.5 text-xs text-gh-accent hover:underline cursor-pointer"
                        :title="`Cave: ${pb.cave_name} | Colonne: ${pb.column_name || '?'} | Rangée: ${pb.row_name || '?'}`"
                      >
                        <MapPinIcon class="w-3 h-3 flex-shrink-0" />
                        {{ pb.cave_name }} → {{ pb.position_code }}
                      </button>
                      <span v-else class="text-gh-text-secondary text-xs italic">(non placée)</span>
                      <span class="text-[10px] sm:text-sm text-gh-text-secondary/70 font-mono truncate max-w-[200px]">{{ pb.qr_code }}</span>
                    </div>
                  </td>
                  <td class="px-3 py-2.5 text-gh-text-secondary text-xs whitespace-nowrap">
                    {{ formatDate(pb.acquisition_date) }}
                  </td>
                  <td class="px-3 py-2.5 text-right">
                    <div class="inline-flex items-center gap-2">
                      <button
                        @click="openQrPopup(pb)"
                        class="flex items-center justify-center gap-1.5 px-2.5 py-1.5 text-gh-accent bg-gh-elevated hover:bg-gh-border border border-gh-border rounded-md transition text-sm"
                        title="Voir l'étiquette QR"
                      >
                        <QrCodeIcon class="w-4 h-4" />
                        <span class="hidden sm:inline text-xs">QR</span>
                      </button>
                      <button
                        @click="showRemoveConfirm(pb)"
                        class="flex items-center justify-center gap-1.5 px-2.5 py-1.5 text-gh-accent-red bg-gh-accent-red/10 hover:bg-gh-accent-red/20 border border-gh-accent-red/30 rounded-md transition text-sm"
                        title="Retirer (marquer comme consommée)"
                      >
                        <TrashIcon class="w-4 h-4" />
                        <span class="hidden sm:inline text-xs">Retirer</span>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Popup étiquette QR -->
        <div
          v-if="selectedQrBottle"
          class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          @click.self="selectedQrBottle = null"
        >
          <div class="bg-gh-surface rounded-xl border border-gh-border max-w-xs w-full p-5 relative shadow-xl">
            <button
              @click="selectedQrBottle = null"
              class="absolute top-2 right-2 p-1.5 text-gh-text-secondary hover:text-gh-text rounded-md hover:bg-gh-elevated transition"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
            <div class="text-center">
              <h3 class="font-bold text-base text-gh-text mb-0.5">{{ bottle.name }}</h3>
              <p class="text-gh-text-secondary text-xs mb-2">
                {{ bottle.year ? bottle.year + ' • ' : '' }}{{ selectedQrBottle.position_code || selectedQrBottle.qr_code }}
              </p>
              <div class="bg-white rounded-lg p-3 inline-block mb-4 w-fit">
                <qrcode-vue
                  :value="getQrUrl(selectedQrBottle.qr_code)"
                  :size="160"
                  level="H"
                  render-as="canvas"
                />
              </div>
              <button
                @click="downloadSingleLabel(selectedQrBottle)"
                class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-white bg-gh-accent-green hover:bg-gh-accent-green-hover rounded-lg transition"
              >
                <ArrowDownTrayIcon class="w-4 h-4" />
                Télécharger l'étiquette
              </button>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div v-if="bottle.description" class="p-3 sm:p-6 border-t border-gh-border">
          <h2 class="text-xs uppercase tracking-wider text-gh-text-secondary mb-2 sm:mb-3 font-medium flex items-center gap-2">
            <DocumentTextIcon class="w-4 h-4" />
            Description
          </h2>
          <p class="text-gh-text whitespace-pre-wrap leading-relaxed text-xs sm:text-sm bg-gh-bg p-3 sm:p-4 rounded-lg border border-gh-border">{{ bottle.description }}</p>
        </div>

        <!-- Tags -->
        <div v-if="bottle.tags" class="px-3 sm:px-6 py-3 sm:py-4 border-t border-gh-border">
          <h2 class="text-xs uppercase tracking-wider text-gh-text-secondary mb-2 sm:mb-3 font-medium flex items-center gap-2">
            <TagIcon class="w-4 h-4" />
            Tags
          </h2>
          <div class="flex flex-wrap gap-1.5 sm:gap-2">
            <button v-for="tag in bottle.tags.split(',')" :key="tag" @click="goToFilter('tag', tag.trim())" 
                    class="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full text-xs text-gh-text-secondary bg-gh-elevated border border-gh-border hover:text-gh-accent-pink hover:border-gh-accent-pink transition cursor-pointer">
              {{ tag.trim() }}
            </button>
          </div>
        </div>

        <!-- Lien externe -->
        <div v-if="bottle.buy_link" class="px-3 sm:px-6 py-3 sm:py-4 border-t border-gh-border">
          <a :href="bottle.buy_link" target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-gh-accent bg-gh-elevated hover:bg-gh-border border border-gh-border hover:border-gh-accent transition text-xs sm:text-sm">
            <LinkIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            Lien externe
            <ArrowTopRightOnSquareIcon class="w-2.5 h-2.5 sm:w-3 sm:h-3" />
          </a>
        </div>

        <!-- Actions -->
        <div class="p-3 sm:p-4 border-t border-gh-border bg-gh-bg/50 flex flex-col sm:flex-row flex-wrap items-stretch sm:items-center gap-2 sm:gap-3">
          <router-link :to="`/edit/${bottle.id}`" class="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 sm:py-2.5 text-xs sm:text-sm font-medium text-gh-accent bg-gh-elevated hover:bg-gh-border rounded-lg transition border border-gh-border">
            <PencilSquareIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            Modifier
          </router-link>
          <div class="flex-1 hidden sm:block"></div>
          <button @click="deleteBottle" class="flex items-center justify-center gap-2 px-3 sm:px-4 py-2 sm:py-2.5 text-xs sm:text-sm font-medium text-gh-text-secondary hover:text-gh-accent-red hover:bg-gh-border rounded-lg transition border border-gh-border" title="Supprimer">
            <TrashIcon class="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20 text-gh-text-secondary">
      <p>Chargement...</p>
    </div>

  </main>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import { 
  PencilIcon, TrashIcon, MapPinIcon, TagIcon, StarIcon as StarIconSolid, 
  HeartIcon, ShoppingCartIcon, ArrowLeftIcon, QrCodeIcon, PlusIcon, MinusIcon,
  ChevronDownIcon, ChevronUpIcon, ClockIcon, CurrencyDollarIcon,
  ArrowTopRightOnSquareIcon, ChartBarIcon, DocumentTextIcon, LinkIcon,
  PencilSquareIcon, ArchiveBoxIcon, ArrowPathIcon,
  ArrowDownTrayIcon, XMarkIcon
} from '@heroicons/vue/24/solid'
import WineBottleIcon from '@/components/WineBottleIcon.vue'
import RemovePositionModal from '@/components/RemovePositionModal.vue'
import WinePhaseBadge from '@/components/WinePhaseBadge.vue'
import WinePhaseTimeline from '@/components/WinePhaseTimeline.vue'
import {
  FlagIcon as FlagIconSVG,
  GrapeIcon as GrapeIconSVG,
  RulerIcon as RulerIconSVG,
  QuantityIcon as QuantityIconSVG,
  CameraIcon as CameraIconSVG,
  CommentIcon as CommentIconSVG,
  WineIcon as WineIconSVG,
  LandscapeIcon as LandscapeIconSVG,
  CrestIcon as CrestIconSVG,
  InfoTagIcon as InfoTagIconSVG,
  LabelIcon as LabelIconSVG
} from '@/components/icons'
import {
  CalendarIcon, MapIcon, BeakerIcon
} from '@heroicons/vue/24/outline'
import { apiRequest } from '../services/api.js'
import config from '../config.js'
import { QrService } from '../services/qrService.js'

const route = useRoute()
const router = useRouter()
const emit = defineEmits(['refresh-data'])

const bottle = ref(null)
const physicalBottles = ref([])
const isLoading = ref(false)
const selectedQrBottle = ref(null)
const isDownloadingLabels = ref(false)

const API_URL = '/bottles'

const activePhysicalBottles = computed(() => {
  return physicalBottles.value.filter(pb => pb.status === 'in_cellar')
})

const cellarCount = computed(() => {
  return activePhysicalBottles.value.filter(pb => pb.position_code).length
})

const qrValue = computed(() => {
    const pb = physicalBottles.value.find(pb => pb.status === 'in_cellar')
    return pb ? `${window.location.origin}/bottle/${pb.qr_code}` : ''
})

const getQrUrl = (qrCode) => {
  return `${window.location.origin}/bottle/${qrCode}`
}

const showRemoveConfirm = async (pb) => {
  if (!confirm(`Retirer la bouteille ${pb.qr_code} ? Son statut sera changé en « consommée ».`)) return
  try {
    await QrService.removeBottle(pb.id)
    pb.status = 'consumed'
    await fetchPhysicalBottles()
    emit('refresh-data')
  } catch (e) {
    console.error('Erreur retrait:', e)
    alert('Erreur lors du retrait: ' + e.message)
  }
}

const openQrPopup = (pb) => {
  selectedQrBottle.value = pb
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  if (isNaN(d)) return dateStr.slice(0, 10)
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

// Route vers la cave via les infos de la bouteille physique
const goToCaveFromPhysicalBottle = (pb) => {
  // La position complète est dans pb avec cave_name, column_name, row_name
  if (pb.cave_name) {
    router.push(`/caves/${encodeURIComponent(pb.cave_name.toLowerCase().replace(/\s+/g, '-'))}`)
  }
}

const fetchBottle = async () => {
  const id = route.params.id
  if (!id) return
  try {
    bottle.value = await apiRequest(`${API_URL}/${id}`)
    // Récupérer les bouteilles physiques
    await fetchPhysicalBottles()
  } catch (e) {
    console.error('Erreur:', e)
  }
}

const fetchPhysicalBottles = async () => {
  if (!bottle.value) return
  try {
    const data = await QrService.getPhysicalBottles(bottle.value.id)
    physicalBottles.value = data.physical_bottles || []
  } catch (e) {
    console.error('Erreur chargement bouteilles physiques:', e)
  }
}

watch(() => route.params.id, () => {
  fetchBottle()
}, { immediate: true })

const downloadSingleLabel = async (pb) => {
  if (!bottle.value) return
  try {
    const token = sessionStorage.getItem('auth_token')
    const response = await fetch(
      `${config.API_BASE_URL}/bottles/${bottle.value.id}/physical-bottles/${pb.qr_code}/label`,
      {
        method: 'GET',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      }
    )
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Erreur génération PDF')
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const safeName = (bottle.value.name || 'Vin')
      .replace(/[^a-zA-Z0-9]/g, '_')
      .substring(0, 25)
    a.download = `Etiquette_${safeName}_${pb.qr_code}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Erreur DL étiquette:', e)
    alert('Erreur lors du téléchargement : ' + e.message)
  }
}

const downloadAllLabels = async () => {
  if (!bottle.value) return
  isDownloadingLabels.value = true
  try {
    const token = sessionStorage.getItem('auth_token')
    const response = await fetch(
      `${config.API_BASE_URL}/bottles/${bottle.value.id}/batch-labels`,
      {
        method: 'GET',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      }
    )
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Erreur génération ZIP')
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const safeName = (bottle.value.name || 'Vin')
      .replace(/[^a-zA-Z0-9]/g, '_')
      .substring(0, 25)
    a.download = `Etiquettes_${safeName}.zip`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Erreur DL labels:', e)
    alert('Erreur lors du téléchargement : ' + e.message)
  } finally {
    isDownloadingLabels.value = false
  }
}

const deleteBottle = async () => {
  if (confirm(`Supprimer "${bottle.value.name}" ?`)) {
    try {
      await apiRequest(`${API_URL}/${route.params.id}`, {
        method: 'DELETE'
      })
      emit('refresh-data')
      router.push('/')
    } catch (e) {
      console.error('Erreur lors de la suppression:', e)
    }
  }
}

const goToFilter = (key, value) => {
  router.push(`/?${key}=${encodeURIComponent(value)}`)
}

const goToCavePosition = (pos) => {
  router.push(`/caves/${pos.cave_id}?column=${pos.column_name}&row=${pos.row_name}&position=${pos.code}`)
}

import { useWineTypeStyles } from '@/composables/useWineTypeStyles.js'

const { getTypeBgClass } = useWineTypeStyles()

const getTypeBgColor = (type) => {
  return getTypeBgClass(type)
}

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  if (path.includes('uploads')) return path
  return `${config.API_BASE_URL}${path}`
}

onMounted(() => {
  fetchBottle()
})
</script>