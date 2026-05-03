import { ref, watch, onMounted } from 'vue'

const THEME_KEY = 'pinarr-theme-v2'
const theme = ref('champagne')

export function useTheme() {
  const isDark = ref(true)
  
  onMounted(() => {
    const savedTheme = localStorage.getItem(THEME_KEY)
    if (savedTheme === 'champagne' || savedTheme === 'champagne-dark') {
      theme.value = savedTheme
    } else {
      theme.value = 'champagne'
      localStorage.setItem(THEME_KEY, 'champagne')
    }
    applyTheme(theme.value)
  })
  
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
    localStorage.setItem(THEME_KEY, newTheme)
  })
  
  const applyTheme = (newTheme) => {
    document.documentElement.setAttribute('data-theme', newTheme)
    isDark.value = newTheme === 'champagne-dark'
  }
  
  const toggleTheme = () => {
    theme.value = theme.value === 'champagne' ? 'champagne-dark' : 'champagne'
  }
  
  const setTheme = (newTheme) => {
    theme.value = newTheme
  }
  
  return {
    theme,
    isDark,
    toggleTheme,
    setTheme,
    applyTheme
  }
}
