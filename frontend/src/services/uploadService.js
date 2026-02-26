import config from '../config.js'
import { API_BASE_URL } from './api.js'

/**
 * Service pour la gestion des uploads d'images
 */

const UploadService = {
  /**
   * Upload une image
   * @param {File} file - Fichier à uploader
   * @returns {Promise<Object>} - { filename, path }
   */
  async uploadImage(file) {
    // Validation côté client
    if (!file) {
      throw new Error('Aucun fichier sélectionné')
    }

    // Vérifier la taille
    const sizeMB = file.size / (1024 * 1024)
    if (sizeMB > config.MAX_FILE_SIZE_MB) {
      throw new Error(`Fichier trop volumineux (${sizeMB.toFixed(1)}MB). Maximum: ${config.MAX_FILE_SIZE_MB}MB`)
    }

    // Vérifier le type
    if (!config.ALLOWED_IMAGE_TYPES.includes(file.type)) {
      throw new Error(`Type de fichier non supporté. Types acceptés: ${config.ALLOWED_IMAGE_TYPES.join(', ')}`)
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/upload/`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `Erreur upload ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Upload error:', error)
      throw error
    }
  },

  /**
   * Construit l'URL complète d'une image
   * @param {string} path - Chemin de l'image (ex: /uploads/filename.png)
   * @returns {string} - URL complète
   */
  getImageUrl(path) {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `${API_BASE_URL}${path}`
  },
}

export default UploadService
export { UploadService }
