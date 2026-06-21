<template>
  <div>
    <h2 class="page-title">🎓 Apprenants</h2>

    <!-- Filtres + Recherche -->
    <div class="filters card">
      <input v-model="recherche" type="text" placeholder="🔍 Rechercher par nom, email…" class="search-input" />
      <div class="select-wrapper">
        <select v-model="filtreNiveau" @change="charger">
          <option value="">Tous les niveaux</option>
          <option value="A">Niveau A</option>
          <option value="B">Niveau B</option>
          <option value="C">Niveau C</option>
        </select>
        <span class="select-arrow">▼</span>
      </div>
      <button class="btn btn-export" @click="exportCSV">
        <span class="export-icon">⬇</span> Exporter CSV
      </button>
    </div>

    <div class="card table-card">
      <table>
        <thead>
          <tr>
            <th>APPRENANT</th>
            <th>EMAIL</th>
            <th>TÉLÉPHONE</th>
            <th>FORMATION</th>
            <th>NIVEAU</th>
            <th>MOYENNE</th>
            <th>STATUT</th>
            <th>ACTIONS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in apprenantsFiltres" :key="a.id">
            <td>
              <div class="user-cell">
                <div class="avatar">
                  <img v-if="a.photo_url" :src="a.photo_url" :alt="initiales(a)"
                       class="avatar-img" referrerpolicy="no-referrer" />
                  <span v-else>{{ initiales(a) }}</span>
                </div>
                <span class="user-name">{{ a.prenom }} {{ a.nom }}</span>
                <span v-if="!a.is_active" class="badge-desactive">Désactivé</span>
              </div>
            </td>
            <td class="email-cell">{{ a.email }}</td>
            <td>{{ a.telephone || '—' }}</td>
            <td>{{ a.formation_nom || '—' }}</td>
            <td>
              <span v-if="a.formation_niveau" class="niveau-badge" :class="'niveau-' + a.formation_niveau.toLowerCase()">
                {{ a.formation_niveau }}
              </span>
              <span v-else class="dash">—</span>
            </td>
            <td>
              <span v-if="a.moyenne !== null" class="moyenne" :class="a.moyenne >= 10 ? 'moyenne--ok' : 'moyenne--fail'">
                {{ a.moyenne }}/20
              </span>
              <span v-else class="moyenne moyenne--fail">/20</span>
            </td>
            <td>
              <span class="statut-badge" :class="a.moyenne >= 10 ? 'statut--admis' : a.moyenne !== null ? 'statut--ajourn' : 'statut--cours'">
                <span class="statut-icon">{{ a.moyenne >= 10 ? '✅' : a.moyenne !== null ? '✕' : '⏳' }}</span>
                <span class="statut-text">{{ a.moyenne >= 10 ? 'Admis' : a.moyenne !== null ? 'Ajourné' : 'En cours' }}</span>
              </span>
            </td>
            <td>
              <div class="actions">
                <button class="btn-pill btn-pill--voir" @click="voirDetail(a)">
                  <span class="pill-icon">👁</span> Voir
                </button>
                <button class="btn-pill btn-pill--supprimer" :disabled="suppBusy === a.id" @click="supprimerApprenant(a.id)">
                  <span v-if="suppBusy === a.id">⏳</span>
                  <span v-else>🗑 Supprimer</span>
                </button>
                <button
                  v-if="a.is_active"
                  class="btn-pill btn-pill--stop"
                  :disabled="busy === a.id"
                  @click="desactiver(a.id)"
                  title="Désactiver le compte"
                >
                  <span v-if="busy === a.id">⏳</span>
                  <span v-else>🚫</span>
                </button>
                <button
                  v-else
                  class="btn-pill btn-pill--activer"
                  :disabled="busy === a.id"
                  @click="activer(a.id)"
                  title="Activer le compte"
                >
                  <span v-if="busy === a.id">⏳</span>
                  <span v-else>✅</span>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="apprenantsFiltres.length === 0">
            <td colspan="8" class="empty-td">Aucun apprenant trouvé.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal détail -->
    <div v-if="detail" class="modal-overlay" @click.self="detail = null">
      <div class="modal-box">
        <div class="modal-head">
          <div class="modal-avatar">
            <img v-if="detail.photo_url" :src="detail.photo_url" :alt="initiales(detail)"
                 class="avatar-img" referrerpolicy="no-referrer" />
            <span v-else>{{ initiales(detail) }}</span>
          </div>
          <h3>{{ detail.prenom }} {{ detail.nom }}</h3>
          <button @click="detail = null" class="close-btn">×</button>
        </div>
        <div class="detail-grid">
          <div class="detail-item"><label>Email</label><span>{{ detail.email }}</span></div>
          <div class="detail-item"><label>Téléphone</label><span>{{ detail.telephone || '—' }}</span></div>
          <div class="detail-item"><label>Formation</label><span>{{ detail.formation_nom || '—' }}</span></div>
          <div class="detail-item"><label>Niveau</label>
            <span v-if="detail.formation_niveau" class="niveau-badge" :class="'niveau-' + detail.formation_niveau.toLowerCase()">
              {{ detail.formation_niveau }}
            </span>
            <span v-else>—</span>
          </div>
          <div class="detail-item"><label>Moyenne</label>
            <span class="moyenne" :class="detail.moyenne >= 10 ? 'moyenne--ok' : detail.moyenne !== null ? 'moyenne--fail' : ''">
              {{ detail.moyenne !== null ? detail.moyenne + '/20' : '—' }}
            </span>
          </div>
          <div class="detail-item"><label>Statut</label>
            <span class="statut-badge" :class="detail.moyenne >= 10 ? 'statut--admis' : detail.moyenne !== null ? 'statut--ajourn' : 'statut--cours'">
              <span class="statut-icon">{{ detail.moyenne >= 10 ? '✅' : detail.moyenne !== null ? '✕' : '⏳' }}</span>
              <span class="statut-text">{{ detail.moyenne >= 10 ? 'Admis' : detail.moyenne !== null ? 'Ajourné' : 'En cours' }}</span>
            </span>
          </div>
        </div>
        <div v-if="detail.notes && detail.notes.length" style="margin-top:20px;">
          <h4 style="margin-bottom:12px;font-size:0.95rem;">📝 Notes</h4>
          <table class="notes-table">
            <thead><tr><th>Formation</th><th>Note</th><th>Commentaire</th></tr></thead>
            <tbody>
              <tr v-for="n in detail.notes" :key="n.id">
                <td>{{ n.formation_nom }}</td>
                <td><strong :style="{ color: n.valeur >= 10 ? '#4CAF50' : '#F44336' }">{{ n.valeur }}/20</strong></td>
                <td>{{ n.commentaire || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div style="margin-top:20px;text-align:right;">
          <button v-if="detail.is_active" class="btn-pill btn-pill--stop" @click="desactiver(detail.id); detail = null">
            🚫 Désactiver le compte
          </button>
          <button v-else class="btn-pill btn-pill--activer" @click="activer(detail.id); detail = null">
            ✅ Activer le compte
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

const apprenants   = ref([])
const recherche    = ref('')
const filtreNiveau = ref('')
const detail       = ref(null)
const busy         = ref(null)
const suppBusy     = ref(null)

const apprenantsFiltres = computed(() => {
  let list = apprenants.value
  if (filtreNiveau.value) list = list.filter(a => a.formation_niveau === filtreNiveau.value)
  if (recherche.value) {
    const q = recherche.value.toLowerCase()
    list = list.filter(a =>
      (a.nom + ' ' + a.prenom + ' ' + a.email).toLowerCase().includes(q)
    )
  }
  return list
})

function initiales(a) {
  return ((a.prenom?.[0] || '') + (a.nom?.[0] || '')).toUpperCase()
}

async function charger() {
  const params = {}
  if (filtreNiveau.value) params.niveau = filtreNiveau.value
  const { data } = await api.get('/users/', { params: { role: 'etudiant', ...params } })
  apprenants.value = data.results || data
}

async function voirDetail(a) {
  try {
    const { data } = await api.get(`/users/${a.id}/`)
    detail.value = data
  } catch {
    detail.value = { ...a, notes: [] }
  }
}

async function desactiver(id) {
  if (!confirm('Désactiver ce compte apprenant ?')) return
  busy.value = id
  try {
    await api.patch(`/users/${id}/`, { is_active: false })
    charger()
  } finally {
    busy.value = null
  }
}

async function activer(id) {
  if (!confirm('Activer ce compte apprenant ?')) return
  busy.value = id
  try {
    await api.patch(`/users/${id}/`, { is_active: true })
    charger()
  } finally {
    busy.value = null
  }
}

async function supprimerApprenant(id) {
  if (!confirm('Supprimer définitivement cet apprenant ? Cette action est irréversible.')) return
  suppBusy.value = id
  try {
    await api.delete(`/users/${id}/`)
    apprenants.value = apprenants.value.filter(a => a.id !== id)
    if (detail.value?.id === id) detail.value = null
  } catch (e) {
    alert(e.response?.data?.error || 'Erreur lors de la suppression.')
  } finally {
    suppBusy.value = null
  }
}

function exportCSV() {
  const rows = [
    ['Nom', 'Prénom', 'Email', 'Téléphone', 'Formation', 'Niveau', 'Moyenne', 'Statut'],
    ...apprenantsFiltres.value.map(a => [
      a.nom, a.prenom, a.email, a.telephone || '',
      a.formation_nom || '', a.formation_niveau || '',
      a.moyenne !== null ? a.moyenne : '',
      a.moyenne >= 10 ? 'Admis' : a.moyenne !== null ? 'Ajourné' : 'En cours'
    ])
  ]
  const csv  = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href = url; a.download = 'apprenants.csv'; a.click()
  URL.revokeObjectURL(url)
}

onMounted(charger)
</script>

<style scoped>
/* ── Page title ── */
.page-title { margin-bottom: 20px; font-size: 1.4rem; font-weight: 800; }

/* ── Filters bar ── */
.filters {
  margin-bottom: 16px; padding: 14px 18px;
  display: flex; gap: 12px; flex-wrap: wrap; align-items: center;
}
.search-input {
  flex: 1; min-width: 200px;
  padding: 10px 16px;
  border: 2px solid var(--border, #2a3547);
  border-radius: 12px;
  background: var(--input-bg, #1a2332);
  color: var(--text, #e0e6f0);
  font-size: 0.88rem; outline: none;
  transition: border-color .2s;
}
.search-input:focus { border-color: var(--primary, #0097A7); }
.search-input::placeholder { color: #6b7a99; }

/* Select wrapper */
.select-wrapper { position: relative; }
.select-wrapper select {
  appearance: none;
  padding: 9px 36px 9px 14px;
  border: 2px solid var(--border, #2a3547);
  border-radius: 12px;
  background: var(--input-bg, #1a2332);
  color: var(--text, #e0e6f0);
  font-size: 0.88rem; cursor: pointer; outline: none;
}
.select-arrow {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  font-size: 0.65rem; color: #6b7a99; pointer-events: none;
}

/* Export button */
.btn-export {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 9px 18px;
  border: 2px solid var(--primary, #0097A7);
  border-radius: 12px;
  background: transparent;
  color: var(--primary, #0097A7);
  font-size: 0.85rem; font-weight: 700; cursor: pointer;
  transition: .2s; white-space: nowrap;
}
.btn-export:hover { background: var(--primary, #0097A7); color: white; }
.export-icon { font-size: 0.9rem; }

/* ── Table card ── */
.table-card { padding: 0; overflow: hidden; }
table { width: 100%; border-collapse: collapse; }
thead tr {
  background: var(--card-bg, #111c2d);
  border-bottom: 1px solid var(--border, #2a3547);
}
th {
  padding: 14px 16px;
  text-align: left;
  font-size: 0.72rem; font-weight: 700;
  color: var(--gray, #8898aa);
  letter-spacing: 0.6px; text-transform: uppercase;
}
tbody tr {
  border-bottom: 1px solid var(--border, #1e2d40);
  transition: background .15s;
}
tbody tr:last-child { border-bottom: none; }
tbody tr:hover { background: rgba(255,255,255,0.03); }
td { padding: 14px 16px; font-size: 0.88rem; vertical-align: middle; }

/* ── User cell ── */
.user-cell { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, #4caf50, #2196f3);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 0.72rem; font-weight: 900; flex-shrink: 0; overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.user-name { font-weight: 600; }
.badge-desactive {
  display: inline-block; margin-left: 8px;
  padding: 2px 9px; border-radius: 12px;
  font-size: 0.68rem; font-weight: 700;
  background: rgba(220,53,69,0.15); color: #ff5252;
}
.email-cell { color: var(--gray, #8898aa); font-size: 0.84rem; }
.dash { color: var(--gray, #8898aa); }

/* ── Niveau badge ── */
.niveau-badge {
  display: inline-block; padding: 3px 10px;
  border-radius: 20px; font-size: 0.72rem; font-weight: 700; color: white;
}
.niveau-a { background: #2196F3; }
.niveau-b { background: #FF9800; }
.niveau-c { background: #9C27B0; }

/* ── Moyenne ── */
.moyenne { font-weight: 700; font-size: 0.9rem; }
.moyenne--ok   { color: #4CAF50; }
.moyenne--fail { color: #F44336; }

/* ── Statut badge ── */
.statut-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 5px 10px; border-radius: 8px;
  font-size: 0.78rem; font-weight: 700;
}
.statut--admis  { background: rgba(76,175,80,0.15);  color: #4CAF50; }
.statut--ajourn { background: rgba(244,67,54,0.18);  color: #ff5252; }
.statut--cours  { background: rgba(255,152,0,0.15);  color: #FF9800; }
.statut-icon { font-size: 0.85rem; }

/* ── Action buttons (pill style) ── */
.actions { display: flex; gap: 8px; align-items: center; }

.btn-pill {
  display: inline-flex; align-items: center; gap: 5px;
  border: none; border-radius: 20px; cursor: pointer;
  font-weight: 700; font-size: 0.8rem;
  padding: 6px 16px; transition: .15s;
}
.btn-pill .pill-icon { font-size: 0.85rem; }

.btn-pill--voir {
  background: #28a745; color: white;
  padding: 6px 16px;
}
.btn-pill--voir:hover { background: #218838; transform: translateY(-1px); }

.btn-pill--supprimer {
  background: #dc3545; color: white;
  padding: 6px 14px;
}
.btn-pill--supprimer:hover:not(:disabled) { background: #b02a37; transform: translateY(-1px); }
.btn-pill--supprimer:disabled { opacity: .6; cursor: not-allowed; }

.btn-pill--stop {
  background: #dc3545; color: white;
  padding: 6px 14px; min-width: 40px; justify-content: center;
}
.btn-pill--stop:hover:not(:disabled) { background: #b02a37; transform: translateY(-1px); }
.btn-pill--stop:disabled { opacity: .6; cursor: not-allowed; }

.btn-pill--activer {
  background: #28a745; color: white;
  padding: 6px 14px; min-width: 40px; justify-content: center;
}
.btn-pill--activer:hover:not(:disabled) { background: #218838; transform: translateY(-1px); }
.btn-pill--activer:disabled { opacity: .6; cursor: not-allowed; }

/* ── Empty row ── */
.empty-td { text-align: center; color: var(--gray, #8898aa); padding: 40px; }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.55);
  z-index: 500; display: flex; align-items: center; justify-content: center; padding: 16px;
}
.modal-box {
  background: var(--card-bg, #1a2332); border-radius: 20px; padding: 28px;
  width: 100%; max-width: 540px; max-height: 90vh; overflow-y: auto;
  box-shadow: 0 24px 64px rgba(0,0,0,0.45);
  border: 1px solid var(--border, #2a3547);
}
.modal-head {
  display: flex; align-items: center; gap: 12px; margin-bottom: 22px;
}
.modal-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, #4caf50, #2196f3);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem; font-weight: 900; flex-shrink: 0; overflow: hidden;
}
.modal-head h3 { font-size: 1.1rem; flex: 1; }
.close-btn {
  background: none; border: none; font-size: 1.5rem;
  cursor: pointer; color: var(--gray, #8898aa); line-height: 1;
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  border-radius: 50%; transition: .15s;
}
.close-btn:hover { background: rgba(255,255,255,0.08); color: var(--text, white); }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.detail-item { display: flex; flex-direction: column; gap: 5px; }
.detail-item label {
  font-size: 0.72rem; font-weight: 700; color: var(--gray, #8898aa);
  text-transform: uppercase; letter-spacing: 0.5px;
}
.detail-item span { font-size: 0.9rem; }

.notes-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
.notes-table th { padding: 8px 12px; text-align: left; color: var(--gray, #8898aa); font-size: 0.72rem; text-transform: uppercase; border-bottom: 1px solid var(--border, #2a3547); }
.notes-table td { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }

@media (max-width: 768px) {
  .detail-grid { grid-template-columns: 1fr; }
  th:nth-child(3), td:nth-child(3),
  th:nth-child(4), td:nth-child(4) { display: none; }
}
</style>