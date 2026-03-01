/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Fonds
        'gh-bg': 'var(--bg-primary)',
        'gh-surface': 'var(--bg-surface)',
        'gh-elevated': 'var(--bg-elevated)',
        'gh-header': 'var(--bg-header)',
        'gh-overlay': 'var(--bg-overlay)',
        
        // Bordures
        'gh-border': 'var(--border-default)',
        'gh-border-hover': 'var(--border-hover)',
        'gh-border-active': 'var(--border-active)',
        'gh-border-error': 'var(--border-error)',
        'gh-border-success': 'var(--border-success)',
        
        // Texte
        'gh-text': 'var(--text-primary)',
        'gh-text-secondary': 'var(--text-secondary)',
        'gh-text-muted': 'var(--text-muted)',
        'gh-text-inverse': 'var(--text-inverse)',
        
        // Accents
        'gh-accent': 'var(--accent-blue)',
        'gh-accent-green': 'var(--accent-green)',
        'gh-accent-green-hover': 'var(--accent-green-hover)',
        'gh-accent-green-text': 'var(--accent-green-text)',
        'gh-accent-red': 'var(--accent-red)',
        'gh-accent-orange': 'var(--accent-orange)',
        'gh-accent-gold': 'var(--accent-gold)',
        'gh-accent-pink': 'var(--accent-pink)',
        'gh-accent-purple': 'var(--accent-purple)',
        
        // Types de vin
        'wine-red': 'var(--wine-red)',
        'wine-white': 'var(--wine-white)',
        'wine-rose': 'var(--wine-rose)',
        'wine-champagne': 'var(--wine-champagne)',
        'wine-default': 'var(--wine-default)',
      },
      borderRadius: {
        'card': 'var(--radius-md)',
        'button': 'var(--radius-md)',
        'tag': 'var(--radius-sm)',
        'modal': 'var(--radius-lg)',
        'pill': 'var(--radius-full)',
      },
      transitionDuration: {
        'fast': 'var(--transition-fast)',
        'base': 'var(--transition-base)',
        'slow': 'var(--transition-slow)',
      },
      boxShadow: {
        'sm': 'var(--shadow-sm)',
        'md': 'var(--shadow-md)',
        'lg': 'var(--shadow-lg)',
        'glow-blue': 'var(--shadow-glow-blue)',
      },
      zIndex: {
        'dropdown': 'var(--z-dropdown)',
        'sticky': 'var(--z-sticky)',
        'modal': 'var(--z-modal)',
        'tooltip': 'var(--z-tooltip)',
        'toast': 'var(--z-toast)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
