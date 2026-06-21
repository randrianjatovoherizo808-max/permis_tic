<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">🗺️ Sites PIFTIC</h2>
      <button class="btn btn-primary" @click="ouvrirModal()">+ Ajouter un site</button>
    </div>

    <!-- Grille des sites -->
    <div v-if="loading" class="card" style="text-align:center;padding:40px;color:var(--gray);">Chargement…</div>
    <div v-else class="sites-grid">
      <div v-for="s in sites" :key="s.id" class="site-card card">
        <div class="site-icon">🏢</div>
        <div class="site-info">
          <h3 class="site-nom">{{ s.nom }}</h3>
          <p class="site-loc">📍 {{ s.localisation }}</p>
          <p v-if="s.responsable" class="site-resp">👤 {{ s.responsable }}</p>
          <p v-if="s.telephone" class="site-tel">📞 {{ s.telephone }}</p>
          <div v-if="s.nb_sessions !== undefined" class="site-sessions">
            <span class="badge badge--info">{{ s.nb_sessions }} session(s)</span>
          </div>
        </div>
        <div class="site-actions">
          <button class="btn btn-primary btn-sm" @click="ouvrirModal(s)">✏️ Modifier</button>
          <button class="btn btn-danger btn-sm" @click="supprimer(s.id)">🗑️</button>
        </div>
      </div>

      <div v-if="sites.length === 0" class="empty-sites">
        <div style="font-size:3rem;margin-bottom:12px;">🗺️</div>
        <p>Aucun site enregistré.</p>
        <button class="btn btn-primary" style="margin-top:12px" @click="ouvrirModal()">+ Ajouter le premier site</button>
      </div>
    </div>

    <!-- Modal ajout / édition -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box" style="max-width:480px">
        <div class="modal-head">
          <h3>{{ form.id ? '✏️ Modifier le site' : '🗺️ Nouveau site PIFTIC' }}</h3>
          <button @click="showModal = false" class="close-btn">×</button>
        </div>

        <form @submit.prevent="sauvegarder">
          <div class="form-group">
            <label>Nom du site *</label>
            <input v-model="form.nom" type="text" required placeholder="Ex: PIFTIC Ampandrianomby" />
          </div>
          <div class="form-group">
            <label>Localisation *</label>
            <input v-model="form.localisation" type="text" required placeholder="Ex: Antananarivo" />
          </div>
          <div class="form-group">
            <label>Responsable</label>
            <input v-model="form.responsable" type="text" placeholder="Nom du responsable" />
          </div>
          <div class="form-group">
            <label>Téléphone</label>
            <input
              v-model="form.telephone"
              type="tel"
              inputmode="tel"
              pattern="^\+?[0-9\s]{10,}$"
              placeholder="+261 XX XXX XX XX"
            />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model="form.email" type="email" placeholder="site@permistic.mg" />
          </div>
          <div class="form-group">
            <label>Capacité max (par session)</label>
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
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import { useToast } from '../../composables/useToast'

const { showToast } = useToast()
const loading   = ref(true)
const saving    = ref(false)
const sites     = ref([])
const showModal = ref(false)
const erreur    = ref('')

const formVide = () => ({
  id: null, nom: '', localisation: '',
  responsable: '', telephone: '', email: '', capacite: 15,
})
const form = ref(formVide())

async function charger() {
  loading.value = true
  try {
    const { data } = await api.get('/sites/')
    sites.value = data.results ?? data
  } catch {
    showToast('Erreur lors du chargement des sites.', 'error')
  } finally {
    loading.value = false
  }
}

function ouvrirModal(site = null) {
  erreur.value = ''
  form.value = site ? { ...formVide(), ...site } : formVide()
  showModal.value = true
}

async function sauvegarder() {
  erreur.value = ''
  saving.value = true
  try {
    if (form.value.id) {
      await api.put(`/sites/${form.value.id}/`, form.value)
      showToast('Site modifié avec succès.', 'success')
    } else {
      await api.post('/sites/', form.value)
      showToast('Site ajouté avec succès.', 'success')
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
  if (!confirm('Supprimer ce site ?')) return
  try {
    await api.delete(`/sites/${id}/`)
    showToast('Site supprimé.', 'info')
    await charger()
  } catch {
    showToast('Erreur lors de la suppression.', 'error')
  }
}

onMounted(charger)
</script>

<style scoped>
.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.site-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.site-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.1);
}

.site-icon  { font-size: 2.2rem; text-align: center; }
.site-info  { flex: 1; }
.site-nom   { font-size: 1rem; font-weight: 800; margin-bottom: 8px; color: var(--secondary); }
.site-loc, .site-resp, .site-tel {
  font-size: 13px; color: var(--gray);
  margin-bottom: 4px; display: flex; align-items: center; gap: 4px;
}
.site-sessions { margin-top: 8px; }
.site-actions  { display: flex; gap: 8px; }
.site-actions .btn { flex: 1; }

.empty-sites {
  grid-column: 1 / -1;
  text-align: center; padding: 60px 20px;
  background: var(--card); border-radius: 16px;
  border: 2px dashed var(--border); color: var(--gray);
}
</style>
