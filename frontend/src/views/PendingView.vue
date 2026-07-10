<template>
  <div class="pending-page">
    <div class="pending-card">
      <div class="pending-logo">
        <h1>🎓 PERMIS TIC</h1>
        <p>Plateforme de formation numérique</p>
      </div>
      <div v-if="aEnAttente" class="state-box attente">
        <div class="state-icon">⏳</div>
        <h2>Compte en attente de validation</h2>
        <p>Votre compte est <strong>en attente de validation</strong> par l administrateur.</p>
        <div class="email-notice">📧 Un email vous sera envoyé sur <strong>{{ auth.user?.email }}</strong> dès que votre accès sera activé.</div>
        <div class="steps-row">
          <div class="step done">✅ Compte créé</div>
          <div class="step-arrow">→</div>
          <div class="step active">⏳ Validation admin</div>
          <div class="step-arrow">→</div>
          <div class="step">🔓 Accès cours</div>
        </div>
        <button class="btn-check" @click="verifierStatut" :disabled="checking">{{ checking ? "Vérification…" : "🔄 Vérifier mon statut" }}</button>
      </div>
      <div v-else-if="aRefus" class="state-box refuse">
        <div class="state-icon">❌</div>
        <h2>Inscription non retenue</h2>
        <p>Votre demande a été refusée par l administrateur.</p>
        <button class="btn-primary" @click="router.push('/register')">📝 Nouvelle inscription</button>
      </div>
      <div v-else class="state-box nouveau">
        <div class="state-icon">📋</div>
        <h2>Aucune inscription trouvée</h2>
        <button class="btn-primary" @click="router.push('/register')">📝 Choisir une formation</button>
      </div>
      <button class="btn-logout" @click="deconnexion">🚪 Se déconnecter</button>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "../store/auth"
const router = useRouter()
const auth = useAuthStore()
const checking = ref(false)
const inscriptions = computed(() => auth.user?.inscriptions || [])
const aEnAttente = computed(() => inscriptions.value.some(i => i.statut === "en_attente"))
const aRefus = computed(() => !aEnAttente.value && inscriptions.value.some(i => i.statut === "rejete"))
async function verifierStatut() {
  checking.value = true
  try {
    await auth.fetchUser()
    if ((auth.user?.inscriptions || []).some(i => i.statut === "confirme")) {
      router.replace("/espace-apprenant")
    }
  } finally { checking.value = false }
}
function deconnexion() { auth.logout(); router.push("/") }
onMounted(() => {
  if ((auth.user?.inscriptions || []).some(i => i.statut === "confirme")) {
    router.replace("/espace-apprenant")
  }
})
</script>
<style scoped>
.pending-page { min-height:100vh; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg,#2e7d32,#f9c514); padding:24px 16px; }
.pending-card { background:white; border-radius:24px; padding:40px 32px; width:100%; max-width:520px; box-shadow:0 20px 60px rgba(0,0,0,0.2); text-align:center; }
.pending-logo h1 { font-size:1.4rem; color:#2e7d32; margin:0 0 4px; }
.pending-logo p { color:#888; font-size:0.85rem; margin:0 0 24px; }
.state-box { padding:24px; border-radius:16px; margin-bottom:20px; }
.state-box.attente { background:#fff8e1; border:1px solid #ffe082; }
.state-box.refuse { background:#ffebee; border:1px solid #ef9a9a; }
.state-box.nouveau { background:#e8f5e9; border:1px solid #a5d6a7; }
.state-icon { font-size:3rem; margin-bottom:12px; }
.state-box h2 { font-size:1.1rem; margin:0 0 10px; }
.state-box p { font-size:0.9rem; color:#555; margin:0 0 12px; }
.email-notice { background:white; border-radius:10px; padding:12px; font-size:0.82rem; color:#555; margin-bottom:16px; border:1px solid #ffe082; }
.steps-row { display:flex; align-items:center; justify-content:center; gap:6px; flex-wrap:wrap; margin-bottom:16px; }
.step { background:#f5f5f5; border-radius:20px; padding:6px 12px; font-size:0.75rem; color:#888; }
.step.done { background:#e8f5e9; color:#2e7d32; }
.step.active { background:#fff3e0; color:#e65100; border:1px solid #ff9800; }
.step-arrow { color:#ccc; }
.btn-check { background:#2e7d32; color:white; border:none; padding:10px 24px; border-radius:10px; cursor:pointer; font-size:0.9rem; font-weight:600; }
.btn-check:disabled { opacity:0.6; cursor:not-allowed; }
.btn-primary { background:#2e7d32; color:white; border:none; padding:10px 24px; border-radius:10px; cursor:pointer; font-size:0.9rem; font-weight:600; margin-top:8px; }
.btn-logout { background:none; border:1px solid #ddd; color:#888; padding:8px 20px; border-radius:10px; cursor:pointer; font-size:0.85rem; margin-top:8px; }
</style>
