// Configuration centralisée du frontend
const config = {
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  
  // Upload
  MAX_FILE_SIZE_MB: 5,
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
  
  // Pagination
  DEFAULT_PAGE_SIZE: 20,
  
  // Timeouts
  REQUEST_TIMEOUT: 30000, // 30s
}

export default config
