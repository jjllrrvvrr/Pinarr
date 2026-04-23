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
:root {
  --phase-jeunesse: #58a6ff;
  --phase-maturite: #3fb950;
  --phase-apogee: #a371f7;
  --phase-declin: #f85149;
}

[data-theme="light"] {
  --phase-jeunesse: #0969da;
  --phase-maturite: #1a7f37;
  --phase-apogee: #8250df;
  --phase-declin: #cf222e;
}

[data-theme="red-wine"] {
  --phase-jeunesse: #d45656;
  --phase-maturite: #2a8a3a;
  --phase-apogee: #a070e0;
  --phase-declin: #e06666;
}

[data-theme="green-nature"] {
  --phase-jeunesse: #56aa56;
  --phase-maturite: #3a8a3a;
  --phase-apogee: #7a50cf;
  --phase-declin: #cc5555;
}

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
  background: color-mix(in srgb, var(--phase-jeunesse) 20%, transparent);
  color: var(--phase-jeunesse);
}

.wine-phase-badge.phase-maturite {
  background: color-mix(in srgb, var(--phase-maturite) 20%, transparent);
  color: var(--phase-maturite);
}

.wine-phase-badge.phase-apogee {
  background: color-mix(in srgb, var(--phase-apogee) 20%, transparent);
  color: var(--phase-apogee);
}

.wine-phase-badge.phase-declin {
  background: color-mix(in srgb, var(--phase-declin) 20%, transparent);
  color: var(--phase-declin);
}
</style>
