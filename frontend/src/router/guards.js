import AuthService from '../services/AuthService.js'

/**
 * Garde de route pour vérifier l'authentification
 * Redirige vers /login si non authentifié
 */
export async function authGuard(to, from, next) {
  // Routes publiques (patterns inclus)
  const publicRoutes = ['/login', '/bottle/']
  const isPublic = publicRoutes.some(route => to.path === route || to.path.startsWith(route))

  if (isPublic) {
    // Sur /login, si déjà connecté → home
    if (to.path === '/login') {
      try {
        const isAuth = await AuthService.checkAuth()
        if (isAuth) {
          next('/')
          return
        }
      } catch (e) {
        // laisser passer
      }
    }
    // Routes publiques (scan QR) → laisser passer sans auth
    next()
    return
  }

  // Vérifier l'authentification pour les routes protégées
  try {
    const isAuthenticated = await AuthService.checkAuth()
    if (!isAuthenticated) {
      next('/login')
      return
    }
  } catch (e) {
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
