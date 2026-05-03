<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { 
  PlusIcon, XMarkIcon, HomeIcon, TrashIcon, MapIcon, CubeIcon, Bars3Icon
} from '@heroicons/vue/24/solid'
import { useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import config from './config.js'
import AuthService from './services/AuthService.js'
import RemovePositionModal from './components/RemovePositionModal.vue'

import { useTheme } from './composables/useTheme.js'

const router = useRouter()

const { theme, setTheme } = useTheme()

const API_URL = `${config.API_BASE_URL}/bottles`
const API_LOCATIONS_URL = `${config.API_BASE_URL}/caves`

const bottles = ref([])
const storageLocations = ref([])
const isQRModalOpen = ref(false)
const isLocationModalOpen = ref(false)
const isEditingLocation = ref(false)
const currentBottleQR = ref(null)
const selectedLocationId = ref(null)

const defaultLocationForm = { id: null, name: '' }
const locationForm = ref({ ...defaultLocationForm })

// User menu state
const isUserMenuOpen = ref(false)
const isChangePasswordModalOpen = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const passwordError = ref('')
const passwordSuccess = ref('')

const username = computed(() => AuthService.getUsername() || 'Utilisateur')

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

const closeUserMenu = () => {
  isUserMenuOpen.value = false
}

const openChangePasswordModal = () => {
  isChangePasswordModalOpen.value = true
  passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
  passwordError.value = ''
  passwordSuccess.value = ''
  closeUserMenu()
}

const closeChangePasswordModal = () => {
  isChangePasswordModalOpen.value = false
}

const changePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = 'Les mots de passe ne correspondent pas'
    return
  }
  
  try {
    await AuthService.changePassword(passwordForm.value.oldPassword, passwordForm.value.newPassword)
    passwordSuccess.value = 'Mot de passe modifié avec succès. Vous allez être déconnecté.'
    setTimeout(async () => {
      await logout()
    }, 2000)
  } catch (err) {
    passwordError.value = err.message || 'Échec du changement de mot de passe'
  }
}

const logout = async () => {
  await AuthService.logout()
  router.push('/login')
}

// Username change state
const isChangeUsernameModalOpen = ref(false)
const newUsername = ref('')
const usernameError = ref('')
const usernameSuccess = ref('')

const openChangeUsernameModal = () => {
  isChangeUsernameModalOpen.value = true
  // Attendre le prochain tick pour que le DOM soit prêt
  nextTick(() => {
    newUsername.value = username.value || ''
  })
  usernameError.value = ''
  usernameSuccess.value = ''
  closeUserMenu()
}

const closeChangeUsernameModal = () => {
  isChangeUsernameModalOpen.value = false
}

const changeUsername = async () => {
  usernameError.value = ''
  usernameSuccess.value = ''
  
  const usernameValue = newUsername.value
  
  if (!usernameValue || usernameValue.trim() === '') {
    usernameError.value = 'Le nom d\'utilisateur ne peut pas être vide'
    return
  }
  
  if (usernameValue === username.value) {
    usernameError.value = 'Le nouveau nom doit être différent'
    return
  }
  
  try {
    await AuthService.updateUsername(usernameValue.trim())
    usernameSuccess.value = 'Nom d\'utilisateur modifié avec succès'
    setTimeout(() => {
      window.location.reload()
    }, 1500)
  } catch (err) {
    usernameError.value = err.message || 'Échec du changement de nom'
  }
}

const fetchBottles = async () => {
  try {
    const res = await fetch(API_URL, {
      headers: {
        'Authorization': `Bearer ${sessionStorage.getItem('auth_token') || ''}`
      }
    })
    if (res.ok) bottles.value = await res.json()
  } catch (e) { console.error("Erreur connexion:", e) }
}

const fetchStorageLocations = async () => {
  // Fonctionnalité désactivée - le système de locations a été remplacé par le système de caves
  storageLocations.value = []
}

watch(() => router.currentRoute.value.path, (newPath) => {
  if (newPath === '/' || newPath === '/map') {
    fetchBottles()
    // fetchStorageLocations() - Désactivé
  }
})

const deleteBottle = async (id) => {
  try { 
    await fetch(`${API_URL}/${id}`, { 
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${sessionStorage.getItem('auth_token') || ''}`
      }
    }); 
    fetchBottles() 
  }
  catch (e) { console.error(e) }
}

const updateQuantity = async (id, newQuantity) => {
  if (newQuantity < 0) return

  // Trouver la bouteille concernée
  const bottle = bottles.value.find(b => b.id === id)
  if (!bottle) return

  // Quantité réelle = cellar_quantity (physical_bottles en cave)
  const oldQuantity = bottle.cellar_quantity || 0

  // Si diminution ET positions existent, utiliser le modal
  if (newQuantity < oldQuantity && bottle.positions?.length > 0) {
    const diff = oldQuantity - newQuantity
    const positionsToRemoveCount = Math.min(diff, bottle.positions.length)

    // Ouvrir le modal et attendre la réponse
    const result = await openRemovePositionModal(bottle, positionsToRemoveCount)

    if (!result) {
      // Annulation - ne rien faire
      return
    }
  }

  // Mettre à jour la quantité
  try {
    const res = await fetch(`${API_URL}/${id}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionStorage.getItem('auth_token') || ''}`
      },
      body: JSON.stringify({ quantity: newQuantity })
    })
    if (res.ok) fetchBottles()
  } catch (e) { console.error(e) }
}

// État pour le modal de retrait
const showRemoveModal = ref(false)
const currentBottleForModal = ref(null)
const positionsToRemove = ref(0)
const positionsRemoved = ref(0)
const selectedPositionId = ref(null)
const isProcessing = ref(false)
let resolveModalPromise = null

const openRemovePositionModal = (bottle, count) => {
  return new Promise((resolve) => {
    currentBottleForModal.value = bottle
    positionsToRemove.value = count
    positionsRemoved.value = 0
    selectedPositionId.value = null
    showRemoveModal.value = true
    resolveModalPromise = resolve
  })
}

const confirmRemovePosition = async () => {
  if (!selectedPositionId.value || !currentBottleForModal.value) return
  
  isProcessing.value = true
  try {
    await fetch(`${config.API_BASE_URL}/positions/${selectedPositionId.value}/bottle`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${sessionStorage.getItem('auth_token') || ''}`
      }
    })
    
    // Retirer la position localement
    currentBottleForModal.value.positions = currentBottleForModal.value.positions.filter(
      p => p.id !== selectedPositionId.value
    )
    
    positionsRemoved.value++
    selectedPositionId.value = null
    
    if (positionsRemoved.value >= positionsToRemove.value) {
      showRemoveModal.value = false
      if (resolveModalPromise) {
        resolveModalPromise(true)
        resolveModalPromise = null
      }
    }
  } catch (e) {
    console.error('Erreur:', e)
    alert('Erreur lors du retrait')
  } finally {
    isProcessing.value = false
  }
}

const cancelRemove = () => {
  showRemoveModal.value = false
  if (resolveModalPromise) {
    resolveModalPromise(false)
    resolveModalPromise = null
  }
}

const selectPosition = (positionId) => {
  selectedPositionId.value = positionId
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
  // Fonctionnalité désactivée - utiliser le système de caves à la place
  alert("Cette fonctionnalité est désactivée. Utilisez le système de caves.")
  closeLocationModal()
}

const deleteLocation = async (id) => {
  // Fonctionnalité désactivée - utiliser le système de caves à la place
  alert("Cette fonctionnalité est désactivée. Utilisez le système de caves.")
}

const qrValue = computed(() => {
    if (!currentBottleQR.value) return ''
    const pb = currentBottleQR.value.physical_bottles?.find(pb => pb.status === 'in_cellar')
    return pb ? `${window.location.origin}/bottle/${pb.qr_code}` : `${window.location.origin}/wine/${currentBottleQR.value.id}`
})

const totalBottles = computed(() => bottles.value.reduce((acc, b) => acc + (b.cellar_quantity || 0), 0))
const totalValue = computed(() => bottles.value.reduce((acc, b) => acc + ((b.price || 0) * (b.cellar_quantity || 0)), 0).toFixed(2))

// Close user menu when clicking outside
const handleClickOutside = (event) => {
  const userMenu = document.querySelector('.user-menu-container')
  if (userMenu && !userMenu.contains(event.target)) {
    isUserMenuOpen.value = false
  }
}

onMounted(() => {
  fetchBottles()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

</script>

<template>
  <div class="min-h-screen bg-gh-bg text-gh-text-secondary font-sans selection:bg-gh-accent/30">
    
    <header class="sticky top-0 z-40 bg-gh-header backdrop-blur-md border-b border-gh-border">
      <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <!-- User Menu -->
          <div class="relative user-menu-container">
            <button 
              @click="toggleUserMenu" 
              class="flex items-center text-gh-text-secondary hover:text-gh-text transition p-1 rounded hover:bg-gh-elevated"
            >
              <Bars3Icon class="w-5 h-5" />
            </button>
            
            <!-- Dropdown Menu -->
            <div 
              v-if="isUserMenuOpen" 
              class="absolute left-0 top-full mt-2 w-56 bg-gh-surface border border-gh-border rounded-md shadow-2xl py-1 z-50"
            >
              <div class="px-4 py-3 border-b border-gh-border">
                <p class="text-sm font-medium text-gh-text">{{ username }}</p>
                <p class="text-xs text-gh-text-secondary">Connecté</p>
              </div>
              <button 
                @click="openChangePasswordModal"
                class="w-full text-left px-4 py-2 text-sm text-gh-text-secondary hover:bg-gh-elevated hover:text-gh-text transition"
              >
                Changer mot de passe
              </button>
              <button 
                @click="openChangeUsernameModal"
                class="w-full text-left px-4 py-2 text-sm text-gh-text-secondary hover:bg-gh-elevated hover:text-gh-text transition"
              >
                Changer nom d'utilisateur
              </button>
              <div class="border-t border-gh-border my-1"></div>
              <div class="px-4 py-2 text-xs font-semibold text-gh-text-secondary uppercase tracking-wider">
                Thème
              </div>
              <button
                v-for="t in [
                  { key: 'champagne', label: 'Clair' },
                  { key: 'champagne-dark', label: 'Sombre' }
                ]"
                :key="t.key"
                @click="setTheme(t.key)"
                class="w-full text-left px-4 py-2 text-sm text-gh-text-secondary hover:bg-gh-elevated hover:text-gh-text transition flex items-center justify-between"
                :class="{ 'bg-gh-elevated text-gh-text': theme === t.key }"
              >
                <span>{{ t.label }}</span>
                <span v-if="theme === t.key" class="text-gh-accent-green-text">✓</span>
              </button>
              <div class="border-t border-gh-border my-1"></div>
              <button 
                @click="logout"
                class="w-full text-left px-4 py-2 text-sm text-gh-accent-red hover:bg-gh-elevated hover:text-gh-accent-red/70 transition"
              >
                Se déconnecter
              </button>
            </div>
          </div>
          
          <router-link to="/" class="flex items-center gap-2">
            <span class="text-2xl sm:text-3xl">🍷</span>
            <h1 class="text-lg sm:text-xl font-bold text-gh-text" style="font-family: 'Beth Ellen', cursive;">Pinaar</h1>
          </router-link>
        </div>
        
        <div class="flex flex-col md:flex-row items-center gap-1 md:gap-6 mr-2 md:mr-4">
          <div class="text-center">
            <div class="text-[10px] sm:text-xs md:text-[10px] font-bold text-gh-text-secondary uppercase tracking-wider">Bouteilles</div>
            <div class="text-xs md:text-lg font-bold text-gh-accent-green-text leading-tight">{{ totalBottles }}</div>
          </div>
          <div class="hidden md:block w-px h-8 bg-gh-border"></div>
          <div class="text-center">
            <div class="text-[10px] sm:text-xs md:text-[10px] font-bold text-gh-text-secondary uppercase tracking-wider">Valeur</div>
            <div class="text-xs md:text-lg font-bold text-gh-accent-green-text leading-tight">{{ totalValue }} €</div>
          </div>
        </div>
        
        <nav class="flex gap-2 sm:gap-4 items-center">
          <router-link to="/" class="hidden sm:flex items-center gap-2 text-gh-text-secondary hover:text-gh-text transition px-3 py-2 rounded-md hover:bg-gh-elevated">
            <HomeIcon class="w-5 h-5" /> <span>Accueil</span>
          </router-link>
          <router-link to="/caves" class="hidden sm:flex items-center gap-2 text-gh-text-secondary hover:text-gh-text transition px-3 py-2 rounded-md hover:bg-gh-elevated">
            <CubeIcon class="w-5 h-5" /> <span>Cave</span>
          </router-link>
          <router-link to="/map" class="hidden sm:flex items-center gap-2 text-gh-text-secondary hover:text-gh-text transition px-3 py-2 rounded-md hover:bg-gh-elevated">
            <MapIcon class="w-5 h-5" /> <span>Carte</span>
          </router-link>
          <div class="sm:hidden flex gap-1">
            <router-link to="/" class="p-2 text-gh-text-secondary hover:text-gh-text rounded-md hover:bg-gh-elevated">
              <HomeIcon class="w-5 h-5" />
            </router-link>
            <router-link to="/caves" class="p-2 text-gh-text-secondary hover:text-gh-text rounded-md hover:bg-gh-elevated">
              <CubeIcon class="w-5 h-5" />
            </router-link>
            <router-link to="/map" class="p-2 text-gh-text-secondary hover:text-gh-text rounded-md hover:bg-gh-elevated">
              <MapIcon class="w-5 h-5" />
            </router-link>
          </div>
          <router-link to="/add" class="flex items-center gap-1 sm:gap-2 bg-gh-accent-green hover:bg-gh-accent-green-hover text-white px-3 sm:px-4 py-2 rounded-md font-medium transition border border-gh-accent-green">
            <PlusIcon class="w-5 h-5" /> <span class="hidden sm:inline">Ajouter</span>
          </router-link>
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
      <div class="bg-gh-surface w-full max-w-md rounded-md shadow-2xl border border-gh-border animate-fade-in">
        <div class="flex justify-between items-center p-4 border-b border-gh-border">
          <h2 class="text-lg font-bold text-gh-text">{{ isEditingLocation ? 'Modifier' : 'Nouvel' }} emplacement</h2>
          <button @click="closeLocationModal" class="text-gh-text-secondary hover:text-gh-text transition p-1"><XMarkIcon class="w-5 h-5" /></button>
        </div>
        <div class="p-4">
          <label class="block text-xs font-bold text-gh-text-secondary uppercase mb-1">Nom *</label>
          <input v-model="locationForm.name" class="w-full bg-gh-bg border border-gh-border rounded-md p-2 text-gh-text focus:border-gh-border-active outline-none text-sm" placeholder="ex: Cave Principale">
        </div>
        <div class="p-4 border-t border-gh-border flex justify-end gap-3">
          <button @click="closeLocationModal" class="px-4 py-2 rounded-md text-gh-text-secondary hover:bg-gh-elevated transition font-medium border border-gh-border">Annuler</button>
          <button @click="saveLocation" class="px-4 py-2 rounded-md bg-gh-accent-green hover:bg-gh-accent-green-hover text-gh-text font-medium transition">Enregistrer</button>
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

    <!-- Change Password Modal -->
    <div v-if="isChangePasswordModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click.self="closeChangePasswordModal">
      <div class="bg-gh-surface w-full max-w-md rounded-md shadow-2xl border border-gh-border animate-fade-in">
        <div class="flex justify-between items-center p-4 border-b border-gh-border">
          <h2 class="text-lg font-bold text-gh-text">Changer le mot de passe</h2>
          <button @click="closeChangePasswordModal" class="text-gh-text-secondary hover:text-gh-text transition p-1">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        
        <div class="p-4 space-y-4">
          <!-- Error Message -->
          <div v-if="passwordError" class="rounded-md bg-red-50 p-3 border border-red-200">
            <p class="text-sm text-red-800">{{ passwordError }}</p>
          </div>
          
          <!-- Success Message -->
          <div v-if="passwordSuccess" class="rounded-md bg-green-50 p-3 border border-green-200">
            <p class="text-sm text-green-800">{{ passwordSuccess }}</p>
          </div>
          
          <div>
            <label class="block text-xs font-bold text-gh-text-secondary uppercase mb-1">Ancien mot de passe</label>
            <input 
              v-model="passwordForm.oldPassword" 
              type="password"
              class="w-full bg-gh-bg border border-gh-border rounded-md p-2 text-gh-text focus:border-gh-border-active outline-none text-sm" 
              placeholder="Votre mot de passe actuel"
            >
          </div>
          
          <div>
            <label class="block text-xs font-bold text-gh-text-secondary uppercase mb-1">Nouveau mot de passe</label>
            <input 
              v-model="passwordForm.newPassword" 
              type="password"
              class="w-full bg-gh-bg border border-gh-border rounded-md p-2 text-gh-text focus:border-gh-border-active outline-none text-sm" 
              placeholder="Nouveau mot de passe"
            >
          </div>
          
          <div>
            <label class="block text-xs font-bold text-gh-text-secondary uppercase mb-1">Confirmer le nouveau mot de passe</label>
            <input 
              v-model="passwordForm.confirmPassword" 
              type="password"
              class="w-full bg-gh-bg border border-gh-border rounded-md p-2 text-gh-text focus:border-gh-border-active outline-none text-sm" 
              placeholder="Confirmez le nouveau mot de passe"
            >
          </div>
        </div>
        
        <div class="p-4 border-t border-gh-border flex justify-end gap-3">
          <button 
            @click="closeChangePasswordModal" 
            class="px-4 py-2 rounded-md text-gh-text-secondary hover:bg-gh-elevated transition font-medium border border-gh-border"
          >
            Annuler
          </button>
          <button 
            @click="changePassword" 
            class="px-4 py-2 rounded-md bg-gh-accent-green hover:bg-gh-accent-green-hover text-gh-text font-medium transition"
          >
            Enregistrer
          </button>
        </div>
      </div>
    </div>

    <!-- Change Username Modal -->
    <div v-if="isChangeUsernameModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click.self="closeChangeUsernameModal">
      <div class="bg-gh-surface w-full max-w-md rounded-md shadow-2xl border border-gh-border animate-fade-in">
        <div class="flex justify-between items-center p-4 border-b border-gh-border">
          <h2 class="text-lg font-bold text-gh-text">Changer le nom d'utilisateur</h2>
          <button @click="closeChangeUsernameModal" class="text-gh-text-secondary hover:text-gh-text transition p-1">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
        
        <div class="p-4 space-y-4">
          <!-- Error Message -->
          <div v-if="usernameError" class="rounded-md bg-red-50 p-3 border border-red-200">
            <p class="text-sm text-red-800">{{ usernameError }}</p>
          </div>
          
          <!-- Success Message -->
          <div v-if="usernameSuccess" class="rounded-md bg-green-50 p-3 border border-green-200">
            <p class="text-sm text-green-800">{{ usernameSuccess }}</p>
          </div>
          
          <div>
            <label class="block text-xs font-bold text-gh-text-secondary uppercase mb-1">Nouveau nom d'utilisateur</label>
            <input 
              v-model="newUsername" 
              type="text"
              class="w-full bg-gh-bg border border-gh-border rounded-md p-2 text-gh-text focus:border-gh-border-active outline-none text-sm" 
              placeholder="Nouveau nom d'utilisateur"
            >
          </div>
        </div>
        
        <div class="p-4 border-t border-gh-border flex justify-end gap-3">
          <button 
            @click="closeChangeUsernameModal" 
            class="px-4 py-2 rounded-md text-gh-text-secondary hover:bg-gh-elevated transition font-medium border border-gh-border"
          >
            Annuler
          </button>
          <button 
            @click="changeUsername" 
            class="px-4 py-2 rounded-md bg-gh-accent-green hover:bg-gh-accent-green-hover text-gh-text font-medium transition"
          >
            Enregistrer
          </button>
        </div>
      </div>
    </div>

  </div>

  <!-- Modal de retrait des positions -->
  <RemovePositionModal
    :show="showRemoveModal"
    :total="positionsToRemove"
    :removed="positionsRemoved"
    :selected="selectedPositionId"
    :positions="currentBottleForModal?.positions || []"
    :processing="isProcessing"
    :bottle="currentBottleForModal"
    @select="selectPosition"
    @confirm="confirmRemovePosition"
    @cancel="cancelRemove"
  />
</template>

<style>
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
</style>