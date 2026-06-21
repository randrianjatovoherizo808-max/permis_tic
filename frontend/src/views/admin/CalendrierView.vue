<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">📅 Calendrier des sessions</h2>
      <button class="btn btn-primary" @click="ouvrirModal()">+ Nouvelle session</button>
    </div>

    <!-- Vue switcher -->
    <div class="view-switcher">
      <button :class="['btn btn-sm', vue === 'liste' ? 'btn-primary' : 'btn-outline']" @click="vue = 'liste'">
        📋 Liste
      </button>
      <button :class="['btn btn-sm', vue === 'grille' ? 'btn-primary' : 'btn-outline']" @click="vue = 'grille'">
        🗓️ Grille mensuelle
      </button>
    </div>

    <!-- Filtres -->
    <div class="filters card">
      <select v-model="filtreFormation" @change="charger">
        <option value="">Toutes les formations</option>
        <option v-for="f in formations" :key="f.id" :value="f.id">
          [{{ f.niveau }}] {{ f.nom }}
        </option>
      </select>
      <select v-model="filtreSite" @change="charger">
        <option value="">Tous les sites</option>
        <option v-for="s in sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
      </select>
      <input v-model="filtreAnnee" type="number" min="2020" max="2040" class="annee-input" placeholder="Année" @change="charger" />
    </div>

    <!-- VUE LISTE -->
    <div v-if="vue === 'liste'" class="card">
      <div v-if="loading" class="empty-td">Chargement…</div>
      <table v-else>
        <thead>
          <tr>
            <th>Formation</th>
            <th>Niveau</th>
            <th>Site</th>
            <th>Formateur</th>
            <th>Début</th>
            <th>Fin</th>
            <th>Capacité</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in sessions" :key="s.id">
            <td><strong>{{ s.formation_nom }}</strong></td>
            <td>
              <span class="niveau-badge" :class="'niveau-' + (s.formation_niveau || '').toLowerCase()">
                {{ s.formation_niveau }}
              </span>
            </td>
            <td>{{ s.site_nom || '—' }}</td>
            <td>{{ s.formateur_nom || '—' }}</td>
            <td>{{ formatDate(s.date_debut) }}</td>
            <td>{{ formatDate(s.date_fin) }}</td>
            <td>
              <span class="capacite-badge">
                {{ s.nb_inscrits || 0 }}/{{ s.capacite || '∞' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="statutClass(s)">{{ statutLabel(s) }}</span>
            </td>
            <td>
              <div class="actions">
                <button class="btn btn-primary btn-sm" @click="ouvrirModal(s)">✏️</button>
                <button class="btn btn-danger btn-sm" @click="supprimer(s.id)">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="sessions.length === 0 && !loading">
            <td colspan="9" class="empty-td">Aucune session trouvée.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- VUE GRILLE MENSUELLE -->
    <div v-if="vue === 'grille'" class="calendrier-wrap card">
      <!-- Navigation mois -->
      <div class="cal-nav">
        <button class="btn btn-outline btn-sm" @click="moisPrec">← Mois préc.</button>
        <span class="cal-titre">{{ nomMois }} {{ anneeAff }}</span>
        <button class="btn btn-outline btn-sm" @click="moisSuiv">Mois suiv. →</button>
      </div>

      <!-- En-têtes jours -->
      <div class="cal-grid">
        <div class="cal-header-cell" v-for="j in jours" :key="j">{{ j }}</div>

        <!-- Cellules vides avant le 1er -->
        <div class="cal-cell cal-cell--empty" v-for="n in premierJour" :key="'e-' + n"></div>

        <!-- Jours du mois -->
        <div
          v-for="d in nbJours" :key="d"
          class="cal-cell"
          :class="{ 'cal-cell--today': estAujourd(d), 'cal-cell--has-event': sessionsParJour(d).length > 0 }"
        >
          <span class="cal-day-num">{{ d }}</span>
          <div class="cal-events">
            <div
              v-for="sess in sessionsParJour(d)"
              :key="sess.id"
              class="cal-event"
              :class="'cal-event--' + (sess.formation_niveau || 'a').toLowerCase()"
              :title="sess.formation_nom + ' — ' + sess.site_nom"
              @click="ouvrirModal(sess)"
            >
              {{ sess.formation_nom?.slice(0, 18) }}…
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal session -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ form.id ? '✏️ Modifier la session' : '📅 Nouvelle session' }}</h3>
          <button @click="showModal = false" class="close-btn">×</button>
        </div>

        <form @submit.prevent="sauvegarder">
          <div class="form-group">
            <label>Formation *</label>
            <select v-model="form.formation" required>
              <option value="">— Choisir une formation —</option>
              <option v-for="f in formations" :key="f.id" :value="f.id">
                [{{ f.niveau }}] {{ f.nom }}
              </option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Date de début *</label>
              <input v-model="form.date_debut" type="date" required />
            </div>
            <div class="form-group">
              <label>Date de fin *</label>
              <input v-model="form.date_fin" type="date" required />
            </div>
          </div>
          <div class="form-group">
            <label>Site PIFTIC</label>
            <select v-model="form.site">
              <option value="">— Choisir un site —</option>
              <option v-for="s in sites" :key="s.id" :value="s.id">{{ s.nom }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Formateur</label>
            <select v-model="form.formateur">
              <option value="">— Choisir un formateur —</option>
              <option v-for="f in formateurs" :key="f.id" :value="f.id">
                {{ f.prenom }} {{ f.nom }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Capacité maximale</label>
            <input v-model.number="form.capacite" type="number" min="1" placeholder="15" />
          </div>

          <div v-if="erreur" class="alert alert-error">{{ erreur }}</div>
          <button type="submit" class="btn btn-primary btn-full" :disabled="saving">
            {{ saving ? '⏳ Enregistrement…' : '💾 Enregistrer' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { useToast } from '../../composables/useToast'

const { showToast }    = useToast()
const loading          = ref(true)
const saving           = ref(false)
const sessions         = ref([])
const formations       = ref([])
const sites            = ref([])
const formateurs       = ref([])
const showModal        = ref(false)
const erreur           = ref('')
const vue              = ref('liste')
const filtreFormation  = ref('')
const filtreSite       = ref('')

const now           = new Date()
const moisCourant   = ref(now.getMonth())
const anneeAff      = ref(now.getFullYear())
const filtreAnnee   = ref(now.getFullYear())

const jours = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
const moisNoms = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']

const nomMois = computed(() => moisNoms[moisCourant.value])
const nbJours = computed(() => new Date(anneeAff.value, moisCourant.value + 1, 0).getDate())
const premierJour = computed(() => {
  const d = new Date(anneeAff.value, moisCourant.value, 1).getDay()
  return d === 0 ? 6 : d - 1
})

function moisPrec() {
  if (moisCourant.value === 0) { moisCourant.value = 11; anneeAff.value-- }
  else moisCourant.value--
}
function moisSuiv() {
  if (moisCourant.value === 11) { moisCourant.value = 0; anneeAff.value++ }
  else moisCourant.value++
}

function sessionsParJour(d) {
  const date = new Date(anneeAff.value, moisCourant.value, d)
  return sessions.value.filter((s) => {
    const debut = new Date(s.date_debut)
    const fin   = new Date(s.date_fin)
    return date >= debut && date <= fin
  })
}

function estAujourd(d) {
  const t = new Date()
  return d === t.getDate() && moisCourant.value === t.getMonth() && anneeAff.value === t.getFullYear()
}

const formVide = () => ({
  id: null, formation: '', date_debut: '', date_fin: '',
  site: '', formateur: '', capacite: 15,
})
const form = ref(formVide())

async function charger() {
  loading.value = true
  try {
    const params = {}
    if (filtreFormation.value) params.formation = filtreFormation.value
    if (filtreSite.value)      params.site       = filtreSite.value
    if (filtreAnnee.value)     params.annee      = filtreAnnee.value

    const { data } = await api.get('/sessions/', { params })
    sessions.value = data.results ?? data
  } catch {
    showToast('Erreur lors du chargement des sessions.', 'error')
  } finally {
    loading.value = false
  }
}

function ouvrirModal(sess = null) {
  erreur.value = ''
  form.value = sess ? { ...formVide(), ...sess } : formVide()
  showModal.value = true
}

async function sauvegarder() {
  erreur.value = ''
  saving.value = true
  try {
    if (form.value.id) {
      await api.put(`/sessions/${form.value.id}/`, form.value)
      showToast('Session modifiée.', 'success')
    } else {
      await api.post('/sessions/', form.value)
      showToast('Session créée.', 'success')
    }
    showModal.value = false
    await charger()
  } catch (e) {
    const d = e.response?.data
    erreur.value = typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Erreur lors de l\'enregistrement.'
  } finally {
    saving.value = false
  }
}

async function supprimer(id) {
  if (!confirm('Supprimer cette session ?')) return
  try {
    await api.delete(`/sessions/${id}/`)
    showToast('Session supprimée.', 'info')
    await charger()
  } catch {
    showToast('Erreur lors de la suppression.', 'error')
  }
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })
}

function statutLabel(s) {
  const now   = new Date()
  const debut = new Date(s.date_debut)
  const fin   = new Date(s.date_fin)
  if (now < debut) return '⏳ À venir'
  if (now > fin)   return '✅ Terminée'
  return '🟢 En cours'
}

function statutClass(s) {
  const now   = new Date()
  const debut = new Date(s.date_debut)
  const fin   = new Date(s.date_fin)
  if (now < debut) return 'badge--warning'
  if (now > fin)   return 'badge--success'
  return 'badge--info'
}

async function chargerRefs() {
  const [fRes, sRes, fmRes] = await Promise.all([
    api.get('/formations/'),
    api.get('/sites/'),
    api.get('/users/', { params: { role: 'formateur' } }),
  ])
  formations.value = fRes.data.results ?? fRes.data
  sites.value      = sRes.data.results ?? sRes.data
  formateurs.value = fmRes.data.results ?? fmRes.data
}

onMounted(async () => {
  await chargerRefs()
  await charger()
})
</script>

<style scoped>
.view-switcher  { display: flex; gap: 8px; margin-bottom: 16px; }
.annee-input    { width: 90px; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 50px; font-size: 13px; background: var(--card); color: var(--text); outline: none; }
.capacite-badge { font-size: 12px; font-weight: 700; color: var(--gray); }

/* Calendrier grille */
.calendrier-wrap { overflow-x: auto; }
.cal-nav { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.cal-titre { font-size: 1.1rem; font-weight: 800; color: var(--secondary); }
.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  min-width: 560px;
}
.cal-header-cell {
  text-align: center; font-size: 11px; font-weight: 700;
  color: var(--gray); text-transform: uppercase;
  padding: 8px 0; background: var(--light); border-radius: 4px;
}
.cal-cell {
  min-height: 80px; padding: 4px; border: 1px solid var(--border);
  border-radius: 6px; background: var(--card); position: relative;
  transition: background 0.15s;
}
.cal-cell:hover { background: rgba(76,175,80,0.04); }
.cal-cell--empty   { background: transparent; border: none; }
.cal-cell--today   { background: rgba(76,175,80,0.08); border-color: var(--primary); }
.cal-day-num { font-size: 12px; font-weight: 700; color: var(--gray); display: block; margin-bottom: 2px; }
.cal-cell--today .cal-day-num { color: var(--primary); }
.cal-events { display: flex; flex-direction: column; gap: 2px; }
.cal-event {
  font-size: 10px; padding: 2px 4px; border-radius: 3px;
  cursor: pointer; white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; font-weight: 600;
  transition: opacity 0.15s;
}
.cal-event:hover { opacity: 0.8; }
.cal-event--a { background: rgba(33,150,243,0.15); color: #1565C0; }
.cal-event--b { background: rgba(255,152,0,0.15);  color: #E65100; }
.cal-event--c { background: rgba(156,39,176,0.15); color: #6A1B9A; }

@media (max-width: 768px) {
  th:nth-child(2), td:nth-child(2),
  th:nth-child(4), td:nth-child(4),
  th:nth-child(6), td:nth-child(6),
  th:nth-child(7), td:nth-child(7) { display: none; }
}
</style>