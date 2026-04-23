/**
 * Service pour la gestion des QR codes et bouteilles physiques
 */

import { apiRequest } from './api.js'
import config from '../config.js'

export const QrService = {
  /**
   * Génère N codes QR pour une bouteille
   * @param {number} bottleId - ID de la bouteille (vin)
   * @param {number} count - Nombre de QR codes à générer
   * @returns {Promise<Object>} - { qr_codes: [...], count: N }
   */
  async generateQrCodes(bottleId, count) {
    return await apiRequest(`/bottles/${bottleId}/generate-qr-codes`, {
      method: 'POST',
      body: JSON.stringify({ count }),
    })
  },

  /**
   * Récupère les bouteilles physiques d'un vin
   * @param {number} bottleId - ID de la bouteille (vin)
   * @returns {Promise<Object>} - { physical_bottles: [...], cellar_count: N }
   */
  async getPhysicalBottles(bottleId) {
    return await apiRequest(`/bottles/${bottleId}/physical-bottles`)
  },

  /**
   * Scan un QR code (récupère les infos)
   * @param {string} qrCode - Code QR (ex: "X7K9M2P4")
   * @returns {Promise<Object>} - Détails de la bouteille physique
   */
  /**
   * Scan un QR code (récupère les infos)
   * @param {string} qrCode - Code QR (ex: "X7K9M2P4")
   * @returns {Promise<Object>} - Détails de la bouteille physique
   */
  async scanQrCode(qrCode) {
    // Route publique sans /api/v1 prefix
    return await apiRequest(`/api/scan/${qrCode}`, {}, false)
  },

  /**
   * Retire une bouteille de la cave (public via QR)
   * @param {number} physicalBottleId - ID de la bouteille physique
   * @returns {Promise<Object>}
   */
  async removeBottle(physicalBottleId) {
    return await apiRequest(`/api/remove/${physicalBottleId}`, {
      method: 'POST',
    }, false)
  },

  /**
   * Déplace une bouteille physique
   * @param {number} physicalBottleId - ID de la bouteille physique
   * @param {number|null} positionId - ID de la nouvelle position (null pour stock libre)
   * @returns {Promise<Object>} - { message }
   */
  async moveBottle(physicalBottleId, positionId) {
    return await apiRequest(`/physical-bottles/${physicalBottleId}/move`, {
      method: 'PUT',
      body: JSON.stringify({ position_id: positionId }),
    })
  },

  /**
   * Génère l'URL complète pour un QR code
   * @param {string} qrCode - Code QR
   * @returns {string} - URL complète
   */
  getQrUrl(qrCode) {
    return `${window.location.origin}/bottle/${qrCode}`
  },
}
