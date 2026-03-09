import { ref } from 'vue'
import { apiRequest } from '../services/api'

/**
 * Composable pour gérer le retrait automatique de positions
 * quand la quantité diminue
 */
export function useQuantityManager() {
  // État du modal
  const showRemoveModal = ref(false)
  const positionsToRemove = ref(0)
  const positionsRemoved = ref(0)
  const selectedPositionId = ref(null)
  const isProcessing = ref(false)
  
  // Données temporaires
  let currentBottle = null
  let originalQuantity = 0
  let newQuantity = 0
  let onCompleteCallback = null
  let onCancelCallback = null

  /**
   * Vérifie si on doit ouvrir le modal de retrait
   * @param {Object} bottle - La bouteille concernée
   * @param {number} qty - Nouvelle quantité
   * @param {number} oldQty - Ancienne quantité
   * @param {Function} onComplete - Callback quand tout est terminé
   * @param {Function} onCancel - Callback si annulation
   * @returns {boolean} - true si modal ouvert, false sinon
   */
  const checkQuantityDecrease = (bottle, qty, oldQty, onComplete, onCancel) => {
    // Réinitialiser l'état
    showRemoveModal.value = false
    positionsToRemove.value = 0
    positionsRemoved.value = 0
    selectedPositionId.value = null
    isProcessing.value = false
    
    // Vérifier si on doit ouvrir le modal
    if (qty < oldQty && bottle.positions?.length > 0) {
      const diff = oldQty - qty
      positionsToRemove.value = Math.min(diff, bottle.positions.length)
      positionsRemoved.value = 0
      
      currentBottle = bottle
      originalQuantity = oldQty
      newQuantity = qty
      onCompleteCallback = onComplete
      onCancelCallback = onCancel
      
      showRemoveModal.value = true
      return true
    }
    
    return false
  }

  /**
   * Confirme le retrait d'une position
   */
  const confirmRemove = async () => {
    if (!selectedPositionId.value || !currentBottle) return
    
    isProcessing.value = true
    try {
      // Appel API pour retirer la bouteille de la position
      await apiRequest(`/positions/${selectedPositionId.value}/bottle`, {
        method: 'DELETE'
      })
      
      // Mettre à jour la liste des positions localement
      currentBottle.positions = currentBottle.positions.filter(
        p => p.id !== selectedPositionId.value
      )
      
      positionsRemoved.value++
      selectedPositionId.value = null
      
      // Vérifier si on a terminé
      if (positionsRemoved.value >= positionsToRemove.value) {
        showRemoveModal.value = false
        
        // Appeler le callback de completion
        if (onCompleteCallback) {
          await onCompleteCallback(newQuantity)
        }
        
        // Réinitialiser
        resetState()
      }
    } catch (e) {
      console.error('Erreur lors du retrait:', e)
      alert('Erreur lors du retrait de la position: ' + e.message)
    } finally {
      isProcessing.value = false
    }
  }

  /**
   * Annule l'opération et restaure la quantité
   */
  const cancelRemove = () => {
    showRemoveModal.value = false
    
    // Restaurer la quantité originale
    if (currentBottle && onCancelCallback) {
      onCancelCallback(originalQuantity)
    }
    
    resetState()
  }

  /**
   * Réinitialise l'état
   */
  const resetState = () => {
    currentBottle = null
    originalQuantity = 0
    newQuantity = 0
    onCompleteCallback = null
    onCancelCallback = null
  }

  /**
   * Sélectionne une position
   */
  const selectPosition = (positionId) => {
    selectedPositionId.value = positionId
  }

  return {
    // État
    showRemoveModal,
    positionsToRemove,
    positionsRemoved,
    selectedPositionId,
    isProcessing,
    currentBottle,
    
    // Méthodes
    checkQuantityDecrease,
    confirmRemove,
    cancelRemove,
    selectPosition
  }
}