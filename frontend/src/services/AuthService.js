/**
 * Service d'authentification
 * Gère le login, logout et la vérification de session
 */

import config from '../config.js'

const API_URL = config.API_BASE_URL

class AuthService {
  /**
   * Vérifie si l'utilisateur est connecté
   */
  static isAuthenticated() {
    return !!sessionStorage.getItem('auth_token')
  }

  /**
   * Récupère le token d'authentification
   */
  static getToken() {
    return sessionStorage.getItem('auth_token')
  }

  /**
   * Connexion utilisateur
   * @param {string} username 
   * @param {string} password 
   */
  static async login(username, password) {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Identifiants invalides')
    }

    const data = await response.json()
    
    // Stocker le token (pour référence, mais l'authentification se fait via cookie)
    if (data.access_token) {
      sessionStorage.setItem('auth_token', data.access_token)
      sessionStorage.setItem('username', data.username)
    }

    return data
  }

  /**
   * Déconnexion
   */
  static async logout() {
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
    } catch (e) {
      // Ignorer les erreurs réseau
    }
    
    // Nettoyer le storage
    sessionStorage.removeItem('auth_token')
    sessionStorage.removeItem('username')
  }

  /**
   * Vérifie la session active
   */
  static async checkAuth() {
    try {
      const response = await fetch(`${API_URL}/auth/check`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.authenticated) {
          sessionStorage.setItem('username', data.username)
          return true
        }
      }
      
      sessionStorage.removeItem('auth_token')
      sessionStorage.removeItem('username')
      return false
    } catch (e) {
      return false
    }
  }

  /**
   * Récupère l'utilisateur courant
   */
  static async getCurrentUser() {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        credentials: 'include'
      })
      
      if (response.ok) {
        return await response.json()
      }
      return null
    } catch (e) {
      return null
    }
  }

  /**
   * Change le mot de passe
   * @param {string} oldPassword 
   * @param {string} newPassword 
   */
  static async changePassword(oldPassword, newPassword) {
    const response = await fetch(`${API_URL}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Échec du changement de mot de passe')
    }

    return await response.json()
  }

  /**
   * Récupère le nom d'utilisateur
   */
  static getUsername() {
    return sessionStorage.getItem('username')
  }

  /**
   * Met à jour le nom d'utilisateur
   * @param {string} newUsername 
   */
  static async updateUsername(newUsername) {
    const response = await fetch(`${API_URL}/auth/update-profile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ new_username: newUsername })
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.detail || 'Échec de la mise à jour du nom')
    }

    const data = await response.json()
    
    // Mettre à jour le username dans le storage
    if (data.username) {
      sessionStorage.setItem('username', data.username)
    }

    return data
  }
}

export default AuthService