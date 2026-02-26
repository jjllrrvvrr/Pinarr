import config from '../config.js'

/**
 * Client HTTP configuré pour l'API SudoWine
 */

const API_BASE_URL = config.API_BASE_URL

/**
 * Effectue une requête HTTP avec gestion d'erreurs
 * @param {string} endpoint - Chemin de l'API
 * @param {Object} options - Options fetch
 * @returns {Promise<any>} - Données JSON
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  }
  
  // Supprimer Content-Type si c'est un FormData
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type']
  }
  
  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `Erreur HTTP ${response.status}`)
    }
    
    return await response.json()
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error)
    throw error
  }
}

export { apiRequest, API_BASE_URL }
export default apiRequest
