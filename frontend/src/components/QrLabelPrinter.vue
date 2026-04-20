<template>
  <div v-if="show" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-[#161b22] rounded-xl border border-[#30363d] max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="p-4 border-b border-[#30363d] flex items-center justify-between">
        <div>
          <h2 class="text-lg font-bold text-white">Étiquettes QR</h2>
          <p class="text-sm text-[#8b949e]">{{ physicalBottles.length }} étiquette(s) à imprimer (3cm x 5cm)</p>
        </div>
        <div class="flex items-center gap-2">
          <button 
            @click="printLabels"
            class="flex items-center gap-2 px-4 py-2 bg-[#238636] hover:bg-[#2ea043] text-white rounded-lg transition text-sm font-medium"
          >
            <PrinterIcon class="w-4 h-4" />
            Imprimer
          </button>
          <button 
            @click="$emit('close')"
            class="p-2 text-[#8b949e] hover:text-white transition"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Preview -->
      <div class="flex-1 overflow-auto p-8 bg-[#0d1117]">
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
                <div v-if="bottleInfo.jeunesse_end">
                  Maturité: {{ bottleInfo.jeunesse_end }}
                </div>
                <div v-if="bottleInfo.apogee_start || bottleInfo.apogee_end">
                  Apogée: {{ bottleInfo.apogee_start || '?' }}-{{ bottleInfo.apogee_end || '?' }}
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
      <div class="p-4 border-t border-[#30363d] bg-[#161b22]">
        <div class="flex items-start gap-3 text-sm text-[#8b949e]">
          <InformationCircleIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p><strong class="text-white">Instructions d'impression :</strong></p>
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

  <!-- Print-only styles -->
  <style>
    @media print {
      /* Cacher tout sauf les étiquettes */
      body * {
        visibility: hidden !important;
      }
      
      .print-container,
      .print-container * {
        visibility: visible !important;
      }
      
      .print-container {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
      }
      
      /* Taille exacte des étiquettes */
      .label-3x5 {
        width: 3cm !important;
        height: 5cm !important;
        page-break-after: always !important;
        page-break-inside: avoid !important;
        border: 1px solid #000 !important;
        background: white !important;
        color: black !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.3cm !important;
        box-sizing: border-box !important;
        margin: 0 !important;
      }
      
      /* Masquer le dernier page-break */
      .label-3x5:last-child {
        page-break-after: auto !important;
      }
      
      /* Styles des éléments internes */
      .label-qr {
        margin-bottom: 0.2cm !important;
      }
      
      .label-qr svg {
        width: 1.8cm !important;
        height: 1.8cm !important;
      }
      
      .label-info {
        text-align: center !important;
        width: 100% !important;
      }
      
      .label-name {
        font-weight: bold !important;
        font-size: 8pt !important;
        line-height: 1.2 !important;
        margin-bottom: 0.1cm !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 2.4cm !important;
      }
      
      .label-year {
        font-size: 8pt !important;
        margin-bottom: 0.1cm !important;
      }
      
      .label-phases {
        font-size: 6pt !important;
        color: #666 !important;
        line-height: 1.2 !important;
      }
      
      .label-code {
        font-size: 6pt !important;
        color: #999 !important;
        margin-top: 0.1cm !important;
        font-family: monospace !important;
      }
      
      /* Marges de page */
      @page {
        margin: 0;
        size: auto;
      }
    }
  </style>
</template>

<script setup>
import { computed } from 'vue'
import QrcodeVue from 'qrcode.vue'
import { 
  XMarkIcon, 
  PrinterIcon,
  InformationCircleIcon 
} from '@heroicons/vue/24/solid'
import config from '../config.js'

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
         props.bottleInfo.apogee_start || 
         props.bottleInfo.apogee_end
})

const getQrUrl = (qrCode) => {
  return `${config.API_BASE_URL}/bottle/${qrCode}`
}

const printLabels = () => {
  window.print()
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
  border: 1px dashed #30363d;
  background: #0d1117;
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
  color: white;
  line-height: 1.2;
  margin-bottom: 0.1cm;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 2.4cm;
}

.label-year {
  font-size: 8pt;
  color: #8b949e;
  margin-bottom: 0.1cm;
}

.label-phases {
  font-size: 6pt;
  color: #6e7681;
  line-height: 1.2;
}

.label-code {
  font-size: 6pt;
  color: #484f58;
  margin-top: 0.1cm;
  font-family: monospace;
}
</style>
