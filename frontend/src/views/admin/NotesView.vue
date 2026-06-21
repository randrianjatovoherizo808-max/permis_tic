<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">📝 Notes</h2>
      <button class="btn btn-primary" @click="ouvrirModal()">+ Saisir une note</button>
    </div>

    <!-- Filtres -->
    <div class="filters card">
      <select v-model="filtreFormation" @change="charger">
        <option value="">Toutes les formations</option>
        <option v-for="f in formations" :key="f.id" :value="f.id">
          [{{ f.niveau }}] {{ f.nom }}
        </option>
      </select>
    </div>

    <div class="card">
      <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Apprenant</th>
            <th>Formation</th>
            <th>Niveau</th>
            <th>Note /20</th>
            <th>Statut</th>
            <th>Commentaire</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="n in notes" :key="n.id">
            <td>
              <div class="user-cell">
                <div class="avatar">
                  <img
                    v-if="n.apprenant_photo"
                    :src="n.apprenant_photo"
                    :alt="n.apprenant_nom"
                    class="avatar-img"
                    referrerpolicy="no-referrer"
                  />
                  <span v-else>{{ initiales(n.apprenant_nom) }}</span>
                </div>
                <span>{{ n.apprenant_nom }}</span>
              </div>
            </td>
            <td>{{ n.formation_nom }}</td>
            <td><span class="niveau-badge" :class="'niveau-' + (n.formation_niveau || '').toLowerCase()">{{ n.formation_niveau }}</span></td>
            <td>
              <span class="note-val" :style="{ color: n.valeur >= 10 ? '#4CAF50' : '#F44336' }">
                {{ n.valeur }}/20
              </span>
            </td>
            <td>
              <span class="badge" :class="n.valeur >= 10 ? 'badge--success' : 'badge--danger'">
                {{ n.valeur >= 10 ? '🏅 Admis' : '❌ Ajourné' }}
              </span>
            </td>
            <td class="comment-cell">{{ n.commentaire || '—' }}</td>
            <td>{{ formatDate(n.date) }}</td>
            <td>
              <div class="actions">
                <button class="btn btn-primary btn-sm" @click="ouvrirModal(n)">✏️</button>
                <button class="btn btn-danger btn-sm" @click="supprimer(n.id)">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="notes.length === 0">
            <td colspan="8" class="empty-td">Aucune note enregistrée.</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Récapitulatif moyennes -->
    <div v-if="moyennes.length" class="card" style="margin-top:20px;">
      <h3 style="margin-bottom:16px; font-size:1rem;">📊 Moyennes générales par apprenant</h3>
      <div class="moyennes-grid">
        <div v-for="m in moyennes" :key="m.id" class="moyenne-card">
          <div class="avg-avatar">
            <img
              v-if="m.photo"
              :src="m.photo"
              :alt="m.nom"
              class="avatar-img"
              referrerpolicy="no-referrer"
            />
            <span v-else>{{ initiales(m.nom) }}</span>
          </div>
          <div class="avg-info">
            <div class="avg-name">{{ m.nom }}</div>
            <div class="avg-formation">{{ m.formation }}</div>
          </div>
          <div class="avg-val" :style="{ color: m.moy >= 10 ? '#4CAF50' : '#F44336' }">
            {{ m.moy }}/20
          </div>
          <span class="badge" :class="m.moy >= 10 ? 'badge--success' : 'badge--danger'" style="font-size:0.7rem;">
            {{ m.moy >= 10 ? 'Admis' : 'Ajourné' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ form.id ? '✏️ Modifier la note' : '📊 Saisir une note' }}</h3>
          <button @click="showModal = false" class="close-btn">×</button>
        </div>
        <form @submit.prevent="sauvegarder">
          <div class="form-group">
            <label>Apprenant *</label>
            <select v-model="form.apprenant" required>
              <option value="">— Choisir —</option>
              <option v-for="a in apprenants" :key="a.id" :value="a.id">{{ (a.first_name || a.prenom || '') + ' ' + (a.last_name || a.nom || '') || a.email }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Formation *</label>
            <select v-model="form.formation" required>
              <option value="">— Choisir —</option>
              <option v-for="f in formations" :key="f.id" :value="f.id">
                [{{ f.niveau }}] {{ f.nom }}
              </option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Note /20 *</label>
              <input v-model.number="form.valeur" type="number" step="0.5" min="0" max="20" required placeholder="0–20" />
            </div>
            <div class="form-group">
              <label>Date</label>
              <input v-model="form.date" type="date" />
            </div>
          </div>
          <div class="form-group">
            <label>Commentaire</label>
            <textarea v-model="form.commentaire" rows="3" placeholder="Appréciation, observations…"></textarea>
          </div>

          <!-- Aperçu -->
          <div v-if="form.valeur !== ''" class="apercu" :class="form.valeur >= 10 ? 'apercu--ok' : 'apercu--ko'">
            {{ form.valeur >= 10 ? '🏅 Admis — ' : '❌ Ajourné — ' }}
            Note : {{ form.valeur }}/20
          </div>

          <div v-if="error" class="alert alert-error">❌ {{ error }}</div>

          <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
            <span v-if="loading">⏳ Enregistrement…</span>
            <span v-else>💾 Enregistrer</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'

const notes           = ref([])
const formations      = ref([])
const apprenants      = ref([])
const filtreFormation = ref('')
const showModal       = ref(false)
const loading         = ref(false)
const error           = ref('')

const today = new Date().toISOString().split('T')[0]
const form  = ref({ id: null, apprenant: '', formation: '', valeur: '', date: today, commentaire: '' })

const moyennes = computed(() => {
  const map = {}
  notes.value.forEach(n => {
    if (!map[n.apprenant]) {
      map[n.apprenant] = { id: n.apprenant, nom: n.apprenant_nom, photo: n.apprenant_photo, formation: n.formation_nom, vals: [] }
    }
    map[n.apprenant].vals.push(n.valeur)
  })
  return Object.values(map).map(m => ({
    ...m,
    moy: parseFloat((m.vals.reduce((a, b) => a + b, 0) / m.vals.length).toFixed(2))
  }))
})

function initiales(nom) {
  return (nom || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('fr-FR')
}

function ouvrirModal(n = null) {
  error.value = ''
  form.value = n
    ? { id: n.id, apprenant: n.apprenant, formation: n.formation, valeur: n.valeur, date: n.date || today, commentaire: n.commentaire || '' }
    : { id: null, apprenant: '', formation: filtreFormation.value || '', valeur: '', date: today, commentaire: '' }
  showModal.value = true
}

async function sauvegarder() {
  error.value = ''
  loading.value = true
  try {
    const payload = { apprenant: form.value.apprenant, formation: form.value.formation, valeur: form.value.valeur, commentaire: form.value.commentaire }
    if (form.value.id) {
      await api.put(`/notes/${form.value.id}/`, payload)
    } else {
      await api.post('/notes/', payload)
    }
    showModal.value = false
    charger()
  } catch (e) {
    const data = e.response?.data
    error.value = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Erreur.'
  } finally {
    loading.value = false
  }
}

async function supprimer(id) {
  if (!confirm('Supprimer cette note ?')) return
  await api.delete(`/notes/${id}/`)
  charger()
}

async function charger() {
  const params = filtreFormation.value ? { formation: filtreFormation.value } : {}
  const [{ data: nData }, { data: fData }, { data: aData }] = await Promise.all([
    api.get('/notes/', { params }),
    api.get('/formations/'),
    api.get('/users/', { params: { role: 'etudiant' } }),
  ])
  notes.value      = nData.results || nData
  formations.value = fData.results || fData
  const tousEtudiants = aData.results || aData
    // N'afficher que les étudiants ayant au moins une inscription confirmée
    try {
      const { data: inscData } = await api.get('/inscriptions/', { params: { statut: 'confirme' } })
      const inscriptions = inscData.results || inscData
      const idsConfirmes = new Set(inscriptions.map(i => i.utilisateur))
      apprenants.value = tousEtudiants.filter(u => idsConfirmes.has(u.id))
    } catch {
      apprenants.value = tousEtudiants
    }
}

onMounted(charger)
</script>

<style scoped>
.table-wrapper { overflow-x: auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title  { font-size: 1.4rem; }
.filters     { margin-bottom: 16px; padding: 12px 16px; }
.filters select { padding: 8px 12px; border: 2px solid var(--border); border-radius: 10px; font-size: 0.88rem; min-width: 260px; }
.user-cell   { display: flex; align-items: center; gap: 10px; }
.avatar      { width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 900; flex-shrink: 0; overflow: hidden; }
.avatar-img  { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; display: block; }
.niveau-badge { display: inline-block; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; color: white; }
.niveau-a { background: #2196F3; } .niveau-b { background: #FF9800; } .niveau-c { background: #9C27B0; }
.note-val    { font-size: 1rem; font-weight: 900; }
.comment-cell { max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.82rem; color: var(--gray); }
.btn-sm      { padding: 5px 10px; font-size: 0.78rem; }
.actions     { display: flex; gap: 6px; }
.empty-td    { text-align: center; color: var(--gray); padding: 30px; }

.moyennes-grid   { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; }
.moyenne-card    { display: flex; align-items: center; gap: 10px; padding: 12px; background: var(--bg); border-radius: 14px; border: 1px solid var(--border); }
.avg-avatar      { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: white; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 0.78rem; flex-shrink: 0; overflow: hidden; }
.avg-info        { flex: 1; min-width: 0; }
.avg-name        { font-weight: 700; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.avg-formation   { font-size: 0.72rem; color: var(--gray); }
.avg-val         { font-size: 1rem; font-weight: 900; flex-shrink: 0; }

.apercu    { padding: 10px 14px; border-radius: 10px; font-size: 0.85rem; margin-bottom: 14px; font-weight: 700; }
.apercu--ok { background: rgba(76,175,80,0.12); color: #4CAF50; border: 1px solid rgba(76,175,80,0.3); }
.apercu--ko { background: rgba(244,67,54,0.1); color: #F44336; border: 1px solid rgba(244,67,54,0.25); }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 500; display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal-box { background: white; border-radius: 20px; padding: 28px; width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.25); }
.modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-btn  { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--gray); }
.form-row   { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.btn-full   { width: 100%; margin-top: 8px; }
.alert      { padding: 10px 14px; border-radius: 10px; font-size: 0.85rem; margin-bottom: 14px; }
.alert-error { background: #FFF3F3; color: #F44336; border: 1px solid #FFCDD2; }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
  th:nth-child(3), td:nth-child(3),
  th:nth-child(6), td:nth-child(6),
  th:nth-child(7), td:nth-child(7) { display: none; }
}
</style>