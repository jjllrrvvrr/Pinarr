<template>
  <main class="max-w-7xl mx-auto px-4 py-8 pb-20">
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 mb-6 text-gh-text-secondary text-sm">
      <router-link to="/" class="hover:text-gh-accent transition-fast">Accueil</router-link>
      <span>/</span>
      <span class="text-gh-text">{{ isEditing ? 'Modifier' : 'Ajouter' }}</span>
    </div>

    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-xl font-bold text-gh-text">{{ isEditing ? 'Modifier le vin' : 'Nouveau vin' }}</h1>
      <p class="text-sm text-gh-text-secondary">Remplissez les informations ci-dessous</p>
    </div>

    <!-- Formulaire -->
    <form @submit.prevent="saveBottle" class="space-y-6">
      
      <!-- Carte 1: Informations essentielles -->
      <BaseCard title="Informations essentielles">
        <template #icon>
          <ArchiveBoxIcon class="w-5 h-5 text-gh-accent" />
        </template>
        
        <div class="space-y-4">
          <!-- Nom du vin -->
          <div class="relative">
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <TagIcon class="w-4 h-4" />
              Nom du vin <span class="text-gh-accent-red">*</span>
            </label>
            <div class="relative">
              <input 
                v-model="form.name" 
                @input="onNameInput" 
                @blur="hideSuggestions" 
                @focus="showSuggestionsIfResults"
                type="text"
                required
                class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text placeholder-gh-text-muted focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
                :class="{ 'border-gh-accent-red': errors.name }"
                placeholder="ex: Château Margaux"
                autocomplete="off"
              />
              <MagnifyingGlassIcon v-if="!isEditing && showSuggestions" class="w-5 h-5 text-gh-accent absolute right-3 top-3.5 animate-pulse" />
            </div>
            <p v-if="errors.name" class="mt-1 text-sm text-gh-accent-red flex items-center gap-1">
              <ExclamationCircleIcon class="w-4 h-4" />
              {{ errors.name }}
            </p>
            
            <!-- Suggestions -->
            <div v-if="!isEditing && showSuggestions && searchResults.length > 0" 
                 class="absolute z-50 w-full mt-1 bg-gh-surface border border-gh-border rounded-card shadow-lg max-h-60 overflow-y-auto">
              <div class="px-3 py-2 text-xs text-gh-text-secondary border-b border-gh-border">
                Vins similaires déjà présents :
              </div>
              <div v-for="wine in searchResults" :key="wine.id" 
                   @click.stop="selectWine(wine)"
                   class="flex items-center gap-3 px-3 py-2 hover:bg-gh-elevated cursor-pointer border-b border-gh-border last:border-0 transition-fast">
                <div class="w-10 h-10 rounded bg-gh-bg border border-gh-border flex items-center justify-center overflow-hidden">
                  <img v-if="wine.image_path" :src="getImageUrl(wine.image_path)" class="w-full h-full object-cover" @error="$event.target.style.display='none'">
                  <ArchiveBoxIcon v-else class="w-5 h-5 text-gh-text-muted" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm text-gh-text font-medium truncate">{{ wine.name }}</div>
                  <div class="text-xs text-gh-text-secondary">
                    {{ wine.year || 'Millésime inconnu' }}
                    <span v-if="wine.domaine" class="text-gh-accent"> • {{ wine.domaine }}</span>
                  </div>
                </div>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="wine.quantity > 0 ? 'bg-gh-accent-green/20 text-gh-accent-green-text' : 'bg-gh-accent-red/20 text-gh-accent-red'">
                  {{ wine.quantity }} en cave
                </span>
              </div>
            </div>
          </div>

          <!-- Type de vin -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <TypeIconSVG class="w-4 h-4" />
              Type <span class="text-gh-accent-red">*</span>
            </label>
            <WineTypeSelector v-model="form.type" />
            <p v-if="errors.type" class="mt-1 text-sm text-gh-accent-red flex items-center gap-1">
              <ExclamationCircleIcon class="w-4 h-4" />
              {{ errors.type }}
            </p>
          </div>

          <!-- Millésime -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <CalendarIcon class="w-4 h-4" />
              Millésime
            </label>
            <input 
              v-model="form.year" 
              type="number" 
              required
              min="1900"
              :max="new Date().getFullYear() + 1"
              class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
              :class="{ 'border-gh-accent-red': errors.year }"
              placeholder="2024"
            />
            <p v-if="errors.year" class="mt-1 text-sm text-gh-accent-red">{{ errors.year }}</p>
          </div>
        </div>
      </BaseCard>

      <!-- Carte 2: Origine -->
      <BaseCard title="Origine">
        <template #icon>
          <MapPinIcon class="w-5 h-5 text-gh-accent" />
        </template>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Pays -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <FlagIconSVG class="w-4 h-4" />
              Pays
            </label>
            <select v-model="form.country" 
                    class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast appearance-none cursor-pointer">
              <option :value="null">Sélectionner un pays</option>
              <option v-for="c in countries" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <!-- Région -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <LandscapeIconSVG class="w-4 h-4" />
              Région
            </label>
            <input 
              v-model="form.region" 
              type="text"
              class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text placeholder-gh-text-muted focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
              placeholder="ex: Bordeaux, Bourgogne..."
            />
          </div>

          <!-- Domaine -->
          <div class="md:col-span-2">
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <CrestIconSVG class="w-4 h-4" />
              Domaine viticole
            </label>
            <input 
              v-model="form.domaine" 
              type="text"
              class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text placeholder-gh-text-muted focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
              placeholder="ex: Domaine de la Romanée-Conti"
            />
          </div>
        </div>
      </BaseCard>

      <!-- Carte 3: Caractéristiques -->
      <BaseCard title="Caractéristiques">
        <template #icon>
          <InfoTagIconSVG class="w-5 h-5 text-gh-accent" />
        </template>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Cépages -->
          <div class="md:col-span-2">
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <GrapeIconSVG class="w-4 h-4" />
              Cépages
            </label>
            <input 
              v-model="form.cepage" 
              type="text"
              class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text placeholder-gh-text-muted focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
              placeholder="ex: Merlot, Cabernet Sauvignon"
            />
          </div>

          <!-- Degré d'alcool -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <ThermometerIconSVG class="w-4 h-4" />
              Degré (%)
            </label>
            <input 
              v-model="form.alcohol" 
              type="number" 
              step="0.5"
              min="0"
              max="100"
              class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
              placeholder="13.5"
            />
          </div>

          <!-- Contenance -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <RulerIconSVG class="w-4 h-4" />
              Contenance
            </label>
            <input 
              v-model="form.size" 
              type="text"
              class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
              placeholder="75cl"
            />
          </div>

          <!-- Description -->
          <div class="md:col-span-2">
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
              <DescriptionIconSVG class="w-4 h-4" />
              Description
            </label>
            <textarea 
              v-model="form.description" 
              rows="3"
              class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text placeholder-gh-text-muted focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast resize-none"
              placeholder="Notes de dégustation, caractéristiques..."
            ></textarea>
          </div>
        </div>
      </BaseCard>

      <!-- Carte 4: Gestion & Évaluation -->
      <BaseCard title="Gestion & Évaluation">
        <template #icon>
          <ClockIconSVG class="w-5 h-5 text-gh-accent" />
        </template>
        
        <div class="space-y-6">
          <!-- Position dans la cave -->
          <div>
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-3">
              <MapPinIcon class="w-4 h-4" />
              Position dans la cave
            </label>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <select v-model="form.position_cave_id" @change="onCaveChange" 
                      class="bg-gh-bg border border-gh-border rounded-card p-2.5 text-gh-text focus:border-gh-accent outline-none transition-fast text-sm">
                <option :value="null">Cave...</option>
                <option v-for="cave in caves" :key="cave.id" :value="cave.id">{{ cave.name }}</option>
              </select>
              <select v-model="form.position_column_id" @change="onColumnChange" :disabled="!form.position_cave_id"
                      class="bg-gh-bg border border-gh-border rounded-card p-2.5 text-gh-text focus:border-gh-accent outline-none transition-fast text-sm disabled:opacity-50">
                <option :value="null">Colonne...</option>
                <option v-for="col in availableColumns" :key="col.id" :value="col.id">{{ col.name }}</option>
              </select>
              <select v-model="form.position_row_id" @change="onRowChange" :disabled="!form.position_column_id"
                      class="bg-gh-bg border border-gh-border rounded-card p-2.5 text-gh-text focus:border-gh-accent outline-none transition-fast text-sm disabled:opacity-50">
                <option :value="null">Étagère...</option>
                <option v-for="row in availableRows" :key="row.id" :value="row.id">{{ row.name }}</option>
              </select>
              <select v-model="form.position_id" :disabled="!form.position_row_id"
                      class="bg-gh-bg border border-gh-border rounded-card p-2.5 text-gh-text focus:border-gh-accent outline-none transition-fast text-sm disabled:opacity-50">
                <option :value="null">Position...</option>
                <option v-for="pos in availablePositions" :key="pos.id" :value="pos.id" :disabled="pos.occupied && pos.bottle_id !== form.id">
                  L{{ pos.line }}/{{ pos.position }}{{ pos.occupied ? ' (occupée)' : '' }}
                </option>
              </select>
            </div>
          </div>

          <!-- Ligne 1: Quantité | Prix | Note -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Quantité -->
            <div>
              <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
                <QuantityIconSVG class="w-4 h-4" />
                Quantité
              </label>
              <input 
                v-model="form.quantity" 
                type="number" 
                min="0"
                class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
              />
            </div>

            <!-- Prix -->
            <div>
              <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
                <CurrencyDollarIcon class="w-4 h-4" />
                Prix (€)
              </label>
              <input 
                v-model="form.price" 
                type="number" 
                step="0.01"
                min="0"
                class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
                placeholder="45.00"
              />
            </div>

            <!-- Note -->
            <div>
              <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
                <StarIcon class="w-4 h-4" />
                Note
              </label>
              <StarRating v-model="form.rating" />
            </div>
          </div>

          <!-- Ligne 2: Phases de développement (ligne complète) -->
          <div v-if="form.year" class="mt-6">
            <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-3">
              <ClockIconSVG class="w-4 h-4" />
              Phases de développement
            </label>
            <WinePhaseTimeline
              :vintage-year="form.year"
              v-model:jeunesse-end="form.jeunesse_end"
              v-model:maturite-end="form.maturite_end"
              v-model:apogee-end="form.apogee_end"
              :editable="true"
              :show-inputs="true"
            />
          </div>

          <!-- Ligne 3: Tags | Lien externe -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <!-- Tags -->
            <div>
              <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
                <TagIcon class="w-4 h-4" />
                Tags
              </label>
              <div class="relative">
                <input
                  v-model="tagInput"
                  @keydown.enter.prevent="addTag"
                  @input="handleTagInput"
                  class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text placeholder-gh-text-muted focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
                  placeholder="Ajouter des tags séparés par virgule"
                />
              </div>
              <div class="flex flex-wrap gap-2 mt-2">
                <span v-for="tag in currentTags" :key="tag" 
                      class="inline-flex items-center gap-1 bg-gh-elevated px-3 py-1 rounded-tag text-sm text-gh-text border border-gh-border">
                  {{ tag }}
                  <button @click="removeTag(tag)" class="text-gh-text-secondary hover:text-gh-accent-red transition-fast">
                    <XMarkIcon class="w-4 h-4" />
                  </button>
                </span>
              </div>
            </div>

            <!-- Lien externe -->
            <div>
              <label class="flex items-center gap-2 text-sm font-medium text-gh-text-secondary mb-2">
                <ExternalLinkIconSVG class="w-4 h-4" />
                Lien externe
              </label>
              <input 
                v-model="form.buy_link" 
                type="url"
                class="w-full bg-gh-bg border border-gh-border rounded-card p-3 text-gh-text placeholder-gh-text-muted focus:border-gh-accent focus:ring-1 focus:ring-gh-accent outline-none transition-fast"
                placeholder="https://..."
              />
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Carte 5: Photo -->
      <BaseCard title="Photo">
        <template #icon>
          <CameraIconSVG class="w-5 h-5 text-gh-accent" />
        </template>
        
        <div>
          <div v-if="imagePreview" class="relative inline-block mb-4">
            <img :src="imagePreview" class="w-32 h-32 object-cover rounded-card border border-gh-border" />
            <button @click="removeImage" 
                    class="absolute -top-2 -right-2 bg-gh-accent-red text-white rounded-full w-7 h-7 flex items-center justify-center hover:bg-gh-accent-red-hover transition-fast shadow-md">
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
          
          <div v-else 
               @dragover.prevent="dragOver = true" 
               @dragleave.prevent="dragOver = false" 
               @drop.prevent="handleDrop"
               :class="[
                 'border-2 border-dashed rounded-card p-8 text-center transition-fast cursor-pointer',
                 dragOver ? 'border-gh-accent bg-gh-accent/10' : 'border-gh-border hover:border-gh-accent'
               ]"
               @click="triggerFileInput">
            <CameraIconSVG class="w-10 h-10 mx-auto text-gh-text-secondary mb-3" />
            <p class="text-sm text-gh-text-secondary mb-1">Glissez une photo ou cliquez</p>
            <p class="text-xs text-gh-text-muted">Toutes les images sont converties en WebP (optimisé)</p>
            <input type="file" ref="fileInput" @change="handleImageUpload" accept="image/*" capture="environment" class="hidden" />
          </div>
          
          <div v-if="!imagePreview" class="mt-3">
            <button type="button" @click="showUrlInput = !showUrlInput" 
                    class="text-sm text-gh-accent hover:text-gh-accent hover:underline transition-fast">
              Utiliser une URL
            </button>
            <div v-if="showUrlInput" class="mt-2 flex gap-2">
              <input v-model="imageUrl" type="url" placeholder="https://..." 
                     :disabled="isLoadingImage"
                     class="flex-1 bg-gh-bg border border-gh-border rounded-card p-2.5 text-gh-text text-sm" />
              <button type="button" @click="useImageUrl" 
                      :disabled="isLoadingImage || !imageUrl"
                      class="px-4 py-2 bg-gh-accent-green text-white rounded-card text-sm font-medium hover:bg-gh-accent-green-hover disabled:opacity-50 disabled:cursor-not-allowed transition-fast flex items-center gap-2">
                <span v-if="isLoadingImage" class="animate-spin">
                  <ArrowPathIcon class="w-4 h-4" />
                </span>
                <span v-else>OK</span>
              </button>
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Boutons d'action -->
      <div class="flex flex-col sm:flex-row justify-between gap-3 pt-4 border-t border-gh-border">
        <router-link to="/" 
                     class="px-6 py-3 rounded-card text-gh-text-secondary hover:bg-gh-elevated transition-fast font-medium text-center border border-gh-border">
          Annuler
        </router-link>
        <div class="flex gap-3">
          <button type="submit" 
                  :disabled="isSubmitting"
                  class="flex-1 sm:flex-none px-8 py-3 rounded-card bg-gh-accent-green hover:bg-gh-accent-green-hover disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium transition-fast flex items-center justify-center gap-2">
            <span v-if="isSubmitting" class="animate-spin">
              <ArrowPathIcon class="w-5 h-5" />
            </span>
            <span v-else>{{ isEditing ? 'Enregistrer' : 'Ajouter' }}</span>
          </button>
        </div>
      </div>
    </form>

    <!-- Modal doublon -->
    <div v-if="showDuplicateModal" 
         class="fixed inset-0 bg-gh-overlay backdrop-blur-sm z-modal flex items-center justify-center p-4"
         @click="showDuplicateModal = false">
      <div class="bg-gh-surface p-6 rounded-card max-w-md w-full border border-gh-border shadow-lg" 
           @click.stop>
        <h2 class="text-lg font-bold text-gh-text mb-2 flex items-center gap-2">
          <ExclamationTriangleIcon class="w-5 h-5 text-gh-accent-orange" />
          Bouteille similaire trouvée
        </h2>
        <p class="text-gh-text-secondary text-sm mb-4">
          Une ou plusieurs bouteilles avec le même nom et la même millésime existent déjà.
        </p>
        <div class="space-y-2 mb-4 max-h-40 overflow-y-auto">
          <div v-for="dup in duplicateMatches" :key="dup.id" 
               class="p-3 bg-gh-bg rounded-card border border-gh-border flex items-center justify-between">
            <div>
              <span class="text-gh-text font-medium">{{ dup.name }}</span>
              <span class="text-gh-text-secondary text-xs ml-2">({{ dup.year }})</span>
            </div>
            <span :class="[
              'text-xs px-2 py-0.5 rounded-tag',
              dup.quantity > 0 ? 'bg-gh-accent-green/20 text-gh-accent-green-text' : 'bg-gh-accent-red/20 text-gh-accent-red'
            ]">
              {{ dup.quantity > 0 ? `${dup.quantity} en cave` : 'Épuisé' }}
            </span>
          </div>
        </div>
        <div class="flex gap-2">
          <button @click="editDuplicate" 
                  class="flex-1 px-4 py-2.5 bg-gh-accent text-white rounded-card text-sm font-medium hover:bg-gh-accent/90 transition-fast">
            Éditer l'existante
          </button>
          <button @click="forceCreate" 
                  class="flex-1 px-4 py-2.5 bg-gh-elevated text-gh-text rounded-card text-sm font-medium hover:bg-gh-border transition-fast border border-gh-border">
            Créer quand même
          </button>
        </div>
        <button @click="showDuplicateModal = false" 
                class="w-full mt-2 text-sm text-gh-text-secondary hover:text-gh-text transition-fast">
          Annuler
        </button>
      </div>
    </div>
  </main>

  <!-- Modal de retrait des positions -->
  <RemovePositionModal
    :show="showRemoveModal"
    :total="positionsToRemove"
    :removed="positionsRemoved"
    :selected="selectedPositionId"
    :positions="form?.positions || []"
    :processing="isProcessing"
    :bottle="form"
    @select="selectPosition"
    @confirm="confirmRemovePosition"
    @cancel="cancelRemovePosition"
  />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import QrcodeVue from 'qrcode.vue'
import { 
  ArchiveBoxIcon, CalendarIcon, BeakerIcon, 
  MapPinIcon, TagIcon, PhotoIcon, StarIcon, 
  HeartIcon, ShoppingCartIcon, FlagIcon as FlagIconHero,
  MagnifyingGlassIcon, DocumentDuplicateIcon,
  ExclamationCircleIcon, PlusIcon, MinusIcon,
  GlobeAltIcon, CurrencyDollarIcon, ChevronLeftIcon, CheckCircleIcon,
  ArrowPathIcon, TrashIcon
} from '@heroicons/vue/24/solid'
import {
  FlagIcon as FlagIconSVG,
  GrapeIcon as GrapeIconSVG,
  LandscapeIcon as LandscapeIconSVG,
  CrestIcon as CrestIconSVG,
  InfoTagIcon as InfoTagIconSVG,
  ThermometerIcon as ThermometerIconSVG,
  RulerIcon as RulerIconSVG,
  QuantityIcon as QuantityIconSVG,
  WineIcon as WineIconSVG,
  CameraIcon as CameraIconSVG,
  LabelIcon as LabelIconSVG,
  TypeIcon as TypeIconSVG,
  DescriptionIcon as DescriptionIconSVG,
  ClockIcon as ClockIconSVG,
  ExternalLinkIcon as ExternalLinkIconSVG
} from '@/components/icons'
import BaseCard from '../components/ui/BaseCard.vue'
import WineTypeSelector from '../components/WineTypeSelector.vue'
import StarRating from '../components/StarRating.vue'
import config from '../config.js'
import { apiRequest } from '../services/api.js'
import RemovePositionModal from '../components/RemovePositionModal.vue'
import WinePhaseTimeline from '../components/WinePhaseTimeline.vue'
import { useQuantityManager } from '../composables/useQuantityManager.js'

const route = useRoute()
const router = useRouter()

const API_URL = '/bottles'
const API_UPLOAD_URL = `${config.API_BASE_URL}/upload`
const CAVES_URL = '/caves'

const countries = ['France', 'Italie', 'Espagne', 'Portugal', 'Allemagne', 'États-Unis', 'Argentine', 'Chili', 'Australie', 'Nouvelle-Zélande', 'Afrique du Sud', 'Autre']

// État
const isEditing = ref(false)
const isSubmitting = ref(false)
const errors = ref({})
const caves = ref([])
const availableColumns = ref([])
const availableRows = ref([])
const availablePositions = ref([])

// Image
const imagePreview = ref(null)
const imageFile = ref(null)
const showUrlInput = ref(false)
const imageUrl = ref('')
const isLoadingImage = ref(false)
const dragOver = ref(false)
const fileInput = ref(null)

// Recherche
const showSuggestions = ref(false)
const searchResults = ref([])
const searchTimeout = ref(null)

// Doublons
const showDuplicateModal = ref(false)
const duplicateMatches = ref([])

// Tags
const tagInput = ref('')

// Formulaire
const defaultForm = {
  id: null,
  name: '', 
  domaine: '', 
  country: null,
  year: new Date().getFullYear(), 
  type: 'Rouge',
  region: '', 
  cepage: '', 
  alcohol: null, 
  size: '75cl',
  apogee_start: null,
  apogee_end: null,
  // Phases de développement
  jeunesse_end: null,
  maturite_end: null,
  location: '',
  quantity: 1, 
  price: null, 
  description: '', 
  rating: 0, 
  tags: '',
  is_favorite: false, 
  buy_link: '', 
  image_path: null,
  position_id: null,
  position_cave_id: null,
  position_column_id: null,
  position_row_id: null
}

const form = ref({ ...defaultForm })

// Gestion du retrait des positions
const { 
  showRemoveModal,
  positionsToRemove,
  positionsRemoved,
  selectedPositionId,
  isProcessing,
  checkQuantityDecrease,
  confirmRemove: confirmRemovePosition,
  cancelRemove: cancelRemovePosition,
  selectPosition
} = useQuantityManager()

// Watch sur la quantité pour détecter les diminutions en mode édition
watch(() => form.value.quantity, (newVal, oldVal) => {
  if (isEditing.value && newVal < oldVal) {
    // Récupérer les positions actuelles de la bouteille
    const bottleData = {
      id: form.value.id,
      quantity: oldVal,
      positions: form.value.positions || []
    }
    
    checkQuantityDecrease(
      bottleData,
      newVal,
      oldVal,
      async (finalQuantity) => {
        // Callback de succès - la quantité sera mise à jour par le watch
        console.log('Positions retirées, quantité finale:', finalQuantity)
      },
      (originalQuantity) => {
        // Callback d'annulation - restaurer la quantité
        form.value.quantity = originalQuantity
      }
    )
  }
})

const currentTags = computed({
  get: () => form.value.tags ? form.value.tags.split(',').map(t => t.trim()).filter(t => t) : [],
  set: (val) => { form.value.tags = val.join(',') }
})

// Méthodes
const processTags = (text) => {
  if (!text) return
  
  const parts = text.split(',').map(t => t.trim()).filter(t => t)
  if (parts.length === 0) return
  
  // Récupérer les tags existants
  const existingTags = currentTags.value
  const newTags = [...existingTags]
  
  // Ajouter chaque nouveau tag s'il n'existe pas déjà
  parts.forEach(tag => {
    if (!newTags.includes(tag)) {
      newTags.push(tag)
    }
  })
  
  // Mettre à jour form.value.tags une seule fois avec tous les tags
  form.value.tags = newTags.join(',')
}

const handleTagInput = () => {
  // Détecter si une virgule a été tapée
  if (tagInput.value.includes(',')) {
    processTags(tagInput.value)
    // Garder le texte après la dernière virgule (peut être vide)
    const lastCommaIndex = tagInput.value.lastIndexOf(',')
    const afterLastComma = tagInput.value.substring(lastCommaIndex + 1)
    tagInput.value = afterLastComma
  }
}

const addTag = () => {
  // Ne traiter que s'il y a du texte non vide
  if (tagInput.value.trim()) {
    processTags(tagInput.value)
  }
  tagInput.value = ''
}

const removeTag = (tag) => {
  const newTags = currentTags.value.filter(t => t !== tag)
  form.value.tags = newTags.join(',')
}

const validateForm = () => {
  const newErrors = {}
  if (!form.value.name?.trim()) newErrors.name = 'Le nom est obligatoire'
  if (form.value.year && (form.value.year < 1900 || form.value.year > 2100)) {
    newErrors.year = 'Millésime invalide'
  }
  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

const saveBottle = async (force = false) => {
  if (!validateForm()) return
  
  // Valider les tags restants dans l'input avant sauvegarde
  processTags(tagInput.value)
  tagInput.value = ''
  
  isSubmitting.value = true
  
  try {
    if (!isEditing.value && !force) {
      const matches = await checkDuplicate()
      if (matches.length > 0) {
        duplicateMatches.value = matches
        showDuplicateModal.value = true
        isSubmitting.value = false
        return
      }
    }

    let imagePath = form.value.image_path
    
    // Si une URL est entrée mais pas encore traitée, télécharger automatiquement
    if (imageUrl.value && !imagePath) {
      try {
        isLoadingImage.value = true
        const response = await apiRequest('/upload-from-url', {
          method: 'POST',
          body: JSON.stringify({ url: imageUrl.value })
        })
        imagePath = response.path
        form.value.image_path = response.path
        imageUrl.value = ''
      } catch (error) {
        alert('Erreur lors du téléchargement de l\'image: ' + error.message)
        isSubmitting.value = false
        isLoadingImage.value = false
        return
      } finally {
        isLoadingImage.value = false
      }
    }
    
    if (imageFile.value) {
      imagePath = await uploadImage()
    }

    const payload = {
      name: form.value.name,
      domaine: form.value.domaine || null,
      country: form.value.country || null,
      year: parseInt(form.value.year) || null,
      type: form.value.type || "Rouge",
      region: form.value.region || null,
      cepage: form.value.cepage || null,
      alcohol: parseFloat(form.value.alcohol) || null,
      size: form.value.size || "75cl",
      apogee_start: parseInt(form.value.apogee_start) || null,
      apogee_end: parseInt(form.value.apogee_end) || null,
      jeunesse_end: parseInt(form.value.jeunesse_end) || null,
      maturite_end: parseInt(form.value.maturite_end) || null,
      location: form.value.location || null,
      quantity: parseInt(form.value.quantity) || 1,
      price: parseFloat(form.value.price) || null,
      description: form.value.description || null,
      rating: parseInt(form.value.rating) || null,
      tags: form.value.tags || null,
      is_favorite: form.value.is_favorite || false,
      buy_link: form.value.buy_link || null,
      image_path: imagePath
    }

    const method = isEditing.value ? 'PUT' : 'POST'
    const url = isEditing.value ? `${API_URL}/${form.value.id}` : API_URL
    const savedBottle = await apiRequest(url, {
      method,
      body: JSON.stringify(payload)
    })
    
    if (form.value.position_id) {
      await apiRequest(`/positions/${form.value.position_id}`, {
        method: 'PUT',
        body: JSON.stringify({ bottle_id: savedBottle.id })
      })
    }
    
    router.push(`/wine/${savedBottle.id}`)
  } catch (e) {
    alert("Erreur: " + e.message)
  } finally {
    isSubmitting.value = false
  }
}

const checkDuplicate = async () => {
  if (!form.value.name || !form.value.year) return []
  try {
    const data = await apiRequest(`${API_URL}/check-duplicate/?name=${encodeURIComponent(form.value.name)}&year=${form.value.year}`)
    return data.matches || []
  } catch (e) { console.error(e) }
  return []
}

const uploadImage = async () => {
  if (!imageFile.value) return null
  const formData = new FormData()
  formData.append('file', imageFile.value)
  
  const headers = {}
  const token = sessionStorage.getItem('auth_token')
  if (token) headers['Authorization'] = `Bearer ${token}`
  
  try {
    const res = await fetch(API_UPLOAD_URL, { 
      method: 'POST', 
      headers,
      body: formData 
    })
    if (res.ok) {
      const data = await res.json()
      return data.path
    }
  } catch (e) { console.error(e) }
  return null
}

const compressImage = (file) => {
  return new Promise((resolve) => {
    // Si c'est une image HEIC/HEIF ou si le fichier fait moins de 1MB, on ne compresse pas
    if (file.type === 'image/heic' || file.type === 'image/heif' || file.size < 1024 * 1024) {
      resolve(file)
      return
    }

    const img = new Image()
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    img.onload = () => {
      // Calculer les nouvelles dimensions (max 1920px)
      let width = img.width
      let height = img.height
      const maxSize = 1920
      
      if (width > maxSize || height > maxSize) {
        if (width > height) {
          height = (height / width) * maxSize
          width = maxSize
        } else {
          width = (width / height) * maxSize
          height = maxSize
        }
      }
      
      canvas.width = width
      canvas.height = height
      ctx.drawImage(img, 0, 0, width, height)
      
      // Convertir en blob avec compression (qualité 0.8)
      canvas.toBlob((blob) => {
        if (blob) {
          const compressedFile = new File([blob], file.name.replace(/\.heic$/i, '.jpg').replace(/\.heif$/i, '.jpg'), {
            type: 'image/jpeg',
            lastModified: Date.now()
          })
          resolve(compressedFile)
        } else {
          resolve(file)
        }
      }, 'image/jpeg', 0.8)
    }
    
    img.onerror = () => resolve(file)
    
    const reader = new FileReader()
    reader.onload = (e) => { img.src = e.target.result }
    reader.readAsDataURL(file)
  })
}

const handleImageUpload = async (e) => {
  const file = e.target.files[0]
  if (file) {
    // Comprimer l'image avant de l'utiliser
    const compressedFile = await compressImage(file)
    imageFile.value = compressedFile
    const reader = new FileReader()
    reader.onload = (ev) => { imagePreview.value = ev.target.result }
    reader.readAsDataURL(compressedFile)
  }
}

const handleDrop = async (e) => {
  dragOver.value = false
  const file = e.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    const compressedFile = await compressImage(file)
    imageFile.value = compressedFile
    const reader = new FileReader()
    reader.onload = (ev) => { imagePreview.value = ev.target.result }
    reader.readAsDataURL(compressedFile)
  }
}

const triggerFileInput = () => fileInput.value?.click()

const removeImage = () => {
  imageFile.value = null
  imagePreview.value = null
  form.value.image_path = null
}

const useImageUrl = async () => {
  if (!imageUrl.value) return
  
  isLoadingImage.value = true
  
  try {
    // Appeler l'API backend pour télécharger l'image depuis l'URL
    const response = await apiRequest('/upload-from-url', {
      method: 'POST',
      body: JSON.stringify({ url: imageUrl.value })
    })
    
    // Utiliser le chemin local retourné par le backend
    imagePreview.value = response.path
    form.value.image_path = response.path
    imageFile.value = null
    showUrlInput.value = false
    imageUrl.value = ''
    
  } catch (error) {
    console.error('Erreur lors du téléchargement de l\'image:', error)
    alert('Erreur lors du téléchargement: ' + error.message)
  } finally {
    isLoadingImage.value = false
  }
}

const fetchBottle = async (id) => {
  try {
    const bottle = await apiRequest(`${API_URL}/${id}`)
    form.value = { ...defaultForm, ...bottle }
    
    // Stocker les positions pour la gestion du retrait
    if (bottle.positions) {
      form.value.positions = bottle.positions
    }
    
    if (bottle.image_path) {
      imagePreview.value = bottle.image_path.startsWith('http') 
        ? bottle.image_path 
        : bottle.image_path.includes('uploads') 
          ? bottle.image_path 
          : `${config.API_BASE_URL}${bottle.image_path}`
    }
    if (bottle.position) {
      form.value.position_row_id = bottle.position.row_id
      if (caves.value.length > 0) {
        for (const cave of caves.value) {
          for (const col of cave.columns || []) {
            const row = col.rows?.find(r => r.id === bottle.position.row_id)
            if (row) {
              form.value.position_cave_id = cave.id
              form.value.position_column_id = col.id
              availableColumns.value = cave.columns || []
              availableRows.value = col.rows || []
              await loadPositions(bottle.position.row_id)
              form.value.position_id = bottle.position.id
              break
            }
          }
        }
      }
    }
    isEditing.value = true
  } catch (e) { console.error(e) }
}

const fetchCaves = async () => {
  try {
    caves.value = await apiRequest(CAVES_URL)
  } catch (e) { console.error(e) }
}

const onCaveChange = () => {
  form.value.position_column_id = null
  form.value.position_row_id = null
  form.value.position_id = null
  availableRows.value = []
  availablePositions.value = []
  const cave = caves.value.find(c => c.id === form.value.position_cave_id)
  availableColumns.value = cave?.columns || []
}

const onColumnChange = () => {
  form.value.position_row_id = null
  form.value.position_id = null
  availablePositions.value = []
  const cave = caves.value.find(c => c.id === form.value.position_cave_id)
  const col = cave?.columns?.find(c => c.id === form.value.position_column_id)
  availableRows.value = col?.rows || []
}

const onRowChange = async () => {
  form.value.position_id = null
  if (form.value.position_row_id) {
    await loadPositions(form.value.position_row_id)
  } else {
    availablePositions.value = []
  }
}

const loadPositions = async (rowId) => {
  try {
    const data = await apiRequest(`/rows/${rowId}/positions/`)
    availablePositions.value = data.map(p => ({
      id: p.id,
      line: p.line,
      position: p.position,
      occupied: !!p.bottle_at_position,
      bottle_id: p.bottle_at_position?.id
    }))
  } catch (e) { console.error(e) }
}

const searchSimilarWines = async (name) => {
  if (!name || name.length < 2) return
  try {
    const data = await apiRequest(`/bottles/search/?q=${encodeURIComponent(name)}`)
    searchResults.value = data.results || []
    showSuggestions.value = searchResults.value.length > 0
  } catch (error) {
    console.error('Erreur recherche:', error)
    searchResults.value = []
    showSuggestions.value = false
  }
}

const onNameInput = () => {
  if (isEditing.value) return
  if (searchTimeout.value) clearTimeout(searchTimeout.value)
  if (!form.value.name || form.value.name.length < 2) {
    searchResults.value = []
    showSuggestions.value = false
    return
  }
  searchTimeout.value = setTimeout(() => searchSimilarWines(form.value.name), 300)
}

const hideSuggestions = () => {
  setTimeout(() => { showSuggestions.value = false }, 200)
}

const showSuggestionsIfResults = () => {
  if (isEditing.value) return
  if (searchResults.value.length > 0) showSuggestions.value = true
}

const selectWine = (wine) => {
  router.push({ name: 'wine-detail', params: { id: wine.id } })
}

const editDuplicate = () => {
  if (duplicateMatches.value.length > 0) {
    router.push(`/edit/${duplicateMatches.value[0].id}`)
  }
}

const forceCreate = () => {
  showDuplicateModal.value = false
  saveBottle(true)
}

const getImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  if (path.includes('uploads')) return path
  return `${config.API_BASE_URL}${path}`
}

// Watch
watch(() => form.value.name, onNameInput)

onMounted(async () => {
  await fetchCaves()
  if (route.params.id) await fetchBottle(route.params.id)
})
</script>