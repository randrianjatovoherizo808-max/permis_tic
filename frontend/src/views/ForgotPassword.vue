<template>
  <div class="page">
    <div class="card">

      <!-- Panneau gauche -->
      <div class="card-left">
        <img src="/logo.png" alt="Pif-tic" class="brand-logo" />
        <span class="brand-name">Pif-tic</span>
      </div>

      <!-- Panneau droit -->
      <div class="card-right">

        <!-- ÉTAPE 1 : Email -->
        <template v-if="step === 1">
          <h2>Mot de passe oublié ?</h2>
          <div class="form-group">
            <input
              v-model="email"
              type="email"
              placeholder="Votre adresse e-mail"
              :disabled="loading"
              @keyup.enter="envoyerCode"
            />
          </div>
          <div v-if="error" class="alert-error">{{ error }}</div>
          <button class="btn-primary" @click="envoyerCode" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Envoi…' : 'Envoyer le code' }}
          </button>
          <RouterLink to="/login" class="link-back">Retour à la connexion</RouterLink>
        </template>

        <!-- ÉTAPE 2 : Code de réinitialisation -->
        <template v-if="step === 2">
          <div class="step-icon">
            <img src="/logo5.png" alt="Code de réinitialisation" class="step-img" />
          </div>
          <h2>Code de réinitialisation</h2>
          <div class="form-group">
            <input
              v-model="codeInput"
              type="text"
              inputmode="numeric"
              placeholder="Entrez le code reçu"
              maxlength="6"
              :disabled="loading"
              @keyup.enter="verifierCode"
            />
          </div>
          <div v-if="error" class="alert-error">{{ error }}</div>
          <button class="btn-primary" @click="verifierCode" :disabled="loading || codeInput.length < 6">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Vérification…' : 'Valider le code' }}
          </button>
          <div class="row-links">
            <button class="link-back plain" @click="renvoyerCode">Code non reçu ?</button>
            <button class="link-back plain" @click="step = 1">Annuler</button>
          </div>
        </template>

        <!-- ÉTAPE 3 : Nouveau mot de passe -->
        <template v-if="step === 3">
          <h2>Définir un nouveau mot de passe</h2>
          <p class="subtitle">Votre code a été validé. Choisissez un mot de passe sécurisé.</p>
          <div class="form-group">
            <div class="pwd-wrap">
              <input
                v-model="password"
                :type="showPwd ? 'text' : 'password'"
                placeholder="Nouveau mot de passe"
                :disabled="loading"
              />
              <button type="button" class="eye" @click="showPwd = !showPwd">
                {{ showPwd ? '🙈' : '👁' }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <div class="pwd-wrap">
              <input
                v-model="passwordConfirm"
                :type="showPwd2 ? 'text' : 'password'"
                placeholder="Confirmer le mot de passe"
                :disabled="loading"
              />
              <button type="button" class="eye" @click="showPwd2 = !showPwd2">
                {{ showPwd2 ? '🙈' : '👁' }}
              </button>
            </div>
          </div>
          <div v-if="error" class="alert-error">{{ error }}</div>
          <button class="btn-primary" @click="changerMotDePasse" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Enregistrement…' : 'Réinitialiser le mot de passe' }}
          </button>
          <RouterLink to="/login" class="link-back">← Retour à la connexion</RouterLink>
        </template>

        <!-- ÉTAPE 4 : Succès -->
        <template v-if="step === 4">
          <div class="success-state">
            <div class="success-icon">✅</div>
            <h2>Mot de passe modifié !</h2>
            <p>Votre mot de passe a été mis à jour avec succès.<br />Vous pouvez maintenant vous connecter.</p>
            <RouterLink to="/login" class="btn-primary" style="text-decoration:none;display:block;text-align:center;margin-top:24px;">
              Se connecter
            </RouterLink>
          </div>
        </template>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const step            = ref(1)
const email           = ref('')
const codeInput       = ref('')
const password        = ref('')
const passwordConfirm = ref('')
const showPwd         = ref(false)
const showPwd2        = ref(false)
const loading         = ref(false)
const error           = ref('')

async function envoyerCode() {
  error.value = ''
  if (!email.value || !email.value.includes('@')) {
    error.value = 'Adresse email invalide.'
    return
  }
  loading.value = true
  try {
    const res = await api.post('/auth/forgot-password/', { email: email.value })
    codeInput.value = res.data.code || ''  // Remplir automatiquement le code
    step.value = 2
  } catch (e) {
    error.value = e.response?.data?.error || "Erreur lors de l'envoi. Vérifiez votre email."
  } finally {
    loading.value = false
  }
}

async function renvoyerCode() {
  error.value = ''
  codeInput.value = ''
  loading.value = true
  try {
    const res = await api.post('/auth/forgot-password/', { email: email.value })
    codeInput.value = res.data.code || ''  // Remplir automatiquement le code
  } catch (e) {
    error.value = e.response?.data?.error || "Erreur lors du renvoi."
  } finally {
    loading.value = false
  }
}

async function verifierCode() {
  if (codeInput.value.length < 6) return
  error.value = ''
  loading.value = true
  try {
    await api.post('/auth/verify-otp/', { email: email.value, code: codeInput.value })
    step.value = 3
  } catch (e) {
    error.value = e.response?.data?.error || 'Code incorrect.'
    codeInput.value = ''
  } finally {
    loading.value = false
  }
}

async function changerMotDePasse() {
  error.value = ''
  if (password.value.length < 6) {
    error.value = 'Le mot de passe doit contenir au moins 6 caractères.'
    return
  }
  if (password.value !== passwordConfirm.value) {
    error.value = 'Les mots de passe ne correspondent pas.'
    return
  }
  loading.value = true
  try {
    await api.post('/auth/reset-password/', {
      email: email.value,
      code: codeInput.value,
      password: password.value
    })
    step.value = 4
  } catch (e) {
    error.value = e.response?.data?.error || 'Erreur lors de la modification.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9, #fffde7);
  padding: 24px 16px;
}

.card {
  display: flex;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.13);
  overflow: hidden;
  width: 100%;
  max-width: 600px;
  min-height: 340px;
}

/* Panneau gauche vert-jaune */
.card-left {
  background: linear-gradient(160deg, #4CAF50 0%, #8BC34A 60%, #CDDC39 100%);
  width: 180px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  gap: 14px;
}

.brand-logo {
  width: 90px;
  height: 90px;
  object-fit: contain;
  border-radius: 14px;
  background: #fff;
  padding: 6px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15);
}

.brand-name {
  color: #fff;
  font-weight: 800;
  font-size: 16px;
  letter-spacing: 1px;
  text-shadow: 0 1px 4px rgba(0,0,0,0.2);
}

/* Panneau droit blanc */
.card-right {
  flex: 1;
  padding: 36px 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-right h2 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0 0 20px;
  text-align: center;
}

.subtitle {
  font-size: 13px;
  color: #666;
  text-align: center;
  margin: -12px 0 18px;
  line-height: 1.6;
}

.form-group {
  margin-bottom: 14px;
}

.form-group input {
  width: 100%;
  border: 1.5px solid #c8e6c9;
  border-radius: 8px;
  padding: 12px 14px;
  font-size: 14px;
  color: #333;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
  background: #f9fef9;
}

.form-group input:focus {
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.12);
  background: #fff;
}

.form-group input::placeholder {
  color: #aaa;
}

.pwd-wrap {
  position: relative;
}

.pwd-wrap input {
  padding-right: 42px;
}

.eye {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.step-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.step-img {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.alert-error {
  background: #fff0f0;
  color: #c62828;
  border-left: 3px solid #e53935;
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 13px;
  margin-bottom: 12px;
}

.btn-primary {
  width: 100%;
  padding: 13px;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: filter 0.2s, transform 0.1s;
  margin-bottom: 6px;
  text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.btn-primary:hover:not(:disabled) {
  filter: brightness(1.07);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.link-back {
  display: block;
  text-align: center;
  margin-top: 10px;
  font-size: 13px;
  color: #4CAF50;
  text-decoration: none;
  font-weight: 600;
  cursor: pointer;
  background: none;
  border: none;
  width: 100%;
}

.link-back:hover {
  text-decoration: underline;
  color: #388E3C;
}

.link-back.plain {
  color: #888;
  font-weight: 500;
}

.row-links {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.row-links .link-back {
  width: auto;
  margin-top: 0;
}

/* Succès */
.success-state {
  text-align: center;
  padding: 8px 0;
}

.success-icon {
  font-size: 56px;
  margin-bottom: 12px;
}

.success-state h2 {
  color: #2e7d32;
}

.success-state p {
  font-size: 14px;
  color: #555;
  line-height: 1.7;
}

/* Spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 480px) {
  .card {
    flex-direction: column;
  }
  .card-left {
    width: 100%;
    flex-direction: row;
    padding: 16px 24px;
    gap: 14px;
    min-height: unset;
  }
  .brand-logo {
    width: 50px;
    height: 50px;
  }
  .card-right {
    padding: 24px 20px;
  }
}
</style>