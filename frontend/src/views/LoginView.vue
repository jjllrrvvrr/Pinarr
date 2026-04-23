<template>
  <div class="min-h-screen flex items-center justify-center bg-gh-bg py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gh-text">
          Pinarr
        </h2>
        <p class="mt-2 text-center text-sm text-gh-text-secondary">
          Connexion à votre cave à vin
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">Nom d'utilisateur</label>
            <input
              id="username"
              v-model="form.username"
              name="username"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gh-border placeholder-gh-text-muted text-gh-text bg-gh-bg rounded-t-md focus:outline-none focus:ring-gh-accent-red focus:border-gh-accent-red focus:z-10 sm:text-sm"
              placeholder="Nom d'utilisateur"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Mot de passe</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gh-border placeholder-gh-text-muted text-gh-text bg-gh-bg rounded-b-md focus:outline-none focus:ring-gh-accent-red focus:border-gh-accent-red focus:z-10 sm:text-sm"
              placeholder="Mot de passe"
            />
          </div>
        </div>

        <div v-if="error" class="rounded-md bg-gh-accent-red/10 border border-gh-accent-red/30 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-gh-accent-red" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-gh-accent-red">{{ error }}</p>
            </div>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-gh-accent-red hover:bg-gh-accent-red-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gh-accent-red disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading">Connexion...</span>
            <span v-else>Se connecter</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import AuthService from '../services/AuthService'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    await AuthService.login(form.username, form.password)
    router.push('/')
  } catch (err) {
    error.value = err.message || 'Échec de la connexion'
  } finally {
    loading.value = false
  }
}
</script>
