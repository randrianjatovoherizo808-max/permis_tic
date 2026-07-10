<template>
  <div class="register-page">
    <div class="reg-lang-bar"><LangSwitcher variant="light" /></div>
    <div class="register-card">

      <!-- En-tête -->
      <div class="reg-header">
        <h1>🎓 PERMIS TIC</h1>
        <p>{{ t.creerCompte }}</p>
      </div>

      <!-- Indicateur d'étapes -->
      <div class="steps">
        <div
          v-for="n in 3" :key="n"
          class="step-dot"
          :class="{ active: step >= n, done: step > n }"
        >
          <span v-if="step > n">✓</span>
          <span v-else>{{ n }}</span>
        </div>
        <div class="step-bar" :style="{ width: stepBarWidth }"></div>
      </div>
      <div class="step-labels">
        <span :class="{ bold: step === 1 }">{{ t.etape1 }}</span>
        <span :class="{ bold: step === 2 }">{{ t.etape2 }}</span>
        <span :class="{ bold: step === 3 }">{{ t.etape3 }}</span>
      </div>

      <!-- Étape 1 : Identifiants -->
      <div v-if="step === 1">
        <div class="form-group">
          <label>{{ t.prenomLabel }} *</label>
          <input v-model="form.prenom" type="text" required placeholder="Votre prénom" autocomplete="given-name"
            @keypress="filtrerCaracteres" @paste="filtrerCollage($event, 'prenom')" />
        </div>
        <div class="form-group">
          <label>{{ t.nomLabel }} *</label>
          <input v-model="form.nom" type="text" required placeholder="Votre nom" autocomplete="family-name"
            @keypress="filtrerCaracteres" @paste="filtrerCollage($event, 'nom')" />
        </div>
        <div class="form-group">
          <label>Email *</label>
          <input v-model="form.email" type="email" required placeholder="votre@email.com" autocomplete="email" />
        </div>
        <div class="form-group">
          <label>{{ t.telephoneLabel }}</label>
          <input
            v-model="form.telephone"
            type="tel"
            inputmode="numeric"
            pattern="^[0-9]{10}$"
            maxlength="10"
            placeholder="0341234567"
            @input="onTelephoneInput"
            @paste="onTelephonePaste"
          />
          <small v-if="telError" class="field-error">{{ telError }}</small>
        </div>
        <div class="form-group">
          <label>{{ t.passwordLabel }} *</label>
          <div class="input-pwd">
            <input
              v-model="form.password"
              :type="showPwd ? 'text' : 'password'"
              required
              placeholder="Minimum 6 caractères"
              minlength="6"
            />
            <button type="button" @click="showPwd = !showPwd">{{ showPwd ? '🙈' : '👁' }}</button>
          </div>
        </div>
        <div class="form-group">
          <label>{{ t.confirmerMdp }} *</label>
          <div class="input-pwd">
            <input
              v-model="form.passwordConfirm"
              :type="showPwdC ? 'text' : 'password'"
              required
              placeholder="Répéter le mot de passe"
            />
            <button type="button" @click="showPwdC = !showPwdC">{{ showPwdC ? '🙈' : '👁' }}</button>
          </div>
        </div>
        <div v-if="errStep1" class="alert alert-error">{{ errStep1 }}</div>
        <button class="btn btn-primary btn-full" @click="validerStep1">Suivant →</button>
      </div>

      <!-- Étape 2 : Choix de la formation -->
      <div v-if="step === 2">
        <p class="step-intro">
          Bonjour <strong>{{ form.prenom }}</strong> ! Choisissez la formation qui vous convient.
        </p>

        <!-- Filtre niveau -->
        <div class="niveau-tabs">
          <button
            v-for="n in ['A', 'B', 'C']" :key="n"
            class="niveau-tab"
            :class="{ active: niveauSelec === n, [`niv-${n.toLowerCase()}`]: true }"
            @click="niveauSelec = n"
          >
            Niveau {{ n }}
          </button>
        </div>

        <div v-if="loadingFormations" class="loading-msg">Chargement des formations…</div>
        <div v-else class="formations-list">
          <div
            v-for="f in formationsFiltrees"
            :key="f.id"
            class="formation-option"
            :class="{ selected: form.formation === f.id, [`niv-border-${f.niveau.toLowerCase()}`]: true }"
            @click="form.formation = f.id; form.formationNom = f.nom; form.formationNiveau = f.niveau"
          >
            <div class="fo-header">
              <span class="niveau-badge" :class="'niveau-' + f.niveau.toLowerCase()">Niveau {{ f.niveau }}</span>
              <span class="fo-duree">⏱ {{ f.duree }}h</span>
            </div>
            <div class="fo-nom">{{ f.nom }}</div>
            <div class="fo-desc">{{ f.description || 'Formation professionnelle en informatique.' }}</div>
            <div class="fo-meta">
              <span>👥 {{ f.places }} places</span>
              <span v-if="f.formateur_nom">👨‍🏫 {{ f.formateur_nom }}</span>
            </div>
          </div>
          <div v-if="formationsFiltrees.length === 0" class="empty-msg">
            Aucune formation disponible pour ce niveau.
          </div>
        </div>

        <div v-if="errStep2" class="alert alert-error">{{ errStep2 }}</div>
        <div class="step-nav">
          <button class="btn btn-outline" @click="step = 1">← Retour</button>
          <button class="btn btn-primary" @click="validerStep2">Suivant →</button>
        </div>
      </div>

      <!-- Étape 3 : Récapitulatif + confirmation -->
      <div v-if="step === 3">
        <div class="recap-card">
          <h3>📋 Récapitulatif de votre inscription</h3>
          <div class="recap-row"><span>{{ t.nomComplet }}</span><strong>{{ form.prenom }} {{ form.nom }}</strong></div>
          <div class="recap-row"><span>Email</span><strong>{{ form.email }}</strong></div>
          <div class="recap-row"><span>{{ t.telephoneLabel }}</span><strong>{{ form.telephone || '—' }}</strong></div>
          <div class="recap-row"><span>{{ t.formation }}</span><strong>{{ form.formationNom }}</strong></div>
          <div class="recap-row">
            <span>Niveau</span>
            <span class="niveau-badge" :class="'niveau-' + (form.formationNiveau || '').toLowerCase()">
              {{ form.formationNiveau }}
            </span>
          </div>
        </div>

        <p class="recap-note">
          ℹ️ Votre inscription sera examinée par un administrateur. Vous recevrez une confirmation par email.
        </p>

        <div v-if="errStep3" class="alert alert-error">{{ errStep3 }}</div>
        <div v-if="success"   class="alert alert-success">{{ success }}</div>

        <div class="step-nav" v-if="!success">
          <button class="btn btn-outline" @click="step = 2" :disabled="submitting">← Retour</button>
          <button class="btn btn-primary" @click="soumettre" :disabled="submitting">
            {{ submitting ? '⏳ Envoi…' : '✅ Confirmer l\'inscription' }}
          </button>
        </div>

        <div v-if="success" class="success-actions">
          <RouterLink to="/login" class="btn btn-primary btn-full">🔐 Se connecter</RouterLink>
        </div>
      </div>
<!-- Bouton Google -->
<div class="google-box">
  <button class="google-btn" @click="googleRegister">
    <img
      src="https://developers.google.com/identity/images/g-logo.png"
      alt="Google"
      class="google-icon"
    />
    {{ t.sinscrireGoogle }}
  </button>
</div>
<p class="auth-link">
  {{ t.dejaInscrit }} <RouterLink to="/login">{{ t.seConnecter }}</RouterLink>
</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import { useLangStore } from '../store/lang'
import { storeToRefs } from 'pinia'
import LangSwitcher from '../components/LangSwitcher.vue'

const langStore = useLangStore()
const { t } = storeToRefs(langStore)

const step       = ref(1)
const showPwd    = ref(false)
const showPwdC   = ref(false)
const submitting = ref(false)
const success    = ref('')
const errStep1   = ref('')
const errStep2   = ref('')
const errStep3   = ref('')
const niveauSelec      = ref('A')
const loadingFormations = ref(false)
const formations        = ref([])
const telError          = ref('')

const form = ref({
  prenom: '', nom: '', email: '', telephone: '',
  password: '', passwordConfirm: '',
  formation: null, formationNom: '', formationNiveau: '',
})

function googleRegister() {
 window.location.href = `${import.meta.env.VITE_API_URL}/auth/google/`
}

function onTelephoneInput(e) {
  const raw = e.target.value
  const cleaned = raw.replace(/\D/g, '').slice(0, 10)

  if (/[^0-9]/.test(raw)) {
    telError.value = 'Seuls les chiffres sont autorisés.'
  } else if (raw.replace(/\D/g, '').length > 10) {
    telError.value = 'Le numéro ne doit pas dépasser 10 chiffres.'
  } else {
    telError.value = ''
  }

  form.value.telephone = cleaned
}

function onTelephonePaste(e) {
  e.preventDefault()
  const text = (e.clipboardData || window.clipboardData).getData('text')
  const cleaned = text.replace(/\D/g, '').slice(0, 10)
  if (/[^0-9]/.test(text)) {
    telError.value = 'Seuls les chiffres sont autorisés.'
  } else {
    telError.value = ''
  }
  form.value.telephone = cleaned
}





const stepBarWidth = computed(() => `${(step.value - 1) * 50}%`)

const formationsFiltrees = computed(() =>
  formations.value.filter((f) => f.niveau === niveauSelec.value)
)

async function chargerFormations() {
  loadingFormations.value = true
  try {
    const { data } = await api.get('/formations/')
    formations.value = data.results ?? data
  } catch {
    formations.value = []
  } finally {
    loadingFormations.value = false
  }
}

function validerStep1() {
// Bloquer la saisie de caractères spéciaux et chiffres en temps réel
function filtrerCaracteres(e) {
  const allowed = /^[a-zA-ZÀ-ÿ\s\-']$/
  if (!allowed.test(e.key)) {
    e.preventDefault()
  }
}
function filtrerCollage(e, champ) {
  e.preventDefault()
  const texte = (e.clipboardData || window.clipboardData).getData('text')
  const nettoye = texte.replace(/[^a-zA-ZÀ-ÿ\s\-']/g, '')
  form.value[champ] = (form.value[champ] || '') + nettoye
}

  errStep1.value = ''
  const { prenom, nom, email, telephone, password, passwordConfirm } = form.value
  if (!prenom || !nom || !email || !password) {
    errStep1.value = 'Veuillez remplir tous les champs obligatoires.'
    return
  }
  // Seules les lettres (y compris accents), espaces, tirets et apostrophes sont autorisés
  const regexNom = /^[a-zA-ZÀ-ÿ\s\-']+$/
  if (!regexNom.test(prenom)) {
    errStep1.value = 'Le prénom ne peut pas contenir de caractères spéciaux ou de chiffres.'
    return
  }
  if (!regexNom.test(nom)) {
    errStep1.value = 'Le nom ne peut pas contenir de caractères spéciaux ou de chiffres.'
    return
  }
  if (telephone && !/^[0-9]{10}$/.test(telephone)) {
    errStep1.value = 'Le téléphone doit contenir exactement 10 chiffres.'
    return
  }
  if (password.length < 6) {
    errStep1.value = 'Le mot de passe doit contenir au moins 6 caractères.'
    return
  }
  if (password !== passwordConfirm) {
    errStep1.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  step.value = 2
}

function validerStep2() {
  errStep2.value = ''
  if (!form.value.formation) {
    errStep2.value = 'Veuillez choisir une formation.'
    return
  }
  step.value = 3
}

async function soumettre() {
  errStep3.value = ''
  submitting.value = true
  try {
    await api.post('/auth/register/', {
      prenom:     form.value.prenom,
      nom:        form.value.nom,
      email:      form.value.email,
      telephone:  form.value.telephone,
      password:   form.value.password,
      formation:  form.value.formation,
    })
    success.value = t.value.successInscription
  } catch (e) {
    const data = e.response?.data
    errStep3.value = typeof data === 'object'
      ? Object.values(data).flat().join(' ')
      : 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    submitting.value = false
  }
}

// useRoute au niveau setup (pas dans onMounted)
const route = useRoute()

onMounted(async () => {
  await chargerFormations()
  // Pré-remplir depuis query param ?formation=ID (venant de FormationsPublicView)
  const fid = route.query.formation ? parseInt(route.query.formation) : null
  if (fid) {
    const f = formations.value.find(f => f.id === fid)
    if (f) {
      form.value.formation      = f.id
      form.value.formationNom   = f.nom
      form.value.formationNiveau = f.niveau
      niveauSelec.value         = f.niveau
      // Aller directement à l'étape 2 avec formation pré-sélectionnée
      step.value = 2
    }
  }
})
</script>

<style scoped>
.reg-lang-bar { position: fixed; top: 10px; right: 16px; z-index: 200; }
.register-page  { min-height: 100vh; display: flex; align-items: flex-start; justify-content: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); padding: 30px 16px; }
.register-card  { background: white; border-radius: 24px; padding: 32px 28px; width: 100%; max-width: 520px; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
.reg-header     { text-align: center; margin-bottom: 24px; }
.reg-header h1  { font-size: 1.5rem; color: var(--primary); }
.reg-header p   { color: var(--gray); font-size: 0.88rem; margin-top: 4px; }

/* Étapes */
.steps        { display: flex; align-items: center; justify-content: center; gap: 0; position: relative; margin-bottom: 6px; }
.step-bar     { position: absolute; top: 50%; height: 3px; background: var(--primary); left: calc(50% - 56px); transition: width 0.4s ease; z-index: 0; transform: translateY(-50%); }
.step-dot     { width: 32px; height: 32px; border-radius: 50%; background: var(--light); border: 2px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; z-index: 1; transition: all 0.3s; margin: 0 28px; }
.step-dot.active { background: var(--primary); border-color: var(--primary); color: white; }
.step-dot.done   { background: var(--secondary); border-color: var(--secondary); color: white; }
.step-labels  { display: flex; justify-content: space-around; font-size: 11px; color: var(--gray); margin-bottom: 20px; }
.step-labels .bold { font-weight: 700; color: var(--primary); }

.step-intro { font-size: 13px; color: var(--gray); margin-bottom: 16px; text-align: center; }

/* Niveau tabs */
.niveau-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.niveau-tab  { flex: 1; padding: 8px; border: 2px solid var(--border); border-radius: 10px; background: white; cursor: pointer; font-weight: 700; font-size: 13px; transition: 0.2s; }
.niveau-tab.niv-a.active { border-color: var(--niveau-a); background: var(--niveau-a); color: white; }
.niveau-tab.niv-b.active { border-color: var(--niveau-b); background: var(--niveau-b); color: white; }
.niveau-tab.niv-c.active { border-color: var(--niveau-c); background: var(--niveau-c); color: white; }

/* Cartes de formation */
.formations-list { display: flex; flex-direction: column; gap: 10px; max-height: 320px; overflow-y: auto; padding-right: 4px; margin-bottom: 14px; }
.formation-option { border: 2px solid var(--border); border-radius: 14px; padding: 14px; cursor: pointer; transition: 0.2s; }
.formation-option:hover   { border-color: var(--primary); }
.formation-option.selected { border-color: var(--primary); background: rgba(76,175,80,0.06); }
.niv-border-a.selected { border-color: var(--niveau-a); background: rgba(33,150,243,0.06); }
.niv-border-b.selected { border-color: var(--niveau-b); background: rgba(255,152,0,0.06); }
.niv-border-c.selected { border-color: var(--niveau-c); background: rgba(156,39,176,0.06); }
.fo-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.fo-duree  { font-size: 11px; color: var(--gray); }
.fo-nom    { font-weight: 700; font-size: 0.95rem; margin-bottom: 4px; }
.fo-desc   { font-size: 12px; color: var(--gray); margin-bottom: 8px; }
.fo-meta   { display: flex; gap: 12px; font-size: 11px; color: var(--gray); }

/* Récap */
.recap-card { background: var(--light); border-radius: 14px; padding: 16px; margin-bottom: 16px; }
.recap-card h3 { font-size: 0.95rem; margin-bottom: 12px; }
.recap-row    { display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 13px; }
.recap-row:last-child { border-bottom: none; }
.recap-note   { font-size: 12px; color: var(--gray); margin-bottom: 16px; line-height: 1.5; }

.step-nav       { display: flex; gap: 10px; margin-top: 12px; }
.step-nav .btn  { flex: 1; }
.loading-msg    { text-align: center; color: var(--gray); padding: 20px; font-size: 13px; }
.empty-msg      { text-align: center; color: var(--gray); padding: 16px; font-size: 13px; }
.success-actions { margin-top: 12px; }
.field-error { color: #e53935; font-size: 12px; margin-top: 4px; display: block; }
.auth-link   { text-align: center; margin-top: 20px; font-size: 0.85rem; color: var(--gray); }
.auth-link a { color: var(--primary); font-weight: 700; text-decoration: none; }

.google-box {
  margin-bottom: 20px;
}

.google-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;

  padding: 12px 16px;
  background: white;
  border: 1px solid #dadce0;
  border-radius: 12px;

  font-size: 14px;
  font-weight: 600;
  color: #3c4043;

  cursor: pointer;
  transition: all 0.2s ease;
}

.google-btn:hover {
  background: #f8f9fa;
  border-color: #4285f4;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.google-icon {
  width: 20px;
  height: 20px;
}



@media (max-width: 500px) {
  .register-page { padding: 0; align-items: flex-start; }
  .register-card { border-radius: 0; min-height: 100vh; padding: 24px 16px 40px; box-shadow: none; }
  .niveau-tabs { flex-direction: column; }
  .niveau-tab  { text-align: left; }
  .formations-list { max-height: 260px; }
  .step-nav { flex-direction: column; }
  .step-nav .btn { width: 100%; }
}
</style>