<template>
  <div class="page">
    <div class="card">

      <!-- Header -->
      <div class="card-header">
        <img src="/logo.png" alt="PIFTIC" class="header-logo" />
        <h1>PERMIS TIC</h1>
        <p>Plateforme de formation numérique</p>
      </div>

      <!-- Chargement -->
      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <p>Connexion en cours…</p>
      </div>

      <!-- Erreur -->
      <div v-else-if="error" class="state-box">
        <div class="state-icon">❌</div>
        <p class="state-msg error-msg">{{ error }}</p>
        <RouterLink to="/login" class="btn-primary">← Retour à la connexion</RouterLink>
      </div>

      <!-- ══ INSCRIPTION RÉUSSIE ══ -->
      <div v-else-if="statut === 'inscription_reussie'" class="email-preview">
        <div class="email-body">
          <p>Bonjour <strong>{{ prenom }}</strong>,</p>
          <p>
            Votre demande d'inscription au
            <strong>« {{ niveauLabel }} »</strong>
            a bien été reçue.
          </p>
          <div class="email-notice">
            <p>
              ⏳ <strong>Votre inscription est actuellement en attente de validation par l'administrateur.</strong><br/>
              <span>Vous recevrez un email dès que votre accès aux cours sera activé.</span>
            </p>
          </div>
          <p class="email-merci">Merci de votre patience.</p>
        </div>
        <div class="email-footer">
          <p>© 2025 Permis TIC · Madagascar</p>
          <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
        </div>
        <button class="btn-outline" style="margin:0 32px 24px;width:calc(100% - 64px)" @click="statut = 'en_attente'">
          🔄 Voir le statut de mon inscription
        </button>
      </div>

      <!-- ══ EN ATTENTE ══ -->
      <div v-else-if="statut === 'en_attente'" class="state-box attente">
        <div class="state-icon">⏳</div>
        <h2>Compte en attente de validation</h2>
        <p>
          Votre compte est actuellement <strong>en attente de validation</strong>
          par l'administrateur.
        </p>
        <div class="info-box">
          <p>📧 Un email de confirmation vous sera envoyé automatiquement
             sur <strong>{{ userEmail }}</strong> dès que votre accès sera activé.</p>
        </div>
        <div class="steps">
          <div class="step done">✅ Compte créé</div>
          <div class="step active">⏳ Validation admin</div>
          <div class="step">🔓 Accès aux cours</div>
        </div>
        <button class="btn-outline" @click="verifierStatut" :disabled="checkLoading">
          <span v-if="checkLoading" class="spinner-sm"></span>
          {{ checkLoading ? 'Vérification…' : '🔄 Vérifier mon statut' }}
        </button>
        <RouterLink to="/" class="link-back">← Retour à l'accueil</RouterLink>
      </div>

      <!-- ══ REJETÉE ══ -->
      <div v-else-if="statut === 'rejete'" class="state-box">
        <div class="state-icon">❌</div>
        <h2>Inscription non acceptée</h2>
        <p>Votre demande d'inscription n'a pas été retenue par l'administrateur.</p>
        <p style="font-size:13px;color:#888;margin-top:8px;">Vous pouvez vous inscrire à une autre formation.</p>
        <button class="btn-primary" style="margin-top:18px;" @click="statut = 'nouveau'">
          📋 Choisir une autre formation
        </button>
        <RouterLink to="/" class="link-back">← Retour à l'accueil</RouterLink>
      </div>

      <!-- ══ NOUVEAU ÉTUDIANT : choisir formation ou niveau ══ -->
      <div v-else-if="statut === 'nouveau'" class="form-section">
        <div class="welcome">
          <div class="welcome-avatar" :class="{ 'no-bg': photoUrl }">
            <img v-if="photoUrl" :src="photoUrl" alt="Photo de profil" class="avatar-img" />
            <span v-else>{{ initiales }}</span>
          </div>
          <div>
            <h2>Bienvenue, {{ prenom }} !</h2>
            <p>Choisissez un cours ou un niveau pour vous inscrire.</p>
          </div>
        </div>

        <!-- Tabs mode -->
        <div class="insc-mode-tabs">
          <button class="insc-mode-tab" :class="{active: inscMode==='cours'}"
                  @click="inscMode='cours'; niveau=''">
            📘 Cours spécifique
          </button>
          <button class="insc-mode-tab" :class="{active: inscMode==='niveau'}"
                  @click="inscMode='niveau'; formationId=null">
            🎓 Par niveau
          </button>
        </div>

        <!-- Mode cours spécifique -->
        <div v-if="inscMode === 'cours'" class="form-group" style="margin-top:14px">
          <label>Choisir un cours *</label>
          <div class="cours-list">
            <div v-for="f in formations" :key="f.id"
                 class="cours-item"
                 :class="{ 'cours-item--active': formationId === f.id }"
                 @click="formationId = f.id; niveau = f.niveau">
              <div class="cours-item-info">
                <strong>{{ f.nom }}</strong>
                <span class="niv-tag" :class="'niv-'+f.niveau.toLowerCase()">Niveau {{ f.niveau }}</span>
              </div>
              <span v-if="formationId === f.id" class="check-icon">✅</span>
            </div>
          </div>
          <p v-if="formations.length === 0" style="font-size:13px;color:#888;margin-top:8px;">
            Aucune formation disponible pour le moment.
          </p>
        </div>

        <!-- Mode niveau général -->
        <div v-if="inscMode === 'niveau'" class="form-group" style="margin-top:14px">
          <label>Niveau *</label>
          <div class="niveau-choices">
            <div v-for="niv in niveauxOptions" :key="niv.value"
                 class="niveau-choice"
                 :class="{ 'niveau-choice--active': niveau === niv.value }"
                 @click="niveau = niv.value">
              <span class="niv-icon">{{ niv.icon }}</span>
              <div>
                <strong>{{ niv.label }}</strong>
                <small>{{ niv.desc }}</small>
              </div>
            </div>
          </div>
        </div>

        <div v-if="error" class="alert error-msg" style="background:#ffebee;padding:10px 14px;border-radius:8px;margin-bottom:12px;">
          {{ error }}
        </div>
        <div v-if="successInscrit" class="alert success">
          ✅ Inscription enregistrée ! Vous serez notifié par email.
        </div>

        <button class="btn-primary" @click="valider"
                :disabled="inscLoading || (inscMode==='cours' ? !formationId : !niveau)">
          <span v-if="inscLoading" class="spinner-sm"></span>
          {{ inscLoading ? 'Envoi…' : "✅ Confirmer l'inscription" }}
        </button>
        <RouterLink to="/" class="link-back">← Annuler</RouterLink>
      </div>


    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore }   from '../store/auth'
import { useRoute, useRouter } from 'vue-router'
import api from '../services/api'

const auth   = useAuthStore()
const route  = useRoute()
const router = useRouter()

const loading       = ref(true)
const error         = ref('')
const statut        = ref('')   // 'en_attente' | 'confirme' | 'rejete' | 'nouveau'
const userEmail     = ref('')
const prenom        = ref('')
const initiales     = ref('')

const photoUrl      = ref('')
const niveau        = ref('')
const inscMode      = ref('cours')   // 'niveau' | 'cours'
const formationId   = ref(null)
const formations    = ref([])
const inscLoading      = ref(false)
const successInscrit   = ref(false)
const checkLoading     = ref(false)
const niveauLabel      = ref('')

const niveauxOptions = [
  { value: 'A', label: 'Niveau A – Débutant',      icon: '🟢', desc: 'Bureautique & outils essentiels' },
  { value: 'B', label: 'Niveau B – Intermédiaire', icon: '🟡', desc: 'Design graphique & création' },
  { value: 'C', label: 'Niveau C – Avancé',        icon: '🔴', desc: 'Développement & cybersécurité' },
]

onMounted(async () => {
  try {
    const access  = route.query.access
    const refresh = route.query.refresh
    const role    = route.query.role

    if (access)  localStorage.setItem('access_token',  access)
    if (refresh) localStorage.setItem('refresh_token', refresh)

    // Photo de profil Google
    photoUrl.value = route.query.photo_url || auth.user?.profil?.photo_url || ''

    await auth.restore()

    userEmail.value = auth.user?.email || ''
    prenom.value    = auth.user?.prenom || auth.user?.first_name || ''
    initiales.value = ((prenom.value[0] || '') + (auth.user?.nom?.[0] || auth.user?.last_name?.[0] || '')).toUpperCase()

    // Admin / formateur → dashboard
    if (role === 'admin' || role === 'formateur') {
      router.replace('/admin')
      return
    }

    // Charger toutes les formations disponibles
    try {
      const { data: fData } = await api.get('/formations/')
      formations.value = fData.results || fData
    } catch { formations.value = [] }

    // Récupérer les inscriptions existantes de l'utilisateur
    try {
      const { data: inscData } = await api.get('/inscriptions/mon-inscription/')
      const inscriptions = Array.isArray(inscData) ? inscData : (inscData ? [inscData] : [])

      if (inscriptions.length === 0) {
        // Aucune inscription → formulaire de choix
        statut.value = 'nouveau'
      } else {
        // A des inscriptions existantes
        const confirmee  = inscriptions.find(i => i.statut === 'confirme')
        const enAttente  = inscriptions.find(i => i.statut === 'en_attente')

        // Si l'utilisateur vient pour s'inscrire à un NOUVEAU cours (paramètre new_inscription=1)
        // OU s'il n'a que des inscriptions rejetées → montrer le formulaire
        const veutNouvelleInscription = route.query.new_inscription === '1'

        if (veutNouvelleInscription || (!confirmee && !enAttente)) {
          statut.value = 'nouveau'
        } else if (enAttente && !confirmee) {
          statut.value = 'en_attente'
        } else if (confirmee && !veutNouvelleInscription) {
          // Déjà confirmé et pas de demande d'ajout → espace apprenant
          router.replace('/espace-apprenant')
          return
        } else {
          statut.value = 'nouveau'
        }
      }
    } catch {
      statut.value = 'nouveau'
    }

  } catch (e) {
    error.value = 'Une erreur est survenue. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
})

async function verifierStatut() {
  checkLoading.value = true
  try {
    const { data } = await api.get('/inscriptions/mon-inscription/')
    const inscriptions = Array.isArray(data) ? data : (data ? [data] : [])
    const confirmee = inscriptions.find(i => i.statut === 'confirme')
    if (confirmee) {
      router.replace('/espace-apprenant')
    } else {
      const enAttente = inscriptions.find(i => i.statut === 'en_attente')
      statut.value = enAttente ? 'en_attente' : (inscriptions[0]?.statut || 'en_attente')
    }
  } catch {
    // silencieux
  } finally {
    checkLoading.value = false
  }
}

async function valider() {
  error.value = ''
  if (inscMode.value === 'cours' && !formationId.value) {
    error.value = 'Veuillez choisir un cours.'; return
  }
  if (inscMode.value === 'niveau' && !niveau.value) {
    error.value = 'Veuillez choisir un niveau.'; return
  }

  inscLoading.value = true
  try {
    const payload = {}
    if (inscMode.value === 'cours' && formationId.value) {
      payload.formation_id = formationId.value
      const f = formations.value.find(f => f.id === formationId.value)
      payload.niveau = f?.niveau || 'A'
      const niveauMap = { A: 'Niveau A – Débutant', B: 'Niveau B – Intermédiaire', C: 'Niveau C – Avancé' }
      niveauLabel.value = f?.nom ? `cours « ${f.nom} »` : niveauMap[f?.niveau] || 'Niveau A'
    } else {
      payload.niveau = niveau.value
      const niveauMap = { A: 'Niveau A – Débutant', B: 'Niveau B – Intermédiaire', C: 'Niveau C – Avancé' }
      niveauLabel.value = niveauMap[niveau.value] || niveau.value
    }
    await api.post('/google/register/formation/', payload)
    statut.value = 'inscription_reussie'
  } catch (e) {
    error.value = e.response?.data?.error || "Erreur lors de l'inscription."
  } finally {
    inscLoading.value = false
  }
}

</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #4CAF50, #F9C514);
  padding: 24px 16px;
}
.card {
  background: #fff; border-radius: 20px;
  width: 100%; max-width: 460px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18);
  overflow: hidden;
}

/* Header */
.card-header {
  background: linear-gradient(135deg, #4CAF50, #F9C514);
  padding: 24px 32px; text-align: center;
}
.header-logo { height: 44px; object-fit: contain; margin-bottom: 6px; }
.card-header h1 { color: #fff; font-size: 18px; font-weight: 900; margin: 0; letter-spacing: .5px; }
.card-header p  { color: rgba(255,255,255,.8); font-size: 12px; margin: 4px 0 0; }

/* States */
.state-box { padding: 36px 32px; text-align: center; }
.state-icon { font-size: 52px; margin-bottom: 14px; }
.state-box h2 { font-size: 1.2rem; margin: 0 0 10px; color: #222; }
.state-box p  { font-size: 14px; color: #555; line-height: 1.6; margin-bottom: 8px; }

/* Attente */
.attente h2   { color: #E65100; }
.info-box {
  background: #FFF8E1; border-left: 4px solid #FF9800;
  border-radius: 10px; padding: 14px 16px; margin: 16px 0; text-align: left;
}
.info-box p { font-size: 13px; color: #555; margin: 0; }

.steps { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin: 18px 0; }
.step { padding: 7px 14px; border-radius: 20px; font-size: 12px; font-weight: 600; background: #eee; color: #999; }
.step.done   { background: #E8F5E9; color: #2E7D32; }
.step.active { background: #FFF3E0; color: #E65100; border: 1px solid #FF9800; }

/* Form */
.form-section { padding: 28px 32px; }
.welcome { display: flex; align-items: center; gap: 14px; margin-bottom: 22px; padding-bottom: 18px; border-bottom: 1px solid #eee; }
.welcome-avatar {
  width: 50px; height: 50px; border-radius: 50%;
  background: linear-gradient(135deg, #4CAF50, #F9C514);
  color: white; font-weight: 900; font-size: 1.2rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; overflow: hidden;
}
.welcome-avatar.no-bg {
  background: transparent;
}
.avatar-img {
  width: 100%; height: 100%;
  object-fit: cover; border-radius: 50%;
}
.welcome h2 { font-size: 1.1rem; margin: 0 0 4px; }
.welcome p  { font-size: 12px; color: #888; margin: 0; }

.form-group { margin-bottom: 18px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #444; margin-bottom: 7px; }
.form-group select {
  width: 100%; border: 1.5px solid #ddd; border-radius: 10px;
  padding: 11px 14px; font-size: 14px; outline: none; transition: .2s;
  background: white; cursor: pointer;
}
.form-group select:focus { border-color: #4CAF50; }
.hint { font-size: 12px; color: #FF9800; margin-top: 6px; }

/* Niveau choices */
.niveau-choices { display: flex; flex-direction: column; gap: 10px; }
.niveau-choice {
  display: flex; align-items: center; gap: 14px;
  border: 2px solid #e5e7eb; border-radius: 12px;
  padding: 14px 16px; cursor: pointer; transition: .2s;
}
.niveau-choice:hover { border-color: #4CAF50; background: #f0faf0; }
.niveau-choice--active { border-color: #4CAF50; background: #e8f5e9; }
.niv-icon { font-size: 1.5rem; flex-shrink: 0; }
.niveau-choice div { display: flex; flex-direction: column; }
.niveau-choice strong { font-size: 14px; color: #222; }
.niveau-choice small { font-size: 11px; color: #888; margin-top: 2px; }

/* Buttons */
.btn-primary {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; padding: 13px; background: #4CAF50; color: #fff;
  border: none; border-radius: 10px; font-size: 14px; font-weight: 700;
  cursor: pointer; transition: .2s; text-decoration: none; margin-bottom: 0;
}
.btn-primary:hover:not(:disabled) { background: #43a047; transform: translateY(-1px); }
.btn-primary:disabled { opacity: .65; cursor: not-allowed; }

.btn-outline {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; padding: 11px; background: none;
  border: 2px solid #4CAF50; color: #4CAF50;
  border-radius: 10px; font-size: 13px; font-weight: 700;
  cursor: pointer; transition: .2s; margin-top: 14px;
}
.btn-outline:hover:not(:disabled) { background: #f0faf0; }
.btn-outline:disabled { opacity: .55; cursor: not-allowed; }

.link-back {
  display: block; text-align: center; margin-top: 14px;
  font-size: 13px; color: #4CAF50; text-decoration: none; font-weight: 600;
}
.link-back:hover { text-decoration: underline; }

.alert { padding: 11px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 14px; }
.success { background: #e8f5e9; color: #2e7d32; }
.error-msg { color: #c62828; }

/* Email preview */
.email-preview {
  background: #f5f5f5;
}
.email-body {
  background: #fff;
  padding: 32px 32px 24px;
  font-size: 14px;
  color: #333;
  line-height: 1.8;
}
.email-body p { margin: 0 0 14px; }
.email-notice {
  background: #fffbea;
  border-left: 4px solid #f0a500;
  border-radius: 6px;
  padding: 14px 16px;
  margin: 18px 0;
}
.email-notice p {
  margin: 0;
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}
.email-notice strong { color: #7a5000; }
.email-merci { color: #888; font-size: 13px; }
.email-footer {
  background: #f0f0f0;
  padding: 16px 32px;
  text-align: center;
  border-top: 1px solid #e0e0e0;
}
.email-footer p {
  margin: 2px 0;
  font-size: 11px;
  color: #999;
}

/* Spinners */
.spinner {
  width: 36px; height: 36px; margin: 0 auto 16px;
  border: 3px solid #e5e7eb; border-top-color: #4CAF50;
  border-radius: 50%; animation: spin .7s linear infinite;
}
.spinner-sm {
  width: 14px; height: 14px; display: inline-block;
  border: 2px solid rgba(255,255,255,.4); border-top-color: #fff;
  border-radius: 50%; animation: spin .7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Tabs mode inscription */
.insc-mode-tabs { display:flex; gap:8px; margin-bottom:4px; }
.insc-mode-tab {
  flex:1; padding:10px; border:2px solid #e5e7eb; border-radius:10px;
  background:white; cursor:pointer; font-size:13px; font-weight:600;
  color:#888; transition:.15s;
}
.insc-mode-tab.active { border-color:#4CAF50; background:#e8f5e9; color:#2e7d32; }

/* Liste cours spécifiques */
.cours-list {
  display:flex; flex-direction:column; gap:8px;
  max-height:260px; overflow-y:auto; padding-right:2px; margin-top:8px;
}
.cours-item {
  display:flex; align-items:center; justify-content:space-between;
  padding:11px 14px; border:2px solid #e5e7eb; border-radius:10px;
  cursor:pointer; transition:.15s;
}
.cours-item:hover { border-color:#4CAF50; background:#f0faf0; }
.cours-item--active { border-color:#4CAF50; background:#e8f5e9; }
.cours-item-info { display:flex; align-items:center; gap:10px; }
.cours-item-info strong { font-size:13px; color:#222; }
.niv-tag {
  font-size:11px; font-weight:700; padding:2px 8px; border-radius:20px; color:white;
}
.niv-a { background:#2196F3; }
.niv-b { background:#FF9800; }
.niv-c { background:#9C27B0; }
.check-icon { font-size:16px; }
</style>