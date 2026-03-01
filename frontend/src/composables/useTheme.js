import { ref, watch, onMounted } from 'vue'

const THEME_KEY = 'pinarr-theme'
const theme = ref('dark')

export function useTheme() {
  const isDark = ref(true)
  
  onMounted(() => {
    const savedTheme = localStorage.getItem(THEME_KEY)
    if (savedTheme) {
      theme.value = savedTheme
    }
    applyTheme(theme.value)
  })
  
  watch(theme, (newTheme) => {
    applyTheme(newTheme)
    localStorage.setItem(THEME_KEY, newTheme)
  })
  
  const applyTheme = (newTheme) => {
    document.documentElement.setAttribute('data-theme', newTheme)
    isDark.value = newTheme === 'dark'
  }
  
  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
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
