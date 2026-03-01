<template>
  <main class="max-w-5xl mx-auto px-4 py-8 pb-20">
    <div v-if="bottle">
      <!-- Breadcrumb -->
      <div class="flex items-center gap-2 mb-6 text-[#8b949e] text-sm">
        <router-link to="/" class="hover:text-[#58a6ff]">Accueil</router-link>
        <span>/</span>
        <span class="text-white truncate">{{ bottle.name }}</span>
      </div>

      <!-- Card principale -->
      <div class="bg-[#161b22] rounded-xl border border-[#30363d] overflow-hidden">
        
        <!-- SECTION HAUT : Image + Header + Caractéristiques (2 colonnes) -->
        <div class="flex flex-col sm:flex-row">
          <!-- Image à gauche sticky -->
          <div class="w-full sm:w-64 flex-shrink-0 bg-[#0d1117] border-b sm:border-b-0 sm:border-r border-[#30363d] flex items-center justify-center">
            <div class="sm:sticky sm:top-0 p-6 flex items-center justify-center w-full h-full min-h-[300px] sm:min-h-[500px]">
              <div class="relative flex items-center justify-center w-full h-full">
                <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full h-full max-w-[200px] max-h-[350px] object-contain" />
                <WineBottleIcon v-else :type="bottle.type" :size="140" />
                <span v-if="bottle.quantity === 0" class="absolute top-0 left-0 bg-[#f85149] text-white text-xs px-3 py-1 rounded-full font-medium">Épuisé</span>
              </div>
            </div>
          </div>
          
          <!-- Contenu droite : Header + Caractéristiques -->
          <div class="flex-1">
            <!-- Header Info - Layout compact -->
            <div class="p-4 border-b border-[#30363d]">
              <!-- Ligne 1 : Tags sans fond -->
              <div class="flex flex-wrap items-center gap-x-2 text-sm text-[#8b949e] mb-2">
                <span class="flex items-center gap-1.5 text-white">
                  <span :class="['w-2 h-2 rounded-full', getTypeBgColor(bottle.type)]"></span>
                  {{ bottle.type }}
                </span>
                <span v-if="bottle.year" class="text-[#8b949e]">•</span>
                <span v-if="bottle.year" @click="goToFilter('year', bottle.year)" 
                      class="hover:text-[#58a6ff] cursor-pointer transition font-mono">
                  {{ bottle.year }}
                </span>
                <span v-if="bottle.cepage" class="text-[#8b949e]">•</span>
                <span v-if="bottle.cepage" @click="goToFilter('cepage', bottle.cepage)" 
                      class="hover:text-[#f85149] cursor-pointer transition">
                  {{ bottle.cepage }}
                </span>
              </div>
              
              <!-- Ligne 2 : Nom -->
              <h1 class="text-2xl sm:text-3xl font-bold text-white leading-tight">{{ bottle.name }}</h1>
              
              <!-- Ligne 3 : Domaine + Note -->
              <div class="flex flex-wrap items-center gap-x-4 mt-1">
                <p v-if="bottle.domaine" @click="goToFilter('domaine', bottle.domaine)" 
                   class="text-[#8b949e] hover:text-[#e3b341] cursor-pointer transition">
                  {{ bottle.domaine }}
                </p>
                <div v-if="bottle.rating" class="flex items-center gap-1 text-[#e3b341]">
                  <StarIconSolid class="w-4 h-4" />
                  <span class="font-bold">{{ bottle.rating }}</span>
                  <span class="text-[#8b949e] text-xs">/5</span>
                </div>
              </div>
            </div>

            <!-- Section ORIGINE & CARACTÉRISTIQUES -->
            <div class="p-6">
              <h2 class="text-xs uppercase tracking-wider text-[#8b949e] mb-4 font-medium flex items-center gap-2">
                <InfoTagIcon class="w-4 h-4" />
                Origine & Caractéristiques
              </h2>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <!-- Origine -->
                <div v-if="bottle.country || bottle.region" class="bg-[#0d1117] rounded-lg p-4 border border-[#30363d]">
                  <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                    <FlagIcon class="w-4 h-4" />
                    Origine
                  </div>
                  <div class="text-white font-medium">
                    <span v-if="bottle.country" @click="goToFilter('country', bottle.country)" class="hover:text-[#3fb950] cursor-pointer transition">{{ bottle.country }}</span>
                    <span v-if="bottle.country && bottle.region" class="text-[#8b949e]"> - </span>
                    <span v-if="bottle.region" @click="goToFilter('region', bottle.region)" class="hover:text-[#a371f7] cursor-pointer transition">{{ bottle.region }}</span>
                  </div>
                </div>

                <!-- Cépage -->
                <div v-if="bottle.cepage" class="bg-[#0d1117] rounded-lg p-4 border border-[#30363d]">
                  <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                    <GrapeIcon class="w-4 h-4" />
                    Cépage
                  </div>
                  <div @click="goToFilter('cepage', bottle.cepage)" class="text-white font-medium hover:text-[#f85149] cursor-pointer transition">{{ bottle.cepage }}</div>
                </div>

                <!-- Alcool -->
                <div v-if="bottle.alcohol" class="bg-[#0d1117] rounded-lg p-4 border border-[#30363d]">
                  <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                    <ThermometerIcon class="w-4 h-4" />
                    Alcool
                  </div>
                  <div class="text-white font-medium text-lg">{{ bottle.alcohol }}%</div>
                </div>

                <!-- Contenance -->
                <div v-if="bottle.size" class="bg-[#0d1117] rounded-lg p-4 border border-[#30363d]">
                  <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                    <RulerIcon class="w-4 h-4" />
                    Contenance
                  </div>
                  <div class="text-white font-medium text-lg">{{ bottle.size }}</div>
                </div>

                <!-- Positions en cave -->
                <div v-if="bottle.positions && bottle.positions.length > 0" class="bg-[#0d1117] rounded-lg p-4 border border-[#30363d] sm:col-span-2">
                  <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-3">
                    <MapPinIcon class="w-4 h-4" />
                    Positions en cave ({{ bottle.positions.length }})
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <button 
                      v-for="pos in bottle.positions" 
                      :key="pos.id"
                      @click="goToCavePosition(pos)"
                      class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-[#58a6ff] bg-[#21262d] hover:bg-[#30363d] border border-[#58a6ff]/30 hover:border-[#58a6ff] transition-all cursor-pointer group"
                      :title="`Cave: ${pos.cave_name} | Colonne: ${pos.column_name} | Rangée: ${pos.row_name}`"
                    >
                      <MapPinIcon class="w-4 h-4" />
                      <span>{{ pos.code }}</span>
                      <ArrowTopRightOnSquareIcon class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </button>
                  </div>
                </div>

                <!-- Emplacement texte -->
                <div v-else-if="bottle.location" class="bg-[#0d1117] rounded-lg p-4 border border-[#30363d]">
                  <div class="flex items-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                    <MapPinIcon class="w-4 h-4" />
                    Emplacement
                  </div>
                  <div class="text-white font-medium">{{ bottle.location }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- SECTION BAS : Stats, Description, Tags, Actions (pleine largeur) -->
        
        <!-- Section STATS RAPIDES -->
        <div class="p-6 border-t border-[#30363d] bg-[#0d1117]/30">
          <h2 class="text-xs uppercase tracking-wider text-[#8b949e] mb-4 font-medium flex items-center gap-2">
            <ChartBarIcon class="w-4 h-4" />
            Stats rapides
          </h2>
          
          <div class="grid gap-4" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
            <!-- Quantité -->
            <div class="bg-[#161b22] rounded-xl p-4 border border-[#30363d] text-center">
              <div class="flex items-center justify-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                <QuantityIcon class="w-4 h-4" />
                Quantité
              </div>
              <div class="flex items-center justify-center gap-3">
                <button @click="updateQty(bottle.quantity - 1)" class="w-8 h-8 flex items-center justify-center text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded-lg transition border border-[#30363d]">−</button>
                <span class="text-white text-2xl font-bold">{{ bottle.quantity }}</span>
                <button @click="updateQty(bottle.quantity + 1)" class="w-8 h-8 flex items-center justify-center text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded-lg transition border border-[#30363d]">+</button>
              </div>
            </div>

            <!-- Prix -->
            <div v-if="bottle.price" class="bg-[#161b22] rounded-xl p-4 border border-[#30363d] text-center">
              <div class="flex items-center justify-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                <CurrencyIcon class="w-4 h-4" />
                Prix
              </div>
              <div class="text-[#3fb950] text-2xl font-bold">{{ bottle.price }} €</div>
            </div>

            <!-- Année -->
            <div v-if="bottle.year" class="bg-[#161b22] rounded-xl p-4 border border-[#30363d] text-center">
              <div class="flex items-center justify-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                <CalendarIcon class="w-4 h-4" />
                Année
              </div>
              <div class="text-white text-2xl font-bold">{{ bottle.year }}</div>
            </div>

            <!-- Apogée -->
            <div v-if="bottle.apogee_start || bottle.apogee_end" class="bg-[#161b22] rounded-xl p-4 border border-[#30363d] text-center">
              <div class="flex items-center justify-center gap-2 text-[#8b949e] text-xs uppercase tracking-wide mb-2">
                <CalendarIcon class="w-4 h-4" />
                Apogée
              </div>
              <div class="text-white text-xl font-bold">
                {{ bottle.apogee_start || '?' }}{{ bottle.apogee_end && bottle.apogee_end !== bottle.apogee_start ? ` - ${bottle.apogee_end}` : '' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Description -->
        <div v-if="bottle.description" class="p-6 border-t border-[#30363d]">
          <h2 class="text-xs uppercase tracking-wider text-[#8b949e] mb-3 font-medium flex items-center gap-2">
            <DocumentTextIcon class="w-4 h-4" />
            Description
          </h2>
          <p class="text-white whitespace-pre-wrap leading-relaxed text-sm bg-[#0d1117] p-4 rounded-lg border border-[#30363d]">{{ bottle.description }}</p>
        </div>

        <!-- Tags -->
        <div v-if="bottle.tags" class="px-6 py-4 border-t border-[#30363d]">
          <h2 class="text-xs uppercase tracking-wider text-[#8b949e] mb-3 font-medium flex items-center gap-2">
            <TagIcon class="w-4 h-4" />
            Tags
          </h2>
          <div class="flex flex-wrap gap-2">
            <button v-for="tag in bottle.tags.split(',')" :key="tag" @click="goToFilter('tag', tag.trim())" 
                    class="px-3 py-1.5 rounded-full text-xs text-[#8b949e] bg-[#21262d] border border-[#30363d] hover:text-[#db61a2] hover:border-[#db61a2] transition cursor-pointer">
              {{ tag.trim() }}
            </button>
          </div>
        </div>

        <!-- Lien externe -->
        <div v-if="bottle.buy_link" class="px-6 py-4 border-t border-[#30363d]">
          <a :href="bottle.buy_link" target="_blank" rel="noopener" class="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-[#58a6ff] bg-[#21262d] hover:bg-[#30363d] border border-[#30363d] hover:border-[#58a6ff] transition text-sm">
            <LinkIcon class="w-4 h-4" />
            Lien externe
            <ArrowTopRightOnSquareIcon class="w-3 h-3" />
          </a>
        </div>

        <!-- Actions -->
        <div class="p-4 border-t border-[#30363d] bg-[#0d1117]/50 flex flex-wrap items-center gap-3">
          <router-link :to="`/edit/${bottle.id}`" class="flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-[#58a6ff] bg-[#21262d] hover:bg-[#30363d] rounded-lg transition border border-[#30363d]">
            <PencilSquareIcon class="w-4 h-4" />
            Modifier
          </router-link>
          <button v-if="bottle.quantity > 0" @click="archiveBottle" class="flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-[#f85149] bg-[#21262d] hover:bg-[#30363d] rounded-lg transition border border-[#30363d]">
            <ArchiveBoxIcon class="w-4 h-4" />
            Archiver
          </button>
          <button v-else @click="restoreBottle" class="flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-[#3fb950] bg-[#21262d] hover:bg-[#30363d] rounded-lg transition border border-[#30363d]">
            <ArrowPathIcon class="w-4 h-4" />
            Restaurer
          </button>
          <div class="flex-1"></div>
          <button @click="showQRModal = true" class="flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-[#8b949e] hover:text-white bg-[#21262d] hover:bg-[#30363d] rounded-lg transition border border-[#30363d]" title="QR Code">
            <QrCodeIcon class="w-4 h-4" />
            QR Code
          </button>
          <button @click="deleteBottle" class="flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-[#8b949e] hover:text-[#f85149] hover:bg-[#30363d] rounded-lg transition border border-[#30363d]" title="Supprimer">
            <TrashIcon class="w-4 h-4" />
            Supprimer
          </button>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-20 text-[#8b949e]">
      <p>Chargement...</p>
    </div>

    <div v-if="showQRModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click="showQRModal = false">
      <div class="bg-white p-8 rounded-md text-center shadow-2xl" @click.stop>
        <QrcodeVue :value="qrValue" :size="200" level="H" />
        <p class="font-bold text-lg text-gray-900 mt-4">{{ bottle?.name }}</p>
        <p class="text-gray-500 text-sm">{{ bottle?.year }} - {{ bottle?.type }}</p>
        <button @click="showQRModal = false" class="mt-4 text-sm text-[#58a6ff] hover:underline">Fermer</button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import { 
  QrCodeIcon, PencilSquareIcon, StarIcon as StarIconSolid, 
  ArrowTopRightOnSquareIcon, TrashIcon, LinkIcon,
  ArchiveBoxIcon, ArrowPathIcon, MapPinIcon, ChartBarIcon, DocumentTextIcon, TagIcon
} from '@heroicons/vue/24/solid'
import WineBottleIcon from '@/components/WineBottleIcon.vue'
import {
  FlagIcon, LandscapeIcon, ThermometerIcon, RulerIcon,
  CalendarIcon, GrapeIcon, CurrencyIcon, QuantityIcon, InfoTagIcon
} from '../components/icons'
import { apiRequest } from '../services/api.js'
import config from '../config.js'

const route = useRoute()
const router = useRouter()
const emit = defineEmits(['refresh-data'])

const bottle = ref(null)
const showQRModal = ref(false)

const API_URL = '/bottles'

const qrValue = computed(() => bottle.value ? `${window.location.origin}/wine/${bottle.value.id}` : '')

const fetchBottle = async () => {
  const id = route.params.id
  if (!id) return
  try {
    bottle.value = await apiRequest(`${API_URL}/${id}`)
  } catch (e) {
    console.error('Erreur:', e)
  }
}

watch(() => route.params.id, () => {
  fetchBottle()
}, { immediate: true })

const updateQty = async (qty) => {
  if (qty < 0) return
  try {
    await apiRequest(`${API_URL}/${route.params.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ quantity: qty })
    })
    bottle.value.quantity = qty
    emit('refresh-data')
  } catch (e) {
    console.error(e)
  }
}

const archiveBottle = async () => {
  await updateQty(0)
}

const restoreBottle = async () => {
  await updateQty(1)
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

const getTypeBgColor = (type) => {
  if (type === 'Rouge') return 'bg-[#f85149]'
  if (type === 'Blanc') return 'bg-[#e3b341]'
  if (type === 'Rosé') return 'bg-[#db61a2]'
  if (type === 'Champagne') return 'bg-[#a371f7]'
  return 'bg-[#8b949e]'
}

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  if (path.startsWith('/uploads/')) return path
  return `${config.API_BASE_URL}${path}`
}

onMounted(() => {
  fetchBottle()
})
</script>