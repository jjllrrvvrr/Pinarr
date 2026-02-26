<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { 
  PlusIcon, XMarkIcon, HomeIcon, TrashIcon, MapIcon, CubeIcon
} from '@heroicons/vue/24/solid'
import { useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'

const router = useRouter()

const API_URL = 'http://127.0.0.1:8000/bottles'
const API_LOCATIONS_URL = 'http://127.0.0.1:8000/locations'

const bottles = ref([])
const storageLocations = ref([])
const isQRModalOpen = ref(false)
const isLocationModalOpen = ref(false)
const isEditingLocation = ref(false)
const currentBottleQR = ref(null)
const selectedLocationId = ref(null)

const defaultLocationForm = { id: null, name: '' }
const locationForm = ref({ ...defaultLocationForm })

const fetchBottles = async () => {
  try {
    const res = await fetch(API_URL)
    if (res.ok) bottles.value = await res.json()
  } catch (e) { console.error("Erreur connexion:", e) }
}

const fetchStorageLocations = async () => {
  try {
    const res = await fetch(`${API_LOCATIONS_URL}`)
    if (res.ok) {
      const data = await res.json()
      storageLocations.value = [...data]
      if (!selectedLocationId.value && storageLocations.value.length > 0) {
        selectedLocationId.value = storageLocations.value[0].id
      }
    }
  } catch (e) { console.error("Erreur récupération emplacements:", e) }
}

watch(() => router.currentRoute.value.path, (newPath) => {
  if (newPath === '/' || newPath === '/map') {
    fetchBottles()
    fetchStorageLocations()
  }
})

const deleteBottle = async (id) => {
  if (!confirm("Voulez-vous vraiment supprimer cette bouteille ?")) return
  try { await fetch(`${API_URL}/${id}`, { method: 'DELETE' }); fetchBottles() }
  catch (e) { console.error(e) }
}

const updateQuantity = async (id, newQuantity) => {
  if (newQuantity < 0) return
  try {
    const res = await fetch(`${API_URL}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quantity: newQuantity })
    })
    if (res.ok) fetchBottles()
  } catch (e) { console.error(e) }
}

const openLocationModal = (location = null) => {
  if (location && location.id) {
    locationForm.value = { id: location.id, name: location.name }
    isEditingLocation.value = true
  } else {
    locationForm.value = { ...defaultLocationForm }
    isEditingLocation.value = false
  }
  isLocationModalOpen.value = true
}

const closeLocationModal = () => {
  isLocationModalOpen.value = false
  locationForm.value = { ...defaultLocationForm }
  isEditingLocation.value = false
}

const saveLocation = async () => {
  if (!locationForm.value.name) return alert("Le nom est obligatoire")
  try {
    const method = isEditingLocation.value ? 'PUT' : 'POST'
    const url = isEditingLocation.value ? `${API_LOCATIONS_URL}/${locationForm.value.id}` : API_LOCATIONS_URL
    const res = await fetch(url, {
      method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: locationForm.value.name })
    })
    if (res.ok) { closeLocationModal(); fetchStorageLocations() }
    else { const txt = await res.text(); alert("Erreur: " + txt) }
  } catch (e) { alert("Erreur réseau: " + e.message) }
}

const deleteLocation = async (id) => {
  if (!confirm("Supprimer cet emplacement et toutes ses étagères ?")) return
  try { await fetch(`${API_LOCATIONS_URL}/${id}`, { method: 'DELETE' }); fetchStorageLocations() }
  catch (e) { console.error(e) }
}

const qrValue = computed(() => currentBottleQR.value ? `${window.location.origin}/wine/${currentBottleQR.value.id}` : '')

const totalBottles = computed(() => bottles.value.reduce((acc, b) => acc + (b.quantity || 0), 0))
const totalValue = computed(() => bottles.value.reduce((acc, b) => acc + ((b.price || 0) * (b.quantity || 0)), 0).toFixed(2))

onMounted(() => { fetchBottles(); fetchStorageLocations() })

</script>

<template>
  <div class="min-h-screen bg-[#0d1117] text-gray-300 font-sans selection:bg-[#58a6ff]/30">
    
    <header class="sticky top-0 z-40 bg-[#0d1117]/90 backdrop-blur-md border-b border-[#30363d]">
      <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-2">
          <span class="text-2xl sm:text-3xl">🍷</span>
          <h1 class="text-lg sm:text-xl font-bold text-white">SudoWine</h1>
        </router-link>
        
        <div class="hidden md:flex items-center gap-6 mr-4">
          <div class="text-center">
            <div class="text-[10px] font-bold text-[#8b949e] uppercase tracking-wider">Bouteilles</div>
            <div class="text-lg font-bold text-white leading-tight">{{ totalBottles }}</div>
          </div>
          <div class="w-px h-8 bg-[#30363d]"></div>
          <div class="text-center">
            <div class="text-[10px] font-bold text-[#8b949e] uppercase tracking-wider">Valeur</div>
            <div class="text-lg font-bold text-[#3fb950] leading-tight">{{ totalValue }} €</div>
          </div>
        </div>
        
        <nav class="flex gap-2 sm:gap-4 items-center">
          <router-link to="/" class="hidden sm:flex items-center gap-2 text-gray-400 hover:text-white transition px-3 py-2 rounded-md hover:bg-[#21262d]">
            <HomeIcon class="w-5 h-5" /> <span>Accueil</span>
          </router-link>
          <router-link to="/caves" class="hidden sm:flex items-center gap-2 text-gray-400 hover:text-white transition px-3 py-2 rounded-md hover:bg-[#21262d]">
            <CubeIcon class="w-5 h-5" /> <span>Cave</span>
          </router-link>
          <router-link to="/map" class="hidden sm:flex items-center gap-2 text-gray-400 hover:text-white transition px-3 py-2 rounded-md hover:bg-[#21262d]">
            <MapIcon class="w-5 h-5" /> <span>Carte</span>
          </router-link>
          <router-link to="/add" class="flex items-center gap-1 sm:gap-2 bg-[#238636] hover:bg-[#2ea043] text-white px-3 sm:px-4 py-2 rounded-md font-medium transition border border-[#238636]">
            <PlusIcon class="w-5 h-5" /> <span class="hidden sm:inline">Ajouter</span>
          </router-link>
          <div class="sm:hidden flex gap-1">
            <router-link to="/" class="p-2 text-gray-400 hover:text-white rounded-md hover:bg-[#21262d]">
              <HomeIcon class="w-5 h-5" />
            </router-link>
          </div>
        </nav>
      </div>
    </header>

    <router-view 
      :bottles="bottles"
      :storageLocations="storageLocations"
      @delete-bottle="deleteBottle"
      @update-quantity="updateQuantity"
      @show-qr="(bottle) => { currentBottleQR = bottle; isQRModalOpen = true }"
      @open-location-modal="openLocationModal"
      @delete-location="deleteLocation"
      @refresh-data="() => { fetchBottles(); fetchStorageLocations() }"
      v-model:selectedLocationId="selectedLocationId"
    />

    <div v-if="isLocationModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click.self="closeLocationModal">
      <div class="bg-[#161b22] w-full max-w-md rounded-md shadow-2xl border border-[#30363d] animate-fade-in">
        <div class="flex justify-between items-center p-4 border-b border-[#30363d]">
          <h2 class="text-lg font-bold text-white">{{ isEditingLocation ? 'Modifier' : 'Nouvel' }} emplacement</h2>
          <button @click="closeLocationModal" class="text-[#8b949e] hover:text-white transition p-1"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <div class="p-4">
          <label class="block text-xs font-bold text-[#8b949e] uppercase mb-1">Nom *</label>
          <input v-model="locationForm.name" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="ex: Cave Principale">
        </div>
        <div class="p-4 border-t border-[#30363d] flex justify-end gap-3">
          <button @click="closeLocationModal" class="px-4 py-2 rounded-md text-[#8b949e] hover:bg-[#21262d] transition font-medium border border-[#30363d]">Annuler</button>
          <button @click="saveLocation" class="px-4 py-2 rounded-md bg-[#238636] hover:bg-[#2ea043] text-white font-medium transition">Enregistrer</button>
        </div>
      </div>
    </div>

    <div v-if="isQRModalOpen" class="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center p-4" @click="isQRModalOpen=false">
      <div class="bg-white p-8 rounded-md text-center shadow-2xl animate-fade-in" @click.stop>
        <div class="mb-4">
           <QrcodeVue :value="qrValue" :size="220" level="H" />
        </div>
        <p class="font-bold text-xl text-gray-900 mb-1">{{ currentBottleQR?.name }}</p>
        <p class="text-gray-500 text-sm">{{ currentBottleQR?.year }} - {{ currentBottleQR?.type }}</p>
        <button @click="isQRModalOpen=false" class="mt-6 text-sm text-gray-400 hover:text-gray-600 underline">Fermer</button>
      </div>
    </div>

  </div>
</template>

<style>
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
</style>