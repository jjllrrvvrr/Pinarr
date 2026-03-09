<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="show" 
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="$emit('cancel')"
      >
        <Transition
          enter-active-class="transition ease-out duration-300"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition ease-in duration-200"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div class="bg-gh-surface rounded-card p-6 max-w-lg w-full mx-4 border border-gh-border shadow-2xl">
            <!-- Header -->
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-full bg-gh-accent-red/20 flex items-center justify-center flex-shrink-0">
                <ArchiveBoxIcon class="w-5 h-5 text-gh-accent-red" />
              </div>
              <div class="min-w-0">
                <h3 class="text-lg font-bold text-gh-text truncate">
                  Retrait de bouteille(s)
                </h3>
                <p class="text-sm text-gh-text-secondary">
                  Étape {{ removed + 1 }} sur {{ total }}
                </p>
              </div>
            </div>
            
            <!-- Message -->
            <div class="mb-6 p-3 bg-gh-bg rounded-card border border-gh-border">
              <p class="text-gh-text-secondary text-sm">
                Vous avez diminué le stock de 
                <span class="text-gh-text font-bold">{{ bottle?.quantity + total - removed }}</span>
                à 
                <span class="text-gh-text font-bold">{{ bottle?.quantity }}</span>
                bouteilles.
              </p>
              <p class="text-gh-text-secondary text-sm mt-2">
                Sélectionnez l'emplacement de la 
                <span class="text-gh-accent font-bold">{{ removed + 1 }}<sup>ère</sup></span>
                bouteille retirée :
              </p>
            </div>
            
            <!-- Liste des positions -->
            <div class="space-y-2 mb-6 max-h-64 overflow-y-auto">
              <button 
                v-for="pos in positions" 
                :key="pos.id"
                @click="$emit('select', pos.id)"
                :class="[
                  'w-full flex items-center justify-between p-3 rounded-card border-2 transition-all text-left',
                  selected === pos.id 
                    ? 'border-gh-accent bg-gh-accent/10 shadow-glow-blue' 
                    : 'border-gh-border bg-gh-bg hover:border-gh-accent hover:bg-gh-elevated'
                ]"
                :disabled="processing"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <MapPinIcon 
                    class="w-5 h-5 flex-shrink-0" 
                    :class="selected === pos.id ? 'text-gh-accent' : 'text-gh-text-secondary'" 
                  />
                  <div class="min-w-0">
                    <div class="text-sm font-medium text-gh-text truncate">
                      {{ pos.cave_name }} → {{ pos.column_name }} → {{ pos.row_name }}
                    </div>
                    <div class="text-xs text-gh-text-secondary">
                      Position {{ pos.code }}
                    </div>
                  </div>
                </div>
                
                <div 
                  v-if="selected === pos.id"
                  class="w-6 h-6 rounded-full bg-gh-accent flex items-center justify-center flex-shrink-0"
                >
                  <CheckIcon class="w-4 h-4 text-white" />
                </div>
              </button>
            </div>
            
            <!-- Message si pas de positions -->
            <div v-if="positions.length === 0" class="text-center py-4 text-gh-text-secondary">
              Aucune position disponible
            </div>
            
            <!-- Boutons d'action -->
            <div class="flex gap-3">
              <button 
                @click="$emit('cancel')"
                :disabled="processing"
                class="flex-1 px-4 py-2.5 text-gh-text-secondary hover:bg-gh-elevated disabled:opacity-50 rounded-card transition-fast font-medium"
              >
                Annuler
              </button>
              <button 
                @click="$emit('confirm')" 
                :disabled="!selected || processing"
                class="flex-1 px-4 py-2.5 bg-gh-accent-red hover:bg-gh-accent-red-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-card transition-fast font-medium flex items-center justify-center gap-2"
              >
                <span v-if="processing" class="animate-spin">
                  <ArrowPathIcon class="w-4 h-4" />
                </span>
                <span v-else>
                  Retirer de cet emplacement
                </span>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { MapPinIcon, CheckIcon, ArrowPathIcon, ArchiveBoxIcon } from '@heroicons/vue/24/solid'

defineProps({
  show: {
    type: Boolean,
    default: false
  },
  total: {
    type: Number,
    default: 0
  },
  removed: {
    type: Number,
    default: 0
  },
  selected: {
    type: [Number, null],
    default: null
  },
  positions: {
    type: Array,
    default: () => []
  },
  processing: {
    type: Boolean,
    default: false
  },
  bottle: {
    type: Object,
    default: null
  }
})

defineEmits(['select', 'confirm', 'cancel'])
</script>