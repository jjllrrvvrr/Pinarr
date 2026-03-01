/**
 * Composable pour gérer les couleurs des types de vin
 * Centralise la logique pour éviter les duplications
 */

export const WINE_COLORS = {
  'Rouge': '#f85149',
  'Blanc': '#e3b341', 
  'Rosé': '#db61a2',
  'Champagne': '#a371f7',
  'default': '#8b949e'
}

export const WINE_BG_COLORS = {
  'Rouge': 'bg-[#f85149]',
  'Blanc': 'bg-[#e3b341]',
  'Rosé': 'bg-[#db61a2]', 
  'Champagne': 'bg-[#a371f7]',
  'default': 'bg-[#8b949e]'
}

export const WINE_TEXT_COLORS = {
  'Rouge': 'text-[#f85149]',
  'Blanc': 'text-[#e3b341]',
  'Rosé': 'text-[#db61a2]',
  'Champagne': 'text-[#a371f7]',
  'default': 'text-[#8b949e]'
}

export function useWineColors() {
  /**
   * Retourne la classe Tailwind pour le fond selon le type
   * @param {string} type - Type de vin
   * @returns {string} - Classe Tailwind bg-[color]
   */
  const getTypeBgColor = (type) => {
    return WINE_BG_COLORS[type] || WINE_BG_COLORS.default
  }
  
  /**
   * Retourne la classe Tailwind pour le texte selon le type
   * @param {string} type - Type de vin
   * @returns {string} - Classe Tailwind text-[color]
   */
  const getTypeTextColor = (type) => {
    return WINE_TEXT_COLORS[type] || WINE_TEXT_COLORS.default
  }
  
  /**
   * Retourne la classe Tailwind pour la bordure selon le type
   * @param {string} type - Type de vin
   * @returns {string} - Classe Tailwind border-[color]
   */
  const getTypeBorderColor = (type) => {
    const baseColor = WINE_COLORS[type] || WINE_COLORS.default
    return `border-[${baseColor}]`
  }
  
  /**
   * Retourne la couleur hexadécimale brute
   * @param {string} type - Type de vin
   * @returns {string} - Code couleur hex
   */
  const getTypeHexColor = (type) => {
    return WINE_COLORS[type] || WINE_COLORS.default
  }
  
  /**
   * Retourne la classe complète pour un badge
   * @param {string} type - Type de vin
   * @returns {string} - Classes Tailwind complètes
   */
  const getTypeBadgeClasses = (type) => {
    const color = getTypeBgColor(type)
    return `w-3 h-3 rounded-full flex-shrink-0 ${color}`
  }
  
  return {
    WINE_COLORS,
    WINE_BG_COLORS,
    WINE_TEXT_COLORS,
    getTypeBgColor,
    getTypeTextColor,
    getTypeBorderColor,
    getTypeHexColor,
    getTypeBadgeClasses
  }
}
