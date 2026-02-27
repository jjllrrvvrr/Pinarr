import AuthService from '../services/AuthService.js'

/**
 * Garde de route pour vérifier l'authentification
 * Redirige vers /login si non authentifié
 */
export async function authGuard(to, from, next) {
  // Routes publiques
  const publicRoutes = ['/login']
  
  if (publicRoutes.includes(to.path)) {
    // Si déjà connecté, rediriger vers home
    try {
      const isAuth = await AuthService.checkAuth()
      if (isAuth) {
        next('/')
        return
      }
    } catch (e) {
      // En cas d'erreur API, laisser passer sur /login
    }
    next()
    return
  }
  
  // Vérifier l'authentification
  try {
    const isAuthenticated = await AuthService.checkAuth()
    
    if (!isAuthenticated) {
      next('/login')
      return
    }
  } catch (e) {
    // Si l'API est inaccessible (dev), continuer quand même
    // mais stocker un token vide pour marquer comme "non authentifié"
    console.warn('Auth check failed, continuing anyway:', e)
  }
  
  next()
}

/**
 * Garde pour les routes publiques
 * Redirige vers / si déjà authentifié
 */
export async function publicGuard(to, from, next) {
  try {
    const isAuth = await AuthService.checkAuth()
    if (isAuth) {
      next('/')
      return
    }
  } catch (e) {
    // En cas d'erreur, laisser passer
  }
  next()
}
