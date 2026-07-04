<template>
  <div class="login-page">
    <div class="login-lang-bar"><LangSwitcher variant="dark" /></div>

    <!-- ══ PANNEAU GAUCHE ══ -->
    <div class="left-panel">
      <div class="left-content">
        <div class="logo-card">
          <img src="/logo.png" alt="PERMIS TIC" class="logo-img" />
        </div>
        <h2 class="welcome-title">{{ t.bienvenue }}</h2>
        <p class="welcome-sub">{{ t.seConnecterSub }}</p>
        <div class="divider-line"></div>
      </div>
      <div class="left-footer">© {{ new Date().getFullYear() }} PERMIS TIC</div>
    </div>

    <!-- ══ PANNEAU DROIT ══ -->
    <div class="right-panel">
      <div class="form-wrapper">

        <h1 class="form-title">{{ t.connexion }}</h1>
        <p class="form-sub">
          {{ t.pasDeCompte }}
          <RouterLink to="/register" class="link-register">{{ t.inscrivezVous }}</RouterLink>
        </p>

        <form @submit.prevent="handleLogin" class="login-form">

          <!-- Email -->
          <div class="field-group">
            <label>{{ t.emailLabel }}</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              </span>
              <input
                v-model="form.email"
                type="email"
                required
                placeholder="votre@email.com"
                autocomplete="email"
              />
            </div>
          </div>

          <!-- Mot de passe -->
          <div class="field-group">
            <label>{{ t.mdpLabel }}</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
              </span>
              <input
                v-model="form.password"
                :type="showPwd ? 'text' : 'password'"
                required
                placeholder="Votre mot de passe"
                autocomplete="current-password"
              />
              <button type="button" class="toggle-pwd" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <!-- Mot de passe oublié -->
          <div class="forgot-row">
            <RouterLink to="/mot-de-passe-oublie" class="forgot-link">{{ t.mdpOublie }}</RouterLink>
          </div>

          <!-- Erreur -->
          <div v-if="error" class="alert-error">{{ error }}</div>

          <!-- Bouton connexion -->
          <button type="submit" class="btn-connect" :disabled="loading">
            <span v-if="loading" class="spinner"></span>  
            <span v-else>{{ t.seConnecter }}</span>
          </button>

          <!-- Google -->
          <div class="separator"><span>ou</span></div>

          <button type="button" class="btn-google" @click="googleLogin">
            <svg width="18" height="18" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.08 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-3.59-13.46-8.83l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            {{ t.continuerGoogle }}
          </button>

          <!-- Retour accueil -->
          <div class="back-home">
            <RouterLink to="/">{{ t.visiterSite }}</RouterLink>
          </div>

        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useLangStore } from '../store/lang'
import { storeToRefs } from 'pinia'
import LangSwitcher from '../components/LangSwitcher.vue'

const router    = useRouter()
const route     = useRoute()
const auth      = useAuthStore()
const langStore = useLangStore()
const { t } = storeToRefs(langStore)
const loading = ref(false)
const error   = ref('')
const showPwd = ref(false)
const form    = ref({ email: '', password: '' })

const GOOGLE_ERROR_MESSAGES = {
  google_denied:          'Connexion Google annulée ou refusée.',
  google_token_failed:    'Impossible de valider la connexion avec Google. Veuillez réessayer.',
  google_no_token:        'Google n\'a pas renvoyé de jeton d\'accès. Veuillez réessayer.',
  google_userinfo_failed: 'Impossible de récupérer vos informations Google. Veuillez réessayer.',
  google_no_email:        'Votre compte Google ne fournit pas d\'adresse email accessible.',
  account_disabled:       'Ce compte a été désactivé par un administrateur. Contactez le support pour le réactiver.',
}

onMounted(() => {
  const errCode = route.query.error
  if (errCode) {
    if (errCode === 'account_disabled' && route.query.email) {
      error.value = `Le compte ${route.query.email} a été désactivé par un administrateur. Contactez le support pour le réactiver.`
    } else {
      error.value = GOOGLE_ERROR_MESSAGES[errCode] || 'La connexion avec Google a échoué. Veuillez réessayer.'
    }
  }
})

async function handleLogin() {
  error.value = ''
  loading.value = true

  try {
    await auth.login(form.value.email, form.value.password)
    await auth.fetchUser()

    const role = auth.user?.role

    if (role === 'etudiant') {
      // Vérifier si l'inscription est confirmée avant d'accéder à l'espace apprenant
      const inscriptions = auth.user?.inscriptions || []
      const aConfirme = inscriptions.some(i => i.statut === 'confirme')
      const aInscription = inscriptions.length > 0

      if (aConfirme) {
        // Inscription validée → espace apprenant
        router.push('/espace-apprenant')
      } else if (aInscription) {
        // Inscription en attente ou rejetée → page d'attente Google
        router.push('/auth/google/success')
      } else {
        // Pas encore inscrit → page d'attente pour choisir formation
        router.push('/auth/google/success')
      }
    } else if (role === 'admin') {
      router.push('/admin')
    } else if (role === 'formateur') {
      router.push('/admin')
    } else {
      router.push('/login')
    }

  } catch (e) {
    const data = e.response?.data

    if (e.response?.status === 401) {
      error.value = t.value.erreurLogin
    } else if (e.response?.status === 403) {
      error.value = t.value.erreurValidation
    } else {
      error.value = typeof data === 'object'
        ? Object.values(data).flat().join(' ')
        : 'Une erreur est survenue.'
    }
  } finally {
    loading.value = false
  }
}

function googleLogin() {
window.location.href = `${import.meta.env.VITE_API_URL}/auth/google/`
}
</script>

<style scoped>
/* ── Barre langue ────────────────────────────────────────────── */
.login-lang-bar {
  position: fixed; top: 10px; right: 16px; z-index: 200;
}
/* ── Layout split ─────────────────────────────────────────────── */
.login-page {
  min-height: 100vh;
  display: flex;
}

/* ── Panneau gauche ───────────────────────────────────────────── */
.left-panel {
  width: 42%;
  background: linear-gradient(135deg, #0097A7 0%, #8bc34a 50%, #c6d822 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 60px 40px 32px;
  position: relative;
  overflow: hidden;
}

/* Cercles décoratifs en fond */
.left-panel::before {
  content: '';
  position: absolute;
  width: 320px; height: 320px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.12);
  top: -80px; left: -80px;
}
.left-panel::after {
  content: '';
  position: absolute;
  width: 220px; height: 220px;
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.08);
  bottom: 60px; right: -60px;
}

.left-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  flex: 1;
  justify-content: center;
  z-index: 1;
}

.logo-card {
  background: rgba(255,255,255,0.18);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 24px;
  padding: 28px 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}

.logo-img {
  max-width: 180px;
  max-height: 120px;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(0,0,0,0.2));
}

.welcome-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #ffffff;
  margin: 0;
  letter-spacing: -0.5px;
}

.welcome-sub {
  color: rgba(255,255,255,0.75);
  font-size: 1rem;
  margin: 0;
}

.divider-line {
  width: 60px;
  height: 2px;
  background: rgba(255,255,255,0.35);
  border-radius: 2px;
}

.left-footer {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
  z-index: 1;
}

/* ── Panneau droit ────────────────────────────────────────────── */
.right-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  padding: 40px 24px;
}

.form-wrapper {
  width: 100%;
  max-width: 420px;
}

.form-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1a2332;
  margin: 0 0 8px;
  letter-spacing: -0.5px;
}

.form-sub {
  font-size: 0.9rem;
  color: #888;
  margin: 0 0 32px;
}

.link-register {
  color: #0097A7;
  font-weight: 600;
  text-decoration: none;
}
.link-register:hover { text-decoration: underline; }

/* ── Champs ───────────────────────────────────────────────────── */
.login-form { display: flex; flex-direction: column; gap: 0; }

.field-group {
  margin-bottom: 18px;
}

.field-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 16px;
  color: #aaa;
  display: flex;
  align-items: center;
}

.input-wrap input {
  width: 100%;
  padding: 14px 44px 14px 44px;
  border: 1.5px solid #e8eaed;
  border-radius: 14px;
  font-size: 15px;
  color: #1a2332;
  background: #f8fafc;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  box-sizing: border-box;
}

.input-wrap input:focus {
  border-color: #0097A7;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(76,175,80,0.12);
}

.toggle-pwd {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  cursor: pointer;
  color: #aaa;
  display: flex;
  align-items: center;
  padding: 4px;
  transition: color 0.2s;
}
.toggle-pwd:hover { color: #0097A7; }

.forgot-row {
  text-align: right;
  margin: -6px 0 18px;
}
.forgot-link {
  font-size: 13px;
  color: #0097A7;
  text-decoration: none;
}
.forgot-link:hover { text-decoration: underline; }

/* ── Erreur ───────────────────────────────────────────────────── */
.alert-error {
  background: #fff0f0;
  color: #e53935;
  border-left: 3px solid #e53935;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 13px;
  margin-bottom: 14px;
}

/* ── Bouton connexion ─────────────────────────────────────────── */
.btn-connect {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #0097A7, #8bc34a);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
  box-shadow: 0 4px 20px rgba(76,175,80,0.35);
  letter-spacing: 0.2px;
  margin-bottom: 20px;
}
.btn-connect:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 24px rgba(76,175,80,0.45);
}
.btn-connect:disabled { opacity: 0.65; cursor: not-allowed; }

.spinner {
  display: inline-block;
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Séparateur ───────────────────────────────────────────────── */
.separator {
  text-align: center;
  position: relative;
  color: #ccc;
  font-size: 13px;
  margin-bottom: 16px;
}
.separator::before,
.separator::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 44%;
  height: 1px;
  background: #eee;
}
.separator::before { left: 0; }
.separator::after  { right: 0; }

/* ── Bouton Google ────────────────────────────────────────────── */
.btn-google {
  width: 100%;
  padding: 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 14px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-weight: 600;
  font-size: 0.9rem;
  color: #444;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-bottom: 16px;
}
.btn-google:hover {
  border-color: #0097A7;
  box-shadow: 0 2px 12px rgba(76,175,80,0.12);
}

/* ── Créer compte ─────────────────────────────────────────────── */
.btn-create {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1.5px solid #0097A7;
  color: #0097A7;
  border-radius: 14px;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  transition: background 0.2s, transform 0.15s;
  margin-bottom: 20px;
  box-sizing: border-box;
}
.btn-create:hover {
  background: rgba(76,175,80,0.07);
  transform: translateY(-1px);
}

/* ── Retour accueil ───────────────────────────────────────────── */
.back-home {
  text-align: center;
}
.back-home a {
  color: #aaa;
  font-size: 13px;
  text-decoration: none;
  transition: color 0.2s;
}
.back-home a:hover { color: #0097A7; }

/* ── Responsive mobile ────────────────────────────────────────── */
@media (max-width: 768px) {
  .login-page { flex-direction: column; }
  .left-panel {
    width: 100%;
    padding: 40px 24px 32px;
    min-height: auto;
  }
  .welcome-title { font-size: 1.6rem; }
  .logo-img { max-width: 140px; }
  .right-panel { padding: 36px 20px; }
  .form-title { font-size: 1.6rem; }
}
</style>