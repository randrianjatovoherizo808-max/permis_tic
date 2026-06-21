import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {

  // ── État ────────────────────────────────────────────────────────────────────
  const user         = ref(null)
  const accessToken  = ref(localStorage.getItem('access_token')  || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  let   _restoring   = null   // Promise partagée pour éviter les appels parallèles

  // ── Getters ─────────────────────────────────────────────────────────────────
const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin         = computed(() => user.value?.role === 'admin')
  const isFormateur     = computed(() => user.value?.role === 'formateur')
  const isEtudiant      = computed(() => user.value?.role === 'etudiant')
  const isStaff         = computed(() =>
    user.value?.role === 'admin' || user.value?.role === 'formateur'
  )

  // ── Actions ─────────────────────────────────────────────────────────────────

  /** Connexion email + mot de passe  */
  async function login(email, password) {
  const { data } = await api.post('/auth/token/', {
    username: email,
    password: password
  })
  _saveTokens(data.access, data.refresh)

  await fetchUser()
  return user.value
}

  /** Récupère le profil de l'utilisateur connecté */
  async function fetchUser() {
  try {
    const { data } = await api.get('/auth/me/')
    user.value = data
  } catch (e) {
    console.log("ME ERROR:", e)
    logout()
  }
}

  /** Déconnexion (révocation du refresh côté serveur si dispo) */
  async function logout() {
    try {
      if (refreshToken.value) {
        await api.post('/auth/logout/', { refresh: refreshToken.value })
      }
    } catch {
      // Silencieux — on déconnecte quand même
    } finally {
      _clearTokens()
    }
  }

  /** Changement de mot de passe */
  async function changePassword(ancien, nouveau) {
    await api.post('/auth/change-password/', {
      old_password: ancien,
      new_password: nouveau,
    })
  }

  /** Restaure la session depuis le localStorage au démarrage de l'app */
  async function restore() {
  const token = localStorage.getItem('access_token')

  if (!token) return

  // Si l'utilisateur est déjà chargé, pas besoin de refaire un appel réseau
  if (user.value) return

  // Si un restore est déjà en cours, attendre le même
  if (_restoring) return _restoring

  accessToken.value = token
  refreshToken.value = localStorage.getItem('refresh_token')

  _restoring = fetchUser().finally(() => { _restoring = null })
  return _restoring
}
  // ── Helpers privés ──────────────────────────────────────────────────────────
  function _saveTokens(access, refresh) {
    accessToken.value  = access
    refreshToken.value = refresh
    localStorage.setItem('access_token',  access)
    localStorage.setItem('refresh_token', refresh)
  }

  function _clearTokens() {
    user.value         = null
    accessToken.value  = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    // état
    user,
    accessToken,
    // getters
    isAuthenticated,
    isAdmin,
    isFormateur,
    isEtudiant,
    isStaff,
    // actions
    login,
    logout,
    fetchUser,
    changePassword,
    restore,
  }
})