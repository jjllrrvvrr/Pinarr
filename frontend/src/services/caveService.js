import { apiRequest, API_BASE_URL } from './api.js'

/**
 * Service pour la gestion des caves, colonnes, rangées et positions
 */

const CaveService = {
  // === CAVES ===
  
  /**
   * Récupère toutes les caves
   * @returns {Promise<Array>} - Liste des caves
   */
  async getAll() {
    return await apiRequest('/caves/')
  },

  /**
   * Récupère une cave par ID
   * @param {number} id - ID de la cave
   * @returns {Promise<Object>} - Détails de la cave
   */
  async getById(id) {
    return await apiRequest(`/caves/${id}`)
  },

  /**
   * Crée une nouvelle cave
   * @param {Object} caveData - Données de la cave
   * @returns {Promise<Object>} - Cave créée
   */
  async create(caveData) {
    return await apiRequest('/caves', {
      method: 'POST',
      body: JSON.stringify(caveData),
    })
  },

  /**
   * Met à jour une cave
   * @param {number} id - ID de la cave
   * @param {Object} caveData - Données mises à jour
   * @returns {Promise<Object>} - Cave mise à jour
   */
  async update(id, caveData) {
    return await apiRequest(`/caves/${id}`, {
      method: 'PUT',
      body: JSON.stringify(caveData),
    })
  },

  /**
   * Supprime une cave
   * @param {number} id - ID de la cave
   * @returns {Promise<Object>} - Confirmation
   */
  async delete(id) {
    return await apiRequest(`/caves/${id}`, {
      method: 'DELETE',
    })
  },

  // === COLUMNS ===
  
  /**
   * Crée une nouvelle colonne
   * @param {number} caveId - ID de la cave parente
   * @param {Object} columnData - Données de la colonne
   * @returns {Promise<Object>} - Colonne créée
   */
  async createColumn(caveId, columnData) {
    return await apiRequest(`/caves/${caveId}/columns`, {
      method: 'POST',
      body: JSON.stringify(columnData),
    })
  },

  /**
   * Met à jour une colonne
   * @param {number} columnId - ID de la colonne
   * @param {Object} columnData - Données mises à jour
   * @returns {Promise<Object>} - Colonne mise à jour
   */
  async updateColumn(columnId, columnData) {
    return await apiRequest(`/columns/${columnId}`, {
      method: 'PUT',
      body: JSON.stringify(columnData),
    })
  },

  /**
   * Supprime une colonne
   * @param {number} columnId - ID de la colonne
   * @returns {Promise<Object>} - Confirmation
   */
  async deleteColumn(columnId) {
    return await apiRequest(`/columns/${columnId}`, {
      method: 'DELETE',
    })
  },

  // === ROWS ===
  
  /**
   * Crée une nouvelle rangée avec positions automatiques
   * @param {number} columnId - ID de la colonne parente
   * @param {Object} rowData - Données de la rangée
   * @returns {Promise<Object>} - Rangée créée
   */
  async createRow(columnId, rowData) {
    return await apiRequest(`/columns/${columnId}/rows`, {
      method: 'POST',
      body: JSON.stringify(rowData),
    })
  },

  /**
   * Met à jour une rangée
   * @param {number} rowId - ID de la rangée
   * @param {Object} rowData - Données mises à jour
   * @returns {Promise<Object>} - Rangée mise à jour
   */
  async updateRow(rowId, rowData) {
    return await apiRequest(`/rows/${rowId}`, {
      method: 'PUT',
      body: JSON.stringify(rowData),
    })
  },

  /**
   * Supprime une rangée
   * @param {number} rowId - ID de la rangée
   * @returns {Promise<Object>} - Confirmation
   */
  async deleteRow(rowId) {
    return await apiRequest(`/rows/${rowId}`, {
      method: 'DELETE',
    })
  },

  // === POSITIONS ===
  
  /**
   * Récupère les positions d'une rangée
   * @param {number} rowId - ID de la rangée
   * @returns {Promise<Array>} - Liste des positions
   */
  async getPositions(rowId) {
    return await apiRequest(`/rows/${rowId}/positions`)
  },

  /**
   * Crée une position
   * @param {number} rowId - ID de la rangée parente
   * @param {Object} positionData - Données de la position
   * @returns {Promise<Object>} - Position créée
   */
  async createPosition(rowId, positionData) {
    return await apiRequest(`/rows/${rowId}/positions`, {
      method: 'POST',
      body: JSON.stringify(positionData),
    })
  },

  /**
   * Assigne une bouteille à une position
   * @param {number} positionId - ID de la position
   * @param {number} bottleId - ID de la bouteille (null pour retirer)
   * @returns {Promise<Object>} - Position mise à jour
   */
  async assignBottle(positionId, bottleId) {
    return await apiRequest(`/positions/${positionId}`, {
      method: 'PUT',
      body: JSON.stringify({ bottle_id: bottleId }),
    })
  },

  /**
   * Retire une bouteille d'une position
   * @param {number} positionId - ID de la position
   * @returns {Promise<Object>} - Confirmation
   */
  async removeBottle(positionId) {
    return await apiRequest(`/positions/${positionId}/bottle`, {
      method: 'DELETE',
    })
  },
}

export default CaveService
export { CaveService }
