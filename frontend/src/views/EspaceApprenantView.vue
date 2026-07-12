<template>
  <div class="apprenant-page">
    <!-- Header -->
    <header class="appr-header">
      <div class="header-inner">
        <div class="logo">
          <span>🎓</span>
          <span class="logo-title">PERMIS TIC</span>
        </div>
        <button class="btn btn-outline" @click="deconnexion">🚪 Déconnexion</button>
      </div>
    </header>

    <div class="appr-body">
      <!-- COVER + PROFIL -->
      <div class="profile-cover">
        <div class="cover-bg"></div>
        <div class="profile-card">
          <div class="avatar">
            <img v-if="auth.user?.photo_url" :src="auth.user.photo_url" alt="Photo de profil" class="avatar-img" referrerpolicy="no-referrer" />
            <span v-else>{{ initiales }}</span>
          </div>
          <div class="profile-info">
            <h2>{{ auth.user?.prenom }} {{ auth.user?.nom }}</h2>
            <p>{{ auth.user?.email }}</p>
            <div class="badges">
              <span class="badge badge--success">✅ Compte confirmé</span>
              <span class="badge badge--info" v-if="inscription">{{ inscription.formation_nom }}</span>
              <span class="badge" :class="'badge--' + niveauColor" v-if="inscription">Niveau {{ inscription.formation_niveau }}</span>
            </div>
          </div>
        </div>

        <!-- Stats -->
        <div class="profile-stats">
          <div class="stat-box">
            <div class="stat-val" style="color:var(--primary)">{{ statsAppr.formations }}</div>
            <div class="stat-lbl">Formation(s)</div>
          </div>
          <div class="stat-box">
            <div class="stat-val" style="color:#2196F3">{{ statsAppr.lecons }}</div>
            <div class="stat-lbl">Leçon(s)</div>
          </div>
          <div class="stat-box">
            <div class="stat-val" style="color:#FF9800">{{ statsAppr.moyenne || '—' }}</div>
            <div class="stat-lbl">Moyenne /20</div>
          </div>
        </div>
      </div>

      <!-- TABS -->
      <div class="tabs">
        <button
          v-for="t in tabs" :key="t.key"
          class="tab"
          :class="{ 'tab--active': tabActif === t.key, 'tab--disabled': t.disabled }"
          :disabled="t.disabled"
          :title="t.disabled ? 'Accès disponible après validation de votre inscription' : ''"
          @click="!t.disabled && (tabActif = t.key)"
        >
          {{ t.label }}
          <span v-if="t.disabled" style="font-size:11px;margin-left:4px;">🔒</span>
        </button>
      </div>

      <!-- PANEL : Formations -->
      <div v-if="tabActif === 'formations'" class="panel">
        <div v-if="loading" class="loading">Chargement…</div>

        <!-- Aucune inscription -->
        <div v-else-if="!inscription" class="empty-state">
          <p>Vous n’êtes inscrit à aucune formation pour le moment.</p>
        </div>

        <!-- En attente de confirmation admin -->
        <div v-else-if="inscription.statut === 'en_attente'" class="attente-card">
          <div class="attente-icon">⏳</div>
          <h3>Demande en cours de validation</h3>
          <p>
            Votre inscription à <strong>{{ inscription.formation_nom }}</strong>
            a bien été reçue. L'administrateur doit la valider avant que vous puissiez accéder au cours.
          </p>
          <p class="attente-sub">📧 Vous recevrez un email dès que votre accès sera activé.</p>
          <div class="attente-steps">
            <div class="step done">✅ Inscription envoyée</div>
            <div class="step active">⏳ Validation en cours</div>
            <div class="step">🔓 Accès au cours</div>
          </div>
        </div>

        <!-- Rejetée -->
        <div v-else-if="inscription.statut === 'rejete'" class="empty-state card" style="border-left:4px solid #f44336;padding:24px;">
          <p style="font-size:1.5rem;margin-bottom:8px">❌</p>
          <h3 style="margin-bottom:8px">Inscription non acceptée</h3>
          <p>Votre inscription à <strong>{{ inscription.formation_nom }}</strong> n’a pas été retenue.</p>
          <p v-if="inscription.motif_rejet" style="margin-top:8px;color:var(--gray);font-size:13px">Motif : {{ inscription.motif_rejet }}</p>
        </div>

        <!-- Confirmée -->
        <div v-else class="formation-detail card">
          <div class="fd-header">
            <span class="niveau-badge" :class="'niveau-bg-' + (inscription.formation_niveau || '').toLowerCase()">
              Niveau {{ inscription.formation_niveau }}
            </span>
            <span class="badge badge--success">✅ Confirmée</span>
          </div>
          <h3>{{ inscription.formation_nom }}</h3>
          <p class="fd-date">📅 Inscrit le {{ formatDate(inscription.date) }}</p>
          <div class="fd-formateur" v-if="inscription.formation_formateur">
            👨‍🏫 Formateur : <strong>{{ inscription.formation_formateur }}</strong>
          </div>
        </div>
      </div>

      <!-- PANEL : Leçons -->
      <div v-if="tabActif === 'lecons'" class="panel">
        <div v-if="!estConfirme" class="attente-card">
          <div class="attente-icon">🔒</div>
          <h3>Accès non disponible</h3>
          <p>Vous pourrez accéder aux leçons une fois votre inscription validée par l'administrateur.</p>
        </div>
        <div v-else-if="loading" class="loading">Chargement…</div>
        <div v-else-if="lecons.length === 0" class="empty-state">
          <p>Aucune leçon disponible pour le moment.</p>
        </div>
        <div v-else class="lecons-list">
          <div v-for="(l, i) in lecons" :key="l.id" class="lecon-card card">
            <div class="lecon-num">{{ i + 1 }}</div>
            <div class="lecon-body">
              <h4>{{ l.titre }}</h4>
              <p>{{ l.contenu }}</p>
              <div v-if="ressources(l).length" class="ressources">
                <a v-for="r in ressources(l)" :key="r" :href="r" target="_blank" rel="noopener" class="ressource-link">
                  🔗 Ressource
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- PANEL : Informations -->
      <div v-if="tabActif === 'infos'" class="panel">
        <div class="card">
          <h3 style="margin-bottom:20px;">👤 Mes informations</h3>
          <div class="info-grid">
            <div class="info-item"><label>Prénom</label><span>{{ auth.user?.prenom }}</span></div>
            <div class="info-item"><label>Nom</label><span>{{ auth.user?.nom }}</span></div>
            <div class="info-item"><label>Email</label><span>{{ auth.user?.email }}</span></div>
            <div class="info-item"><label>Téléphone</label><span>{{ auth.user?.telephone || '—' }}</span></div>
            <div class="info-item"><label>Rôle</label><span>Apprenant</span></div>
            <div class="info-item"><label>Statut</label><span class="badge badge--success">✅ Actif</span></div>
          </div>
        </div>
      </div>

      <!-- PANEL : Certificats -->
      <div v-if="tabActif === 'certificats'" class="panel">

        <!-- Certificats officiels délivrés par l'administrateur -->
        <div v-if="certificats.length" class="certificats-list">
          <div v-for="c in certificats" :key="c.id" class="card certificat-card">
            <div class="cert-icon">🎓</div>
            <div class="cert-body">
              <h3>{{ c.formation_nom || 'Certificat Permis TIC' }}</h3>
              <p class="cert-numero">N° {{ c.numero }}</p>
              <p v-if="c.niveau">Niveau {{ c.niveau }}</p>
              <p v-if="c.mention">Mention : {{ c.mention }}</p>
              <p class="fd-date">📅 Délivré le {{ formatDate(c.date_delivrance) }}</p>
              <button class="btn btn-outline btn-sm cert-view-btn" @click="voirCertificat(c)">
                👁️ Visualiser le certificat
              </button>
            </div>
          </div>
        </div>

        <!-- Aucun certificat officiel délivré pour le moment -->
        <div v-else class="card" style="text-align:center; padding:40px 20px;">
          <div style="font-size:4rem; margin-bottom:16px;">🎓</div>
          <h3 style="margin-bottom:8px;">Certificat de formation</h3>
          <p style="color:var(--gray); margin-bottom:24px;">
            Votre certificat sera disponible une fois votre formation terminée et votre note finale enregistrée.
          </p>
          <div v-if="statsAppr.moyenne && statsAppr.moyenne >= 10" class="certificat-dispo">
            <p class="badge badge--success" style="font-size:0.95rem; padding:10px 20px;">
              🏅 Admis(e) — Moyenne : {{ statsAppr.moyenne }}/20
            </p>
            <button class="btn btn-primary" style="margin-top:16px;" @click="telechargerCertificat">
              ⬇️ Télécharger le certificat (PDF)
            </button>
          </div>
          <div v-else-if="statsAppr.moyenne" class="badge badge--danger" style="font-size:0.9rem; padding:8px 16px;">
            Ajourné(e) — Moyenne : {{ statsAppr.moyenne }}/20
          </div>
        </div>
      </div>
    </div>

    <!-- MODALE : Visualisation du certificat (lecture seule) -->
    <div v-if="certificatOuvert" class="cert-modal-overlay" @click.self="fermerCertificat" @contextmenu.prevent>
      <div class="cert-modal-box">
        <button class="cert-modal-close" @click="fermerCertificat" title="Fermer">×</button>

        <div class="cert-view" @contextmenu.prevent>
          <div class="cert-view-header">
            <span class="cert-view-logo">🎓</span>
            <h2>PERMIS TIC</h2>
            <p>Plateforme de formation numérique</p>
          </div>

          <h3 class="cert-view-title">Certificat de formation</h3>

          <div class="cert-view-body">
            <p class="cert-view-line">
              Ce certificat est délivré à
              <strong>{{ auth.user?.prenom }} {{ auth.user?.nom }}</strong>
            </p>
            <p class="cert-view-line" v-if="certificatOuvert.formation_nom">
              pour la formation <strong>{{ certificatOuvert.formation_nom }}</strong>
            </p>
            <p class="cert-view-line" v-if="certificatOuvert.niveau">
              Niveau <strong>{{ certificatOuvert.niveau }}</strong>
            </p>
            <p class="cert-view-line" v-if="certificatOuvert.mention">
              Mention : <strong>{{ certificatOuvert.mention }}</strong>
            </p>

            <div class="cert-view-grid">
              <div>
                <label>N° de certificat</label>
                <span>{{ certificatOuvert.numero }}</span>
              </div>
              <div>
                <label>Date de délivrance</label>
                <span>{{ formatDate(certificatOuvert.date_delivrance) }}</span>
              </div>
              <div v-if="certificatOuvert.date_debut">
                <label>Début de formation</label>
                <span>{{ formatDate(certificatOuvert.date_debut) }}</span>
              </div>
              <div v-if="certificatOuvert.date_fin">
                <label>Fin de formation</label>
                <span>{{ formatDate(certificatOuvert.date_fin) }}</span>
              </div>
            </div>
          </div>

          <p class="cert-view-watermark">Document consultable uniquement — aperçu non téléchargeable</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import api from '../services/api'

const router      = useRouter()
const auth        = useAuthStore()
const loading     = ref(true)
const inscription = ref(null)
const lecons      = ref([])
const notes       = ref([])
const certificats = ref([])
const certificatOuvert = ref(null)
const tabActif    = ref('formations')

const estConfirme = computed(() => inscription.value?.statut === 'confirme')

const tabs = computed(() => [
  { key: 'formations',  label: '📚 Formations' },
  { key: 'lecons',      label: '📖 Leçons',         disabled: !estConfirme.value },
  { key: 'infos',       label: '👤 Informations' },
  { key: 'certificats', label: '🎓 Mes Certificats', disabled: !estConfirme.value },
])

const initiales = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return ((u.prenom?.[0] || '') + (u.nom?.[0] || '')).toUpperCase() || '?'
})

const niveauColor = computed(() => {
  const n = (inscription.value?.formation_niveau || '').toLowerCase()
  return n === 'a' ? 'info' : n === 'b' ? 'warning' : 'info'
})

const statsAppr = computed(() => {
  const total = notes.value.length
  const moy = total
    ? (notes.value.reduce((s, n) => s + n.valeur, 0) / total).toFixed(2)
    : null
  return {
    formations: inscription.value ? 1 : 0,
    lecons: lecons.value.length,
    moyenne: moy,
  }
})

function ressources(lecon) {
  if (!lecon.ressources) return []
  return lecon.ressources.split(',').map(r => r.trim()).filter(Boolean)
}

// ✅ Ouvre uniquement un certificat déjà présent dans `certificats.value`,
// lequel provient de /certificats/mes-certificats/ (filtré côté serveur sur
// l'utilisateur connecté). Aucun appel par identifiant n'est fait ici, donc
// un apprenant ne peut jamais visualiser le certificat d'un autre.
function voirCertificat(c) {
  certificatOuvert.value = c
}

function fermerCertificat() {
  certificatOuvert.value = null
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('fr-FR')
}

async function charger() {
  try {
    const { data: inscData } = await api.get('/inscriptions/mon-inscription/')

    // ✅ Cet endpoint renvoie toujours un tableau (une entrée par niveau/formation).
    // On sélectionne l'inscription confirmée en priorité, sinon celle en attente,
    // sinon la première disponible — au lieu d'utiliser le tableau brut comme un objet.
    const inscriptions = Array.isArray(inscData) ? inscData : (inscData ? [inscData] : [])
    inscription.value =
      inscriptions.find(i => i.statut === 'confirme') ||
      inscriptions.find(i => i.statut === 'en_attente') ||
      inscriptions[0] ||
      null

    // Ne charger les leçons et notes QUE si l'inscription est confirmée
    if (inscription.value?.formation && inscription.value?.statut === 'confirme') {
      try {
        const { data: lecData } = await api.get('/formations/' + inscription.value.formation + '/lecons/')
        lecons.value = lecData.results || lecData
      } catch { /* accès cours non disponible */ }

      try {
        const { data: notesData } = await api.get('/notes/mes-notes/')
        notes.value = notesData.results || notesData
      } catch { /* pas de notes encore */ }
    }

    // Certificats délivrés par l'administrateur (indépendant du statut de l'inscription en cours)
    try {
      const { data: certData } = await api.get('/certificats/mes-certificats/')
      certificats.value = certData.results || certData
    } catch { /* aucun certificat encore délivré */ }
  } catch (e) {
    // Toute erreur (404, réseau…) → pas d'inscription affichée
    inscription.value = null
  } finally {
    loading.value = false
  }
}

function telechargerCertificat() {
  // Simple génération textuelle — à remplacer par jsPDF si besoin
  const u = auth.user
  const insc = inscription.value
  const texte = `CERTIFICAT DE FORMATION\n\nNom : ${u?.prenom} ${u?.nom}\nFormation : ${insc?.formation_nom}\nNiveau : ${insc?.formation_niveau}\nMoyenne : ${statsAppr.value.moyenne}/20\nStatut : Admis(e)\n\nDélivré par PERMIS TIC`
  const blob = new Blob([texte], { type: 'text/plain' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `certificat_permis_tic_${u?.nom}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

function deconnexion() {
  auth.logout()
  router.push('/')
}

onMounted(charger)
</script>

<style scoped>
.apprenant-page { min-height: 100vh; background: var(--bg); }

/* Header */
.appr-header { background: linear-gradient(135deg, var(--primary), var(--secondary)); padding: 12px 20px; }
.header-inner { max-width: 860px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }
.logo { display: flex; align-items: center; gap: 10px; color: white; font-weight: 900; font-size: 1.1rem; }
.logo-title { letter-spacing: 1px; }
.btn-outline { background: rgba(255,255,255,0.15); border: 2px solid rgba(255,255,255,0.7); color: white; }
.btn-outline:hover { background: rgba(255,255,255,0.3); }

/* Body */
.appr-body { max-width: 860px; margin: 0 auto; padding: 0 16px 40px; }

/* Cover */
.profile-cover { background: white; border-radius: 0 0 24px 24px; box-shadow: var(--shadow); margin-bottom: 20px; overflow: hidden; }
.cover-bg { height: 140px; background: linear-gradient(135deg, #1B5E20, #4CAF50, #FFC107); }
.profile-card { display: flex; align-items: flex-end; gap: 16px; padding: 0 24px 18px; }
.avatar { width: 90px; height: 90px; border-radius: 50%; border: 4px solid white; background: linear-gradient(135deg, #4CAF50, #1B5E20); display: flex; align-items: center; justify-content: center; font-size: 2.2rem; font-weight: 900; color: white; margin-top: -40px; flex-shrink: 0; box-shadow: 0 4px 16px rgba(0,0,0,0.2); overflow: hidden; }
.avatar-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
.profile-info h2 { font-size: 1.3rem; font-weight: 900; margin: 0; }
.profile-info p { color: var(--gray); font-size: 0.82rem; margin: 2px 0 8px; }
.badges { display: flex; gap: 8px; flex-wrap: wrap; }
.profile-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 0 24px 20px; }
.stat-box { background: var(--bg); border-radius: 14px; padding: 14px; text-align: center; border: 1px solid var(--border); }
.stat-val { font-size: 1.5rem; font-weight: 900; }
.stat-lbl { font-size: 0.72rem; color: var(--gray); margin-top: 3px; }

/* Tabs */
.tabs { display: flex; background: white; border-radius: 16px; overflow: hidden; box-shadow: var(--shadow); margin-bottom: 18px; }
.tab { flex: 1; padding: 14px 6px; border: none; background: none; cursor: pointer; font-size: 0.82rem; font-weight: 600; color: var(--gray); transition: 0.2s; }
.tab:hover { background: var(--bg); }
.tab--active { background: var(--primary); color: white; }

/* Panels */
.panel { animation: fadeIn 0.25s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

.loading, .empty-state { text-align: center; color: var(--gray); padding: 40px; background: white; border-radius: 16px; box-shadow: var(--shadow); }
.tab--disabled { opacity: .45; cursor: not-allowed !important; pointer-events: none; }
.attente-card { text-align: center; padding: 40px 32px; background: #FFF8E1; border: 2px solid #FF9800; border-radius: 16px; box-shadow: 0 4px 20px rgba(255,152,0,.15); }
.attente-card h3 { font-size: 1.3rem; margin: 12px 0 10px; color: #E65100; }
.attente-card p { color: #555; margin-bottom: 6px; }
.attente-icon { font-size: 2.5rem; }
.attente-sub { font-size: 13px; color: #888; margin-top: 10px !important; }
.attente-steps { display: flex; justify-content: center; gap: 12px; margin-top: 24px; flex-wrap: wrap; }
.attente-steps .step { padding: 8px 16px; border-radius: 20px; font-size: 13px; background: #eee; color: #999; }
.attente-steps .step.done { background: #E8F5E9; color: #2E7D32; }
.attente-steps .step.active { background: #FFF3E0; color: #E65100; font-weight: 600; border: 1px solid #FF9800; }

/* Formation detail */
.fd-header { display: flex; gap: 10px; align-items: center; margin-bottom: 12px; }
.fd-header h3 { margin: 0; }
.niveau-badge { padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; color: white; }
.niveau-bg-a { background: #2196F3; } .niveau-bg-b { background: #FF9800; } .niveau-bg-c { background: #9C27B0; }
.fd-date { color: var(--gray); font-size: 0.85rem; margin: 8px 0; }
.fd-formateur { font-size: 0.88rem; margin-top: 8px; }

/* Leçons */
.lecons-list { display: flex; flex-direction: column; gap: 14px; }
.lecon-card { display: flex; gap: 16px; align-items: flex-start; }
.lecon-num { min-width: 36px; height: 36px; border-radius: 50%; background: var(--primary); color: white; display: flex; align-items: center; justify-content: center; font-weight: 900; flex-shrink: 0; }
.lecon-body h4 { margin-bottom: 6px; }
.lecon-body p { color: var(--gray); font-size: 0.85rem; }
.ressources { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
.ressource-link { color: var(--primary); font-size: 0.8rem; font-weight: 600; text-decoration: none; background: rgba(76,175,80,0.1); padding: 3px 10px; border-radius: 20px; }

/* Infos */
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.info-item { display: flex; flex-direction: column; gap: 4px; }
.info-item label { font-size: 0.78rem; font-weight: 700; color: var(--gray); text-transform: uppercase; letter-spacing: 0.5px; }
.info-item span { font-size: 0.92rem; }

/* Certificat */
.certificat-dispo { display: flex; flex-direction: column; align-items: center; gap: 10px; }
.cert-view-btn { margin-top: 12px; }

/* Modale de visualisation du certificat (lecture seule) */
.cert-modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.cert-modal-box { position: relative; background: white; border-radius: 20px; max-width: 560px; width: 100%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
.cert-modal-close { position: absolute; top: 12px; right: 16px; background: none; border: none; font-size: 1.8rem; line-height: 1; cursor: pointer; color: var(--gray); z-index: 2; }
.cert-modal-close:hover { color: #333; }

.cert-view { padding: 40px 32px 32px; text-align: center; border: 3px double var(--primary); margin: 16px; border-radius: 12px; user-select: none; -webkit-user-select: none; }
.cert-view-header { margin-bottom: 20px; }
.cert-view-logo { font-size: 2.5rem; display: block; margin-bottom: 6px; }
.cert-view-header h2 { margin: 0; font-weight: 900; letter-spacing: 1px; color: var(--primary); }
.cert-view-header p { margin: 2px 0 0; font-size: 0.8rem; color: var(--gray); }
.cert-view-title { margin: 20px 0; font-size: 1.3rem; font-weight: 800; }
.cert-view-body { text-align: left; }
.cert-view-line { margin: 6px 0; font-size: 0.95rem; }
.cert-view-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); }
.cert-view-grid label { display: block; font-size: 0.72rem; font-weight: 700; color: var(--gray); text-transform: uppercase; letter-spacing: 0.5px; }
.cert-view-grid span { font-size: 0.9rem; }
.cert-view-watermark { margin-top: 24px; font-size: 0.72rem; color: var(--gray); font-style: italic; }

@media print {
  .cert-modal-overlay { display: none !important; }
}

@media (max-width: 600px) {
  .profile-stats { grid-template-columns: repeat(3, 1fr); gap: 8px; }
  .info-grid { grid-template-columns: 1fr; }
  .tab { font-size: 0.72rem; padding: 12px 4px; }
  .cert-view-grid { grid-template-columns: 1fr; }
}
</style>