import { computed } from 'vue'

/**
 * Returns the appropriate Tailwind classes for a wine type badge.
 * Uses CSS custom properties via the gh-* / wine-* Tailwind aliases.
 */
export function useWineTypeStyles() {
  const getTypeBadgeClass = (type) => {
    const map = {
      'Rouge': 'bg-wine-red/30 text-wine-red border-wine-red/50',
      'Blanc': 'bg-wine-white/30 text-wine-white border-wine-white/50',
      'Rosé': 'bg-wine-rose/30 text-wine-rose border-wine-rose/50',
      'Effervescents': 'bg-wine-champagne/30 text-wine-champagne border-wine-champagne/50',
    }
    return map[type] || 'bg-gh-elevated text-gh-text-secondary border-gh-border'
  }

  const getTypeDotClass = (type) => {
    const map = {
      'Rouge': 'bg-wine-red',
      'Blanc': 'bg-wine-white',
      'Rosé': 'bg-wine-rose',
      'Effervescents': 'bg-wine-champagne',
    }
    return map[type] || 'bg-gh-text-muted'
  }

  const getTypeBgClass = (type) => {
    const map = {
      'Rouge': 'bg-wine-red',
      'Blanc': 'bg-wine-white',
      'Rosé': 'bg-wine-rose',
      'Effervescents': 'bg-wine-champagne',
    }
    return map[type] || 'bg-gh-text-muted'
  }

  return { getTypeBadgeClass, getTypeDotClass, getTypeBgClass }
}
