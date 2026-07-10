<template>
  <div class="apprenant-page">
    <!-- Header -->
    <header class="appr-header">
      <div class="header-inner">
        <div class="logo">
          <img src="/logo.png" alt="PIFTIC" style="height:36px;object-fit:contain;" />
          <span class="logo-title">PERMIS TIC</span>
        </div>
        <div class="header-actions">
          <LangSwitcher variant="light" />
          <button class="theme-toggle" @click="toggleTheme"
                  :title="theme === 'dark' ? 'Mode clair' : 'Mode sombre'">
            <span class="toggle-track" :class="{ dark: theme === 'dark' }">
              <span class="toggle-thumb">{{ theme === 'dark' ? '🌙' : '☀️' }}</span>
            </span>
            <span class="toggle-label">{{ theme === 'dark' ? 'Mode sombre' : 'Mode clair' }}</span>
          </button>
          <button class="btn btn-outline" @click="deconnexion">{{ t.deconnexion }}</button>
        </div>
      </div>
    </header>

    <div class="appr-body">

      <!-- CHARGEMENT -->
      <div v-if="loading" class="loading">Chargement…</div>

      <template v-else>

        <!-- ══ AUCUNE INSCRIPTION ══ -->
        <div v-if="inscriptions.length === 0" class="empty-state card">
          <div style="font-size:3rem;margin-bottom:12px;">📋</div>
          <h3>Aucune inscription trouvée</h3>
          <p>{{ t.aucuneInscription }}</p>
          <button class="btn btn-primary" style="margin-top:20px;" @click="showFormInscription = true">
            ➕ S'inscrire à un niveau
          </button>
        </div>

        <template v-else>

          <!-- COVER + PROFIL -->
          <div class="profile-cover">
            <div class="cover-bg"></div>
            <div class="profile-card">
              <div class="avatar">
                <img v-if="auth.user?.photo_url" :src="auth.user.photo_url"
                     :alt="initiales" class="avatar-img" referrerpolicy="no-referrer" />
                <span v-else>{{ initiales }}</span>
              </div>
              <div class="profile-info">
                <h2>{{ auth.user?.prenom || auth.user?.first_name }} {{ auth.user?.nom || auth.user?.last_name }}</h2>
                <p>{{ auth.user?.email }}</p>
                <div class="badges">
                  <span v-for="insc in inscriptionsConfirmees" :key="insc.id"
                        class="badge badge--success">✅ Niveau {{ insc.niveau }}</span>
                  <span v-for="insc in inscriptionsAttente" :key="insc.id"
                        class="badge badge--warning">⏳ Niveau {{ insc.niveau }}</span>
                </div>
              </div>
            </div>
            <div class="profile-stats">
              <div class="stat-box">
                <div class="stat-val" style="color:var(--primary)">{{ inscriptionsConfirmees.length }}</div>
                <div class="stat-lbl">Niveau(x) validé(s)</div>
              </div>
              <div class="stat-box">
                <div class="stat-val" style="color:#2196F3">{{ totalLecons }}</div>
                <div class="stat-lbl">Leçon(s)</div>
              </div>
              <div class="stat-box">
                <div class="stat-val" style="color:#FF9800">{{ moyenneGlobale || '—' }}</div>
                <div class="stat-lbl">Moyenne /20</div>
              </div>
            </div>
          </div>

          <!-- BOUTON NOUVELLE INSCRIPTION -->
          <div class="action-bar">
            <button class="btn btn-primary" @click="showFormInscription = !showFormInscription">
              {{ showFormInscription ? '✕ Annuler' : '➕ S\'inscrire à un autre niveau' }}
            </button>
          </div>

          <!-- FORMULAIRE INSCRIPTION NOUVEAU NIVEAU / COURS -->
          <div v-if="showFormInscription" class="card inscription-form">
            <h3 style="margin-bottom:16px;">📋 S'inscrire à un cours</h3>

            <!-- Tabs : par niveau ou par cours spécifique -->
            <div class="insc-mode-tabs">
              <button class="insc-mode-tab" :class="{active: inscMode==='niveau'}" @click="inscMode='niveau'; newFormationId=null">
                🎓 Par niveau
              </button>
              <button class="insc-mode-tab" :class="{active: inscMode==='cours'}" @click="inscMode='cours'; newNiveau=''">
                📘 Cours spécifique
              </button>
            </div>

            <!-- Mode niveau -->
            <div v-if="inscMode === 'niveau'" class="form-group" style="margin-top:14px">
              <label>Choisir un niveau</label>
              <div class="niveau-cards">
                <div v-for="niv in niveauxDisponibles" :key="niv.value"
                     class="niveau-card"
                     :class="{ 'niveau-card--active': newNiveau === niv.value, 'niveau-card--taken': niv.taken }"
                     @click="!niv.taken && (newNiveau = niv.value)">
                  <div class="niveau-icon">{{ niv.icon }}</div>
                  <div class="niveau-info">
                    <strong>{{ niv.label }}</strong>
                    <span v-if="niv.taken" class="taken-badge">{{ niv.takenStatus }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Mode cours spécifique -->
            <div v-if="inscMode === 'cours'" class="form-group" style="margin-top:14px">
              <label>Choisir un cours</label>
              <div class="cours-list">
                <div v-for="f in toutesFormations" :key="f.id"
                     class="cours-card"
                     :class="{ 'cours-card--active': newFormationId === f.id, 'cours-card--taken': isFormationDejaInscrite(f.id) }"
                     @click="!isFormationDejaInscrite(f.id) && (newFormationId = f.id, newNiveau = f.niveau)">
                  <div class="cours-info">
                    <strong>{{ f.nom }}</strong>
                    <span class="cours-niveau niveau-badge" :class="'niveau-bg-' + f.niveau.toLowerCase()">Niveau {{ f.niveau }}</span>
                  </div>
                  <span v-if="isFormationDejaInscrite(f.id)" class="taken-badge">✅ Déjà inscrit</span>
                </div>
              </div>
            </div>

            <div v-if="inscErreur" class="alert alert-danger">{{ inscErreur }}</div>
            <div v-if="inscSucces" class="alert alert-success">{{ inscSucces }}</div>
            <button class="btn btn-primary"
                    :disabled="(!newNiveau && !newFormationId) || inscLoading"
                    @click="soumettreInscription">
              <span v-if="inscLoading">⏳ Envoi…</span>
              <span v-else>✅ Confirmer l'inscription</span>
            </button>
          </div>

          <!-- TABS par niveau -->
          <div class="tabs">
            <button v-for="tab in tabs" :key="tab.key" class="tab"
                    :class="{ 'tab--active': tabActif === tab.key }"
                    @click="tabActif = tab.key">
              {{ tab.label }}
            </button>
          </div>

          <!-- ══ PANEL : Mes niveaux ══ -->
          <div v-if="tabActif === 'niveaux'" class="panel">
            <div v-for="insc in inscriptions" :key="insc.id" class="niveau-detail card">
              <div class="nd-header">
                <span class="niveau-badge" :class="'niveau-bg-' + insc.niveau.toLowerCase()">
                  Niveau {{ insc.niveau }}
                </span>
                <span class="badge" :class="statutBadgeClass(insc.statut)">
                  {{ statutLabel(insc.statut) }}
                </span>
                <span class="nd-date">Inscrit le {{ formatDate(insc.date_inscription) }}</span>
              </div>
              <p class="nd-label">{{ insc.niveau_label }}</p>

              <!-- En attente -->
              <div v-if="insc.statut === 'en_attente'" class="attente-mini">
                <p>⏳ Votre inscription est en attente de validation par l'administrateur.</p>
                <p class="hint">📧 Vous recevrez un email dès que votre accès sera activé.</p>
              </div>

              <!-- Rejeté -->
              <div v-else-if="insc.statut === 'rejete'" class="rejete-mini">
                <p>❌ Inscription non acceptée.</p>
                <p v-if="insc.motif_rejet" class="hint">Motif : {{ insc.motif_rejet }}</p>
                <button class="btn btn-sm" @click="reinscrire(insc.niveau)">🔄 Réessayer</button>
              </div>

              <!-- Confirmé : liste des formations du niveau -->
              <div v-else-if="insc.statut === 'confirme'" class="formations-list">
                <p class="confirmed-msg">✅ Accès validé — vous pouvez accéder à tous les cours de ce niveau.</p>
                <div v-for="f in formationsParNiveau[insc.niveau] || []" :key="f.id" class="formation-item">
                  <span class="f-icon">📘</span>
                  <span class="f-nom">{{ f.nom }}</span>
                  <div class="f-actions">
                    <button class="btn btn-acces btn-sm" @click="ouvrirFormation(f, insc.niveau)">
                      📖 Accéder au cours
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ══ PANEL : Leçons ══ -->
          <div v-if="tabActif === 'lecons'" class="panel">
            <!-- Sélecteur de formation -->
            <div v-if="toutesFormationsConfirmees.length > 0" class="form-select-bar">
              <label>Choisir une formation :</label>
              <select v-model="formationSelectee" @change="chargerLecons(formationSelectee)">
                <option v-for="f in toutesFormationsConfirmees" :key="f.id" :value="f.id">
                  [Niveau {{ f.niveau }}] {{ f.nom }}
                </option>
              </select>
            </div>
            <div v-if="leconLoading" class="loading">Chargement des leçons…</div>
            <div v-else-if="lecons.length === 0" class="empty-state">
              <p>{{ toutesFormationsConfirmees.length === 0 ? 'Aucun niveau validé pour le moment.' : 'Aucune leçon disponible pour cette formation.' }}</p>
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

          <!-- ══ PANEL : Informations ══ -->
          <div v-if="tabActif === 'infos'" class="panel">
            <div class="card">
              <h3 style="margin-bottom:20px;">👤 Mes informations</h3>
              <div class="info-grid">
                <div class="info-item"><label>{{ t.prenomLabel }}</label><span>{{ auth.user?.prenom || auth.user?.first_name }}</span></div>
                <div class="info-item"><label>Nom</label><span>{{ auth.user?.nom || auth.user?.last_name }}</span></div>
                <div class="info-item"><label>Email</label><span>{{ auth.user?.email }}</span></div>
                <div class="info-item"><label>{{ t.telephoneLabel }}</label><span>{{ auth.user?.telephone || '—' }}</span></div>
                <div class="info-item"><label>Rôle</label><span>Apprenant</span></div>
                <div class="info-item"><label>Niveaux inscrits</label>
                  <span>{{ inscriptions.map(i => 'Niveau ' + i.niveau).join(', ') || '—' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ══ PANEL : Certificats ══ -->
          <div v-if="tabActif === 'certificats'" class="panel">
            <div class="card" style="text-align:center;padding:40px 20px;">
              <div style="font-size:4rem;margin-bottom:16px;">🎓</div>
              <h3 style="margin-bottom:8px;">Certificat de formation</h3>
              <p style="color:var(--gray);margin-bottom:24px;">{{ t.certifDisponible }}</p>
              <div v-if="moyenneGlobale && moyenneGlobale >= 10" class="certificat-dispo">
                <p class="badge badge--success" style="font-size:0.95rem;padding:10px 20px;">
                  🏅 Admis(e) — Moyenne : {{ moyenneGlobale }}/20
                </p>
                <button class="btn btn-primary" style="margin-top:16px;" @click="visualiserCertificat">
                  👁️ Visualiser mon certificat
                </button>
              </div>
              <div v-else-if="moyenneGlobale" class="badge badge--danger" style="font-size:0.9rem;padding:8px 16px;">
                Ajourné(e) — Moyenne : {{ moyenneGlobale }}/20
              </div>
              <p v-else style="color:#aaa;font-size:13px;">Aucune note enregistrée pour le moment.</p>
            </div>
          </div>

        </template>
      </template>
    </div>
  </div>

  <!-- ══ MODAL PRÉVISUALISATION CERTIFICAT ══ -->
  <div v-if="showCertifModal" class="certif-modal-overlay" @click.self="showCertifModal = false">
    <div class="certif-modal">
      <div class="certif-modal-header">
        <h3>🎓 Certificat de formation</h3>
        <button class="certif-close-btn" @click="showCertifModal = false">✕</button>
      </div>
      <div class="certif-modal-body">
        <iframe :srcdoc="certifHtml" class="certif-iframe" frameborder="0"></iframe>
      </div>
      <div class="certif-modal-footer">
        <p class="certif-notice">🔒 Le téléchargement est réservé à l'administrateur.</p>
        <button class="btn btn-secondary" @click="showCertifModal = false">Fermer</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useLangStore } from '../store/lang'
import { storeToRefs } from 'pinia'
import api from '../services/api'
import LangSwitcher from '../components/LangSwitcher.vue'

// Logos du certificat encodés en base64 : embarqués directement dans le HTML
// généré pour l'impression/export PDF, afin qu'ils restent toujours visibles
// même une fois le document téléchargé (un chemin relatif comme /logo.png
// ne se résout pas de façon fiable dans la fenêtre détachée du blob HTML).
const LOGO_METFP = "data:image/jpeg;base64,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"
const LOGO_MADAGASIKARA = "data:image/jpeg;base64,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"
const LOGO_PIFTIC = "data:image/jpeg;base64,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"

const router = useRouter()
const auth   = useAuthStore()
const theme  = ref(localStorage.getItem('theme') || 'light')

function applyTheme(t) {
  theme.value = t
  localStorage.setItem('theme', t)
  t === 'dark'
    ? document.documentElement.setAttribute('data-theme', 'dark')
    : document.documentElement.removeAttribute('data-theme')
}
function toggleTheme() { applyTheme(theme.value === 'dark' ? 'light' : 'dark') }

const loading      = ref(true)
const inscriptions = ref([])   // toutes les inscriptions (tous niveaux)
const notes        = ref([])
const lecons       = ref([])
const leconLoading = ref(false)
const formationsParNiveau = ref({})   // { A: [...], B: [...], C: [...] }
const formationSelectee   = ref(null)
const tabActif     = ref('niveaux')
const showFormInscription = ref(false)
const newNiveau    = ref('')
const newFormationId = ref(null)
const inscMode     = ref('cours')   // 'niveau' ou 'cours'
const toutesFormations = ref([])
const inscLoading  = ref(false)
const inscErreur   = ref('')
const inscSucces   = ref('')

const langStore = useLangStore()
const { t } = storeToRefs(langStore)

const tabs = computed(() => [
  { key: 'niveaux',      label: '🎓 Mes niveaux' },
  { key: 'lecons',       label: '📖 ' + t.value.mesLecons },
  { key: 'infos',        label: '👤 ' + t.value.mesInfos },
  { key: 'certificats',  label: '🎓 ' + t.value.mesCertificats },
])

const initiales = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return ((u.prenom?.[0] || u.first_name?.[0] || '') + (u.nom?.[0] || u.last_name?.[0] || '')).toUpperCase() || '?'
})

const inscriptionsConfirmees = computed(() => inscriptions.value.filter(i => i.statut === 'confirme'))
const inscriptionsAttente    = computed(() => inscriptions.value.filter(i => i.statut === 'en_attente'))

const toutesFormationsConfirmees = computed(() => {
  const result = []
  for (const insc of inscriptionsConfirmees.value) {
    const formations = formationsParNiveau.value[insc.niveau] || []
    result.push(...formations)
  }
  return result
})

const totalLecons = computed(() => lecons.value.length)

const moyenneGlobale = computed(() => {
  if (!notes.value.length) return null
  return (notes.value.reduce((s, n) => s + parseFloat(n.valeur), 0) / notes.value.length).toFixed(2)
})

// Niveaux disponibles pour l'inscription (exclure ceux déjà inscrits et validés)
const niveauxDisponibles = computed(() => {
  const all = [
    { value: 'A', label: 'Niveau A – Débutant',       icon: '🟢' },
    { value: 'B', label: 'Niveau B – Intermédiaire',  icon: '🟡' },
    { value: 'C', label: 'Niveau C – Avancé',         icon: '🔴' },
  ]
  return all.map(n => {
    const existing = inscriptions.value.find(i => i.niveau === n.value)
    return {
      ...n,
      taken: existing && existing.statut !== 'rejete',
      takenStatus: existing
        ? (existing.statut === 'confirme' ? '✅ Validé' : '⏳ En attente')
        : '',
    }
  })
})

function statutLabel(s) {
  return s === 'confirme' ? '✅ Validé' : s === 'en_attente' ? '⏳ En attente' : '❌ Rejeté'
}
function statutBadgeClass(s) {
  return s === 'confirme' ? 'badge--success' : s === 'en_attente' ? 'badge--warning' : 'badge--danger'
}
function ressources(lecon) {
  if (!lecon.ressources) return []
  return lecon.ressources.split(',').map(r => r.trim()).filter(Boolean)
}
function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('fr-FR') : '—'
}

async function chargerLecons(formationId) {
  if (!formationId) return
  leconLoading.value = true
  try {
    const { data } = await api.get('/formations/' + formationId + '/lecons/')
    lecons.value = data.results || data
  } catch {
    lecons.value = []
  } finally {
    leconLoading.value = false
  }
}

async function ouvrirFormation(formation, _niveau) {
  tabActif.value = 'lecons'
  formationSelectee.value = formation.id
  await chargerLecons(formation.id)
}

async function charger() {
  loading.value = true
  try {
    // 1. Inscriptions
    const { data: inscData } = await api.get('/inscriptions/mon-inscription/')
    inscriptions.value = Array.isArray(inscData) ? inscData : (inscData ? [inscData] : [])

    // 2. Toutes les formations (pour affichage par niveau + liste inscription)
    const { data: formationsData } = await api.get('/formations/')
    const allFormations = formationsData.results || formationsData
    toutesFormations.value = allFormations
    const byNiveau = {}
    for (const f of allFormations) {
      if (!byNiveau[f.niveau]) byNiveau[f.niveau] = []
      byNiveau[f.niveau].push(f)
    }
    formationsParNiveau.value = byNiveau

    // 3. Notes
    try {
      const { data: notesData } = await api.get('/notes/mes-notes/')
      notes.value = notesData.results || notesData
    } catch { notes.value = [] }

    // 4. Charger les leçons de la première formation confirmée
    const premiereFormation = toutesFormationsConfirmees.value[0]
    if (premiereFormation) {
      formationSelectee.value = premiereFormation.id
      await chargerLecons(premiereFormation.id)
    }

  } catch (e) {
    inscriptions.value = []
  } finally {
    loading.value = false
  }
}

function isFormationDejaInscrite(formationId) {
  return inscriptions.value.some(
    i => i.formation === formationId && i.statut !== 'rejete'
  )
}

async function soumettreInscription() {
  inscErreur.value = ''
  inscSucces.value = ''
  if (!newFormationId.value && !newNiveau.value) return
  inscLoading.value = true
  try {
    const payload = { niveau: newNiveau.value }
    if (newFormationId.value) payload.formation_id = newFormationId.value
    const { data } = await api.post('/inscriptions/inscrire/', payload)
    inscSucces.value = data.message || 'Inscription enregistrée. En attente de validation.'
    newNiveau.value = ''
    newFormationId.value = null
    await charger()
    setTimeout(() => {
      showFormInscription.value = false
      inscSucces.value = ''
    }, 2500)
  } catch (e) {
    inscErreur.value = e.response?.data?.error || 'Erreur lors de l\'inscription.'
  } finally {
    inscLoading.value = false
  }
}

async function reinscrire(niveau) {
  newNiveau.value = niveau
  await soumettreInscription()
}

// ── Prévisualisation certificat (apprenant) ──
const showCertifModal = ref(false)
const certifHtml      = ref('')

function visualiserCertificat() {
  certifHtml.value  = _buildCertifHtml()
  showCertifModal.value = true
}

function _buildCertifHtml() {
  const u          = auth.user
  const prenom     = u?.prenom || u?.first_name || ''
  const nomFam     = (u?.nom || u?.last_name || '').toUpperCase()
  const nomComplet = `${nomFam} ${prenom}`.trim()
  const insc       = inscriptionsConfirmees.value[0] || {}
  const niveau     = insc.niveau || 'A'
  const contenuNiveau = {
    A: "Essentiel du TIC - Système d'Exploitation - Traitement de texte de base - Power Point - Tableur de base - Internet de base",
    B: 'Traitement de texte avancé - Tableur avancé - Présentation avancée - Retouche photo - Publication assistée par ordinateur',
    C: 'Développement web - Base de données - Réseaux informatiques - Cybersécurité - Programmation',
  }
  const contenu  = contenuNiveau[niveau] || contenuNiveau['A']
  const today    = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
  const mention  = moyenneGlobale.value
    ? (moyenneGlobale.value >= 18 ? 'Excellent' : moyenneGlobale.value >= 16 ? 'Très Bien' : moyenneGlobale.value >= 14 ? 'Bien' : moyenneGlobale.value >= 12 ? 'Assez Bien' : 'Passable')
    : ''
  const annee    = new Date().getFullYear()
  const numCert  = `N° ${annee}/PIFTIC/CNFPPSH`
  // Réutiliser la même fonction de génération HTML que telechargerCertificat
  return _genererHtmlCertificat({ nomComplet, niveau, contenu, today, mention, numCert })
}

function _genererHtmlCertificat({ nomComplet, niveau, contenu, today, mention, numCert }) {
  return `<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<title>Attestation – ${nomComplet}</title>
<style>
  @page { size: A4 landscape; margin: 0; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family:'Times New Roman', Georgia, serif; background:#fff; -webkit-print-color-adjust:exact; print-color-adjust:exact; }

  .page {
    width: 297mm; height: 210mm;
    position: relative;
    overflow: hidden;
    background: white;
  }

  /* Bordure verte tressée — simulée avec un SVG en background */
  .border-outer {
    position: absolute; inset: 4mm;
    border: 5px solid #2e7d32;
    z-index: 1;
  }
  .border-inner {
    position: absolute; inset: 8mm;
    border: 2px solid #2e7d32;
    z-index: 1;
  }
  /* Motif tressé coins */
  .border-outer::before {
    content: '';
    position: absolute; inset: 3px;
    border: 2px dotted #4caf50;
  }

  .content {
    position: relative;
    z-index: 2;
    padding: 11mm 16mm 8mm 16mm;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* Numéro et référence arrêté */
  .ref-block {
    font-size: 7.5pt;
    color: #222;
    margin-bottom: 2mm;
    line-height: 1.5;
  }

  /* Logos */
  .logos {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1mm;
  }
  .logos img { height: 20mm; width: auto; object-fit: contain; }
  .logos img.center { height: 26mm; }

  /* Titre principal */
  .titre-principal {
    text-align: center;
    font-size: 22pt;
    font-weight: 900;
    color: #1b5e20;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 2mm 0 3mm;
  }

  /* Corps */
  .corps { text-align: center; line-height: 1.7; }
  .nom-etudiant {
    font-size: 16pt;
    font-weight: 900;
    color: #000;
    margin: 1mm 0;
  }
  .nee { font-size: 9pt; color: #222; font-style: italic; margin-bottom: 2mm; }
  .texte-suivi { font-size: 9.5pt; color: #222; margin: 1mm 0; }
  .formation-nom {
    font-size: 11pt;
    font-weight: 900;
    color: #1b5e20;
    display: inline;
  }
  .formation-contenu {
    font-size: 9pt;
    font-style: italic;
    font-weight: 700;
    color: #000;
    display: inline;
  }
  .session { font-size: 9pt; color: #222; margin: 2mm 0 1mm; }
  .mention-line {
    font-size: 10pt;
    font-weight: 700;
    text-decoration: underline;
    font-style: italic;
    color: #000;
    margin: 2mm 0;
  }
  .formule {
    font-size: 8.5pt;
    color: #222;
    font-style: italic;
    margin-top: 2mm;
  }

  /* Date + signatures */
  .bas-page {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: auto;
    padding-top: 2mm;
  }
  .date-lieu { font-size: 8.5pt; color: #222; text-align: right; flex: 1; }
  .signatures {
    display: flex;
    justify-content: space-between;
    width: 100%;
  }
  .sig {
    text-align: center;
    font-size: 8pt;
    width: 48%;
  }
  .sig-titre { font-weight: 700; margin-bottom: 12mm; font-size: 8.5pt; }
  .sig-nom   { font-size: 8.5pt; color: #c62828; font-weight: 700; }

  @media print {
    html, body { width: 297mm; height: 210mm; }
    .page { page-break-after: avoid; }
  }
</style>
</head><body>
<div class="page">
  <div class="border-outer"></div>
  <div class="border-inner"></div>

  <div class="content">

    <!-- Référence -->
    <div class="ref-block">
      ${numCert}<br>
      <em>Vu l'Arrêté N° 41 578/2010/MP/SEETFP du Décembre 2010 portant agrément des filières du CNFPPSH</em>
    </div>

    <!-- Logos -->
    <div class="logos">
      <img src="${LOGO_METFP}" alt="METFP" />
      <img src="${LOGO_MADAGASIKARA}" alt="Repoblikan'i Madagasikara" class="center" />
      <img src="${LOGO_PIFTIC}"  alt="PIFTIC" />
    </div>

    <!-- Titre -->
    <div class="titre-principal">Attestation de Formation</div>

    <!-- Corps -->
    <div class="corps">
      <div class="nom-etudiant">${nomComplet}</div>
      <div class="nee">Né(e) le : ${u?.date_naissance || '—'} à ${u?.lieu_naissance || '—'}</div>

      <div class="texte-suivi">a suivi une formation
        <span class="formation-nom">«&nbsp;PERMIS TIC ${niveauLabel}&nbsp;»</span>
        <span class="formation-contenu"> (${contenu})</span>
      </div>

      <div class="session">
        Au PIFTIC CNFPPSH Ampandrianomby, durant 60 heures,
        session du : ${insc.date_debut || '—'} – ${insc.date_fin || '—'}
      </div>

      ${mention ? `<div class="mention-line">Mention : ${mention}</div>` : ''}

      <div class="formule">
        En foi de quoi, le présent Attestation lui est délivrée pour servir et valoir ce que de droit.
      </div>
    </div>

    <!-- Bas de page -->
    <div class="bas-page">
      <div class="signatures">
        <div class="sig">
          <div class="sig-titre">Le Directeur du CNFPPSH</div>
          <div class="sig-nom"></div>
        </div>
        <div style="text-align:right; font-size:8.5pt; align-self:flex-start; padding-top:0;">
          Antananarivo le, ${today}
        </div>
        <div class="sig">
          <div class="sig-titre">Le Coordonnateur du PIF TIC</div>
          <div class="sig-nom"></div>
        </div>
      </div>
    </div>

  </div>
</div>
<script>window.onload = () => { window.print(); }<\/script>
</body></html>`
}

// Réservé à l'admin — non exposé dans l'UI apprenant
function telechargerCertificat() {
  const u          = auth.user
  const prenom     = u?.prenom || u?.first_name || ''
  const nomFam     = (u?.nom || u?.last_name || '').toUpperCase()
  const nomComplet = `${nomFam} ${prenom}`.trim()
  const insc       = inscriptionsConfirmees.value[0] || {}
  const niveau     = insc.niveau || 'A'
  const contenuNiveau = {
    A: "Essentiel du TIC - Système d'Exploitation - Traitement de texte de base - Power Point - Tableur de base - Internet de base",
    B: 'Traitement de texte avancé - Tableur avancé - Présentation avancée - Retouche photo - Publication assistée par ordinateur',
    C: 'Développement web - Base de données - Réseaux informatiques - Cybersécurité - Programmation',
  }
  const contenu  = contenuNiveau[niveau] || contenuNiveau['A']
  const today    = new Date().toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })
  const mention  = moyenneGlobale.value
    ? (moyenneGlobale.value >= 18 ? 'Excellent' : moyenneGlobale.value >= 16 ? 'Très Bien' : moyenneGlobale.value >= 14 ? 'Bien' : moyenneGlobale.value >= 12 ? 'Assez Bien' : 'Passable')
    : ''
  const annee    = new Date().getFullYear()
  const numCert  = `N° ${annee}/PIFTIC/CNFPPSH`
  const html = _genererHtmlCertificat({ nomComplet, niveau, contenu, today, mention, numCert })
  const blob = new Blob([html], { type: 'text/html' })
  const url  = URL.createObjectURL(blob)
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 30000)
}

function deconnexion() { auth.logout(); router.push('/') }

onMounted(() => { applyTheme(theme.value); charger() })
</script>

<style scoped>
.apprenant-page { min-height:100vh; background:var(--bg,#f4f6f8); }

/* Header */
.appr-header { background:linear-gradient(135deg,var(--primary,#0097A7),var(--secondary,#F9C514)); padding:12px 20px; }
.header-inner { max-width:860px; margin:0 auto; display:flex; justify-content:space-between; align-items:center; }
.header-actions { display:flex; align-items:center; gap:14px; }
.logo { display:flex; align-items:center; gap:10px; color:white; font-weight:900; font-size:1.1rem; }
.logo-title { letter-spacing:1px; }
.btn-outline { background:rgba(255,255,255,0.15); border:2px solid rgba(255,255,255,0.7); color:white; padding:7px 16px; border-radius:20px; cursor:pointer; font-weight:600; font-size:13px; transition:.2s; }
.btn-outline:hover { background:rgba(255,255,255,0.3); }

/* Theme toggle */
.theme-toggle { display:flex; align-items:center; gap:8px; background:rgba(255,255,255,0.15); border:none; cursor:pointer; padding:5px 12px 5px 6px; border-radius:30px; transition:background .2s; }
.theme-toggle:hover { background:rgba(255,255,255,0.25); }
.toggle-track { width:46px; height:24px; background:rgba(255,255,255,0.3); border-radius:20px; position:relative; transition:background .3s; flex-shrink:0; }
.toggle-track.dark { background:rgba(0,0,0,0.3); }
.toggle-thumb { position:absolute; top:2px; left:2px; width:20px; height:20px; border-radius:50%; background:white; display:flex; align-items:center; justify-content:center; font-size:11px; box-shadow:0 2px 4px rgba(0,0,0,.2); transition:transform .3s cubic-bezier(.34,1.56,.64,1); }
.toggle-track.dark .toggle-thumb { transform:translateX(22px); }
.toggle-label { font-size:12px; font-weight:600; color:white; white-space:nowrap; }

/* Body */
.appr-body { max-width:860px; margin:0 auto; padding:24px 16px 40px; }
.loading { text-align:center; padding:60px; color:#888; }

/* Cover */
.profile-cover { background:white; border-radius:0 0 24px 24px; box-shadow:0 2px 16px rgba(0,0,0,.08); margin-bottom:16px; overflow:hidden; }
.cover-bg { height:140px; background:linear-gradient(135deg,#0097A7,#F9C514); }
.profile-card { display:flex; align-items:flex-end; gap:16px; padding:0 24px 18px; }
.avatar { width:90px; height:90px; border-radius:50%; border:4px solid white; background:linear-gradient(135deg,#0097A7,#F9C514); display:flex; align-items:center; justify-content:center; font-size:2.2rem; font-weight:900; color:white; margin-top:-40px; flex-shrink:0; box-shadow:0 4px 16px rgba(0,0,0,.2); overflow:hidden; }
.avatar-img { width:100%; height:100%; object-fit:cover; border-radius:50%; }
.profile-info h2 { font-size:1.3rem; font-weight:900; margin:0; }
.profile-info p  { color:#888; font-size:0.82rem; margin:2px 0 8px; }
.badges { display:flex; gap:8px; flex-wrap:wrap; }
.profile-stats { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; padding:0 24px 20px; }
.stat-box { background:#f4f6f8; border-radius:14px; padding:14px; text-align:center; border:1px solid #e5e7eb; }
.stat-val { font-size:1.5rem; font-weight:900; }
.stat-lbl { font-size:0.72rem; color:#888; margin-top:3px; }

/* Action bar */
.action-bar { display:flex; justify-content:flex-end; margin-bottom:12px; }

/* Formulaire inscription */
.inscription-form { margin-bottom:16px; animation:fadeIn .2s ease; }
.form-group { margin-bottom:18px; }
.form-group label { display:block; font-size:13px; font-weight:700; color:#444; margin-bottom:10px; }
.niveau-cards { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
.niveau-card { border:2px solid #e5e7eb; border-radius:12px; padding:14px; cursor:pointer; transition:.2s; display:flex; align-items:center; gap:10px; }
.niveau-card:hover:not(.niveau-card--taken) { border-color:#0097A7; background:#f0fdff; }
.niveau-card--active { border-color:#0097A7; background:#e0f7fa; }
.niveau-card--taken { opacity:.55; cursor:not-allowed; background:#f9f9f9; }
.niveau-icon { font-size:1.4rem; }
.niveau-info { display:flex; flex-direction:column; }
.niveau-info strong { font-size:13px; }
.taken-badge { font-size:11px; color:#888; margin-top:2px; }
.alert { padding:10px 14px; border-radius:8px; font-size:13px; margin-bottom:12px; }
.alert-danger { background:#ffebee; color:#c62828; }
.alert-success { background:#e8f5e9; color:#2e7d32; }

/* Tabs */
.tabs { display:flex; background:white; border-radius:16px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,.07); margin-bottom:18px; }
.tab { flex:1; padding:14px 6px; border:none; background:none; cursor:pointer; font-size:0.82rem; font-weight:600; color:#888; transition:.2s; }
.tab:hover { background:#f4f6f8; }
.tab--active { background:var(--primary,#0097A7); color:white; }

/* Panel */
.panel { animation:fadeIn .25s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }

/* Niveau detail card */
.niveau-detail { margin-bottom:16px; }
.nd-header { display:flex; align-items:center; gap:10px; margin-bottom:8px; flex-wrap:wrap; }
.nd-date { font-size:11px; color:#aaa; margin-left:auto; }
.nd-label { font-size:14px; color:#555; margin-bottom:12px; }

.attente-mini { background:#fff8e1; border-left:4px solid #FF9800; border-radius:8px; padding:12px 14px; }
.attente-mini p { font-size:13px; color:#555; margin-bottom:4px; }
.rejete-mini { background:#ffebee; border-left:4px solid #f44336; border-radius:8px; padding:12px 14px; }
.rejete-mini p { font-size:13px; color:#c62828; margin-bottom:6px; }
.hint { font-size:11px; color:#888; }
.confirmed-msg { font-size:13px; color:#2e7d32; margin-bottom:12px; }

.formations-list { display:flex; flex-direction:column; gap:8px; }
.formation-item { display:flex; align-items:center; gap:10px; padding:10px 14px; background:#f4f6f8; border-radius:10px; transition:.15s; }
.formation-item:hover { background:#e0f7fa; }
.f-icon { font-size:1.1rem; }
.f-nom { flex:1; font-size:14px; font-weight:600; }
.f-actions { display:flex; gap:8px; flex-shrink:0; }
.btn-acces { background:#0097A7; color:white; border-radius:8px; padding:6px 12px; font-size:12px; border:none; cursor:pointer; font-weight:700; transition:.15s; }
.btn-acces:hover { background:#00838f; }

/* Inscription mode tabs */
.insc-mode-tabs { display:flex; gap:8px; margin-bottom:4px; }
.insc-mode-tab { flex:1; padding:9px; border:2px solid #e5e7eb; border-radius:10px; background:white; cursor:pointer; font-size:13px; font-weight:600; color:#888; transition:.15s; }
.insc-mode-tab.active { border-color:#0097A7; background:#e0f7fa; color:#0097A7; }

/* Liste cours spécifiques */
.cours-list { display:flex; flex-direction:column; gap:8px; max-height:280px; overflow-y:auto; padding-right:4px; }
.cours-card { display:flex; align-items:center; justify-content:space-between; padding:10px 14px; border:2px solid #e5e7eb; border-radius:10px; cursor:pointer; transition:.15s; }
.cours-card:hover:not(.cours-card--taken) { border-color:#0097A7; background:#f0fdff; }
.cours-card--active { border-color:#0097A7; background:#e0f7fa; }
.cours-card--taken { opacity:.55; cursor:not-allowed; background:#f9f9f9; }
.cours-info { display:flex; align-items:center; gap:10px; }
.cours-info strong { font-size:13px; }
.cours-niveau { font-size:11px; padding:2px 8px; }

/* Niveau badges */
.niveau-badge { padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700; color:white; }
.niveau-bg-a { background:#2196F3; }
.niveau-bg-b { background:#FF9800; }
.niveau-bg-c { background:#9C27B0; }

/* Leçons */
.form-select-bar { display:flex; align-items:center; gap:12px; margin-bottom:16px; }
.form-select-bar label { font-size:13px; font-weight:700; white-space:nowrap; }
.form-select-bar select { flex:1; border:1.5px solid #ddd; border-radius:8px; padding:9px 12px; font-size:14px; }
.lecons-list { display:flex; flex-direction:column; gap:14px; }
.lecon-card { display:flex; gap:16px; align-items:flex-start; }
.lecon-num { min-width:36px; height:36px; border-radius:50%; background:var(--primary,#0097A7); color:white; display:flex; align-items:center; justify-content:center; font-weight:900; flex-shrink:0; }
.lecon-body h4 { margin-bottom:6px; }
.lecon-body p  { color:#888; font-size:0.85rem; }
.ressources { margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; }
.ressource-link { color:var(--primary,#0097A7); font-size:0.8rem; font-weight:600; text-decoration:none; background:rgba(0,151,167,.1); padding:3px 10px; border-radius:20px; }

/* Infos */
.info-grid { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.info-item { display:flex; flex-direction:column; gap:4px; }
.info-item label { font-size:0.78rem; font-weight:700; color:#888; text-transform:uppercase; letter-spacing:.5px; }
.info-item span  { font-size:0.92rem; }

/* Badges */
.badge { display:inline-block; padding:3px 10px; border-radius:20px; font-size:0.75rem; font-weight:700; }
.badge--success { background:#e0f7fa; color:#0097A7; }
.badge--info    { background:#e3f2fd; color:#1565c0; }
.badge--warning { background:#fff8e1; color:#f57f17; }
.badge--danger  { background:#ffebee; color:#c62828; }

/* Card */
.card { background:white; border-radius:16px; padding:24px; box-shadow:0 2px 12px rgba(0,0,0,.07); }

/* Buttons */
.btn { display:inline-flex; align-items:center; justify-content:center; gap:8px; border:none; border-radius:10px; cursor:pointer; font-weight:700; font-size:14px; transition:.2s; padding:10px 20px; }
.btn-primary { background:var(--primary,#0097A7); color:white; }
.btn-primary:hover:not(:disabled) { opacity:.9; transform:translateY(-1px); }
.btn-primary:disabled { opacity:.6; cursor:not-allowed; }
.btn-sm { padding:6px 14px; font-size:12px; background:#0097A7; color:white; border-radius:8px; margin-top:8px; }

/* Certificat */
.certificat-dispo { display:flex; flex-direction:column; align-items:center; gap:10px; }

/* ── Modal prévisualisation certificat ── */
.certif-modal-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.65);
  display: flex; align-items: center; justify-content: center;
  padding: 16px;
}
.certif-modal {
  background: #fff; border-radius: 16px;
  width: 100%; max-width: 950px; max-height: 90vh;
  display: flex; flex-direction: column;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(0,0,0,0.35);
}
.certif-modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px; border-bottom: 1px solid #eee;
  background: #f8f9fa;
}
.certif-modal-header h3 { margin: 0; font-size: 1rem; color: #1b5e20; }
.certif-close-btn {
  background: none; border: none; font-size: 1.2rem;
  cursor: pointer; color: #666; padding: 4px 8px; border-radius: 6px;
}
.certif-close-btn:hover { background: #eee; color: #333; }
.certif-modal-body { flex: 1; overflow: hidden; min-height: 0; }
.certif-iframe { width: 100%; height: 100%; min-height: 480px; border: none; }
.certif-modal-footer {
  padding: 14px 24px; border-top: 1px solid #eee;
  display: flex; align-items: center; justify-content: space-between;
  background: #f8f9fa; gap: 12px; flex-wrap: wrap;
}
.certif-notice {
  font-size: 12px; color: #888; margin: 0;
  display: flex; align-items: center; gap: 6px;
}

/* Empty */
.empty-state { text-align:center; color:#888; padding:40px; background:white; border-radius:16px; box-shadow:0 2px 12px rgba(0,0,0,.07); }

@media (max-width:600px) {
  .profile-stats { grid-template-columns:repeat(3,1fr); gap:8px; }
  .info-grid { grid-template-columns:1fr; }
  .tab { font-size:0.72rem; padding:12px 4px; }
  .niveau-cards { grid-template-columns:1fr; }
  .form-select-bar { flex-direction:column; align-items:flex-start; }

  /* Inscriptions sur mobile */
  .insc-card { padding: 14px; }
  .niveau-cards { grid-template-columns: 1fr; }
  .insc-mode-tabs { flex-direction: column; gap: 6px; }
  .cours-list { max-height: 220px; }
  .cours-card { padding: 10px 12px; }
  .btn-acces { font-size: 11px; padding: 5px 10px; }
}

@media (max-width: 400px) {
  .tabs { gap: 0; }
  .tab  { font-size: 0.65rem; padding: 10px 2px; }
  .profile-name { font-size: 1.1rem; }
}
</style>