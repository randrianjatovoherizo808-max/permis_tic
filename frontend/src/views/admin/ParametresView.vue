<template>
  <div>
    <h2 class="page-title">⚙️ Paramètres</h2>

    <div class="params-grid">

      <!-- ── Infos du centre ── -->
      <div class="card">
        <h3 class="section-title">🏢 Informations du centre</h3>
        <div class="form-group">
          <label>Nom du centre</label>
          <input v-model="infos.nom" type="text" placeholder="PERMIS TIC" />
        </div>
        <div class="form-group">
          <label>Adresse</label>
          <input v-model="infos.adresse" type="text" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>Téléphone</label>
            <input v-model="infos.telephone" type="tel" placeholder="033 300 5845" />
          </div>
          <div class="form-group">
            <label>WhatsApp</label>
            <input v-model="infos.whatsapp" type="tel" placeholder="0389839798" />
          </div>
        </div>
        <div class="form-group">
          <label>Nom affiché WhatsApp</label>
          <input v-model="infos.whatsapp_nom" type="text" placeholder="Thierry – WhatsApp" />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input v-model="infos.email" type="email" placeholder="contact@permistic.mg" />
        </div>
        <div class="form-group">
          <label>Slogan</label>
          <input v-model="infos.slogan" type="text" placeholder="Formation Numérique — Madagascar" />
        </div>
        <div v-if="infosMsg" class="alert" :class="infosSuccess ? 'alert-success' : 'alert-error'">{{ infosMsg }}</div>
        <button class="btn btn-primary btn-full" @click="sauvegarder" :disabled="loading">
          {{ loading ? '⏳ Enregistrement…' : '💾 Enregistrer' }}
        </button>
      </div>

      <!-- ── Mot de passe ── -->
      <div class="card">
        <h3 class="section-title">🔒 Changer le mot de passe</h3>
        <div class="form-group">
          <label>Mot de passe actuel</label>
          <div class="input-pwd">
            <input v-model="pwd.ancien" :type="showAncien ? 'text' : 'password'" placeholder="Mot de passe actuel" />
            <button type="button" @click="showAncien = !showAncien">{{ showAncien ? '🙈' : '👁' }}</button>
          </div>
        </div>
        <div class="form-group">
          <label>Nouveau mot de passe</label>
          <div class="input-pwd">
            <input v-model="pwd.nouveau" :type="showNouv ? 'text' : 'password'" placeholder="Minimum 4 caractères" minlength="4" />
            <button type="button" @click="showNouv = !showNouv">{{ showNouv ? '🙈' : '👁' }}</button>
          </div>
        </div>
        <div class="form-group">
          <label>Confirmer</label>
          <div class="input-pwd">
            <input v-model="pwd.confirm" :type="showConf ? 'text' : 'password'" placeholder="Répéter le mot de passe" />
            <button type="button" @click="showConf = !showConf">{{ showConf ? '🙈' : '👁' }}</button>
          </div>
        </div>
        <div v-if="pwdMsg" class="alert" :class="pwdSuccess ? 'alert-success' : 'alert-error'">{{ pwdMsg }}</div>
        <button class="btn btn-primary btn-full" @click="changerMdp" :disabled="pwdLoading">
          {{ pwdLoading ? '⏳ Changement…' : '🔑 Changer le mot de passe' }}
        </button>
      </div>

    </div>

    <!-- ── Contenu des 3 Niveaux ── -->
    <div class="card" style="margin-top:24px;">
      <h3 class="section-title">🎓 Contenu des 3 Niveaux (page d'accueil)</h3>
      <p style="font-size:13px;color:#888;margin-bottom:20px;">
        Modifiez les titres, descriptions et matières affichées sur la page d'accueil.
      </p>

      <div class="niveaux-edit-grid">
        <div v-for="nv in niveauxEdit" :key="nv.key" class="niveau-edit-card" :class="'border-' + nv.color">
          <div class="niveau-edit-header" :class="'bg-light-' + nv.color">
            <span class="niveau-edit-icon">{{ nv.emoji }}</span>
            <strong>{{ nv.label }}</strong>
          </div>

          <div class="form-group">
            <label>Titre</label>
            <input v-model="infos[nv.key + '_titre']" type="text" :placeholder="'Niveau ' + nv.label.slice(-1)" />
          </div>
          <div class="form-group">
            <label>Sous-titre</label>
            <input v-model="infos[nv.key + '_sous']" type="text" placeholder="Débutant / Intermédiaire / Avancé" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="infos[nv.key + '_desc']" rows="2" placeholder="Description du niveau…"></textarea>
          </div>
          <div class="form-group">
            <label>Matières</label>
            <div class="matieres-list">
              <div
                v-for="(item, idx) in infos[nv.key + '_items']"
                :key="idx"
                class="matiere-row"
              >
                <input
                  v-model="item.icon"
                  class="matiere-icon-input"
                  maxlength="4"
                  placeholder="📌"
                />
                <input
                  v-model="item.name"
                  class="matiere-name-input"
                  placeholder="Nom de la matière"
                />
                <button
                  type="button"
                  class="matiere-del-btn"
                  @click="removeItem(nv.key, idx)"
                  title="Supprimer cette matière"
                >🗑️</button>
              </div>
              <button type="button" class="matiere-add-btn" @click="addItem(nv.key)">
                ＋ Ajouter une matière
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="infosMsg" class="alert" :class="infosSuccess ? 'alert-success' : 'alert-error'" style="margin-top:16px;">{{ infosMsg }}</div>
      <button class="btn btn-primary" style="margin-top:16px;width:100%;" @click="sauvegarder" :disabled="loading">
        {{ loading ? '⏳ Enregistrement…' : '💾 Enregistrer les niveaux' }}
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'
import { useParametresStore } from '../../store/parametres'

const loading    = ref(false)
const _pStore    = useParametresStore()
const infosMsg   = ref('')
const infosSuccess = ref(false)

const infos = ref({
  nom: 'PERMIS TIC',
  adresse: 'PIFTIC CNFPPSH — Ampandrianomby, Antananarivo',
  telephone: '033 300 5845',
  whatsapp:     '0389839798',
  whatsapp_nom: 'Thierry – WhatsApp',
  email: 'contact@permistic.mg',
  slogan: 'Formation Numérique — Madagascar',
  niveau_a_titre: 'Niveau A',
  niveau_a_sous:  'Débutant',
  niveau_a_desc:  'Maîtrisez les outils bureautiques essentiels utilisés dans tous les métiers.',
  niveau_a_items: [{ name: 'Word', icon: '📝' }, { name: 'Excel', icon: '📊' }, { name: 'PowerPoint', icon: '📽️' }],
  niveau_b_titre: 'Niveau B',
  niveau_b_sous:  'Intermédiaire',
  niveau_b_desc:  'Explorez le design graphique et créez des visuels professionnels percutants.',
  niveau_b_items: [{ name: 'Photoshop', icon: '🖼️' }, { name: 'Illustrator', icon: '✏️' }, { name: 'UI/UX Design', icon: '🎨' }],
  niveau_c_titre: 'Niveau C',
  niveau_c_sous:  'Avancé',
  niveau_c_desc:  'Devenez développeur ou expert cybersécurité avec les technologies actuelles.',
  niveau_c_items: [{ name: 'React', icon: '⚛️' }, { name: 'Laravel', icon: '🔴' }, { name: 'Cybersécurité', icon: '🔐' }],
})

const niveauxEdit = [
  { key: 'niveau_a', label: 'Niveau A', emoji: '🖥️', color: 'blue' },
  { key: 'niveau_b', label: 'Niveau B', emoji: '🎨', color: 'orange' },
  { key: 'niveau_c', label: 'Niveau C', emoji: '🚀', color: 'purple' },
]

// Ajouter une matière
function addItem(key) {
  if (!Array.isArray(infos.value[key + '_items'])) {
    infos.value[key + '_items'] = []
  }
  infos.value[key + '_items'].push({ icon: '📌', name: '' })
}

// Supprimer une matière
function removeItem(key, idx) {
  infos.value[key + '_items'].splice(idx, 1)
}

async function charger() {
  await _pStore.charger()
  // Synchronise le formulaire avec les données du store
  Object.keys(infos.value).forEach(k => {
    if (_pStore.p[k] !== undefined && _pStore.p[k] !== null && _pStore.p[k] !== '') {
      infos.value[k] = _pStore.p[k]
    }
  })
}

async function sauvegarder() {
  loading.value  = true
  infosMsg.value = ''
  try {
    await _pStore.sauvegarder(infos.value)
    infosSuccess.value = true
    infosMsg.value     = '✅ Paramètres enregistrés avec succès.'
  } catch {
    infosSuccess.value = false
    infosMsg.value     = "❌ Erreur lors de l'enregistrement."
  } finally {
    loading.value = false
    setTimeout(() => infosMsg.value = '', 3000)
  }
}

// Mot de passe
const pwd        = ref({ ancien: '', nouveau: '', confirm: '' })
const pwdLoading = ref(false)
const pwdMsg     = ref('')
const pwdSuccess = ref(false)
const showAncien = ref(false)
const showNouv   = ref(false)
const showConf   = ref(false)

async function changerMdp() {
  pwdMsg.value = ''
  if (pwd.value.nouveau !== pwd.value.confirm) {
    pwdSuccess.value = false; pwdMsg.value = '❌ Les mots de passe ne correspondent pas.'; return
  }
  pwdLoading.value = true
  try {
    await api.post('/auth/change-password/', { old_password: pwd.value.ancien, new_password: pwd.value.nouveau })
    pwdSuccess.value = true
    pwdMsg.value     = '✅ Mot de passe modifié avec succès.'
    pwd.value        = { ancien: '', nouveau: '', confirm: '' }
  } catch (e) {
    pwdSuccess.value = false
    pwdMsg.value     = e.response?.data?.error || '❌ Mot de passe actuel incorrect.'
  } finally {
    pwdLoading.value = false
    setTimeout(() => pwdMsg.value = '', 4000)
  }
}

onMounted(charger)
</script>

<style scoped>
.params-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 768px) { .params-grid { grid-template-columns: 1fr; } }

.section-title { font-size: 1rem; font-weight: 700; margin-bottom: 18px; color: var(--primary, #4CAF50); }

.form-group       { margin-bottom: 16px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #555; margin-bottom: 6px; }
.form-group input,
.form-group textarea { width: 100%; border: 1.5px solid #ddd; border-radius: 10px; padding: 10px 14px;
  font-size: 14px; outline: none; transition: .2s; box-sizing: border-box; font-family: inherit; resize: vertical; }
.form-group input:focus,
.form-group textarea:focus { border-color: var(--primary, #4CAF50); }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.input-pwd          { position: relative; }
.input-pwd input    { padding-right: 44px; }
.input-pwd button   { position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; font-size: 16px; }

.btn-full { width: 100%; padding: 12px; margin-top: 4px; }

.alert { padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; }
.alert-success { background: #e8f5e9; color: #2e7d32; border-left: 3px solid #4CAF50; }
.alert-error   { background: #fff0f0; color: #c62828; border-left: 3px solid #e53935; }

/* Niveaux */
.niveaux-edit-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
@media (max-width: 900px) { .niveaux-edit-grid { grid-template-columns: 1fr; } }

.niveau-edit-card { border-radius: 14px; overflow: hidden; border: 2px solid #eee; }
.border-blue   { border-color: #90caf9; }
.border-orange { border-color: #ffcc80; }
.border-purple { border-color: #ce93d8; }

.niveau-edit-header { display: flex; align-items: center; gap: 10px; padding: 14px 16px; font-size: 15px; }
.bg-light-blue   { background: #e3f2fd; color: #1565c0; }
.bg-light-orange { background: #fff8e1; color: #e65100; }
.bg-light-purple { background: #f3e5f5; color: #6a1b9a; }
.niveau-edit-icon { font-size: 1.3rem; }

/* Matières dynamiques */
.matieres-list { display: flex; flex-direction: column; gap: 8px; }

.matiere-row {
  display: grid;
  grid-template-columns: 48px 1fr 36px;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.matiere-icon-input {
  width: 48px;
  border: 1.5px solid #ddd; border-radius: 8px; padding: 8px 4px;
  font-size: 18px; text-align: center; outline: none;
  transition: .2s; box-sizing: border-box;
}
.matiere-icon-input:focus { border-color: var(--primary, #4CAF50); }

.matiere-name-input {
  width: 100%;
  border: 1.5px solid #ddd; border-radius: 8px; padding: 8px 12px;
  font-size: 14px; outline: none; transition: .2s; box-sizing: border-box;
}
.matiere-name-input:focus { border-color: var(--primary, #4CAF50); }

.matiere-del-btn {
  width: 36px; height: 36px;
  border-radius: 8px; border: none; background: #fff0f0;
  font-size: 15px; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
  transition: background .15s; flex-shrink: 0;
}
.matiere-del-btn:hover { background: #ffcdd2; }

.matiere-add-btn {
  align-self: flex-start; margin-top: 4px;
  padding: 8px 16px; border-radius: 8px;
  border: 1.5px dashed var(--primary, #4CAF50);
  background: transparent; color: var(--primary, #4CAF50);
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: background .15s;
}
.matiere-add-btn:hover { background: #e8f5e9; }

.niveau-edit-card .form-group { padding: 0 14px; margin-bottom: 12px; }
.niveau-edit-card .form-group:first-of-type { margin-top: 14px; }
</style>