<template>
  <div>
    <!-- QR "source" invisible render-as canvas -->
    <div ref="qrSource" style="position:absolute;left:-9999px;top:-9999px;">
      <qrcode-vue
        :value="value"
        :size="256"
        level="H"
        render-as="canvas"
      />
    </div>
    <!-- Canvas de l'étiquette 3×5cm @ 300dpi -->
    <canvas ref="labelCanvas" style="display:none" />
    <slot :download="download" />
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import QrcodeVue from 'qrcode.vue'

const props = defineProps({
  value:   { type: String,  required: true },       // URL QR
  qrCode:  { type: String,  required: true },       // AB12CD34
  filename:{ type: String,  default: 'etiquette.png' },
  bottleInfo: { type: Object, default: () => ({}) }
})

const qrSource   = ref(null)
const labelCanvas = ref(null)

/* ── helpers texte ── */
const fmtPhase = (b) => {
  if (b.apogee_end) {
    return `Apogée : ${b.maturite_end || '?'} – ${b.apogee_end}`
  } else if (b.maturite_end) {
    return `Maturité : ${b.jeunesse_end || '?'} – ${b.maturite_end}`
  } else if (b.jeunesse_end) {
    return `Jeunesse jusqu'à ${b.jeunesse_end}`
  }
  return ''
}

const wrapText = (ctx, text, maxWidth) => {
  if (ctx.measureText(text).width <= maxWidth) return text
  let len = text.length
  while (len > 0 && ctx.measureText(text.slice(0, len) + '…').width > maxWidth) len--
  return text.slice(0, len) + '…'
}

/* ── dessin de l'étiquette ── */
const drawLabel = (qrCanvas) => {
  const DPI  = 300
  const W    = Math.round(3 * DPI / 2.54)   // 3  cm → px
  const H    = Math.round(5 * DPI / 2.54)   // 5  cm → px
  const padX = 20
  const padY = 20

  const cvs = labelCanvas.value
  cvs.width  = W
  cvs.height = H
  const ctx  = cvs.getContext('2d')

  /* fond blanc + bordure noire */
  ctx.fillStyle = '#FFFFFF'
  ctx.fillRect(0, 0, W, H)
  ctx.strokeStyle = '#000000'
  ctx.lineWidth   = 2
  ctx.strokeRect(1, 1, W - 2, H - 2)

  /* QR code centré en haut */
  const qrSize = 200
  const qrX    = (W - qrSize) / 2
  const qrY    = 30
  ctx.drawImage(qrCanvas, qrX, qrY, qrSize, qrSize)

  /* zone texte */
  const textY = qrY + qrSize + 24
  const maxW  = W - padX * 2
  const cx    = W / 2

  /* ─ Nom du vin ─ */
  ctx.textAlign = 'center'
  ctx.fillStyle = '#000000'
  ctx.font      = 'bold 24px sans-serif'
  ctx.fillText(wrapText(ctx, props.bottleInfo.name || 'Vin', maxW), cx, textY)

  /* ─ Millésime ─ */
  let y = textY + 34
  if (props.bottleInfo.year) {
    ctx.font = '22px sans-serif'
    ctx.fillStyle = '#333333'
    ctx.fillText(String(props.bottleInfo.year), cx, y)
    y += 30
  }

  /* ─ Phases ─ */
  const phaseText = fmtPhase(props.bottleInfo)
  if (phaseText) {
    ctx.font = '18px sans-serif'
    ctx.fillStyle = '#555555'
    ctx.fillText(phaseText, cx, y)
    y += 28
  }

  /* ─ QR code texte ─ */
  ctx.font = 'bold 18px monospace'
  ctx.fillStyle = '#888888'
  ctx.fillText(props.qrCode, cx, y + 10)
}

const download = async () => {
  await nextTick()

  /* récupère le canvas généré par qrcode.vue */
  const sourceCanvas = qrSource.value?.querySelector('canvas')
  if (!sourceCanvas) return

  drawLabel(sourceCanvas)

  const dataUrl = labelCanvas.value.toDataURL('image/png')
  const a       = document.createElement('a')
  a.href        = dataUrl
  a.download    = props.filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>
