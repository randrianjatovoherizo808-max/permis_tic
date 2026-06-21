<template>
  <div class="ls-wrap" :class="variant" ref="wrapRef">
    <button class="ls-btn" @click.stop="open = !open">
      <span>{{ current.flag }}</span>
      <span class="ls-label">{{ current.label }}</span>
      <svg class="ls-chevron" :class="{ open }" width="11" height="11"
           viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <transition name="ls-drop">
      <ul v-if="open" class="ls-dropdown">
        <li
          v-for="l in LANGUES"
          :key="l.code"
          class="ls-option"
          :class="{ active: l.code === langActif }"
          @click="pick(l.code)"
        >
          <span>{{ l.flag }}</span>
          <span>{{ l.label }}</span>
          <span v-if="l.code === langActif" class="ls-check">✓</span>
        </li>
      </ul>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useLangStore } from '../store/lang'
import { storeToRefs } from 'pinia'

defineProps({ variant: { type: String, default: 'light' } })

// langues est un tableau statique dans le store — on le lit directement
const langStore = useLangStore()
const { langActif } = storeToRefs(langStore)

// Tableau statique — pas besoin de ref
const LANGUES = [
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'en', label: 'English',  flag: '🇬🇧' },
  { code: 'mg', label: 'Malagasy', flag: '🇲🇬' },
]

const open    = ref(false)
const wrapRef = ref(null)

const current = computed(() =>
  LANGUES.find(l => l.code === langActif.value) ?? { flag: '🇫🇷', label: 'Français' }
)

function pick(code) {
  langStore.setLang(code)
  open.value = false
}

function onOutside(e) {
  if (wrapRef.value && !wrapRef.value.contains(e.target)) open.value = false
}
onMounted(()  => document.addEventListener('click', onOutside))
onUnmounted(() => document.removeEventListener('click', onOutside))
</script>

<style scoped>
.ls-wrap { position: relative; display: inline-block; }

/* ── Variante light (sur fond teal/coloré) ── */
.ls-wrap.light .ls-btn {
  background: rgba(255,255,255,0.15);
  border: 1.5px solid rgba(255,255,255,0.45);
  color: white;
}
.ls-wrap.light .ls-btn:hover { background: rgba(255,255,255,0.28); }

/* ── Variante dark (sur fond blanc) ── */
.ls-wrap.dark .ls-btn {
  background: #f0f4f8;
  border: 1.5px solid #d0d5dd;
  color: #333;
}
.ls-wrap.dark .ls-btn:hover { background: #e0f7fa; color: #006064; }

.ls-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 13px; border-radius: 20px;
  cursor: pointer; font-size: 13px; font-weight: 600;
  transition: background .18s, color .18s;
  white-space: nowrap; line-height: 1;
}

.ls-label { display: inline-block; }
.ls-chevron { transition: transform .18s; flex-shrink: 0; }
.ls-chevron.open { transform: rotate(180deg); }

/* ── Dropdown ── */
.ls-dropdown {
  position: absolute; top: calc(100% + 6px); right: 0;
  background: #fff; border-radius: 12px;
  box-shadow: 0 8px 28px rgba(0,0,0,0.13);
  border: 1px solid #eee;
  list-style: none; margin: 0; padding: 5px;
  min-width: 148px; z-index: 9999;
}

.ls-option {
  display: flex; align-items: center; gap: 9px;
  padding: 9px 13px; border-radius: 8px;
  cursor: pointer; font-size: 13.5px; color: #333;
  transition: background .14s;
}
.ls-option:hover  { background: #e0f7fa; }
.ls-option.active { background: #b2ebf2; color: #006064; font-weight: 700; }
.ls-check { margin-left: auto; color: #0097A7; font-weight: 900; font-size: 12px; }

/* ── Animation ── */
.ls-drop-enter-active, .ls-drop-leave-active { transition: opacity .14s, transform .14s; }
.ls-drop-enter-from, .ls-drop-leave-to       { opacity: 0; transform: translateY(-5px); }
</style>