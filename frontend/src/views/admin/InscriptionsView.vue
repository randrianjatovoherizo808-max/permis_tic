<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">📋 Inscriptions</h2>
      <div class="header-stats">
        <span class="badge badge--warning">⏳ {{ enAttente.length }} en attente</span>
        <span class="badge badge--success">✅ {{ confirmees.length }} confirmées</span>
        <span class="badge badge--danger">❌ {{ rejetees.length }} rejetées</span>
      </div>
    </div>

    <!-- Filtres -->
    <div class="filters card">
      <input v-model="recherche" type="text" placeholder="🔍 Rechercher par nom, formation…" class="search-input" />
      <select v-model="filtreStatut" @change="charger">
        <option value="">Tous les statuts</option>
        <option value="en_attente">En attente</option>
        <option value="confirme">Confirmée</option>
        <option value="rejete">Rejetée</option>
      </select>
      <select v-model="filtreNiveau" @change="charger">
        <option value="">Tous les niveaux</option>
        <option value="A">Niveau A</option>
        <option value="B">Niveau B</option>
        <option value="C">Niveau C</option>
      </select>
      <button class="btn btn-outline btn-sm" @click="exportCSV">⬇️ Exporter</button>
    </div>

    <!-- Tableau -->
    <div class="card">
      <div v-if="loading" class="empty-td">Chargement…</div>
      <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Apprenant</th>
            <th>Formation</th>
            <th>Niveau</th>
            <th>Date d'inscription</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="insc in inscriptionsFiltrees" :key="insc.id">
            <td>
              <div class="user-cell">
                <div class="avatar">
                  <img
                    v-if="insc.utilisateur_photo"
                    :src="insc.utilisateur_photo"
                    :alt="insc.utilisateur_nom"
                    class="avatar-img"
                    referrerpolicy="no-referrer"
                  />
                  <span v-else>{{ initiales(insc.utilisateur_nom) }}</span>
                </div>
                <div>
                  <div style="font-weight:600">{{ insc.utilisateur_nom }}</div>
                  <div style="font-size:11px;color:var(--gray)">{{ insc.utilisateur_email }}</div>
                </div>
              </div>
            </td>
            <td>{{ insc.formation_nom }}</td>
            <td>
              <span class="niveau-badge" :class="'niveau-' + (insc.formation_niveau || '').toLowerCase()">
                {{ insc.formation_niveau }}
              </span>
            </td>
            <td>{{ formatDate(insc.created_at) }}</td>
            <td>
              <span class="badge" :class="statutClass(insc.statut)">
                {{ statutLabel(insc.statut) }}
              </span>
            </td>
            <td>
              <div class="actions" v-if="insc.statut === 'en_attente'">
                <button class="btn btn-primary btn-sm" :disabled="busy === insc.id" @click="confirmer(insc)">
                  ✅ Confirmer
                </button>
                <button class="btn btn-danger btn-sm" :disabled="busy === insc.id" @click="ouvrirRejet(insc)">
                  ❌ Rejeter
                </button>
              </div>
              <div v-else class="actions">
                <button class="btn btn-outline btn-sm" @click="voirDetail(insc)">👁 Détail</button>
              </div>
            </td>
          </tr>
          <tr v-if="inscriptionsFiltrees.length === 0 && !loading">
            <td colspan="6" class="empty-td">Aucune inscription trouvée.</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Modal rejet avec motif -->
    <div v-if="showRejet" class="modal-overlay" @click.self="annulerRejet">
      <div class="modal-box" style="max-width:420px">
        <div class="modal-head">
          <h3>❌ Rejeter l'inscription</h3>
          <button @click="annulerRejet" class="close-btn">×</button>
        </div>
        <p style="font-size:13px;color:var(--gray);margin-bottom:16px">
          Rejet de <strong>{{ inscSelec?.utilisateur_nom }}</strong> pour
          <strong>{{ inscSelec?.formation_nom }}</strong>.
        </p>
        <div class="form-group">
          <label>Motif du rejet (facultatif)</label>
          <textarea v-model="motifRejet" rows="3" placeholder="Expliquer la raison du rejet…"></textarea>
        </div>
        <div class="actions" style="justify-content:flex-end">
          <button class="btn btn-outline btn-sm" :disabled="rejetLoading" @click="annulerRejet">Annuler</button>
          <button class="btn btn-danger" :disabled="rejetLoading" @click="rejeter">
            {{ rejetLoading ? 'En cours…' : 'Confirmer le rejet' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal détail -->
    <div v-if="detail" class="modal-overlay" @click.self="detail = null">
      <div class="modal-box">
        <div class="modal-head">
          <h3>📋 Détail de l'inscription</h3>
          <button @click="detail = null" class="close-btn">×</button>
        </div>
        <div class="detail-grid">
          <div class="detail-row"><span class="detail-label">Apprenant</span><span>{{ detail.utilisateur_nom }}</span></div>
          <div class="detail-row"><span class="detail-label">Email</span><span>{{ detail.utilisateur_email }}</span></div>
          <div class="detail-row"><span class="detail-label">Formation</span><span>{{ detail.formation_nom }}</span></div>
          <div class="detail-row"><span class="detail-label">Niveau</span><span>{{ detail.formation_niveau }}</span></div>
          <div class="detail-row"><span class="detail-label">Statut</span><span>{{ statutLabel(detail.statut) }}</span></div>
          <div class="detail-row"><span class="detail-label">Date</span><span>{{ formatDate(detail.created_at) }}</span></div>
          <div v-if="detail.motif_rejet" class="detail-row">
            <span class="detail-label">Motif rejet</span>
            <span>{{ detail.motif_rejet }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { useToast } from '../../composables/useToast'

const { showToast }   = useToast()
const loading         = ref(true)
const busy            = ref(null)
const rejetLoading    = ref(false)
const inscriptions    = ref([])
const recherche       = ref('')
const filtreStatut    = ref('en_attente')
const filtreNiveau    = ref('')
const showRejet       = ref(false)
const inscSelec       = ref(null)
const motifRejet      = ref('')
const detail          = ref(null)

const enAttente  = computed(() => inscriptions.value.filter(i => i.statut === 'en_attente'))
const confirmees = computed(() => inscriptions.value.filter(i => i.statut === 'confirme'))
const rejetees   = computed(() => inscriptions.value.filter(i => i.statut === 'rejete'))

const inscriptionsFiltrees = computed(() => {
  const q = recherche.value.toLowerCase()
  return inscriptions.value.filter((i) => {
    const matchNom       = i.utilisateur_nom?.toLowerCase().includes(q)
    const matchFormation = i.formation_nom?.toLowerCase().includes(q)
    const matchStatut    = !filtreStatut.value || i.statut === filtreStatut.value
    const matchNiveau    = !filtreNiveau.value || i.formation_niveau === filtreNiveau.value
    return (matchNom || matchFormation) && matchStatut && matchNiveau
  })
})

async function charger() {
  loading.value = true
  try {
    const params = {}
    if (filtreStatut.value) params.statut = filtreStatut.value
    if (filtreNiveau.value) params.niveau = filtreNiveau.value
    const { data } = await api.get('/inscriptions/', { params })
    inscriptions.value = data.results ?? data
  } catch {
    showToast('Erreur lors du chargement des inscriptions.', 'error')
  } finally {
    loading.value = false
  }
}

async function confirmer(insc) {
  busy.value = insc.id
  try {
    await api.post(`/inscriptions/${insc.id}/confirmer/`)
    showToast(`✅ Inscription de ${insc.utilisateur_nom} confirmée.`, 'success')
    await charger()
  } catch {
    showToast('Erreur lors de la confirmation.', 'error')
  } finally {
    busy.value = null
  }
}

function ouvrirRejet(insc) {
  inscSelec.value  = insc
  motifRejet.value = ''
  showRejet.value  = true
}

// ✅ Empêche la fermeture de la modal pendant que le rejet est en cours
function annulerRejet() {
  if (rejetLoading.value) return
  showRejet.value = false
  inscSelec.value = null
}

async function rejeter() {
  if (!inscSelec.value || rejetLoading.value) return
  rejetLoading.value = true
  busy.value = inscSelec.value.id
  const inscId  = inscSelec.value.id
  const inscNom = inscSelec.value.utilisateur_nom
  try {
    await api.post(`/inscriptions/${inscId}/rejeter/`, {
      motif: motifRejet.value,
    })
    showToast('Inscription rejetée.', 'info')
    // ✅ Fermer la modal APRÈS le succès de la requête
    showRejet.value = false
    inscSelec.value = null
    await charger()
  } catch {
    showToast('Erreur lors du rejet.', 'error')
  } finally {
    rejetLoading.value = false
    busy.value = null
  }
}

function voirDetail(insc) { detail.value = insc }

function initiales(nom = '') {
  return nom.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase() || '?'
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

function statutLabel(s) {
  return { en_attente: '⏳ En attente', confirme: '✅ Confirmée', rejete: '❌ Rejetée' }[s] ?? s
}
function statutClass(s) {
  return { en_attente: 'badge--warning', confirme: 'badge--success', rejete: 'badge--danger' }[s] ?? ''
}

function exportCSV() {
  const rows = [
    ['Apprenant', 'Email', 'Formation', 'Niveau', 'Statut', 'Date'],
    ...inscriptionsFiltrees.value.map((i) => [
      i.utilisateur_nom, i.utilisateur_email,
      i.formation_nom, i.formation_niveau,
      statutLabel(i.statut), formatDate(i.created_at),
    ]),
  ]
  const csv  = rows.map((r) => r.map((c) => `"${c}"`).join(',')).join('\n')
  const link = document.createElement('a')
  link.href  = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
  link.download = 'inscriptions.csv'
  link.click()
}

onMounted(charger)
</script>

<style scoped>
.table-wrapper { overflow-x: auto; }
.header-stats { display: flex; gap: 8px; flex-wrap: wrap; }
.detail-grid  { display: flex; flex-direction: column; gap: 10px; }
.detail-row   { display: flex; gap: 12px; font-size: 13px; }
.detail-label { min-width: 110px; font-weight: 700; color: var(--gray); }
.avatar-img   { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; display: block; }

@media (max-width: 768px) {
  th:nth-child(3), td:nth-child(3),
  th:nth-child(4), td:nth-child(4) { display: none; }
}
</style>