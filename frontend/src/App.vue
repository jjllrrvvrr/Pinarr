<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { 
  PlusIcon, XMarkIcon, HomeIcon, TrashIcon, MapIcon, CubeIcon, Bars3Icon
} from '@heroicons/vue/24/solid'
import { useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import config from './config.js'
import AuthService from './services/AuthService.js'

const router = useRouter()

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
  
  console.log('DEBUG: newUsername.value =', JSON.stringify(usernameValue))
  console.log('DEBUG: typeof newUsername.value =', typeof usernameValue)
  
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
  if (!confirm("Voulez-vous vraiment supprimer cette bouteille ?")) return
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

const qrValue = computed(() => currentBottleQR.value ? `${window.location.origin}/wine/${currentBottleQR.value.id}` : '')

const totalBottles = computed(() => bottles.value.reduce((acc, b) => acc + (b.quantity || 0), 0))
const totalValue = computed(() => bottles.value.reduce((acc, b) => acc + ((b.price || 0) * (b.quantity || 0)), 0).toFixed(2))

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
  <div class="min-h-screen bg-[#0d1117] text-gray-300 font-sans selection:bg-[#58a6ff]/30">
    
    <header class="sticky top-0 z-40 bg-[#020408] backdrop-blur-md border-b border-[#30363d]">
      <div class="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <!-- User Menu -->
          <div class="relative user-menu-container">
            <button 
              @click="toggleUserMenu" 
              class="flex items-center text-gray-400 hover:text-white transition p-1 rounded hover:bg-[#21262d]"
            >
              <Bars3Icon class="w-5 h-5" />
            </button>
            
            <!-- Dropdown Menu -->
            <div 
              v-if="isUserMenuOpen" 
              class="absolute left-0 top-full mt-2 w-56 bg-[#161b22] border border-[#30363d] rounded-md shadow-2xl py-1 z-50"
            >
              <div class="px-4 py-3 border-b border-[#30363d]">
                <p class="text-sm font-medium text-white">{{ username }}</p>
                <p class="text-xs text-[#8b949e]">Connecté</p>
              </div>
              <button 
                @click="openChangePasswordModal"
                class="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#21262d] hover:text-white transition"
              >
                Changer mot de passe
              </button>
              <button 
                @click="openChangeUsernameModal"
                class="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-[#21262d] hover:text-white transition"
              >
                Changer nom d'utilisateur
              </button>
              <div class="border-t border-[#30363d]"></div>
              <button 
                @click="logout"
                class="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-[#21262d] hover:text-red-300 transition"
              >
                Se déconnecter
              </button>
            </div>
          </div>
          
          <router-link to="/" class="flex items-center gap-2">
            <span class="text-2xl sm:text-3xl">🍷</span>
            <h1 class="text-lg sm:text-xl font-bold text-white">Pinarr</h1>
          </router-link>
        </div>
        
        <div class="flex flex-col md:flex-row items-center gap-1 md:gap-6 mr-2 md:mr-4">
          <div class="text-center">
            <div class="text-[8px] md:text-[10px] font-bold text-[#8b949e] uppercase tracking-wider">Bouteilles</div>
            <div class="text-xs md:text-lg font-bold text-white leading-tight">{{ totalBottles }}</div>
          </div>
          <div class="hidden md:block w-px h-8 bg-[#30363d]"></div>
          <div class="text-center">
            <div class="text-[8px] md:text-[10px] font-bold text-[#8b949e] uppercase tracking-wider">Valeur</div>
            <div class="text-xs md:text-lg font-bold text-[#3fb950] leading-tight">{{ totalValue }} €</div>
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
          <div class="sm:hidden flex gap-1">
            <router-link to="/" class="p-2 text-gray-400 hover:text-white rounded-md hover:bg-[#21262d]">
              <HomeIcon class="w-5 h-5" />
            </router-link>
            <router-link to="/caves" class="p-2 text-gray-400 hover:text-white rounded-md hover:bg-[#21262d]">
              <CubeIcon class="w-5 h-5" />
            </router-link>
            <router-link to="/map" class="p-2 text-gray-400 hover:text-white rounded-md hover:bg-[#21262d]">
              <MapIcon class="w-5 h-5" />
            </router-link>
          </div>
          <router-link to="/add" class="flex items-center gap-1 sm:gap-2 bg-[#238636] hover:bg-[#2ea043] text-white px-3 sm:px-4 py-2 rounded-md font-medium transition border border-[#238636]">
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

    <!-- Change Password Modal -->
    <div v-if="isChangePasswordModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click.self="closeChangePasswordModal">
      <div class="bg-[#161b22] w-full max-w-md rounded-md shadow-2xl border border-[#30363d] animate-fade-in">
        <div class="flex justify-between items-center p-4 border-b border-[#30363d]">
          <h2 class="text-lg font-bold text-white">Changer le mot de passe</h2>
          <button @click="closeChangePasswordModal" class="text-[#8b949e] hover:text-white transition p-1">
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
            <label class="block text-xs font-bold text-[#8b949e] uppercase mb-1">Ancien mot de passe</label>
            <input 
              v-model="passwordForm.oldPassword" 
              type="password"
              class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2 text-white focus:border-[#58a6ff] outline-none text-sm" 
              placeholder="Votre mot de passe actuel"
            >
          </div>
          
          <div>
            <label class="block text-xs font-bold text-[#8b949e] uppercase mb-1">Nouveau mot de passe</label>
            <input 
              v-model="passwordForm.newPassword" 
              type="password"
              class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2 text-white focus:border-[#58a6ff] outline-none text-sm" 
              placeholder="Nouveau mot de passe"
            >
          </div>
          
          <div>
            <label class="block text-xs font-bold text-[#8b949e] uppercase mb-1">Confirmer le nouveau mot de passe</label>
            <input 
              v-model="passwordForm.confirmPassword" 
              type="password"
              class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2 text-white focus:border-[#58a6ff] outline-none text-sm" 
              placeholder="Confirmez le nouveau mot de passe"
            >
          </div>
        </div>
        
        <div class="p-4 border-t border-[#30363d] flex justify-end gap-3">
          <button 
            @click="closeChangePasswordModal" 
            class="px-4 py-2 rounded-md text-[#8b949e] hover:bg-[#21262d] transition font-medium border border-[#30363d]"
          >
            Annuler
          </button>
          <button 
            @click="changePassword" 
            class="px-4 py-2 rounded-md bg-[#238636] hover:bg-[#2ea043] text-white font-medium transition"
          >
            Enregistrer
          </button>
        </div>
      </div>
    </div>

    <!-- Change Username Modal -->
    <div v-if="isChangeUsernameModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm" @click.self="closeChangeUsernameModal">
      <div class="bg-[#161b22] w-full max-w-md rounded-md shadow-2xl border border-[#30363d] animate-fade-in">
        <div class="flex justify-between items-center p-4 border-b border-[#30363d]">
          <h2 class="text-lg font-bold text-white">Changer le nom d'utilisateur</h2>
          <button @click="closeChangeUsernameModal" class="text-[#8b949e] hover:text-white transition p-1">
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
            <label class="block text-xs font-bold text-[#8b949e] uppercase mb-1">Nouveau nom d'utilisateur</label>
            <input 
              v-model="newUsername" 
              type="text"
              class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2 text-white focus:border-[#58a6ff] outline-none text-sm" 
              placeholder="Nouveau nom d'utilisateur"
            >
          </div>
        </div>
        
        <div class="p-4 border-t border-[#30363d] flex justify-end gap-3">
          <button 
            @click="closeChangeUsernameModal" 
            class="px-4 py-2 rounded-md text-[#8b949e] hover:bg-[#21262d] transition font-medium border border-[#30363d]"
          >
            Annuler
          </button>
          <button 
            @click="changeUsername" 
            class="px-4 py-2 rounded-md bg-[#238636] hover:bg-[#2ea043] text-white font-medium transition"
          >
            Enregistrer
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style>
@keyframes fade-in { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-in { animation: fade-in 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
</style>