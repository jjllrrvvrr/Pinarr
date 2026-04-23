<template>
  <div class="wine-phase-timeline" :class="{ 'timeline-compact': compact }">
    <!-- Header minimaliste (caché en mode compact) -->
    <div class="timeline-header" v-if="showHeader && !compact">
      <div class="current-phase-badge" :class="`phase-${currentPhase}`">
        <span class="phase-dot"></span>
        {{ currentPhaseLabel }}
      </div>
      <div class="year-range" v-if="!editable">
        {{ vintageYear }} — {{ timelineEndYear }}
      </div>
    </div>

    <!-- Timeline principale -->
    <div class="timeline-container" :class="{ 'container-compact': compact }">
      <!-- Barre de timeline -->
      <div class="timeline-track" ref="trackRef">
        <!-- Fond -->
        <div class="timeline-background"></div>
        
        <!-- Segments colorés avec noms -->
        <div class="phase-segments">
          <div 
            class="phase-segment jeunesse"
            :style="{ width: jeunessePercent + '%' }"
          >
            <span class="segment-name">JEUNESSE</span>
          </div>
          <div 
            class="phase-segment maturite"
            :style="{ width: maturitePercent + '%' }"
          >
            <span class="segment-name">MATURITÉ</span>
          </div>
          <div 
            class="phase-segment apogee"
            :style="{ width: apogeePercent + '%' }"
          >
            <span class="segment-name">APOGÉE</span>
          </div>
          <div 
            class="phase-segment declin"
            :style="{ width: declinPercent + '%' }"
          >
            <span class="segment-name">DÉCLIN</span>
          </div>
        </div>

        <!-- Marqueur année actuelle -->
        <div 
          class="current-year-marker"
          :style="{ left: currentYearPercent + '%' }"
          v-if="currentYearPercent >= 0 && currentYearPercent <= 100"
        >
          <div class="marker-arrow"></div>
          <div class="marker-line"></div>
          <div class="marker-label">{{ currentYear }}</div>
        </div>

        <!-- Curseurs (seulement en mode éditable) -->
        <div class="timeline-handles" v-if="editable">
          <div
            class="timeline-handle handle-jeunesse"
            :style="{ left: jeunessePercent + '%' }"
            @mousedown="startDrag('jeunesseEnd', $event)"
            @touchstart="startDrag('jeunesseEnd', $event)"
            :class="{ dragging: draggingHandle === 'jeunesseEnd' }"
          >
            <div class="handle-visual"></div>
            <div class="handle-tooltip">{{ jeunesseEndYear }}</div>
          </div>

          <div
            class="timeline-handle handle-maturite"
            :style="{ left: (jeunessePercent + maturitePercent) + '%' }"
            @mousedown="startDrag('maturiteEnd', $event)"
            @touchstart="startDrag('maturiteEnd', $event)"
            :class="{ dragging: draggingHandle === 'maturiteEnd' }"
          >
            <div class="handle-visual"></div>
            <div class="handle-tooltip">{{ maturiteEndYear }}</div>
          </div>

          <div
            class="timeline-handle handle-apogee"
            :style="{ left: (jeunessePercent + maturitePercent + apogeePercent) + '%' }"
            @mousedown="startDrag('apogeeEnd', $event)"
            @touchstart="startDrag('apogeeEnd', $event)"
            :class="{ dragging: draggingHandle === 'apogeeEnd' }"
          >
            <div class="handle-visual"></div>
            <div class="handle-tooltip">{{ apogeeEndYear }}</div>
          </div>
        </div>
      </div>

      <!-- Ligne des dates sous la barre -->
      <div class="phase-dates-row">
        <div class="phase-date-item" :style="{ width: jeunessePercent + '%' }">
          <span class="phase-year">{{ vintageYear }}</span>
        </div>
        <div class="phase-date-item" :style="{ width: maturitePercent + '%' }">
          <span class="phase-year">{{ jeunesseEndYear }}</span>
        </div>
        <div class="phase-date-item" :style="{ width: apogeePercent + '%' }">
          <span class="phase-year">{{ maturiteEndYear }}</span>
        </div>
        <div class="phase-date-item" :style="{ width: declinPercent + '%' }">
          <span class="phase-year">{{ apogeeEndYear }}</span>
        </div>
        <div class="phase-end-year">
          <span class="phase-year">{{ apogeeEndYear + 5 }}</span>
        </div>
      </div>
    </div>

    <!-- Inputs pour édition (optionnel) -->
    <div class="timeline-inputs" v-if="editable && showInputs">
      <div class="input-group">
        <label>Fin Jeunesse</label>
        <input 
          type="number" 
          v-model.number="localJeunesseEnd"
          :min="vintageYear + 1"
          :max="localMaturiteEnd - 1"
          @change="updateFromInput"
        />
      </div>
      <div class="input-group">
        <label>Fin Maturité</label>
        <input 
          type="number" 
          v-model.number="localMaturiteEnd"
          :min="localJeunesseEnd + 1"
          :max="localApogeeEnd - 1"
          @change="updateFromInput"
        />
      </div>
      <div class="input-group">
        <label>Fin Apogée</label>
        <input 
          type="number" 
          v-model.number="localApogeeEnd"
          :min="localMaturiteEnd + 1"
          :max="props.vintageYear + 50"
          @change="updateFromInput"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

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
  editable: {
    type: Boolean,
    default: true
  },
  showInputs: {
    type: Boolean,
    default: false
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showCurrentYear: {
    type: Boolean,
    default: true
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:jeunesseEnd', 'update:maturiteEnd', 'update:apogeeEnd'])

// Valeurs locales
const localJeunesseEnd = ref(props.jeunesseEnd || props.vintageYear + 1)
const localMaturiteEnd = ref(props.maturiteEnd || props.vintageYear + 4)
const localApogeeEnd = ref(props.apogeeEnd || props.vintageYear + 9)

// Année actuelle
const currentYear = new Date().getFullYear()

// Durée fixe du déclin (5 ans)
const DECLIN_DURATION = 5

// Calcul de la fin de la timeline (apogée + 5 ans)
const timelineEndYear = computed(() => localApogeeEnd.value + DECLIN_DURATION)
const TIMELINE_DURATION = computed(() => timelineEndYear.value - props.vintageYear)

// Drag state
const draggingHandle = ref(null)

// Calculs des années
const jeunesseEndYear = computed(() => localJeunesseEnd.value)
const maturiteEndYear = computed(() => localMaturiteEnd.value)
const apogeeEndYear = computed(() => localApogeeEnd.value)

// Calculs des pourcentages
const jeunessePercent = computed(() => {
  const duration = jeunesseEndYear.value - props.vintageYear
  return Math.min(100, Math.max(0, (duration / TIMELINE_DURATION.value) * 100))
})

const maturitePercent = computed(() => {
  const duration = maturiteEndYear.value - jeunesseEndYear.value
  return Math.min(100, Math.max(0, (duration / TIMELINE_DURATION.value) * 100))
})

const apogeePercent = computed(() => {
  const duration = apogeeEndYear.value - maturiteEndYear.value
  return Math.min(100, Math.max(0, (duration / TIMELINE_DURATION.value) * 100))
})

const declinPercent = computed(() => {
  const duration = DECLIN_DURATION
  return Math.min(100, Math.max(0, (duration / TIMELINE_DURATION.value) * 100))
})

const currentYearPercent = computed(() => {
  const elapsed = currentYear - props.vintageYear
  return (elapsed / TIMELINE_DURATION.value) * 100
})

// Détermination de la phase actuelle
const currentPhase = computed(() => {
  if (currentYear <= jeunesseEndYear.value) return 'jeunesse'
  if (currentYear <= maturiteEndYear.value) return 'maturite'
  if (currentYear <= apogeeEndYear.value) return 'apogee'
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

// Drag handlers
const startDrag = (handle, event) => {
  if (!props.editable) return
  
  draggingHandle.value = handle
  event.preventDefault()
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  document.addEventListener('touchmove', onDrag)
  document.addEventListener('touchend', stopDrag)
}

const onDrag = (event) => {
  if (!draggingHandle.value) return
  
  const track = event.target.closest('.timeline-track')
  if (!track) return
  
  const rect = track.getBoundingClientRect()
  const clientX = event.touches ? event.touches[0].clientX : event.clientX
  const x = clientX - rect.left
  const percent = Math.max(0, Math.min(100, (x / rect.width) * 100))
  const yearsFromVintage = Math.round((percent / 100) * TIMELINE_DURATION.value)
  const year = props.vintageYear + yearsFromVintage
  
  if (draggingHandle.value === 'jeunesseEnd') {
    const minYear = props.vintageYear + 1
    const maxYear = localMaturiteEnd.value - 1
    localJeunesseEnd.value = Math.max(minYear, Math.min(maxYear, year))
  } else if (draggingHandle.value === 'maturiteEnd') {
    const minYear = localJeunesseEnd.value + 1
    const maxYear = localApogeeEnd.value - 1
    localMaturiteEnd.value = Math.max(minYear, Math.min(maxYear, year))
  } else if (draggingHandle.value === 'apogeeEnd') {
    const minYear = localMaturiteEnd.value + 1
    const maxYear = timelineEndYear.value
    localApogeeEnd.value = Math.max(minYear, Math.min(maxYear, year))
  }
}

const stopDrag = () => {
  draggingHandle.value = null
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
  
  emit('update:jeunesseEnd', localJeunesseEnd.value)
  emit('update:maturiteEnd', localMaturiteEnd.value)
  emit('update:apogeeEnd', localApogeeEnd.value)
}

const updateFromInput = () => {
  if (localJeunesseEnd.value <= props.vintageYear) {
    localJeunesseEnd.value = props.vintageYear + 1
  }
  if (localJeunesseEnd.value >= localMaturiteEnd.value) {
    localMaturiteEnd.value = localJeunesseEnd.value + 1
  }
  if (localMaturiteEnd.value >= localApogeeEnd.value) {
    localApogeeEnd.value = localMaturiteEnd.value + 1
  }
  if (localApogeeEnd.value > props.vintageYear + 50) {
    localApogeeEnd.value = props.vintageYear + 50
  }
  
  emit('update:jeunesseEnd', localJeunesseEnd.value)
  emit('update:maturiteEnd', localMaturiteEnd.value)
  emit('update:apogeeEnd', localApogeeEnd.value)
}

// Watch props
watch(() => props.jeunesseEnd, (newVal) => {
  if (newVal) localJeunesseEnd.value = newVal
})

watch(() => props.maturiteEnd, (newVal) => {
  if (newVal) localMaturiteEnd.value = newVal
})

watch(() => props.apogeeEnd, (newVal) => {
  if (newVal) localApogeeEnd.value = newVal
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('touchmove', onDrag)
  document.removeEventListener('touchend', stopDrag)
})
</script>

<style scoped>
.wine-phase-timeline {
  width: 100%;
}

/* Header minimaliste */
.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}

.current-phase-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.phase-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.current-phase-badge.phase-jeunesse {
  background: color-mix(in srgb, var(--accent-blue) 15%, transparent);
  color: var(--accent-blue);
}

.current-phase-badge.phase-maturite {
  background: color-mix(in srgb, var(--accent-green) 15%, transparent);
  color: var(--accent-green);
}

.current-phase-badge.phase-apogee {
  background: color-mix(in srgb, var(--accent-purple) 15%, transparent);
  color: var(--accent-purple);
}

.current-phase-badge.phase-declin {
  background: color-mix(in srgb, var(--accent-red) 15%, transparent);
  color: var(--accent-red);
}

.year-range {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-family: monospace;
}

/* Container */
.timeline-container {
  background: transparent;
  border-radius: 8px;
  padding: 0.5rem;
}

.timeline-container.container-compact {
  padding: 0;
}

/* Track de timeline - HAUTEUR 24px */
.timeline-track {
  position: relative;
  height: 24px;
  margin-bottom: 0.5rem;
}

.timeline-background {
  position: absolute;
  inset: 0;
  background: color-mix(in srgb, var(--text-primary) 5%, transparent);
  border-radius: 4px;
}

/* Segments */
.phase-segments {
  position: absolute;
  inset: 2px;
  display: flex;
  border-radius: 3px;
  overflow: hidden;
}

.phase-segment {
  height: 100%;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.phase-segment.jeunesse {
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent-blue) 70%, transparent) 0%, color-mix(in srgb, var(--accent-blue) 50%, transparent) 100%);
}

.phase-segment.maturite {
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent-green) 70%, transparent) 0%, color-mix(in srgb, var(--accent-green) 50%, transparent) 100%);
}

.phase-segment.apogee {
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent-purple) 70%, transparent) 0%, color-mix(in srgb, var(--accent-purple) 50%, transparent) 100%);
}

.phase-segment.declin {
  background: linear-gradient(90deg, color-mix(in srgb, var(--accent-red) 70%, transparent) 0%, color-mix(in srgb, var(--accent-red) 50%, transparent) 100%);
}

.segment-name {
  font-size: 0.6rem;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

/* Ligne des dates sous la barre */
.phase-dates-row {
  display: flex;
  position: relative;
  padding-right: 24px;
  margin-top: 4px;
}

.phase-date-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  position: relative;
  min-width: 30px;
}

.phase-year {
  font-size: 0.6rem;
  color: var(--text-muted);
  font-family: monospace;
}

.phase-end-year {
  position: absolute;
  right: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* Mode compact */
.timeline-compact .timeline-track {
  height: 20px;
}

.timeline-compact .phase-segments {
  inset: 2px;
}

.timeline-compact .segment-name {
  font-size: 0.5rem;
}

.timeline-compact .phase-year {
  font-size: 0.55rem;
}

/* Marqueur année actuelle */
.current-year-marker {
  position: absolute;
  top: -4px;
  bottom: -4px;
  width: 2px;
  transform: translateX(-50%);
  z-index: 10;
}

.marker-arrow {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid var(--text-primary);
}

.marker-line {
  position: absolute;
  top: 6px;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  background: var(--text-primary);
  opacity: 0.8;
}

.marker-label {
  position: absolute;
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--text-primary);
  color: var(--bg-primary);
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  font-size: 0.6rem;
  font-weight: 600;
  white-space: nowrap;
}

/* Curseurs */
.timeline-handles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.timeline-handle {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 16px;
  height: 28px;
  cursor: ew-resize;
  pointer-events: auto;
  z-index: 20;
}

.handle-visual {
  width: 100%;
  height: 100%;
  background: var(--bg-surface);
  border: 2px solid var(--accent-blue);
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.timeline-handle:hover .handle-visual {
  transform: scale(1.1);
}

.timeline-handle.dragging .handle-visual {
  background: var(--accent-blue);
}

.handle-tooltip {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--bg-elevated);
  color: var(--text-primary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.2s ease;
  border: 1px solid var(--border-default);
}

.timeline-handle:hover .handle-tooltip,
.timeline-handle.dragging .handle-tooltip {
  opacity: 1;
}

/* Inputs */
.timeline-inputs {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-default);
}

.input-group {
  flex: 1;
}

.input-group label {
  display: block;
  font-size: 0.7rem;
  color: var(--text-secondary);
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.input-group input {
  width: 100%;
  background: var(--bg-bg);
  border: 1px solid var(--border-default);
  border-radius: 6px;
  padding: 0.5rem;
  color: var(--text-primary);
  font-size: 0.8rem;
}

.input-group input:focus {
  outline: none;
  border-color: var(--accent-blue);
}
</style>
