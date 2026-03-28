<template>
  <span 
    v-if="currentPhase"
    class="wine-phase-badge"
    :class="`phase-${currentPhase}`"
  >
    {{ currentPhaseLabel }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  vintageYear: {
    type: Number,
    required: true
  },
  jeunesseEnd: {
    type: Number,
    default: null
  },
  maturiteEnd: {
    type: Number,
    default: null
  },
  apogeeEnd: {
    type: Number,
    default: null
  },
  currentYear: {
    type: Number,
    default: () => new Date().getFullYear()
  }
})

const currentPhase = computed(() => {
  if (!props.vintageYear) return null
  
  // Ne pas afficher le badge si aucune phase n'est encodée dans la timeline
  if (!props.jeunesseEnd && !props.maturiteEnd && !props.apogeeEnd) return null
  
  const year = props.currentYear
  const jeunesseEnd = props.jeunesseEnd
  const maturiteEnd = props.maturiteEnd
  const apogeeEnd = props.apogeeEnd
  
  if (year <= jeunesseEnd) return 'jeunesse'
  if (year <= maturiteEnd) return 'maturite'
  if (year <= apogeeEnd) return 'apogee'
  return 'declin'
})

const currentPhaseLabel = computed(() => {
  const labels = {
    jeunesse: 'Jeunesse',
    maturite: 'Maturité',
    apogee: 'Apogée',
    declin: 'Déclin'
  }
  return labels[currentPhase.value]
})
</script>

<style scoped>
.wine-phase-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-full);
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.wine-phase-badge.phase-jeunesse {
  background: rgba(88, 166, 255, 0.2);
  color: #58a6ff;
}

.wine-phase-badge.phase-maturite {
  background: rgba(63, 185, 80, 0.2);
  color: #3fb950;
}

.wine-phase-badge.phase-apogee {
  background: rgba(163, 113, 247, 0.2);
  color: #a371f7;
}

.wine-phase-badge.phase-declin {
  background: rgba(248, 81, 73, 0.2);
  color: #f85149;
}
</style>
