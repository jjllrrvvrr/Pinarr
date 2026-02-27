// Configuration - Utilise l'URL de l'environnement ou chemin relatif par défaut
// En production (Docker), on utilise une URL relative pour passer par le proxy nginx
// En dev, on utilise l'URL complète
const isProduction = import.meta.env.PROD || import.meta.env.MODE === 'production'
const baseUrl = isProduction ? '' : (import.meta.env.VITE_API_URL || 'http://localhost:9994')

const config = {
  API_BASE_URL: `${baseUrl}/api/v1`,
  // Configuration uploads
  MAX_FILE_SIZE_MB: 5,
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
}

export default config
