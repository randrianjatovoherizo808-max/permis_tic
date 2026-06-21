<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">📘 Formations</h2>
      <button class="btn btn-primary" @click="ouvrirModal()">+ Nouvelle formation</button>
    </div>

    <!-- Filtres -->
    <div class="filters card">
      <button v-for="n in ['', 'A', 'B', 'C']" :key="n"
        class="filter-btn"
        :class="{ active: filtreNiveau === n }"
        @click="filtreNiveau = n"
      >
        {{ n === '' ? 'Tous' : 'Niveau ' + n }}
      </button>
    </div>

    <div class="formations-grid">
      <div v-for="f in formationsFiltrees" :key="f.id" class="formation-card card"
        :class="'border-' + f.niveau.toLowerCase()">
        <div class="fc-header">
          <span class="niveau-badge" :class="'niveau-bg-' + f.niveau.toLowerCase()">Niveau {{ f.niveau }}</span>
          <span class="duree">⏱ {{ f.duree }}h</span>
        </div>
        <h3 class="fc-nom">{{ f.nom }}</h3>
        <p class="fc-desc">{{ f.description || 'Aucune description.' }}</p>
        <div class="fc-meta">
          <span>📦 Coeff. {{ f.coefficient }}</span>
          <span v-if="f.formateur_nom">👨‍🏫 {{ f.formateur_nom }}</span>
        </div>
        <div class="fc-actions">
          <button class="btn btn-outline btn-sm" @click="ouvrirModal(f)">✏️ Modifier</button>
          <button class="btn btn-danger btn-sm" @click="supprimer(f.id)">🗑️</button>
        </div>
      </div>
      <div v-if="formationsFiltrees.length === 0" class="empty-state">
        Aucune formation pour ce niveau.
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ form.id ? '✏️ Modifier la formation' : '📘 Nouvelle formation' }}</h3>
          <button @click="showModal = false" class="close-btn">×</button>
        </div>

        <form @submit.prevent="sauvegarder">
          <div class="form-group">
            <label>Nom de la formation *</label>
            <input v-model="form.nom" type="text" required placeholder="Ex: Introduction à Excel" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Description du contenu…"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Niveau *</label>
              <select v-model="form.niveau" required>
                <option value="">— Choisir —</option>
                <option value="A">A — Débutant</option>
                <option value="B">B — Intermédiaire</option>
                <option value="C">C — Avancé</option>
              </select>
            </div>
            <div class="form-group">
              <label>Durée (heures) *</label>
              <input v-model.number="form.duree" type="number" required min="1" />
            </div>
          </div>
          <div class="form-group">
              <label>Coefficient</label>
              <select v-model.number="form.coefficient">
                <option v-for="c in [1,2,3,4,5]" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          <div class="form-group">
            <label>Formateur</label>
            <select v-model="form.formateur">
              <option :value="null">— Aucun —</option>
              <option v-for="f in formateurs" :key="f.id" :value="f.id">
                {{ f.prenom }} {{ f.nom }}
              </option>
            </select>
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

const formations   = ref([])
const formateurs   = ref([])
const filtreNiveau = ref('')
const showModal    = ref(false)
const loading      = ref(false)
const error        = ref('')

const form = ref({ id: null, nom: '', description: '', niveau: '', duree: 20, places: 30, coefficient: 2, formateur: null })

const formationsFiltrees = computed(() =>
  filtreNiveau.value
    ? formations.value.filter(f => f.niveau === filtreNiveau.value)
    : formations.value
)

function ouvrirModal(f = null) {
  error.value = ''
  form.value = f
    ? { id: f.id, nom: f.nom, description: f.description || '', niveau: f.niveau, duree: f.duree, places: f.places, coefficient: f.coefficient, formateur: f.formateur || null }
    : { id: null, nom: '', description: '', niveau: '', duree: 20, places: 30, coefficient: 2, formateur: null }
  showModal.value = true
}

async function sauvegarder() {
  error.value = ''
  loading.value = true
  try {
    const payload = { ...form.value }
    if (form.value.id) {
      await api.put(`/formations/${form.value.id}/`, payload)
    } else {
      await api.post('/formations/', payload)
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
  if (!confirm('Supprimer cette formation ? Les leçons et notes associées seront perdues.')) return
  await api.delete(`/formations/${id}/`)
  charger()
}

async function charger() {
  const [{ data: fData }, { data: frData }] = await Promise.all([
    api.get('/formations/'),
    api.get('/users/', { params: { role: 'formateur' } }),
  ])
  formations.value = fData.results || fData
  formateurs.value = frData.results || frData
}

onMounted(charger)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title  { font-size: 1.4rem; }
.filters     { margin-bottom: 18px; padding: 12px 16px; display: flex; gap: 10px; flex-wrap: wrap; }
.filter-btn  { padding: 7px 18px; border: 2px solid var(--border); border-radius: 20px; background: none; cursor: pointer; font-weight: 600; font-size: 0.85rem; transition: 0.2s; }
.filter-btn.active { background: var(--primary); border-color: var(--primary); color: white; }

.formations-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; }
.formation-card  { border-left: 4px solid transparent; transition: transform 0.2s; }
.formation-card:hover { transform: translateY(-3px); }
.border-a { border-left-color: #2196F3; } .border-b { border-left-color: #FF9800; } .border-c { border-left-color: #9C27B0; }

.fc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.niveau-badge { padding: 3px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; color: white; }
.niveau-bg-a { background: #2196F3; } .niveau-bg-b { background: #FF9800; } .niveau-bg-c { background: #9C27B0; }
.duree { font-size: 0.8rem; color: var(--gray); }
.fc-nom  { font-size: 1rem; font-weight: 700; margin-bottom: 8px; }
.fc-desc { font-size: 0.82rem; color: var(--gray); line-height: 1.5; margin-bottom: 12px; display: -webkit-box; -webkit-line-clamp: 2; line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.fc-meta { display: flex; gap: 12px; flex-wrap: wrap; font-size: 0.78rem; color: var(--gray); margin-bottom: 14px; }
.fc-actions { display: flex; gap: 8px; }
.btn-sm  { padding: 6px 14px; font-size: 0.8rem; }
.empty-state { grid-column: 1/-1; text-align: center; color: var(--gray); padding: 40px; background: white; border-radius: 16px; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 500; display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal-box { background: white; border-radius: 20px; padding: 28px; width: 100%; max-width: 520px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.25); }
.modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-btn  { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--gray); }
.form-row   { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.btn-full   { width: 100%; margin-top: 8px; }
.alert      { padding: 10px 14px; border-radius: 10px; font-size: 0.85rem; margin-bottom: 14px; }
.alert-error { background: #FFF3F3; color: #F44336; border: 1px solid #FFCDD2; }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
}
</style>