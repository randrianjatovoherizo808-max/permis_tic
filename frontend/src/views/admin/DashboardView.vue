<template>
  <div>
    <h2 class="page-title">📊 Tableau de bord</h2>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card" v-for="k in kpis" :key="k.label" :style="{ borderColor: k.color }">
        <div class="kpi-icon">{{ k.icon }}</div>
        <div class="kpi-val" :style="{ color: k.color }">{{ k.val }}</div>
        <div class="kpi-label">{{ k.label }}</div>
      </div>
    </div>

    <!-- Graphique + Inscriptions récentes -->
    <div class="dashboard-grid">
      <!-- Diagramme en bâtons : formations par niveau -->
      <div class="card chart-card">
        <h3 class="card-title">📊 Formations par niveau</h3>
        <div class="bar-chart-wrap">
          <div class="bar-chart">
            <!-- Grille de fond -->
            <div class="grid-lines">
              <div
                v-for="line in gridLines"
                :key="line"
                class="grid-line"
                :style="{ bottom: (line / maxBarValue * 100) + '%' }"
              >
                <span class="grid-label">{{ line }}</span>
              </div>
            </div>

            <!-- Barres -->
            <div class="bars">
              <div
                v-for="bar in barData"
                :key="bar.label"
                class="bar-group"
                @mouseenter="hoveredBar = bar.label"
                @mouseleave="hoveredBar = null"
              >
                <!-- Tooltip -->
                <div v-if="hoveredBar === bar.label" class="bar-tooltip">
                  {{ bar.count }} formation{{ bar.count > 1 ? 's' : '' }}
                </div>

                <!-- Barre -->
                <div
                  class="bar"
                  :style="{
                    height: maxBarValue > 0 ? (bar.count / maxBarValue * 220) + 'px' : '0px',
                    background: bar.color,
                    boxShadow: hoveredBar === bar.label ? '0 4px 20px ' + bar.color + '66' : 'none'
                  }"
                >
                  <span class="bar-value">{{ bar.count }}</span>
                </div>

                <!-- Label -->
                <div class="bar-label">
                  <span class="bar-level" :style="{ color: bar.color }">{{ bar.label }}</span>
                  <span class="bar-desc">{{ bar.desc }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Légende -->
          <div class="bar-legend">
            <div v-for="bar in barData" :key="bar.label" class="legend-item">
              <span class="legend-dot" :style="{ background: bar.color }"></span>
              <span class="legend-label">Niveau {{ bar.label }} — {{ bar.desc }}</span>
              <span class="legend-val" :style="{ color: bar.color }">{{ bar.count }}</span>
            </div>
            <div class="legend-total">
              <span class="legend-label" style="font-weight:700">Total formations</span>
              <span class="legend-val" style="color: var(--primary, #0097A7)">
                {{ niveauxData.A + niveauxData.B + niveauxData.C }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Inscriptions en attente -->
      <div class="card">
        <h3 class="card-title">⏳ Inscriptions en attente</h3>
        <div v-if="inscAttente.length === 0" class="empty">
          <p>Aucune inscription en attente. ✅</p>
        </div>
        <div v-else>
          <div v-for="insc in inscAttente.slice(0, 5)" :key="insc.id" class="insc-item">
            <div class="insc-avatar">
              <img
                v-if="insc.utilisateur_photo"
                :src="insc.utilisateur_photo"
                :alt="insc.utilisateur_nom"
                class="insc-avatar-img"
                referrerpolicy="no-referrer"
              />
              <span v-else>{{ initiales(insc.utilisateur_nom) }}</span>
            </div>
            <div class="insc-info">
              <div class="insc-name">{{ insc.utilisateur_nom }}</div>
              <div class="insc-meta">{{ insc.formation_nom }} — Niveau {{ insc.formation_niveau }}</div>
            </div>
            <div class="insc-actions">
              <button class="btn btn-primary btn-xs" @click="confirmer(insc.id)">✅</button>
              <button class="btn btn-danger btn-xs" @click="rejeter(insc.id)">❌</button>
            </div>
          </div>
          <RouterLink to="/admin/inscriptions" class="voir-plus">Voir toutes →</RouterLink>
        </div>
      </div>
    </div>

    <!-- Activité récente -->
    <div class="card" style="margin-top:20px;">
      <h3 class="card-title">🔔 Activité récente</h3>
      <div v-if="loading" class="empty">Chargement…</div>
      <div v-else-if="activite.length === 0" class="empty">Aucune activité récente.</div>
      <div v-else class="activite-list">
        <div v-for="a in activite" :key="a.id" class="activite-item">
          <span class="act-icon">{{ a.icon }}</span>
          <div class="act-body">
            <span class="act-msg">{{ a.message }}</span>
            <span class="act-date">{{ formatDate(a.date) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../../services/api'

const router      = useRouter()
const loading     = ref(true)
const stats       = ref({ formations: 0, apprenants: 0, formateurs: 0, inscriptions_en_attente: 0 })
const inscAttente = ref([])
const activite    = ref([])
const niveauxData = ref({ A: 0, B: 0, C: 0 })
const hoveredBar  = ref(null)

// ── Données pour les barres ───────────────────────────────────────────────
const barData = computed(() => [
  { label: 'A', desc: 'Débutant',      count: niveauxData.value.A, color: '#2196F3' },
  { label: 'B', desc: 'Intermédiaire', count: niveauxData.value.B, color: '#FF9800' },
  { label: 'C', desc: 'Avancé',        count: niveauxData.value.C, color: '#9C27B0' },
])

const maxBarValue = computed(() =>
  Math.max(niveauxData.value.A, niveauxData.value.B, niveauxData.value.C, 1)
)

const gridLines = computed(() => {
  const max = maxBarValue.value
  const step = Math.ceil(max / 4) || 1
  const lines = []
  for (let i = step; i <= max; i += step) lines.push(i)
  return lines
})

// ── KPIs ─────────────────────────────────────────────────────────────────
const kpis = computed(() => [
  { icon: '📘', label: 'Formations',  val: stats.value.formations,              color: '#2196F3' },
  { icon: '🎓', label: 'Apprenants',  val: stats.value.apprenants,              color: '#0097A7' },
  { icon: '👨‍🏫', label: 'Formateurs', val: stats.value.formateurs,              color: '#FF9800' },
  { icon: '⏳', label: 'En attente',  val: stats.value.inscriptions_en_attente, color: '#F44336' },
])

function initiales(nom) {
  return (nom || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

function formatDate(d) {
  if (!d) return '—'
  const date = new Date(d)
  if (isNaN(date)) return '—'
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function confirmer(id) {
  if (!confirm('Confirmer cette inscription ?')) return
  await api.post(`/inscriptions/${id}/confirmer/`)
  charger()
}

async function rejeter(id) {
  if (!confirm('Rejeter cette inscription ?')) return
  await api.post(`/inscriptions/${id}/rejeter/`)
  charger()
}

async function charger() {
  try {
    const { data: s } = await api.get('/stats/')
    Object.assign(stats.value, s)

    const { data: iData } = await api.get('/inscriptions/', { params: { statut: 'en_attente' } })
    inscAttente.value = iData.results || iData

    const { data: fData } = await api.get('/formations/')
    const formations = fData.results || fData
    niveauxData.value = {
      A: formations.filter(f => f.niveau === 'A').length,
      B: formations.filter(f => f.niveau === 'B').length,
      C: formations.filter(f => f.niveau === 'C').length,
    }

    try {
      const { data: notifs } = await api.get('/notifications/')
      activite.value = (notifs.results || notifs).slice(0, 8).map(n => ({
        id: n.id,
        icon: n.type === 'success' ? '✅' : n.type === 'warning' ? '⚠️' : 'ℹ️',
        message: n.message,
        date: n.created_at || n.date || null,
      }))
    } catch { /* silencieux */ }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(charger)
</script>

<style scoped>
.page-title { margin-bottom: 24px; font-size: 1.4rem; }

/* ── KPI Cards ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.kpi-card {
  background: white;
  border-radius: 18px;
  padding: 22px;
  box-shadow: var(--shadow);
  border-left: 4px solid;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: transform 0.2s;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-icon  { font-size: 1.8rem; }
.kpi-val   { font-size: 2rem; font-weight: 900; }
.kpi-label { font-size: 0.8rem; color: var(--gray); font-weight: 600; }

/* ── Grid layout ── */
.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card-title      { font-size: 1rem; font-weight: 700; margin-bottom: 16px; }
.chart-card      { display: flex; flex-direction: column; }

/* ── Diagramme en bâtons ── */
.bar-chart-wrap {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 8px 0;
}

.bar-chart {
  position: relative;
  height: 270px;
  padding: 0 16px 40px;
}

/* Grille de fond */
.grid-lines {
  position: absolute;
  inset: 0 16px 40px;
  pointer-events: none;
}
.grid-line {
  position: absolute;
  left: 0; right: 0;
  border-top: 1px dashed var(--border, #e5e7eb);
  display: flex;
  align-items: flex-end;
}
.grid-label {
  font-size: 0.7rem;
  color: var(--gray, #9ca3af);
  transform: translateY(50%);
  padding-right: 4px;
  background: white;
  padding: 0 4px;
}

/* Barres */
.bars {
  position: absolute;
  bottom: 40px;
  left: 40px;
  right: 16px;
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 220px;
  border-bottom: 2px solid var(--border, #e5e7eb);
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  position: relative;
  flex: 1;
  max-width: 100px;
  height: 100%;
  justify-content: flex-end;
  cursor: pointer;
}

/* Tooltip */
.bar-tooltip {
  position: absolute;
  top: -38px;
  left: 50%;
  transform: translateX(-50%);
  background: #1f2937;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 8px;
  white-space: nowrap;
  z-index: 10;
  pointer-events: none;
}
.bar-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 5px solid transparent;
  border-top-color: #1f2937;
}

/* La barre elle-même */
.bar {
  width: 60%;
  border-radius: 8px 8px 0 0;
  position: relative;
  transition: height 0.8s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.bar-value {
  position: absolute;
  top: -22px;
  font-size: 0.85rem;
  font-weight: 900;
  color: var(--text, #222);
}

/* Label sous la barre */
.bar-label {
  position: absolute;
  bottom: -38px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
}
.bar-level {
  font-size: 0.85rem;
  font-weight: 900;
}
.bar-desc {
  font-size: 0.68rem;
  color: var(--gray, #9ca3af);
  white-space: nowrap;
}

/* ── Légende ── */
.bar-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px 16px;
  background: var(--main-bg, #f4f6f8);
  border-radius: 12px;
}
.legend-item,
.legend-total {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}
.legend-total {
  padding-top: 8px;
  border-top: 1px solid var(--border, #e5e7eb);
}
.legend-dot {
  width: 12px; height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}
.legend-label { flex: 1; color: var(--text, #444); font-weight: 500; }
.legend-val    { font-weight: 800; font-size: 15px; color: var(--text, #222); min-width: 24px; text-align: right; }

/* ── Inscriptions ── */
.empty { color: var(--gray); font-size: 0.88rem; text-align: center; padding: 20px 0; }

.insc-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0; border-bottom: 1px solid var(--border);
}
.insc-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 0.78rem; flex-shrink: 0;
  overflow: hidden;
}
.insc-avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; display: block; }
.insc-info  { flex: 1; min-width: 0; }
.insc-name  { font-weight: 700; font-size: 0.88rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.insc-meta  { font-size: 0.75rem; color: var(--gray); }
.insc-actions { display: flex; gap: 6px; }
.btn-xs { padding: 4px 10px; font-size: 0.75rem; }
.voir-plus {
  display: block; text-align: right; margin-top: 10px;
  color: var(--primary); font-size: 0.82rem; font-weight: 700; text-decoration: none;
}

/* ── Activité ── */
.activite-list  { display: flex; flex-direction: column; gap: 0; }
.activite-item  { display: flex; align-items: flex-start; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.act-icon       { font-size: 1.1rem; margin-top: 1px; flex-shrink: 0; }
.act-body       { flex: 1; display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
.act-msg        { font-size: 0.85rem; }
.act-date       { font-size: 0.75rem; color: var(--gray); white-space: nowrap; }

/* ── Dark mode ── */
:root[data-theme="dark"] .kpi-card,
[data-theme="dark"] .kpi-card {
  background: var(--card-bg);
}
:root[data-theme="dark"] .grid-label,
[data-theme="dark"] .grid-label {
  background: var(--card-bg);
}
:root[data-theme="dark"] .bar-legend,
[data-theme="dark"] .bar-legend {
  background: rgba(255,255,255,0.04);
}

@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .bar { width: 70%; }
}
</style>