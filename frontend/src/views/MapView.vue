<template>
  <main class="max-w-7xl mx-auto px-4 py-6 pb-20">
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-white">Carte des régions</h1>
      <router-link to="/" class="text-[#8b949e] hover:text-[#58a6ff]">← Retour</router-link>
    </div>

    <div v-if="isLoadingGeocoding" class="mb-4 text-xs text-[#8b949e]">
      Géocodage des régions en cours...
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6">
      <div class="bg-[#161b22] rounded-md border border-[#30363d] overflow-hidden">
        <div id="map" class="h-[400px] lg:h-[600px] w-full"></div>
      </div>

      <div class="bg-[#161b22] rounded-md border border-[#30363d] overflow-hidden flex flex-col">
        <div v-if="!selectedRegion" class="flex-1 flex items-center justify-center text-[#8b949e]">
          <div class="text-center">
            <MapIcon class="w-12 h-12 mx-auto mb-3 text-[#30363d]" />
            <p>Cliquez sur un marqueur pour voir les bouteilles</p>
          </div>
        </div>
        
        <div v-else class="flex-1 flex flex-col">
          <div class="p-4 border-b border-[#30363d] flex items-center justify-between">
            <h2 class="text-lg font-bold text-white">
              {{ selectedRegion.name }} 
              <span class="text-[#8b949e] font-normal text-sm">({{ selectedRegion.bottles.length }})</span>
            </h2>
            <button @click="selectedRegion = null" class="text-[#8b949e] hover:text-white">&times;</button>
          </div>
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div v-for="bottle in selectedRegion.bottles.slice(0, 10)" :key="bottle.id" 
                 class="bg-[#0d1117] rounded-md border border-[#30363d] p-3 hover:border-[#8b949e] transition cursor-pointer"
                 @click="goToBottle(bottle.id)">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full flex-shrink-0" :class="getTypeColor(bottle.type)"></span>
                  <span class="text-white font-medium truncate">{{ bottle.name }}</span>
                </div>
                <span class="text-[#8b949e] text-sm flex-shrink-0">{{ bottle.year }}</span>
              </div>
              <div class="text-sm text-[#8b949e] mt-1 ml-5">
                {{ bottle.quantity }} en stock • {{ bottle.price || '-' }} €
              </div>
            </div>
            <div v-if="selectedRegion.bottles.length > 10" class="pt-2">
              <router-link :to="`/?region=${encodeURIComponent(selectedRegion.name)}`" class="block text-center py-3 text-[#58a6ff] hover:underline">
                Voir les {{ selectedRegion.bottles.length }} bouteilles →
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapIcon } from '@heroicons/vue/24/outline'
import { apiRequest } from '../services/api.js'

const router = useRouter()

const API_URL = '/bottles'
const API_GEOCODED_URL = '/geocoded-regions'

const bottles = ref([])
const map = ref(null)
const markersLayer = ref(null)
const selectedRegion = ref(null)
const geocodedRegionsCache = ref({})
const isLoadingGeocoding = ref(false)

const regionCoordinates = {
  'Bordeaux': [44.8378, -0.5792],
  'Bourgogne': [47.2805, 4.4107],
  'Champagne': [49.2583, 4.0317],
  'Loire': [47.3833, 0.6833],
  'Val de Loire': [47.3833, 0.6833],
  'Rhône': [45.7640, 4.8357],
  'Vallée du Rhône': [45.7640, 4.8357],
  'Provence': [43.9352, 6.0679],
  'Alsace': [48.3076, 7.4698],
  'Languedoc': [43.6047, 3.8868],
  'Languedoc-Roussillon': [43.6047, 3.8868],
  'Roussillon': [42.6736, 2.8799],
  'Beaujolais': [46.1094, 4.6536],
  'Sud-Ouest': [44.3512, 1.7517],
  'Corse': [42.0396, 9.0129],
  'Jura': [47.0919, 5.6094],
  'Savoie': [45.4942, 6.6800],
  'Côtes du Rhône': [45.7640, 4.8357],
  'Médoc': [45.2000, -0.8000],
  'Saint-Émilion': [44.9000, -0.1500],
  'Pomerol': [44.9300, -0.1900],
  'Margaux': [44.9500, -0.6700],
  'Pauillac': [45.1800, -0.7400],
  'Saint-Julien': [45.1200, -0.7600],
  'Graves': [44.6500, -0.5500],
  'Sauternes': [44.5300, -0.3500],
  'Chablis': [47.8200, 3.8000],
  'Côte de Beaune': [47.0400, 4.8400],
  'Côte de Nuits': [47.1700, 4.9500],
  'Mâconnais': [46.3000, 4.8200],
  'Côte Chalonnaise': [46.7800, 4.5200],
  'Nuit-Saint-Georges': [47.1400, 4.9500],
  'Gevrey-Chambertin': [47.2200, 4.9700],
  'Vosne-Romanée': [47.1500, 4.9700],
  'Pommard': [46.9800, 4.7900],
  'Meursault': [46.9700, 4.7700],
  'Puligny-Montrachet': [46.9500, 4.7500],
  'Chassagne-Montrachet': [46.9300, 4.7300],
  'Cahors': [44.4500, 1.4300],
  'Gaillac': [43.9200, 1.9000],
  'Fronton': [43.8400, 1.3800],
  'Madiran': [43.4500, -0.0500],
  'Jurançon': [43.2800, -0.4000],
  'Corsica': [42.0396, 9.0129],
  'Banyuls': [42.4800, 3.1300],
  'Collioure': [42.5200, 3.0800],
  'Minervois': [43.3000, 2.7500],
  'Corbières': [43.1000, 2.6000],
  'Fitou': [42.9000, 2.6500],
  'Cotes du Roussillon': [42.6500, 2.8500],
  'Cotes Catalanes': [42.6000, 2.7000],
  'Ardeche': [44.7500, 4.4000],
  'Drome': [44.6500, 5.0000],
  'Isere': [45.2000, 5.7000],
  'Bugey': [45.8500, 5.6500],
  'Italie': [44.4949, 11.3426],
  'Espagne': [40.4637, -3.7492],
  'Portugal': [39.3999, -8.2245],
  'Allemagne': [51.1657, 10.4515],
  'États-Unis': [37.0902, -95.7129],
  'Argentine': [-38.4161, -63.6167],
  'Chili': [-35.6751, -71.5430],
  'Australie': [-25.2744, 133.7751],
  'Nouvelle-Zélande': [-40.9006, 174.8860],
  'Afrique du Sud': [-30.5595, 22.9375],
}

const getTypeColor = (type) => {
  if (type === 'Rouge') return 'bg-[#f85149]'
  if (type === 'Blanc') return 'bg-[#e3b341]'
  if (type === 'Rosé') return 'bg-[#db61a2]'
  if (type === 'Champagne') return 'bg-[#a371f7]'
  return 'bg-[#8b949e]'
}

const goToBottle = (id) => {
  router.push(`/wine/${id}`)
}

const normalize = (text) => {
  if (!text) return ''
  return text.toString()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

const findRegionCoords = (region) => {
  const normalized = normalize(region)
  
  for (const [key, value] of Object.entries(regionCoordinates)) {
    if (normalize(key) === normalized) {
      return value
    }
  }
  
  for (const [key, value] of Object.entries(regionCoordinates)) {
    const normalizedKey = normalize(key)
    if (normalized.includes(normalizedKey) || normalizedKey.includes(normalized)) {
      return value
    }
  }
  
  const regionWords = normalized.split(' ').filter(w => w.length > 3)
  for (const [key, value] of Object.entries(regionCoordinates)) {
    const keyWords = normalize(key).split(' ')
    if (regionWords.some(w => keyWords.includes(w))) {
      return value
    }
  }
  
  if (geocodedRegionsCache.value[region]) {
    return geocodedRegionsCache.value[region]
  }
  
  return null
}

const loadGeocodedRegions = async () => {
  try {
    const data = await apiRequest(API_GEOCODED_URL)
    data.forEach(r => {
      geocodedRegionsCache.value[r.name] = [r.lat, r.lon]
    })
  } catch (e) {
    console.error('Erreur chargement régions géocodées:', e)
  }
}

const saveGeocodedRegion = async (name, coords) => {
  try {
    await apiRequest(API_GEOCODED_URL, {
      method: 'POST',
      body: JSON.stringify({ name, lat: coords[0], lon: coords[1] })
    })
    geocodedRegionsCache.value[name] = coords
  } catch (e) {
    console.error('Erreur sauvegarde région géocodée:', e)
  }
}

const geocodeRegion = async (region) => {
  const queries = [
    region,
    `${region}, France`,
    `${region}, Europe`,
  ]
  
  for (const query of queries) {
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`,
        { headers: { 'Accept-Language': 'fr' } }
      )
      const data = await res.json()
      if (data[0]) {
        const coords = [parseFloat(data[0].lat), parseFloat(data[0].lon)]
        await saveGeocodedRegion(region, coords)
        return coords
      }
      await new Promise(resolve => setTimeout(resolve, 1100))
    } catch (e) {
      console.error('Géocodage échoué:', e)
    }
  }
  return null
}

const fetchBottles = async () => {
  try {
    bottles.value = await apiRequest(API_URL)
  } catch (e) {
    console.error(e)
  }
}

const updateMap = async () => {
  if (!map.value || !markersLayer.value) return
  
  markersLayer.value.clearLayers()
  
  const regionBottles = {}
  bottles.value.forEach(b => {
    if (b.region) {
      if (!regionBottles[b.region]) {
        regionBottles[b.region] = []
      }
      regionBottles[b.region].push(b)
    }
  })
  
  const regionsToGeocode = []
  
  Object.entries(regionBottles).forEach(([region, bottleList]) => {
    const coords = findRegionCoords(region)
    if (coords) {
      addMarker(region, bottleList, coords)
    } else {
      regionsToGeocode.push({ region, bottleList })
    }
  })
  
  if (regionsToGeocode.length > 0) {
    isLoadingGeocoding.value = true
    for (const { region, bottleList } of regionsToGeocode) {
      const coords = await geocodeRegion(region)
      if (coords) {
        addMarker(region, bottleList, coords)
      }
      await new Promise(resolve => setTimeout(resolve, 1100))
    }
    isLoadingGeocoding.value = false
  }
}

const addMarker = (region, bottleList, coords) => {
  const marker = L.circleMarker(coords, {
    radius: Math.min(12 + bottleList.length * 2, 30),
    fillColor: '#f85149',
    color: '#fff',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.8
  })
  
  marker.bindTooltip(`<strong>${region}</strong><br>${bottleList.length} bouteille${bottleList.length > 1 ? 's' : ''}`, {
    direction: 'top'
  })
  
  marker.on('click', () => {
    selectedRegion.value = { name: region, bottles: bottleList }
  })
  
  markersLayer.value.addLayer(marker)
}

onMounted(async () => {
  map.value = L.map('map').setView([46.603354, 1.888334], 6)
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map.value)
  
  markersLayer.value = L.layerGroup().addTo(map.value)
  
  await loadGeocodedRegions()
  await fetchBottles()
  await updateMap()
})

onUnmounted(() => {
  if (map.value) {
    map.value.remove()
  }
})
</script>

<style>
.leaflet-container { background: #0d1117; }
.leaflet-tooltip { 
  background: #161b22; 
  border: 1px solid #30363d; 
  color: #fff; 
  border-radius: 6px; 
  padding: 6px 10px;
  font-size: 13px;
}
.leaflet-tooltip::before { border-top-color: #30363d; }
</style>