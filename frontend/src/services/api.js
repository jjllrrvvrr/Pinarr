import config from '../config.js'

/**
 * Client HTTP configuré pour l'API Pinarr
 */

const API_BASE_URL = config.API_BASE_URL

/**
 * Effectue une requête HTTP avec gestion d'erreurs
 * @param {string} endpoint - Chemin de l'API
 * @param {Object} options - Options fetch
 * @returns {Promise<any>} - Données JSON
 */
async function apiRequest(endpoint, options = {}) {
  // Normaliser l'endpoint - enlever le trailing slash
  const normalizedEndpoint = endpoint.endsWith('/') ? endpoint.slice(0, -1) : endpoint
  const url = `${API_BASE_URL}${normalizedEndpoint}`
  
  const defaultHeaders = {
    'Content-Type': 'application/json',
  }
  
  // Ajouter le token d'authentification si présent
  const token = sessionStorage.getItem('auth_token')
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`
  }
  
  const fetchConfig = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  }
  
  // Supprimer Content-Type si c'est un FormData
  if (options.body instanceof FormData) {
    delete fetchConfig.headers['Content-Type']
  }
  
  try {
    const response = await fetch(url, fetchConfig)
    
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
