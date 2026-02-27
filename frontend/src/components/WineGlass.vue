<template>
  <div class="wine-glass-container">
    <svg viewBox="0 0 100 120" class="wine-glass" :class="{ 'animate-pour': animate }">
      <!-- Pied du verre -->
      <path d="M45 75 L45 110 Q45 115 50 115 Q55 115 55 110 L55 75" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="3" 
            stroke-linecap="round"/>
      
      <!-- Base du verre -->
      <ellipse cx="50" cy="115" rx="15" ry="4" 
               fill="none" 
               stroke="currentColor" 
               stroke-width="3"/>
      
      <!-- Bol du verre (contour) - légèrement incliné -->
      <path d="M25 30 Q25 75 50 75 Q75 75 75 30" 
            fill="none" 
            stroke="currentColor" 
            stroke-width="3" 
            stroke-linecap="round"/>
      
      <!-- Ouverture supérieure du verre -->
      <ellipse cx="50" cy="30" rx="25" ry="5" 
               fill="none" 
               stroke="currentColor" 
               stroke-width="3"/>
      
      <!-- Vin dans le verre avec ondulation -->
      <defs>
        <linearGradient id="wineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" style="stop-color:#8B1A2D;stop-opacity:0.95" />
          <stop offset="50%" style="stop-color:#722F37;stop-opacity:0.98" />
          <stop offset="100%" style="stop-color:#4A0404;stop-opacity:1" />
        </linearGradient>
        
        <filter id="wineGlow">
          <feGaussianBlur stdDeviation="1" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <!-- Surface du vin avec ondulation -->
      <path d="M28 48 Q35 45 42 48 Q50 52 58 48 Q65 44 72 48 L70 65 Q70 72 50 72 Q30 72 30 65 Z" 
            fill="url(#wineGradient)" 
            filter="url(#wineGlow)"/>
      
      <!-- Reflets sur le verre -->
      <path d="M30 35 Q30 50 35 60" 
            fill="none" 
            stroke="rgba(255,255,255,0.3)" 
            stroke-width="2" 
            stroke-linecap="round"/>
      
      <ellipse cx="38" cy="52" rx="3" ry="5" 
               fill="rgba(255,255,255,0.15)"/>
      
      <!-- Ondulations sur le vin -->
      <path d="M35 50 Q40 47 45 50 Q50 53 55 50 Q60 47 65 50" 
            fill="none" 
            stroke="rgba(139,26,45,0.5)" 
            stroke-width="1.5"/>
      
      <path d="M38 55 Q43 52 48 55 Q53 58 58 55 Q63 52 68 55" 
            fill="none" 
            stroke="rgba(74,4,4,0.3)" 
            stroke-width="1"/>
      
      <!-- Reflet sur le vin -->
      <ellipse cx="45" cy="55" rx="8" ry="3" 
               fill="rgba(255,200,200,0.2)" 
               transform="rotate(-10 45 55)"/>
    </svg>
  </div>
</template>

<script>
export default {
  name: 'WineGlass',
  props: {
    animate: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.wine-glass-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.wine-glass {
  width: 2rem;
  height: 2.4rem;
  color: currentColor;
  transition: transform 0.3s ease;
}

@media (min-width: 640px) {
  .wine-glass {
    width: 2.5rem;
    height: 3rem;
  }
}

.wine-glass:hover {
  transform: rotate(-5deg) scale(1.1);
}

@keyframes winePour {
  0% {
    clip-path: polygon(0 100%, 100% 100%, 100% 100%, 0 100%);
  }
  50% {
    clip-path: polygon(0 50%, 100% 50%, 100% 100%, 0 100%);
  }
  100% {
    clip-path: polygon(0 0%, 100% 0%, 100% 100%, 0 100%);
  }
}

.animate-pour svg path[fill^="url"] {
  animation: winePour 2s ease-in-out;
}
</style>
