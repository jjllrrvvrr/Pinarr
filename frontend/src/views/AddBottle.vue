<template>
  <main class="max-w-3xl mx-auto px-4 py-8 pb-20">
    <div class="flex items-center gap-2 mb-6 text-[#8b949e] text-sm">
      <router-link to="/" class="hover:text-[#58a6ff]">Accueil</router-link>
      <span>/</span>
      <span class="text-white">{{ isEditing ? 'Modifier' : 'Ajouter' }}</span>
    </div>

    <div class="bg-[#161b22] rounded-md border border-[#30363d]">
      <div class="p-4 sm:p-6 border-b border-[#30363d]">
        <h1 class="text-lg font-bold text-white">{{ isEditing ? 'Modifier le vin' : 'Nouveau vin' }}</h1>
      </div>

      <div class="p-4 sm:p-6 space-y-6">
        <div class="flex gap-2 border-b border-[#30363d] pb-3 mb-4">
          <button @click="activeTab='identity'" :class="['pb-2 px-4 font-medium transition text-sm', activeTab==='identity' ? 'text-white border-b-2 border-[#f85149]' : 'text-[#8b949e] hover:text-gray-300']">
            Identité
          </button>
          <button @click="activeTab='stock'" :class="['pb-2 px-4 font-medium transition text-sm', activeTab==='stock' ? 'text-white border-b-2 border-[#f85149]' : 'text-[#8b949e] hover:text-gray-300']">
            Stock & Évaluation
          </button>
        </div>

        <div v-if="activeTab === 'identity'" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-[#8b949e] mb-1">Nom du vin *</label>
            <input v-model="form.name" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] focus:ring-1 focus:ring-[#58a6ff] outline-none text-sm" placeholder="ex: Château Margaux">
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Domaine viticole</label>
              <input v-model="form.domaine" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="ex: Domaine de la Romanée-Conti">
            </div>
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Année</label>
              <input v-model="form.year" type="number" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="2020">
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Pays</label>
              <select v-model="form.country" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm">
                <option :value="null">—</option>
                <option v-for="c in countries" :key="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Région</label>
              <input v-model="form.region" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="ex: Bordeaux, Bourgogne...">
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Type</label>
              <select v-model="form.type" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm">
                <option>Rouge</option>
                <option>Blanc</option>
                <option>Rosé</option>
                <option>Champagne</option>
                <option>Spiritueux</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Cépages</label>
              <input v-model="form.cepage" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="ex: Merlot, Cabernet Sauvignon">
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Degré alcool (%)</label>
              <input v-model="form.alcohol" type="number" step="0.5" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="ex: 13.5">
            </div>
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Contenance</label>
              <input v-model="form.size" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="75cl">
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-[#8b949e] mb-1">Description</label>
            <textarea v-model="form.description" rows="3" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="Notes de dégustation, caractéristiques..."></textarea>
          </div>

          <div>
            <label class="block text-xs font-medium text-[#8b949e] mb-2">Photo</label>
            <div v-if="imagePreview" class="relative inline-block mb-3">
              <img :src="imagePreview" class="w-32 h-32 object-cover rounded-md border border-[#30363d]" />
              <button @click="removeImage" class="absolute -top-2 -right-2 bg-[#f85149] text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-[#da3633]">×</button>
            </div>
            <div v-else @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" @drop.prevent="handleDrop" :class="['border-2 border-dashed rounded-md p-6 text-center transition cursor-pointer', dragOver ? 'border-[#58a6ff] bg-[#58a6ff]/10' : 'border-[#30363d] hover:border-[#58a6ff]']" @click="triggerFileInput">
              <CloudArrowUpIcon class="w-8 h-8 mx-auto text-[#8b949e] mb-2" />
              <p class="text-sm text-[#8b949e]">Glissez une photo ou cliquez</p>
              <input type="file" ref="fileInput" @change="handleImageUpload" accept="image/*" class="hidden" />
            </div>
            <div v-if="!imagePreview" class="mt-2">
              <button type="button" @click="showUrlInput = !showUrlInput" class="text-xs text-[#58a6ff] hover:underline">
                Utiliser une URL
              </button>
              <div v-if="showUrlInput" class="mt-2 flex gap-2">
                <input v-model="imageUrl" type="url" placeholder="https://..." class="flex-1 bg-[#0d1117] border border-[#30363d] rounded-md p-2 text-white text-sm" />
                <button type="button" @click="useImageUrl" class="px-3 py-2 bg-[#238636] text-white rounded-md text-sm">OK</button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'stock'" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-[#8b949e] mb-1">Position dans la cave</label>
            <div class="grid grid-cols-4 gap-2">
              <select v-model="form.position_cave_id" @change="onCaveChange" class="bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm">
                <option :value="null">-- Cave --</option>
                <option v-for="cave in caves" :key="cave.id" :value="cave.id">{{ cave.name }}</option>
              </select>
              <select v-model="form.position_column_id" @change="onColumnChange" :disabled="!form.position_cave_id" class="bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm disabled:opacity-50">
                <option :value="null">-- Col. --</option>
                <option v-for="col in availableColumns" :key="col.id" :value="col.id">{{ col.name }}</option>
              </select>
              <select v-model="form.position_row_id" @change="onRowChange" :disabled="!form.position_column_id" class="bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm disabled:opacity-50">
                <option :value="null">-- Étag. --</option>
                <option v-for="row in availableRows" :key="row.id" :value="row.id">{{ row.name }}</option>
              </select>
              <select v-model="form.position_id" :disabled="!form.position_row_id" class="bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm disabled:opacity-50">
                <option :value="null">-- Pos. --</option>
                <option v-for="pos in availablePositions" :key="pos.id" :value="pos.id" :disabled="pos.occupied && pos.bottle_id !== form.id">
                  L{{ pos.line }}/{{ pos.position }}{{ pos.occupied ? ' (occupée)' : '' }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Quantité</label>
              <input v-model="form.quantity" type="number" min="0" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm">
            </div>
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Prix (€)</label>
              <input v-model="form.price" type="number" step="0.01" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="45.00">
            </div>
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Apogée début</label>
              <input v-model="form.apogee_start" type="number" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="2025" min="1900" max="2100">
            </div>
            <div>
              <label class="block text-xs font-medium text-[#8b949e] mb-1">Apogée fin</label>
              <input v-model="form.apogee_end" type="number" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="2035" min="1900" max="2100">
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-[#8b949e] mb-1">Note</label>
            <div class="flex items-center gap-1">
              <button v-for="i in 5" :key="i" @click="form.rating = i" class="p-1 transition" :class="i <= (form.rating || 0) ? 'text-[#e3b341]' : 'text-[#30363d]'">
                <StarIconSolid class="w-6 h-6" />
              </button>
              <span v-if="form.rating" class="ml-2 text-sm text-[#8b949e]">{{ form.rating }}/5</span>
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-[#8b949e] mb-1">Tags</label>
            <div class="relative">
              <input v-model="tagInput" @keyup.enter="addTag" @keydown.comma.prevent="addTag" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="Entrée pour ajouter">
            </div>
            <div class="flex flex-wrap gap-2 mt-2">
              <span v-for="tag in currentTags" :key="tag" class="inline-flex items-center gap-1 bg-[#21262d] px-2 py-0.5 rounded-full text-xs text-white border border-[#30363d]">
                {{ tag }}
                <button @click="removeTag(tag)" class="text-[#8b949e] hover:text-[#f85149]">×</button>
              </span>
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-[#8b949e] mb-1">Lien externe</label>
            <input v-model="form.buy_link" class="w-full bg-[#0d1117] border border-[#30363d] rounded-md p-2.5 text-white focus:border-[#58a6ff] outline-none text-sm" placeholder="https://...">
          </div>
        </div>
      </div>

      <div class="p-4 sm:p-6 border-t border-[#30363d] flex justify-between">
        <router-link to="/" class="px-4 py-2 rounded-md text-[#8b949e] hover:bg-[#21262d] transition font-medium border border-[#30363d] text-sm">
          Annuler
        </router-link>
        <button @click="saveBottle" class="px-6 py-2 rounded-md bg-[#238636] hover:bg-[#2ea043] text-white font-medium transition text-sm">
          {{ isEditing ? 'Enregistrer' : 'Ajouter' }}
        </button>
      </div>
    </div>

    <div v-if="showDuplicateModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click="showDuplicateModal = false">
      <div class="bg-[#161b22] p-6 rounded-md max-w-md w-full border border-[#30363d]" @click.stop>
        <h2 class="text-lg font-bold text-white mb-2">Bouteille similaire trouvée</h2>
        <p class="text-[#8b949e] text-sm mb-4">
          Une ou plusieurs bouteilles avec le même nom et la même année existent déjà. Voulez-vous éditer l'existante ou créer une nouvelle entrée ?
        </p>
        <div class="space-y-2 mb-4">
          <div v-for="dup in duplicateMatches" :key="dup.id" 
               class="p-3 bg-[#0d1117] rounded-md border border-[#30363d] flex items-center justify-between">
            <div>
              <span class="text-white font-medium">{{ dup.name }}</span>
              <span class="text-[#8b949e] text-xs ml-2">({{ dup.year }})</span>
              <span v-if="dup.domaine" class="text-[#8b949e] text-xs block">{{ dup.domaine }}</span>
            </div>
            <span :class="['text-xs px-2 py-0.5 rounded', dup.quantity > 0 ? 'bg-[#238636]/20 text-[#3fb950]' : 'bg-[#f85149]/20 text-[#f85149]']">
              {{ dup.quantity > 0 ? `${dup.quantity} en cave` : 'Épuisé' }}
            </span>
          </div>
        </div>
        <div class="flex gap-2">
          <button @click="editDuplicate" class="flex-1 px-4 py-2 bg-[#58a6ff] text-white rounded-md text-sm font-medium hover:bg-[#388bfd] transition">
            Éditer l'existante
          </button>
          <button @click="forceCreate" class="flex-1 px-4 py-2 bg-[#21262d] text-white rounded-md text-sm font-medium hover:bg-[#30363d] transition border border-[#30363d]">
            Créer quand même
          </button>
        </div>
        <button @click="showDuplicateModal = false" class="w-full mt-2 text-xs text-[#8b949e] hover:text-white transition">
          Annuler
        </button>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { StarIcon as StarIconSolid } from '@heroicons/vue/24/solid'
import { CloudArrowUpIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()

const API_URL = 'http://127.0.0.1:8000/bottles'
const API_UPLOAD_URL = 'http://127.0.0.1:8000/upload'

const countries = ['France', 'Italie', 'Espagne', 'Portugal', 'Allemagne', 'États-Unis', 'Argentine', 'Chili', 'Australie', 'Nouvelle-Zélande', 'Afrique du Sud', 'Autre']

const isEditing = ref(false)
const activeTab = ref('identity')
const tagInput = ref('')
const imagePreview = ref(null)
const imageFile = ref(null)
const showUrlInput = ref(false)
const imageUrl = ref('')
const dragOver = ref(false)
const fileInput = ref(null)
const showDuplicateModal = ref(false)
const duplicateMatches = ref([])

const caves = ref([])
const availableColumns = ref([])
const availableRows = ref([])
const availablePositions = ref([])

const defaultForm = {
  id: null,
  name: '', 
  domaine: '', 
  country: null,
  year: new Date().getFullYear(), 
  type: 'Rouge',
  region: '', 
  cepage: '', 
  alcohol: null, 
  size: '75cl',
  apogee_start: null,
  apogee_end: null,
  location: '',
  quantity: 1, 
  price: null, 
  description: '', 
  rating: 0, 
  tags: '',
  is_favorite: false, 
  buy_link: '', 
  image_path: null,
  position_id: null,
  position_cave_id: null,
  position_column_id: null,
  position_row_id: null
}
const form = ref({ ...defaultForm })

const currentTags = computed({
  get: () => form.value.tags ? form.value.tags.split(',').map(t => t.trim()).filter(t => t) : [],
  set: (val) => { form.value.tags = val.join(',') }
})

const addTag = () => {
  const tag = tagInput.value.trim().replace(/,/g, '')
  if (tag && !currentTags.value.includes(tag)) {
    currentTags.value = [...currentTags.value, tag]
  }
  tagInput.value = ''
}

const removeTag = (tag) => {
  currentTags.value = currentTags.value.filter(t => t !== tag)
}

const handleImageUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    imageFile.value = file
    const reader = new FileReader()
    reader.onload = (ev) => { imagePreview.value = ev.target.result }
    reader.readAsDataURL(file)
  }
}

const handleDrop = (e) => {
  dragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    imageFile.value = file
    const reader = new FileReader()
    reader.onload = (ev) => { imagePreview.value = ev.target.result }
    reader.readAsDataURL(file)
  }
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const removeImage = () => {
  imageFile.value = null
  imagePreview.value = null
  form.value.image_path = null
}

const useImageUrl = () => {
  if (imageUrl.value) {
    imagePreview.value = imageUrl.value
    form.value.image_path = imageUrl.value
    imageFile.value = null
    showUrlInput.value = false
    imageUrl.value = ''
  }
}

const uploadImage = async () => {
  if (!imageFile.value) return null
  const formData = new FormData()
  formData.append('file', imageFile.value)
  try {
    const res = await fetch(API_UPLOAD_URL, { method: 'POST', body: formData })
    if (res.ok) {
      const data = await res.json()
      return data.path
    }
  } catch (e) { console.error(e) }
  return null
}

const fetchBottle = async (id) => {
  try {
    const res = await fetch(`${API_URL}/${id}`)
    if (res.ok) {
      const bottle = await res.json()
      form.value = { 
        ...defaultForm,
        ...bottle 
      }
      if (bottle.image_path) {
        imagePreview.value = bottle.image_path.startsWith('http') 
          ? bottle.image_path 
          : `http://127.0.0.1:8000${bottle.image_path}`
      }
      if (bottle.position) {
        form.value.position_row_id = bottle.position.row_id
        if (caves.value.length > 0) {
          for (const cave of caves.value) {
            for (const col of cave.columns || []) {
              const row = col.rows?.find(r => r.id === bottle.position.row_id)
              if (row) {
                form.value.position_cave_id = cave.id
                form.value.position_column_id = col.id
                availableColumns.value = cave.columns || []
                availableRows.value = col.rows || []
                await loadPositions(bottle.position.row_id)
                form.value.position_id = bottle.position.id
                break
              }
            }
          }
        }
      }
      isEditing.value = true
    }
  } catch (e) { console.error(e) }
}

const fetchCaves = async () => {
  try {
    const res = await fetch(`${CAVES_URL}`)
    if (res.ok) {
      caves.value = await res.json()
    }
  } catch (e) { console.error(e) }
}

const CAVES_URL = 'http://127.0.0.1:8000/caves'

const onCaveChange = () => {
  form.value.position_column_id = null
  form.value.position_row_id = null
  form.value.position_id = null
  availableRows.value = []
  availablePositions.value = []
  
  const cave = caves.value.find(c => c.id === form.value.position_cave_id)
  availableColumns.value = cave?.columns || []
}

const onColumnChange = () => {
  form.value.position_row_id = null
  form.value.position_id = null
  availablePositions.value = []
  
  const cave = caves.value.find(c => c.id === form.value.position_cave_id)
  const col = cave?.columns?.find(c => c.id === form.value.position_column_id)
  availableRows.value = col?.rows || []
}

const onRowChange = async () => {
  form.value.position_id = null
  if (form.value.position_row_id) {
    await loadPositions(form.value.position_row_id)
  } else {
    availablePositions.value = []
  }
}

const loadPositions = async (rowId) => {
  try {
    const res = await fetch(`http://127.0.0.1:8000/rows/${rowId}/positions/`)
    if (res.ok) {
      availablePositions.value = (await res.json()).map(p => ({
        id: p.id,
        line: p.line,
        position: p.position,
        occupied: !!p.bottle_at_position,
        bottle_id: p.bottle_at_position?.id
      }))
    }
  } catch (e) { console.error(e) }
}

const checkDuplicate = async () => {
  if (!form.value.name || !form.value.year) return []
  try {
    const res = await fetch(`${API_URL}/check-duplicate/?name=${encodeURIComponent(form.value.name)}&year=${form.value.year}`)
    if (res.ok) {
      const data = await res.json()
      return data.matches || []
    }
  } catch (e) { console.error(e) }
  return []
}

const saveBottle = async (force = false) => {
  if (!form.value.name) return alert("Le nom est obligatoire")

  if (!isEditing.value && !force) {
    const matches = await checkDuplicate()
    if (matches.length > 0) {
      duplicateMatches.value = matches
      showDuplicateModal.value = true
      return
    }
  }

  let imagePath = form.value.image_path
  if (imageFile.value) {
    imagePath = await uploadImage()
  }

  const payload = {
    name: form.value.name,
    domaine: form.value.domaine || null,
    country: form.value.country || null,
    year: parseInt(form.value.year) || null,
    type: form.value.type || "Rouge",
    region: form.value.region || null,
    cepage: form.value.cepage || null,
    alcohol: parseFloat(form.value.alcohol) || null,
    size: form.value.size || "75cl",
    apogee_start: parseInt(form.value.apogee_start) || null,
    apogee_end: parseInt(form.value.apogee_end) || null,
    location: form.value.location || null,
    quantity: parseInt(form.value.quantity) || 1,
    price: parseFloat(form.value.price) || null,
    description: form.value.description || null,
    rating: parseInt(form.value.rating) || null,
    tags: form.value.tags || null,
    is_favorite: form.value.is_favorite || false,
    buy_link: form.value.buy_link || null,
    image_path: imagePath
  }

  try {
    const method = isEditing.value ? 'PUT' : 'POST'
    const url = isEditing.value ? `${API_URL}/${form.value.id}` : API_URL
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      const savedBottle = await res.json()
      
      if (form.value.position_id) {
        await fetch(`http://127.0.0.1:8000/positions/${form.value.position_id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ bottle_id: savedBottle.id })
        })
      }
      
      router.push(`/wine/${savedBottle.id}`)
    } else {
      const txt = await res.text()
      alert("Erreur: " + txt)
    }
  } catch (e) {
    alert("Erreur réseau: " + e.message)
  }
}

const editDuplicate = () => {
  if (duplicateMatches.value.length > 0) {
    router.push(`/edit/${duplicateMatches.value[0].id}`)
  }
}

const forceCreate = () => {
  showDuplicateModal.value = false
  saveBottle(true)
}

onMounted(async () => {
  await fetchCaves()
  if (route.params.id) {
    await fetchBottle(route.params.id)
  }
})
</script>