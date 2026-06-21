<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">👨‍🏫 Formateurs</h2>
      <button class="btn btn-primary" @click="ouvrirModal()">+ Ajouter un formateur</button>
    </div>

    <div class="card">
      <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Formateur</th>
            <th>Email</th>
            <th>Téléphone</th>
            <th>Formations</th>
            <th>Date d'ajout</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="f in formateurs" :key="f.id">
            <td>
              <div class="user-cell">
                <div class="avatar">{{ initiales(f) }}</div>
                <strong>{{ f.prenom }} {{ f.nom }}</strong>
              </div>
            </td>
            <td>{{ f.email }}</td>
            <td>{{ f.telephone || '—' }}</td>
            <td>
              <span class="badge badge--info">{{ f.nb_formations || 0 }} formation(s)</span>
            </td>
            <td>{{ formatDate(f.created_at) }}</td>
            <td>
              <div class="actions">
                <button class="btn btn-primary btn-sm" @click="ouvrirModal(f)">✏️ Modifier</button>
                <button class="btn btn-danger btn-sm" @click="supprimer(f.id)">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="formateurs.length === 0">
            <td colspan="6" class="empty-td">Aucun formateur enregistré.</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Modal ajout/modif -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ editMode ? '✏️ Modifier le formateur' : '👨‍🏫 Ajouter un formateur' }}</h3>
          <button @click="showModal = false" class="close-btn">×</button>
        </div>

        <form @submit.prevent="sauvegarder">
          <div class="form-row">
            <div class="form-group">
              <label>Nom *</label>
              <input v-model="form.nom" type="text" required placeholder="Nom" />
            </div>
            <div class="form-group">
              <label>Prénom *</label>
              <input v-model="form.prenom" type="text" required placeholder="Prénom" />
            </div>
          </div>
          <div class="form-group">
            <label>Email *</label>
            <input v-model="form.email" type="email" required placeholder="formateur@example.com" :disabled="editMode" />
          </div>
          <div class="form-group">
            <label>Téléphone</label>
            <input v-model="form.telephone" type="tel" placeholder="+261 XX XXX XX XX" />
          </div>
          <div v-if="!editMode" class="form-group">
            <label>Mot de passe *</label>
            <div class="input-pwd">
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" required placeholder="Minimum 4 caractères" minlength="4" />
              <button type="button" @click="showPwd = !showPwd">{{ showPwd ? '🙈' : '👁' }}</button>
            </div>
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
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const formateurs = ref([])
const showModal  = ref(false)
const editMode   = ref(false)
const loading    = ref(false)
const error      = ref('')
const showPwd    = ref(false)
const form       = ref({ id: null, nom: '', prenom: '', email: '', telephone: '', password: '' })

function initiales(f) {
  return ((f.prenom?.[0] || '') + (f.nom?.[0] || '')).toUpperCase()
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('fr-FR')
}

function ouvrirModal(f = null) {
  error.value = ''
  showPwd.value = false
  if (f) {
    editMode.value = true
    form.value = { id: f.id, nom: f.nom, prenom: f.prenom, email: f.email, telephone: f.telephone || '', password: '' }
  } else {
    editMode.value = false
    form.value = { id: null, nom: '', prenom: '', email: '', telephone: '', password: '' }
  }
  showModal.value = true
}

async function sauvegarder() {
  error.value = ''
  loading.value = true
  try {
    const payload = {
      nom: form.value.nom,
      prenom: form.value.prenom,
      email: form.value.email,
      telephone: form.value.telephone,
      role: 'formateur',
      is_active: true,
    }
    if (!editMode.value) {
      payload.password  = form.value.password
      payload.password2 = form.value.password
    }

    if (editMode.value) {
      await api.patch(`/users/${form.value.id}/`, payload)
    } else {
      await api.post('/auth/register/', payload)
    }

    showModal.value = false
    charger()
  } catch (e) {
    const data = e.response?.data
    error.value = typeof data === 'object'
      ? Object.values(data).flat().join(' ')
      : 'Une erreur est survenue.'
  } finally {
    loading.value = false
  }
}

async function supprimer(id) {
  if (!confirm('Supprimer ce formateur ?')) return
  await api.delete(`/users/${id}/`)
  charger()
}

async function charger() {
  const { data } = await api.get('/users/', { params: { role: 'formateur' } })
  formateurs.value = data.results || data
}

onMounted(charger)
</script>

<style scoped>
.table-wrapper { overflow-x: auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-title  { font-size: 1.4rem; }
.user-cell   { display: flex; align-items: center; gap: 10px; }
.avatar      { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, #FF9800, #E65100); color: white; display: flex; align-items: center; justify-content: center; font-size: 0.78rem; font-weight: 900; flex-shrink: 0; }
.btn-sm      { padding: 5px 12px; font-size: 0.78rem; margin-right: 4px; }
.actions     { display: flex; gap: 6px; }
.empty-td    { text-align: center; color: var(--gray); padding: 30px; }
.form-row    { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.input-pwd   { position: relative; }
.input-pwd input  { padding-right: 44px; }
.input-pwd button { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; }
.btn-full    { width: 100%; margin-top: 8px; }
.alert       { padding: 10px 14px; border-radius: 10px; font-size: 0.85rem; margin-bottom: 14px; }
.alert-error { background: #FFF3F3; color: #F44336; border: 1px solid #FFCDD2; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 500; display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal-box { background: white; border-radius: 20px; padding: 28px; width: 100%; max-width: 480px; box-shadow: 0 20px 60px rgba(0,0,0,0.25); }
.modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-head h3 { font-size: 1.1rem; }
.close-btn  { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--gray); }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
  th:nth-child(3), td:nth-child(3),
  th:nth-child(5), td:nth-child(5) { display: none; }
}
</style>