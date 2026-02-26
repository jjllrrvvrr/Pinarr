import { ref, computed, onMounted } from 'vue'
import BottleService from '../services/bottleService.js'

/**
 * Composable pour la gestion des bouteilles
 * @returns {Object} - État et méthodes pour les bouteilles
 */
export function useBottles() {
  const bottles = ref([])
  const loading = ref(false)
  const error = ref(null)

  const totalBottles = computed(() => 
    bottles.value.reduce((acc, b) => acc + (b.quantity || 0), 0)
  )

  const totalValue = computed(() => 
    bottles.value.reduce((acc, b) => acc + ((b.price || 0) * (b.quantity || 0)), 0).toFixed(2)
  )

  async function fetchBottles() {
    loading.value = true
    error.value = null
    
    try {
      bottles.value = await BottleService.getAll()
    } catch (err) {
      error.value = err.message || 'Erreur lors du chargement des bouteilles'
    } finally {
      loading.value = false
    }
  }

  async function deleteBottle(id) {
    if (!confirm('Voulez-vous vraiment supprimer cette bouteille ?')) return
    
    try {
      await BottleService.delete(id)
      bottles.value = bottles.value.filter(b => b.id !== id)
    } catch (err) {
      error.value = err.message || 'Erreur lors de la suppression'
    }
  }

  async function updateQuantity(id, newQuantity) {
    if (newQuantity < 0) return
    
    try {
      await BottleService.updateQuantity(id, newQuantity)
      const bottle = bottles.value.find(b => b.id === id)
      if (bottle) bottle.quantity = newQuantity
    } catch (err) {
      error.value = err.message || 'Erreur lors de la mise à jour'
    }
  }

  onMounted(fetchBottles)

  return {
    bottles,
    loading,
    error,
    totalBottles,
    totalValue,
    fetchBottles,
    deleteBottle,
    updateQuantity,
  }
}
