/**
 * Utilitaire de génération d'étiquettes 3×5cm @ 300dpi
 * Utilisé à la fois pour téléchargement individuel et batch ZIP
 */

/**
 * Génère un Blob PNG d'une étiquette 3×5cm à partir d'un canvas QR source
 * @param {HTMLCanvasElement} qrCanvas - Canvas du QR code déjà généré
 * @param {Object} bottleInfo - { name, year, apogee_end, maturite_end, jeunesse_end }
 * @param {string} qrCode - Code QR texte
 * @returns {Promise<Blob>} - Blob PNG
 */
export async function generateLabelBlob(qrCanvas, bottleInfo, qrCode) {
  const dpi   = 300
  const cmToPx = d => Math.round(d * dpi / 2.54)
  const W     = cmToPx(3)
  const H     = cmToPx(5)

  const offscreen = document.createElement('canvas')
  offscreen.width  = W
  offscreen.height = H
  const ctx = offscreen.getContext('2d')

  drawLabel(ctx, qrCanvas, bottleInfo, qrCode, W, H)

  return new Promise(resolve => {
    offscreen.toBlob(resolve, 'image/png')
  })
}

function drawLabel(ctx, qrCanvas, b, qrCode, W, H) {
  const padX = 20
  const maxW = W - padX * 2
  const cx   = W / 2

  // Fond blanc + bordure noire
  ctx.fillStyle = '#FFFFFF'
  ctx.fillRect(0, 0, W, H)
  ctx.strokeStyle = '#000000'
  ctx.lineWidth   = 2
  ctx.strokeRect(1, 1, W - 2, H - 2)

  // QR code centré en haut
  const qrSize = 200
  const qrX    = (W - qrSize) / 2
  const qrY    = 30
  ctx.drawImage(qrCanvas, qrX, qrY, qrSize, qrSize)

  // Zone texte
  let y = qrY + qrSize + 28

  ctx.textAlign = 'center'
  ctx.fillStyle = '#000000'

  // Nom du vin
  ctx.font = `bold 24px sans-serif`
  ctx.fillText(wrapText(ctx, b?.name || 'Vin', maxW), cx, y)

  // Millésime
  y += 36
  if (b?.year) {
    ctx.font = '22px sans-serif'
    ctx.fillStyle = '#333333'
    ctx.fillText(String(b.year), cx, y)
    y += 32
  }

  // Phases
  const phaseText = fmtPhase(b)
  if (phaseText) {
    ctx.font = '18px sans-serif'
    ctx.fillStyle = '#555555'
    ctx.fillText(phaseText, cx, y)
    y += 30
  }

  // Code QR
  ctx.font = 'bold 18px monospace'
  ctx.fillStyle = '#888888'
  ctx.fillText(qrCode, cx, y + 10)
}

function fmtPhase(b) {
  if (!b) return ''
  if (b.apogee_end) {
    return `Apogée : ${b.maturite_end || '?'} – ${b.apogee_end}`
  }
  if (b.maturite_end) {
    return `Maturité : ${b.jeunesse_end || '?'} – ${b.maturite_end}`
  }
  if (b.jeunesse_end) {
    return `Jeunesse jusqu'à ${b.jeunesse_end}`
  }
  return ''
}

function wrapText(ctx, text, maxWidth) {
  if (ctx.measureText(text).width <= maxWidth) return text
  let len = text.length
  while (len > 0 && ctx.measureText(text.slice(0, len) + '…').width > maxWidth) len--
  return text.slice(0, len) + '…'
}

/**
 * Télécharge un Blob via un lien temporaire
 * @param {Blob} blob
 * @param {string} filename
 */
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
