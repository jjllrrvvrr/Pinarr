import { apiRequest, API_BASE_URL } from './api.js'

/**
 * Service pour la gestion des bouteilles
 */

const BottleService = {
  /**
   * Récupère toutes les bouteilles
   * @param {Object} params - Paramètres de pagination
   * @returns {Promise<Array>} - Liste des bouteilles
   */
  async getAll(params = {}) {
    const { skip = 0, limit = 100 } = params
    return await apiRequest(`/bottles/?skip=${skip}&limit=${limit}`)
  },

  /**
   * Récupère une bouteille par ID
   * @param {number} id - ID de la bouteille
   * @returns {Promise<Object>} - Détails de la bouteille
   */
  async getById(id) {
    return await apiRequest(`/bottles/${id}`)
  },

  /**
   * Crée une nouvelle bouteille
   * @param {Object} bottleData - Données de la bouteille
   * @returns {Promise<Object>} - Bouteille créée
   */
  async create(bottleData) {
    return await apiRequest('/bottles/', {
      method: 'POST',
      body: JSON.stringify(bottleData),
    })
  },

  /**
   * Met à jour une bouteille
   * @param {number} id - ID de la bouteille
   * @param {Object} bottleData - Données mises à jour
   * @returns {Promise<Object>} - Bouteille mise à jour
   */
  async update(id, bottleData) {
    return await apiRequest(`/bottles/${id}`, {
      method: 'PUT',
      body: JSON.stringify(bottleData),
    })
  },

  /**
   * Met à jour partiellement une bouteille
   * @param {number} id - ID de la bouteille
   * @param {Object} bottleData - Données à mettre à jour
   * @returns {Promise<Object>} - Bouteille mise à jour
   */
  async patch(id, bottleData) {
    return await apiRequest(`/bottles/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(bottleData),
    })
  },

  /**
   * Supprime une bouteille
   * @param {number} id - ID de la bouteille
   * @returns {Promise<Object>} - Confirmation
   */
  async delete(id) {
    return await apiRequest(`/bottles/${id}`, {
      method: 'DELETE',
    })
  },

  /**
   * Vérifie les doublons
   * @param {string} name - Nom de la bouteille
   * @param {number} year - Millésime
   * @returns {Promise<Object>} - Résultat de la recherche
   */
  async checkDuplicate(name, year) {
    return await apiRequest(`/bottles/check-duplicate/?name=${encodeURIComponent(name)}&year=${year}`)
  },

  /**
   * Met à jour la quantité d'une bouteille
   * @param {number} id - ID de la bouteille
   * @param {number} quantity - Nouvelle quantité
   * @returns {Promise<Object>} - Bouteille mise à jour
   */
  async updateQuantity(id, quantity) {
    return await this.patch(id, { quantity })
  },
}

export default BottleService
export { BottleService }
