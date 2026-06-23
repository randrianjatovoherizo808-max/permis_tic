<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">📖 Leçons</h2>
      <button class="btn btn-primary" @click="ouvrirModal()">+ Ajouter une leçon</button>
    </div>

    <!-- Filtre formation -->
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
            <th>#</th>
            <th>Titre</th>
            <th>Formation</th>
            <th>Contenu</th>
            <th>Ressources</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(l, i) in lecons" :key="l.id">
            <td>
              <span class="ordre-badge">{{ l.ordre || i + 1 }}</span>
            </td>
            <td><strong>{{ l.titre }}</strong></td>
            <td>
              <span class="formation-tag">{{ l.formation_nom || '—' }}</span>
            </td>
            <td class="contenu-cell">{{ l.contenu || '—' }}</td>
            <td>
              <div v-if="ressourcesList(l).length" class="ressources">
                <a v-for="r in ressourcesList(l)" :key="r" :href="r" target="_blank" rel="noopener"
                  class="ressource-link">🔗</a>
              </div>
              <span v-else class="text-gray">—</span>
            </td>
            <td>
              <div class="actions">
                <button class="btn btn-primary btn-sm" @click="ouvrirModal(l)">✏️</button>
                <button class="btn btn-danger btn-sm" @click="supprimer(l.id)">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="lecons.length === 0">
            <td colspan="6" class="empty-td">Aucune leçon enregistrée.</td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ form.id ? '✏️ Modifier la leçon' : '📖 Nouvelle leçon' }}</h3>
          <button @click="showModal = false" class="close-btn">×</button>
        </div>

        <form @submit.prevent="sauvegarder">
          <div class="form-group">
            <label>Titre *</label>
            <input v-model="form.titre" type="text" required placeholder="Ex: Introduction à Excel" />
          </div>
          <div class="form-group">
            <label>Formation *</label>
            <select v-model="form.formation" required>
              <option value="">— Choisir une formation —</option>
              <option v-for="f in formations" :key="f.id" :value="f.id">
                [{{ f.niveau }}] {{ f.nom }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Contenu / Description</label>
            <textarea v-model="form.contenu" rows="4" placeholder="Décrivez le contenu de la leçon…"></textarea>
          </div>
          <div class="form-group">
            <label>Ordre d'affichage</label>
            <input v-model.number="form.ordre" type="number" min="0" placeholder="0" />
          </div>

          <div class="ressources-section">
            <p class="ressources-title">📎 Ressources pédagogiques</p>
            <div class="form-group">
              <label>🎬 Lien vidéo (YouTube, Drive…)</label>
              <input v-model="form.videoUrl" type="url" placeholder="https://www.youtube.com/watch?v=…" />
            </div>
            <div class="form-group">
              <label>🔗 Lien ressource externe</label>
              <input v-model="form.lienUrl" type="url" placeholder="https://…" />
            </div>
            <div class="form-group">
              <label>📁 Importer un fichier <span class="hint">(PDF, Word, PowerPoint, image…)</span></label>
              <div class="file-upload-zone" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="onFileDrop">
                <input ref="fileInput" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.png,.jpg,.jpeg,.zip" style="display:none" @change="onFileChange" />
                <div v-if="!form.fichierNom" class="file-placeholder">
                  <span class="file-icon">📂</span>
                  <span>Cliquez ou glissez un fichier ici</span>
                  <span class="file-hint">PDF, Word, PowerPoint, Excel, Image…</span>
                </div>
                <div v-else class="file-selected">
                  <span class="file-icon">{{ fileIcon(form.fichierNom) }}</span>
                  <span class="file-name">{{ form.fichierNom }}</span>
                  <button type="button" class="file-remove" @click.stop="retirerFichier">✕</button>
                </div>
              </div>
              <!-- Fichier existant (en mode édition) -->
              <div v-if="form.fichierExistant && !form.fichierNom" class="file-existing">
                📎 Fichier actuel :
                <a :href="form.fichierExistant" target="_blank" class="file-link">Télécharger</a>
                <button type="button" class="file-remove" @click="form.fichierExistant = null">✕ Supprimer</button>
              </div>
            </div>
          </div>

          <div v-if="error" class="alert alert-error">❌ {{ error }}</div>

          <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
            <span v-if="loading">⏳ Enregistrement…</span>
            <span v-else>💾 Enregistrer la leçon</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const lecons          = ref([])
const formations      = ref([])
const filtreFormation = ref('')
const showModal       = ref(false)
const loading         = ref(false)
const error           = ref('')

const form = ref({ id: null, titre: '', formation: '', contenu: '', ordre: 0, videoUrl: '', lienUrl: '', fichier: null, fichierNom: '', fichierExistant: null })

function ressourcesList(l) {
  if (!l.ressources) return []
  return l.ressources.split(',').map(r => r.trim()).filter(Boolean)
}

function ouvrirModal(l = null) {
  error.value = ''
  if (l) {
    const res = ressourcesList(l)
    form.value = {
      id: l.id,
      titre: l.titre,
      formation: l.formation,
      contenu: l.contenu || '',
      ordre: l.ordre || 0,
      videoUrl: res[0] || '',
      lienUrl: res[1] || '',
      fichier: null,
      fichierNom: '',
      fichierExistant: l.fichier || null,
    }
  } else {
    form.value = { id: null, titre: '', formation: filtreFormation.value || '', contenu: '', ordre: 0, videoUrl: '', lienUrl: '', fichier: null, fichierNom: '', fichierExistant: null }
  }
  showModal.value = true
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (file) { form.value.fichier = file; form.value.fichierNom = file.name }
}
function onFileDrop(e) {
  const file = e.dataTransfer.files[0]
  if (file) { form.value.fichier = file; form.value.fichierNom = file.name }
}
function retirerFichier() {
  form.value.fichier = null; form.value.fichierNom = ''
  if (document.querySelector('input[type=file]')) document.querySelector('input[type=file]').value = ''
}
function fileIcon(name) {
  if (!name) return '📄'
  const ext = name.split('.').pop().toLowerCase()
  const icons = { pdf:'📕', doc:'📘', docx:'📘', ppt:'📙', pptx:'📙', xls:'📗', xlsx:'📗', png:'🖼️', jpg:'🖼️', jpeg:'🖼️', zip:'🗜️' }
  return icons[ext] || '📄'
}

async function sauvegarder() {
  error.value = ''
  loading.value = true
  try {
    const ressources = [form.value.videoUrl, form.value.lienUrl].filter(Boolean).join(',')
    const fd = new FormData()
    // ✅ ?? '' évite d'envoyer la string "null"/"undefined" que Django rejette
    fd.append('titre',      form.value.titre      ?? '')
    fd.append('formation',  form.value.formation  ?? '')
    fd.append('contenu',    form.value.contenu     ?? '')
    fd.append('ordre',      form.value.ordre       ?? 0)
    fd.append('ressources', ressources)
    if (form.value.fichier) {
      fd.append('fichier', form.value.fichier)
    } else if (form.value.fichierExistant === null && form.value.id) {
      // Signale au backend de supprimer le fichier existant
      fd.append('fichier', '')
    }
    const config = { headers: { 'Content-Type': 'multipart/form-data' } }
    if (form.value.id) {
      await api.put(`/lecons/${form.value.id}/`, fd, config)
    } else {
      await api.post('/lecons/', fd, config)
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
  if (!confirm('Supprimer cette leçon ?')) return
  await api.delete(`/lecons/${id}/`)
  charger()
}

async function charger() {
  try {
    const lRes = await api.get('/lecons/', {
      params: filtreFormation.value ? { formation: filtreFormation.value } : {}
    })
    lecons.value = lRes.data.results || lRes.data
  } catch (e) {
    console.error('Erreur leçons', e)
    lecons.value = []
  }

  try {
    const fRes = await api.get('/formations/')
    formations.value = fRes.data.results || fRes.data
  } catch (e) {
    console.error('Erreur formations', e)
    formations.value = []
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

.ordre-badge    { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: var(--primary); color: white; border-radius: 50%; font-weight: 700; font-size: 0.78rem; }
.formation-tag  { background: rgba(76,175,80,0.12); color: var(--secondary); padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
.contenu-cell   { max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 0.82rem; color: var(--gray); }
.ressources     { display: flex; gap: 6px; }
.ressource-link { color: var(--primary); text-decoration: none; font-size: 1rem; }
.text-gray      { color: var(--gray); }
.btn-sm         { padding: 5px 10px; font-size: 0.78rem; }
.actions        { display: flex; gap: 6px; }
.empty-td       { text-align: center; color: var(--gray); padding: 30px; }

.ressources-section { border: 2px dashed var(--border); border-radius: 14px; padding: 16px; margin-bottom: 16px; }
.ressources-title { font-weight: 700; color: var(--secondary); margin-bottom: 14px; }

/* Upload fichier */
.hint { font-size: 11px; color: var(--gray); font-weight: 400; margin-left: 6px; }
.file-upload-zone {
  border: 2px dashed #c8e6c9; border-radius: 12px; padding: 20px 16px;
  text-align: center; cursor: pointer; transition: .2s;
  background: #f9fdf9; display: flex; flex-direction: column; align-items: center; gap: 6px;
}
.file-upload-zone:hover { border-color: var(--primary); background: #f0fff0; }
.file-placeholder { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.file-icon { font-size: 2rem; }
.file-placeholder span { font-size: 13px; color: #555; }
.file-hint { font-size: 11px; color: #aaa !important; }
.file-selected {
  display: flex; align-items: center; gap: 10px;
  background: #e8f5e9; border-radius: 8px; padding: 8px 12px; width: 100%;
}
.file-name { flex: 1; font-size: 13px; font-weight: 600; color: #2e7d32; text-align: left; word-break: break-all; }
.file-remove {
  background: none; border: none; color: #e53935; cursor: pointer;
  font-size: 14px; font-weight: 700; padding: 0 4px; flex-shrink: 0;
}
.file-existing {
  margin-top: 8px; font-size: 12px; color: #555; display: flex; align-items: center; gap: 8px;
}
.file-link { color: var(--primary); font-weight: 600; text-decoration: none; }
.file-link:hover { text-decoration: underline; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 500; display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal-box { background: white; border-radius: 20px; padding: 28px; width: 100%; max-width: 560px; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.25); }
.modal-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.close-btn  { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--gray); }
.btn-full   { width: 100%; margin-top: 8px; }
.alert      { padding: 10px 14px; border-radius: 10px; font-size: 0.85rem; margin-bottom: 14px; }
.alert-error { background: #FFF3F3; color: #F44336; border: 1px solid #FFCDD2; }

@media (max-width: 768px) {
  th:nth-child(1), td:nth-child(1),
  th:nth-child(5), td:nth-child(5) { display: none; }
}
</style>