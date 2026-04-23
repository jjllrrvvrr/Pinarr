<template>
  <div v-if="show" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-gh-surface rounded-xl border border-gh-border max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-gh-border flex items-center justify-between">
        <div>
          <h2 class="text-lg font-bold text-gh-text">Étiquettes QR</h2>
          <p class="text-sm text-gh-text-secondary">{{ physicalBottles.length }} étiquette(s) à imprimer (3cm x 5cm)</p>
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="printLabels"
            class="flex items-center gap-2 px-4 py-2 bg-gh-accent-green hover:bg-gh-accent-green-hover text-white rounded-lg transition text-sm font-medium"
          >
            <PrinterIcon class="w-4 h-4" />
            Imprimer
          </button>
          <button 
            @click="$emit('close')"
            class="p-2 text-gh-text-secondary hover:text-gh-text transition"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Preview -->
      <div class="flex-1 overflow-auto p-8 bg-gh-bg">
        <div class="print-container">
          <div 
            v-for="(bottle, index) in physicalBottles" 
            :key="bottle.id"
            class="label-3x5"
          >
            <div class="label-qr">
              <qrcode-vue 
                :value="getQrUrl(bottle.qr_code)" 
                :size="80" 
                level="H"
                render-as="svg"
              />
            </div>
            
              <div class="label-info">
              <div class="label-name">{{ bottleInfo.name }}</div>
              <div class="label-year">{{ bottleInfo.year || 'Sans millésime' }}</div>
              
              <div v-if="hasPhases" class="label-phases">
                <div v-if="bottleInfo.apogee_end">
                  Apogée: {{ bottleInfo.maturite_end || '?' }} – {{ bottleInfo.apogee_end }}
                </div>
                <div v-else-if="bottleInfo.maturite_end">
                  Maturité: {{ bottleInfo.jeunesse_end || '?' }} – {{ bottleInfo.maturite_end }}
                </div>
              </div>
              
              <div class="label-code">
                {{ bottle.qr_code }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Instructions -->
      <div class="p-4 border-t border-gh-border bg-gh-surface">
        <div class="flex items-start gap-3 text-sm text-gh-text-secondary">
          <InformationCircleIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p><strong class="text-gh-text">Instructions d'impression :</strong></p>
            <ul class="mt-1 space-y-1 list-disc list-inside">
              <li>Utilisez des étiquettes de 3cm x 5cm</li>
              <li>Désactivez les en-têtes et pieds de page dans les options d'impression</li>
              <li>Collez chaque étiquette sur sa bouteille physique correspondante</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import QrcodeVue from 'qrcode.vue'
import { 
  XMarkIcon, 
  PrinterIcon,
  InformationCircleIcon 
} from '@heroicons/vue/24/solid'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  physicalBottles: {
    type: Array,
    default: () => []
  },
  bottleInfo: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['close'])

const hasPhases = computed(() => {
  return props.bottleInfo.jeunesse_end || 
         props.bottleInfo.maturite_end || 
         props.bottleInfo.apogee_end
})

const getQrUrl = (qrCode) => {
  return `${window.location.origin}/bottle/${qrCode}`
}

const printLabels = () => {
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    alert('Veuillez autoriser les popups pour l\'impression')
    return
  }

  const labelsHtml = props.physicalBottles.map(bottle => `
    <div class="label-3x5">
      <div class="label-qr">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(getQrUrl(bottle.qr_code))}" />
      </div>
      <div class="label-info">
        <div class="label-name">${props.bottleInfo.name || ''}</div>
        <div class="label-year">${props.bottleInfo.year || 'Sans millésime'}</div>
        ${hasPhases.value ? `
        <div class="label-phases">
          ${props.bottleInfo.apogee_end
            ? `Apogée: ${props.bottleInfo.maturite_end || '?'} – ${props.bottleInfo.apogee_end}`
            : props.bottleInfo.maturite_end
              ? `Maturité: ${props.bottleInfo.jeunesse_end || '?'} – ${props.bottleInfo.maturite_end}`
              : ''}
        </div>` : ''}
        <div class="label-code">${bottle.qr_code}</div>
      </div>
    </div>
  `).join('')

  printWindow.document.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Étiquettes QR - ${props.bottleInfo.name || ''}</title>
      <style>
        body {
          margin: 0;
          padding: 0;
          background: white;
          font-family: system-ui, -apple-system, sans-serif;
        }
        .print-container {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5cm;
          padding: 0.5cm;
          justify-content: center;
        }
        .label-3x5 {
          width: 3cm;
          height: 5cm;
          page-break-after: always;
          page-break-inside: avoid;
          border: 1px solid #000;
          background: white;
          color: black;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 0.3cm;
          box-sizing: border-box;
          margin: 0;
        }
        .label-3x5:last-child {
          page-break-after: auto;
        }
        .label-qr {
          margin-bottom: 0.2cm;
        }
        .label-qr img {
          width: 1.8cm;
          height: 1.8cm;
        }
        .label-info {
          text-align: center;
          width: 100%;
        }
        .label-name {
          font-weight: bold;
          font-size: 8pt;
          line-height: 1.2;
          margin-bottom: 0.1cm;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          max-width: 2.4cm;
        }
        .label-year {
          font-size: 8pt;
          margin-bottom: 0.1cm;
        }
        .label-phases {
          font-size: 6pt;
          color: #666;
          line-height: 1.2;
        }
        .label-code {
          font-size: 6pt;
          color: #999;
          margin-top: 0.1cm;
          font-family: monospace;
        }
        @page {
          margin: 0;
          size: auto;
        }
      </style>
    </head>
    <body>
      <div class="print-container">
        ${labelsHtml}
      </div>
    </body>
    </html>
  `)
  printWindow.document.close()
  setTimeout(() => {
    printWindow.print()
  }, 250)
}
</script>

<style scoped>
.print-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

.label-3x5 {
  width: 3cm;
  height: 5cm;
  border: 1px dashed var(--border-default);
  background: var(--bg-primary);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.3cm;
  box-sizing: border-box;
}

.label-qr {
  margin-bottom: 0.2cm;
}

.label-info {
  text-align: center;
  width: 100%;
}

.label-name {
  font-weight: bold;
  font-size: 8pt;
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 0.1cm;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 2.4cm;
}

.label-year {
  font-size: 8pt;
  color: var(--text-secondary);
  margin-bottom: 0.1cm;
}

.label-phases {
  font-size: 6pt;
  color: var(--text-muted);
  line-height: 1.2;
}

.label-code {
  font-size: 6pt;
  color: var(--text-muted);
  margin-top: 0.1cm;
  font-family: monospace;
}
</style>
