<template>
  <main class="max-w-5xl mx-auto px-4 py-8 pb-20">
    <div v-if="bottle">
      <div class="flex items-center gap-2 mb-6 text-[#8b949e] text-sm">
        <router-link to="/" class="hover:text-[#58a6ff]">Accueil</router-link>
        <span>/</span>
        <span class="text-white truncate">{{ bottle.name }}</span>
      </div>

      <div class="bg-[#161b22] rounded-md border border-[#30363d] overflow-hidden flex flex-col sm:flex-row">
        
        <div class="w-full sm:w-48 flex-shrink-0 bg-[#0d1117] flex items-center justify-center sm:border-r border-b sm:border-b-0 border-[#30363d] min-h-[200px] sm:min-h-0 relative">
          <img v-if="bottle.image_path" :src="getImageUrl(bottle.image_path)" :alt="bottle.name" class="w-full h-full object-contain" />
          <WineBottleIcon v-else :type="bottle.type" :size="96" />
          <span v-if="bottle.quantity === 0" class="absolute top-2 left-2 bg-[#f85149] text-white text-xs px-2 py-0.5 rounded">Épuisé</span>
        </div>
        
        <div class="flex-1 flex flex-col">
          <div class="p-4 border-b border-[#30363d]">
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span class="inline-flex items-center gap-1.5">
                <span :class="['w-2 h-2 rounded-full', getTypeBgColor(bottle.type)]"></span>
                <span class="text-xs text-white font-medium">{{ bottle.type }}</span>
              </span>
              <span class="text-[#8b949e] text-xs">•</span>
              <span v-if="bottle.cepage" @click="goToFilter('cepage', bottle.cepage)" 
                    class="text-xs text-[#8b949e] hover:text-[#f85149] cursor-pointer transition">{{ bottle.cepage }}</span>
              <span v-if="bottle.cepage" class="text-[#8b949e] text-xs">•</span>
              <span @click="goToFilter('year', bottle.year)" 
                    class="text-xs text-white font-mono hover:text-[#58a6ff] cursor-pointer transition">{{ bottle.year }}</span>
            </div>
            <h1 class="text-xl sm:text-2xl font-bold text-white mb-1">{{ bottle.name }}</h1>
            <p v-if="bottle.domaine" @click="goToFilter('domaine', bottle.domaine)" 
               class="text-[#8b949e] hover:text-[#e3b341] cursor-pointer transition">{{ bottle.domaine }}</p>
          </div>

          <div class="p-4 grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm border-b border-[#30363d]">
            <div v-if="bottle.country">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Pays</div>
              <div @click="goToFilter('country', bottle.country)" 
                   class="text-white font-medium hover:text-[#3fb950] cursor-pointer transition">{{ bottle.country }}</div>
            </div>
            <div v-if="bottle.region">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Région</div>
              <div @click="goToFilter('region', bottle.region)" 
                   class="text-white font-medium hover:text-[#a371f7] cursor-pointer transition">{{ bottle.region }}</div>
            </div>
            <div v-if="bottle.alcohol">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Alcool</div>
              <div class="text-white font-medium">{{ bottle.alcohol }}%</div>
            </div>
            <div v-if="bottle.size">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Contenance</div>
              <div class="text-white font-medium">{{ bottle.size }}</div>
            </div>
            <div v-if="bottle.apogee_start || bottle.apogee_end">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Apogée</div>
              <div class="text-white font-medium">
                {{ bottle.apogee_start || '?' }}{{ bottle.apogee_end && bottle.apogee_end !== bottle.apogee_start ? ` - ${bottle.apogee_end}` : '' }}
              </div>
            </div>
            <div v-if="bottle.position">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Position</div>
              <div class="text-white font-medium">{{ bottle.position.code }}</div>
            </div>
            <div v-else-if="bottle.location">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Emplacement</div>
              <div class="text-white font-medium">{{ bottle.location }}</div>
            </div>
            <div v-if="bottle.cepage">
              <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-1">Cépage</div>
              <div @click="goToFilter('cepage', bottle.cepage)" 
                   class="text-white font-medium hover:text-[#f85149] cursor-pointer transition">{{ bottle.cepage }}</div>
            </div>
          </div>

          <div class="p-4 bg-[#0d1117]/50 flex items-center justify-between">
            <div class="flex items-center gap-6">
              <div>
                <div class="text-[#8b949e] text-xs uppercase tracking-wide">Quantité</div>
                <div class="flex items-center gap-2">
                  <button @click="updateQty(bottle.quantity - 1)" class="w-6 h-6 flex items-center justify-center text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded transition">−</button>
                  <span class="text-white text-lg font-bold">{{ bottle.quantity }}</span>
                  <button @click="updateQty(bottle.quantity + 1)" class="w-6 h-6 flex items-center justify-center text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded transition">+</button>
                </div>
              </div>
              <div v-if="bottle.price">
                <div class="text-[#8b949e] text-xs uppercase tracking-wide">Prix</div>
                <div class="text-[#3fb950] text-lg font-bold">{{ bottle.price }} €</div>
              </div>
              <div v-if="bottle.rating">
                <div class="text-[#8b949e] text-xs uppercase tracking-wide">Note</div>
                <div class="flex items-center gap-1 text-[#e3b341]">
                  <StarIconSolid class="w-4 h-4" />
                  <span class="font-bold">{{ bottle.rating }}/5</span>
                </div>
              </div>
            </div>
            <button @click="showQRModal = true" class="p-2 text-[#8b949e] hover:text-white hover:bg-[#21262d] rounded-md transition border border-[#30363d]" title="QR Code">
              <QrCodeIcon class="w-5 h-5" />
            </button>
          </div>

          <div v-if="bottle.description" class="p-4 border-t border-[#30363d]">
            <div class="text-[#8b949e] text-xs uppercase tracking-wide mb-2">Description</div>
            <p class="text-white whitespace-pre-wrap leading-relaxed text-sm">{{ bottle.description }}</p>
          </div>

          <div v-if="bottle.tags" class="px-4 py-3 border-t border-[#30363d]">
            <div class="flex flex-wrap gap-2">
              <button v-for="tag in bottle.tags.split(',')" :key="tag" @click="goToFilter('tag', tag.trim())" 
                      class="px-2 py-0.5 rounded text-xs text-[#8b949e] bg-[#21262d] hover:text-[#db61a2] transition cursor-pointer">
                {{ tag.trim() }}
              </button>
            </div>
          </div>

          <div v-if="bottle.buy_link" class="px-4 py-3 border-t border-[#30363d]">
            <a :href="bottle.buy_link" target="_blank" rel="noopener" class="inline-flex items-center gap-2 text-[#58a6ff] hover:underline text-sm">
              <LinkIcon class="w-4 h-4" />
              Lien externe
              <ArrowTopRightOnSquareIcon class="w-3 h-3" />
            </a>
          </div>

          <div class="p-3 border-t border-[#30363d] mt-auto flex items-center gap-2">
            <router-link :to="`/edit/${bottle.id}`" class="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-[#58a6ff] bg-[#21262d] hover:bg-[#30363d] rounded-md transition border border-[#30363d]">
              <PencilSquareIcon class="w-4 h-4" />
              Modifier
            </router-link>
            <button v-if="bottle.quantity > 0" @click="archiveBottle" class="flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-[#f85149] bg-[#21262d] hover:bg-[#30363d] rounded-md transition border border-[#30363d]">
              <ArchiveBoxIcon class="w-4 h-4" />
              Archiver
            </button>
            <button v-else @click="restoreBottle" class="flex items-center justify-center gap-2 px-3 py-2 text-xs font-medium text-[#3fb950] bg-[#21262d] hover:bg-[#30363d] rounded-md transition border border-[#30363d]">
              <ArrowPathIcon class="w-4 h-4" />
              Restaurer
            </button>
          </div>
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
  ArchiveBoxIcon, ArrowPathIcon
} from '@heroicons/vue/24/solid'
import WineBottleIcon from '@/components/WineBottleIcon.vue'

const route = useRoute()
const router = useRouter()

const bottle = ref(null)
const showQRModal = ref(false)

const API_URL = 'http://127.0.0.1:8000/bottles'

const qrValue = computed(() => bottle.value ? `${window.location.origin}/wine/${bottle.value.id}` : '')

const fetchBottle = async () => {
  const id = route.params.id
  if (!id) return
  try {
    const res = await fetch(`${API_URL}/${id}`)
    if (res.ok) {
      bottle.value = await res.json()
    }
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
    const res = await fetch(`${API_URL}/${route.params.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity: qty })
    })
    if (res.ok) {
      bottle.value.quantity = qty
    }
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

const goToFilter = (key, value) => {
  router.push(`/?${key}=${encodeURIComponent(value)}`)
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
  return `http://127.0.0.1:8000${path}`
}

onMounted(() => {
  fetchBottle()
})
</script>