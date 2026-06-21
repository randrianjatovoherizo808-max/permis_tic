<template>
  <div>
    <div class="page-header">
      <h2 class="page-title">🎓 Certificats</h2>
      <button class="btn btn-primary" @click="ouvrirModal()">+ Générer un certificat</button>
    </div>

    <!-- Filtres -->
    <div class="filters card">
      <input v-model="recherche" type="text" placeholder="🔍 Rechercher par nom, formation…" class="search-input" />
      <select v-model="filtreNiveau">
        <option value="">Tous les niveaux</option>
        <option value="A">Niveau A</option>
        <option value="B">Niveau B</option>
        <option value="C">Niveau C</option>
      </select>
      <button class="btn btn-outline btn-sm" @click="exportCSV">⬇️ Exporter</button>
    </div>

    <!-- Tableau -->
    <div class="card">
      <div v-if="loading" class="empty-td">Chargement…</div>
      <table v-else>
        <thead>
          <tr>
            <th>N° Certificat</th>
            <th>Apprenant</th>
            <th>Formation</th>
            <th>Niveau</th>
            <th>Mention</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in certsFiltres" :key="c.id">
            <td><code class="cert-id">{{ c.identifiant }}</code></td>
            <td>
              <div class="user-cell">
                <div class="avatar">
                  <img v-if="c.apprenant_photo" :src="c.apprenant_photo" :alt="initiales(c.apprenant_nom)"
                       class="avatar-img" referrerpolicy="no-referrer" />
                  <span v-else>{{ initiales(c.apprenant_nom) }}</span>
                </div>
                <span class="user-name">{{ c.apprenant_nom }}</span>
              </div>
            </td>
            <td>{{ c.formation_nom }}</td>
            <td>
              <span class="niveau-badge" :class="'niveau-' + (c.formation_niveau || '').toLowerCase()">
                {{ c.formation_niveau }}
              </span>
            </td>
            <td>
              <span class="badge" :class="mentionClass(c.mention)">{{ c.mention || '—' }}</span>
            </td>
            <td>{{ formatDate(c.date_delivrance) }}</td>
            <td>
              <div class="actions">
                <button class="btn btn-primary btn-sm" @click="previsualiser(c)" title="Prévisualiser">👁</button>
                <button class="btn btn-outline btn-sm" @click="ouvrirModal(c)" title="Modifier">✏️</button>
                <button class="btn btn-danger btn-sm" @click="supprimer(c.id)" title="Supprimer">🗑️</button>
              </div>
            </td>
          </tr>
          <tr v-if="certsFiltres.length === 0 && !loading">
            <td colspan="7" class="empty-td">Aucun certificat trouvé.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal création / édition -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-head">
          <h3>{{ form.id ? '✏️ Modifier le certificat' : '🎓 Générer un certificat' }}</h3>
          <button @click="showModal = false" class="close-btn">×</button>
        </div>

        <form @submit.prevent="sauvegarder">
          <div class="form-group">
            <label>Apprenant *</label>
            <select v-model="form.apprenant" required>
              <option value="">— Choisir un apprenant —</option>
              <option v-for="a in apprenants" :key="a.id" :value="a.id">
                {{ (a.first_name || a.prenom || '') + ' ' + (a.last_name || a.nom || '') }} — {{ a.niveaux_label || 'Aucun niveau validé' }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Niveau *</label>
            <select v-model="form.niveau" required>
              <option value="">— Choisir un niveau —</option>
              <option value="A">Niveau A – Débutant</option>
              <option value="B">Niveau B – Intermédiaire</option>
              <option value="C">Niveau C – Avancé</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Date de délivrance *</label>
              <input v-model="form.date_delivrance" type="date" required />
            </div>
            <div class="form-group">
              <label>Lieu de délivrance</label>
              <input v-model="form.lieu_delivrance" type="text" placeholder="Antananarivo" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Mention</label>
              <select v-model="form.mention">
                <option value="">— Aucune —</option>
                <option value="Passable">Passable (10–12)</option>
                <option value="Assez Bien">Assez Bien (12–14)</option>
                <option value="Bien">Bien (14–16)</option>
                <option value="Très Bien">Très Bien (16–18)</option>
                <option value="Excellent">Excellent (18–20)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Date de début de formation</label>
              <input v-model="form.date_debut" type="date" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Date de fin de formation</label>
              <input v-model="form.date_fin" type="date" />
            </div>
            <div class="form-group">
              <label>Lieu de naissance</label>
              <input v-model="form.lieu_naissance" type="text" placeholder="Antananarivo" />
            </div>
          </div>
          <div class="form-group">
            <label>Date de naissance</label>
            <input v-model="form.date_naissance" type="date" />
          </div>

          <!-- Champs formation PERMIS TIC -->
          <hr style="margin: 12px 0; border-color: #e0e0e0;" />
          <p style="font-size: 0.85rem; color: #666; margin-bottom: 8px;">Informations sur la formation (pour l'attestation)</p>

          <div class="form-group">
            <label>Intitulé de formation (PERMIS TIC ...)</label>
            <input v-model="form.intitule_formation" type="text" placeholder="ex: PERMIS TIC A" />
          </div>

          <div class="form-group">
            <label>Contenu / Modules</label>
            <textarea v-model="form.contenu_formation" rows="3" placeholder="Essentiel du TIC – Système d'Exploitation – Traitement de texte…" style="resize:vertical;"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Durée (heures)</label>
              <input v-model="form.duree_formation" type="number" placeholder="60" min="1" />
            </div>
            <div class="form-group">
              <label>Lieu du centre</label>
              <input v-model="form.lieu_centre" type="text" placeholder="PIFTIC CNFPPSH Ampandrianomby" />
            </div>
          </div>

          <div v-if="erreur" class="alert alert-error">{{ erreur }}</div>
          <button type="submit" class="btn btn-primary btn-full" :disabled="saving">
            {{ saving ? '⏳ Enregistrement…' : (form.id ? '💾 Modifier' : '🎓 Générer') }}
          </button>
        </form>
      </div>
    </div>

    <!-- Modal prévisualisation -->
    <div v-if="certPreview" class="modal-overlay" @click.self="certPreview = null">
      <div class="modal-box preview-box">
        <div class="modal-head">
          <h3>🎓 Prévisualisation du certificat</h3>
          <button @click="certPreview = null" class="close-btn">×</button>
        </div>

        <div class="cert-preview" ref="certRef">
          <div class="cert-header">
            <div class="cert-logos-row">

              <!-- Logo 1 : METFP (gauche) -->
              <div class="cert-logo-wrap">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="64" height="64">
                  <!-- Roue dentée verte -->
                  <circle cx="50" cy="50" r="46" fill="none" stroke="#2e7d32" stroke-width="6"/>
                  <circle cx="50" cy="50" r="38" fill="#2e7d32"/>
                  <!-- Dents de la roue -->
                  <g fill="#2e7d32">
                    <rect x="46" y="2" width="8" height="12" rx="2"/>
                    <rect x="46" y="86" width="8" height="12" rx="2"/>
                    <rect x="2" y="46" width="12" height="8" rx="2"/>
                    <rect x="86" y="46" width="12" height="8" rx="2"/>
                    <rect x="13" y="13" width="8" height="12" rx="2" transform="rotate(45 17 19)"/>
                    <rect x="79" y="13" width="8" height="12" rx="2" transform="rotate(-45 83 19)"/>
                    <rect x="13" y="75" width="8" height="12" rx="2" transform="rotate(-45 17 81)"/>
                    <rect x="79" y="75" width="8" height="12" rx="2" transform="rotate(45 83 81)"/>
                  </g>
                  <!-- Silhouette personne rouge au centre -->
                  <circle cx="50" cy="35" r="9" fill="#c62828"/>
                  <path d="M34 65 Q34 48 50 48 Q66 48 66 65 Z" fill="#c62828"/>
                  <!-- Texte METFP -->
                  <text x="50" y="80" text-anchor="middle" font-size="9" font-weight="900" fill="white" font-family="Arial">METFP</text>
                </svg>
                <span class="cert-logo-label">METFP</span>
              </div>

              <!-- Logo 2 : Armoiries Madagasikara (centre) -->
              <div class="cert-logo-center-wrap">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 130" width="80" height="86">
                  <!-- Fond médaillon doré -->
                  <circle cx="60" cy="58" r="50" fill="#c8a000" stroke="#8b6800" stroke-width="3"/>
                  <circle cx="60" cy="58" r="44" fill="#e8c000"/>
                  <!-- Drapeau Madagascar (rouge, blanc, vert) -->
                  <rect x="36" y="28" width="12" height="42" fill="white"/>
                  <rect x="48" y="28" width="24" height="21" fill="#fc3d32"/>
                  <rect x="48" y="49" width="24" height="21" fill="#007749"/>
                  <!-- Zébu stylisé -->
                  <ellipse cx="60" cy="68" rx="14" ry="8" fill="#8b6800"/>
                  <path d="M46 65 Q44 58 48 62" fill="none" stroke="#8b6800" stroke-width="3"/>
                  <path d="M74 65 Q76 58 72 62" fill="none" stroke="#8b6800" stroke-width="3"/>
                  <circle cx="60" cy="62" r="5" fill="#6d4c00"/>
                  <!-- Texte -->
                  <text x="60" y="115" text-anchor="middle" font-size="7" font-weight="700" fill="#5a3e00" font-family="Arial">REPOBLIKAN'I MADAGASIKARA</text>
                  <text x="60" y="124" text-anchor="middle" font-size="5.5" fill="#5a3e00" font-family="Arial">Fitiavana · Tanindrazana · Fandrosoana</text>
                </svg>
              </div>

              <!-- Logo 3 : PIFTIC (droite) -->
              <div class="cert-logo-wrap">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="64" height="64">
                  <!-- Bordure rouge -->
                  <rect x="2" y="2" width="96" height="96" rx="8" fill="white" stroke="#c62828" stroke-width="5"/>
                  <!-- Lettre P rouge -->
                  <text x="6" y="62" font-size="52" font-weight="900" fill="#c62828" font-family="Arial">P</text>
                  <!-- Ordinateur portable vert -->
                  <rect x="38" y="28" width="46" height="32" rx="3" fill="#2e7d32"/>
                  <rect x="41" y="31" width="40" height="26" rx="2" fill="#a5d6a7"/>
                  <!-- Arbre sur l'écran -->
                  <polygon points="61,36 55,48 67,48" fill="#2e7d32"/>
                  <polygon points="61,33 53,46 69,46" fill="#1b5e20"/>
                  <rect x="59" y="47" width="4" height="5" fill="#5d4037"/>
                  <!-- Base ordinateur -->
                  <rect x="34" y="60" width="54" height="4" rx="2" fill="#2e7d32"/>
                  <!-- Lettres IFTIC -->
                  <text x="40" y="85" font-size="14" font-weight="900" fill="#2e7d32" font-family="Arial">IFTIC</text>
                  <!-- Ligne décorative -->
                  <rect x="5" y="88" width="90" height="2" fill="#c62828"/>
                </svg>
                <span class="cert-logo-label">PIFTIC</span>
              </div>

            </div>
            <!-- Sous-titre organisation -->
            <div class="cert-org-subtitle">
              <div class="cert-org">CNFPPSH — PIFTIC</div>
              <div class="cert-sub">Points d'Information et Formation utilisant les TIC</div>
            </div>
          </div>
          <div class="cert-title">CERTIFICAT DE COMPÉTENCES</div>
          <div class="cert-body">
            <p>Nous certifions que</p>
            <div class="cert-name">{{ certPreview.apprenant_nom }}</div>
            <p v-if="certPreview.date_naissance">
              né(e) le {{ formatDate(certPreview.date_naissance) }}
              <span v-if="certPreview.lieu_naissance"> à {{ certPreview.lieu_naissance }}</span>
            </p>
            <p>a suivi avec succès la formation</p>
            <div class="cert-formation">{{ certPreview.formation_nom }}</div>
            <div class="cert-niveau">
              <span class="niveau-badge" :class="'niveau-' + (certPreview.formation_niveau || '').toLowerCase()">
                Niveau {{ certPreview.formation_niveau }}
              </span>
            </div>
            <p v-if="certPreview.date_debut && certPreview.date_fin">
              du {{ formatDate(certPreview.date_debut) }} au {{ formatDate(certPreview.date_fin) }}
            </p>
            <div v-if="certPreview.mention" class="cert-mention">
              Mention : <strong>{{ certPreview.mention }}</strong>
            </div>
          </div>
          <div class="cert-footer">
            <div class="cert-date-lieu">
              {{ certPreview.lieu_delivrance || 'Antananarivo' }}, le {{ formatDate(certPreview.date_delivrance) }}
            </div>
            <div class="cert-sign">
              <div class="sign-line"></div>
              <div>Le Directeur</div>
            </div>
            <div class="cert-id-badge">N° {{ certPreview.identifiant }}</div>
          </div>
          <!-- QR code placeholder -->
          <div :id="'qr-' + certPreview.id" class="cert-qr"></div>
        </div>

        <div class="preview-actions">
          <button class="btn btn-outline" @click="certPreview = null">Fermer</button>
          <button class="btn btn-primary" @click="imprimerCert">🖨️ Imprimer / PDF</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api'
import { useToast } from '../../composables/useToast'

// Logos du certificat encodés en base64 : embarqués directement dans le HTML
// généré pour l'impression/export PDF, afin qu'ils restent toujours visibles
// même une fois le document téléchargé (un chemin relatif comme /logo.png
// ne se résout pas de façon fiable dans la fenêtre détachée du blob HTML).
const LOGO_METFP = "data:image/jpeg;base64,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"
const LOGO_MADAGASIKARA = "data:image/jpeg;base64,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"
const LOGO_PIFTIC = "data:image/jpeg;base64,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"

const { showToast } = useToast()
const loading     = ref(true)
const saving      = ref(false)
const certificats = ref([])
const apprenants  = ref([])
const recherche   = ref('')
const filtreNiveau = ref('')
const showModal   = ref(false)
const certPreview = ref(null)
const erreur      = ref('')
const certRef     = ref(null)

const formVide = () => ({
  id: null, apprenant: '', niveau: '', date_delivrance: new Date().toISOString().split('T')[0],
  lieu_delivrance: 'Antananarivo', mention: '', date_debut: '', date_fin: '',
  date_naissance: '', lieu_naissance: '',
  intitule_formation: '', contenu_formation: '', duree_formation: 60, lieu_centre: 'PIFTIC CNFPPSH Ampandrianomby',
})
const form = ref(formVide())

const certsFiltres = computed(() => {
  const q = recherche.value.toLowerCase()
  return certificats.value.filter((c) => {
    const matchText  = c.apprenant_nom?.toLowerCase().includes(q) || c.formation_nom?.toLowerCase().includes(q)
    const matchNiv   = !filtreNiveau.value || c.formation_niveau === filtreNiveau.value
    return matchText && matchNiv
  })
})

async function charger() {
  loading.value = true
  try {
    const [certRes, appRes, inscRes, notesRes] = await Promise.all([
      api.get('/certificats/'),
      api.get('/users/', { params: { role: 'etudiant' } }),
      api.get('/inscriptions/', { params: { statut: 'confirme' } }),
      api.get('/notes/'),
    ])
    const rawCerts = certRes.data.results ?? certRes.data
    const usersMap = {}
    ;(appRes.data.results ?? appRes.data).forEach(u => { usersMap[u.id] = u })
    certificats.value = rawCerts.map(c => ({
      ...c,
      apprenant_photo: usersMap[c.apprenant]?.photo_url || null,
    }))

    // Niveaux validés par utilisateur
    const inscriptions = inscRes.data.results ?? inscRes.data
    const niveauxParUser = {}
    for (const insc of inscriptions) {
      if (!niveauxParUser[insc.utilisateur]) niveauxParUser[insc.utilisateur] = []
      niveauxParUser[insc.utilisateur].push(insc.niveau)
    }

    // Utilisateurs ayant au moins une note
    const notes = notesRes.data.results ?? notesRes.data
    const usersAvecNotes = new Set(notes.map(n => n.apprenant))

    const tousEtudiants = appRes.data.results ?? appRes.data
    // Uniquement ceux avec niveau validé ET au moins une note
    apprenants.value = tousEtudiants
      .filter(u => niveauxParUser[u.id]?.length > 0 && usersAvecNotes.has(u.id))
      .map(u => ({
        ...u,
        niveaux: niveauxParUser[u.id] || [],
        niveaux_label: (niveauxParUser[u.id] || []).map(n => 'Niveau ' + n).join(', '),
      }))
  } catch {
    showToast('Erreur chargement des certificats.', 'error')
  } finally {
    loading.value = false
  }
}

function ouvrirModal(cert = null) {
  erreur.value = ''
  form.value = cert
    ? { ...formVide(), ...cert }
    : formVide()
  showModal.value = true
}

async function sauvegarder() {
  erreur.value = ''
  saving.value = true
  try {
    if (form.value.id) {
      await api.put(`/certificats/${form.value.id}/`, form.value)
      showToast('Certificat modifié.', 'success')
    } else {
      await api.post('/certificats/', form.value)
      showToast('Certificat généré.', 'success')
    }
    showModal.value = false
    await charger()
  } catch (e) {
    const d = e.response?.data
    erreur.value = typeof d === 'object' ? Object.values(d).flat().join(' ') : 'Erreur lors de l\'enregistrement.'
  } finally {
    saving.value = false
  }
}

async function supprimer(id) {
  if (!confirm('Supprimer ce certificat ?')) return
  try {
    await api.delete(`/certificats/${id}/`)
    showToast('Certificat supprimé.', 'info')
    await charger()
  } catch {
    showToast('Erreur lors de la suppression.', 'error')
  }
}

function previsualiser(cert) {
  certPreview.value = cert
}

function imprimerCert() {
  const c = certPreview.value
  if (!c) return

  const niveau  = c.formation_niveau || c.niveau || 'A'
  const annee   = new Date().getFullYear()
  const numCert = c.numero || c.identifiant || `N° ${annee}/153-PIFTIC/CNFPPSH`

  const contenuNiveau = {
    A: "Essentiel du TIC – Système d'Exploitation – Traitement de texte de base – Power Point – Tableur de base – Internet de base",
    B: "Traitement de texte avancé – Tableur avancé – Présentation avancée – Retouche photo – Publication assistée par ordinateur",
    C: "Développement web – Base de données – Réseaux informatiques – Cybersécurité – Programmation",
  }
  // Utiliser les valeurs personnalisées du formulaire si disponibles
  const contenu = c.contenu_formation || contenuNiveau[niveau] || contenuNiveau['A']
  const intitule = c.intitule_formation || ('PERMIS TIC ' + niveau)
  const duree = c.duree_formation || 60
  const lieuCentre = c.lieu_centre || 'PIFTIC CNFPPSH Ampandrianomby'

  const fmtDate      = (d) => d ? new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' }) : '—'
  const fmtDateShort = (d) => d ? new Date(d).toLocaleDateString('fr-FR') : '—'

  const dateDelivrance = fmtDate(c.date_delivrance)
  const dateDebut      = fmtDateShort(c.date_debut)
  const dateFin        = fmtDateShort(c.date_fin)
  const dateNaissance  = c.date_naissance ? fmtDate(c.date_naissance) : null
  const lieu           = c.lieu_naissance || ''
  const mention        = c.mention || ''
  const lieuDeliv      = c.lieu_delivrance || 'Antananarivo'

  const ligneNaissance = dateNaissance
    ? `Né(e) le : <strong>${dateNaissance}</strong>${lieu ? ` à <strong>${lieu}</strong>` : ''}`
    : ''
  const ligneSession = (c.date_debut && c.date_fin)
    ? `Au ${lieuCentre}, durant ${duree} heures, session du : <strong>${dateDebut} – ${dateFin}</strong>`
    : `Au ${lieuCentre}`

  const html = `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Attestation – ${c.apprenant_nom}</title>
<style>
  @page { size: A4 landscape; margin: 0; }
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'Times New Roman', Times, Georgia, serif;
    background: #fff;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
    color: #111;
  }

  .page {
    width: 297mm;
    height: 210mm;
    position: relative;
    background: #fff;
    overflow: hidden;
  }

  /* ── Bordure décorative celtique (SVG répété) ── */
  .border-deco {
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 1;
  }

  /* ── Contenu principal ── */
  .content {
    position: relative;
    z-index: 2;
    padding: 13mm 17mm 9mm 17mm;
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  /* ── Référence ── */
  .ref-block {
    font-size: 7pt;
    color: #333;
    line-height: 1.6;
    margin-bottom: 2mm;
  }
  .ref-block em { font-style: italic; }

  /* ── Logos ── */
  .logos {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2mm;
  }
  .logo-wrap { display: flex; flex-direction: column; align-items: center; gap: 1mm; }
  .logo-wrap img { height: 18mm; width: auto; object-fit: contain; }
  .logo-wrap img.logo-center { height: 23mm; }
  .logo-sub {
    text-align: center;
    font-size: 5.5pt;
    color: #5a3e00;
    line-height: 1.4;
    font-style: italic;
  }

  /* ── Titre ATTESTATION DE FORMATION ── */
  .titre {
    text-align: center;
    font-size: 21pt;
    font-weight: 900;
    color: #1b5e20;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 1.5mm 0 2.5mm;
    font-family: 'Times New Roman', Times, serif;
  }

  /* ── Corps ── */
  .corps { text-align: center; flex: 1; }
  .corps p { font-size: 9.5pt; color: #222; line-height: 1.7; margin: 0; }

  .nom-apprenant {
    font-size: 15.5pt;
    font-weight: 900;
    color: #000;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'Times New Roman', Times, serif;
    margin: 1mm 0 0.5mm;
  }
  .naissance {
    font-size: 9pt;
    font-style: italic;
    color: #222;
    margin-bottom: 2mm;
  }
  .suivi { font-size: 9.5pt; color: #222; margin: 1mm 0; }
  .formation-titre  { font-size: 11pt; font-weight: 900; font-style: italic; color: #000; }
  .formation-detail { font-size: 9pt; font-style: italic; font-weight: 700; color: #111; }
  .session-line { font-size: 9pt; color: #222; margin: 1.5mm 0 0.5mm; }
  .mention-line {
    display: inline-block;
    font-size: 10.5pt;
    font-weight: 700;
    font-style: italic;
    text-decoration: underline;
    color: #000;
    margin: 1.5mm 0;
  }
  .formule { font-size: 8.5pt; font-style: italic; color: #333; margin-top: 2mm; }

  /* ── Bas de page ── */
  .bas-page {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: auto;
    padding-top: 2mm;
  }
  .sig { text-align: center; font-size: 8pt; width: 42%; }
  .sig-titre { font-weight: 700; font-size: 8.5pt; margin-bottom: 12mm; }
  .sig-nom   { font-size: 8.5pt; color: #c62828; font-weight: 700; text-decoration: underline; }
  .date-lieu {
    text-align: center;
    font-size: 8.5pt;
    color: #222;
    align-self: flex-end;
    padding-bottom: 2mm;
  }

  @media print {
    html, body { width: 297mm; height: 210mm; }
  }
</style>
</head>
<body>
<div class="page">

  <!-- Bordure SVG celtique verte identique à la photo -->
  <svg class="border-deco" xmlns="http://www.w3.org/2000/svg"
       viewBox="0 0 1122 794" preserveAspectRatio="none"
       style="position:absolute;inset:0;width:100%;height:100%;z-index:1;">
    <defs>
      <!-- Motif tressé celtique horizontal -->
      <pattern id="ph" x="0" y="0" width="28" height="14" patternUnits="userSpaceOnUse">
        <rect width="28" height="14" fill="none"/>
        <!-- losange tressé simplifié -->
        <path d="M0 7 Q7 0 14 7 Q21 14 28 7" fill="none" stroke="#2e7d32" stroke-width="2.2"/>
        <path d="M0 7 Q7 14 14 7 Q21 0 28 7" fill="none" stroke="#4caf50" stroke-width="1.2"/>
      </pattern>
      <!-- Motif vertical -->
      <pattern id="pv" x="0" y="0" width="14" height="28" patternUnits="userSpaceOnUse">
        <rect width="14" height="28" fill="none"/>
        <path d="M7 0 Q0 7 7 14 Q14 21 7 28" fill="none" stroke="#2e7d32" stroke-width="2.2"/>
        <path d="M7 0 Q14 7 7 14 Q0 21 7 28" fill="none" stroke="#4caf50" stroke-width="1.2"/>
      </pattern>
    </defs>

    <!-- Bords extérieurs verts pleins -->
    <rect x="15" y="15" width="1092" height="764" fill="none" stroke="#2e7d32" stroke-width="5"/>
    <rect x="22" y="22" width="1078" height="750" fill="none" stroke="#2e7d32" stroke-width="1.5"/>

    <!-- Bande décorative tressée – haut -->
    <rect x="16" y="16"  width="1090" height="18" fill="url(#ph)"/>
    <!-- Bande décorative tressée – bas -->
    <rect x="16" y="760" width="1090" height="18" fill="url(#ph)"/>
    <!-- Bande décorative tressée – gauche -->
    <rect x="16" y="16"  width="18" height="762" fill="url(#pv)"/>
    <!-- Bande décorative tressée – droite -->
    <rect x="1088" y="16" width="18" height="762" fill="url(#pv)"/>

    <!-- Coins carrés verts -->
    <rect x="15"   y="15"   width="22" height="22" fill="#2e7d32"/>
    <rect x="1085" y="15"   width="22" height="22" fill="#2e7d32"/>
    <rect x="15"   y="757"  width="22" height="22" fill="#2e7d32"/>
    <rect x="1085" y="757"  width="22" height="22" fill="#2e7d32"/>

    <!-- Bordure intérieure fine -->
    <rect x="30" y="30" width="1062" height="734" fill="none" stroke="#2e7d32" stroke-width="1.2" stroke-dasharray="4 3"/>
  </svg>

  <div class="content">

    <!-- Référence -->
    <div class="ref-block">
      ${numCert}<br>
      <em>Vu l'Arrêté N° 41 578/2010/MP/SEETFP du Décembre 2010 portant agrément des filières du CNFPPSH</em>
    </div>

    <!-- Logos -->
    <div class="logos">
      <div class="logo-wrap">
        <img src="${LOGO_METFP}" alt="METFP" />
      </div>
      <div class="logo-wrap">
        <img src="${LOGO_MADAGASIKARA}" alt="Repoblikan'i Madagasikara" class="logo-center" />
        <div class="logo-sub">REPOBLIKAN'I MADAGASIKARA<br>Fitiavana · Tanindrazana · Fandrosoana</div>
      </div>
      <div class="logo-wrap">
        <img src="${LOGO_PIFTIC}" alt="PIFTIC" />
      </div>
    </div>

    <!-- Titre -->
    <div class="titre">Attestation de Formation</div>

    <!-- Corps -->
    <div class="corps">
      <div class="nom-apprenant">${c.apprenant_nom}</div>
      ${ligneNaissance ? `<div class="naissance">${ligneNaissance}</div>` : ''}
      <p class="suivi">
        a suivi une formation
        <span class="formation-titre" style="color: #1b5e20; font-weight: 900;"> «&nbsp;${intitule}&nbsp;» </span>
        <span class="formation-detail">(${contenu})</span>
      </p>
      <p class="session-line">${ligneSession}</p>
      ${mention ? `<div class="mention-line">Mention : ${mention}</div>` : ''}
      <p class="formule">En foi de quoi, le présent Attestation lui est délivré pour servir et valoir ce que de droit.</p>
    </div>

    <!-- Bas de page -->
    <div class="bas-page">
      <div class="sig">
        <div class="sig-titre">Le Directeur du CNFPPSH</div>
        <div class="sig-nom"></div>
      </div>
      <div class="date-lieu">${lieuDeliv} le, ${dateDelivrance}</div>
      <div class="sig">
        <div class="sig-titre">Le Coordonnateur du PIF TIC</div>
        <div class="sig-nom"></div>
      </div>
    </div>

  </div>
</div>
<script>window.onload = () => { window.print(); }<\/script>
</body>
</html>`

  const blob = new Blob([html], { type: 'text/html' })
  const url  = URL.createObjectURL(blob)
  window.open(url, '_blank')
  setTimeout(() => URL.revokeObjectURL(url), 30000)
}

function initiales(nom = '') {
  return nom.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase() || '?'
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' })
}

function mentionClass(m) {
  if (!m) return 'badge--info'
  if (m === 'Excellent' || m === 'Très Bien') return 'badge--success'
  if (m === 'Bien')       return 'badge--info'
  if (m === 'Assez Bien') return 'badge--warning'
  return 'badge--warning'
}

function exportCSV() {
  const rows = [
    ['N° Certificat', 'Apprenant', 'Formation', 'Niveau', 'Mention', 'Date'],
    ...certsFiltres.value.map((c) => [
      c.identifiant, c.apprenant_nom, c.formation_nom,
      c.formation_niveau, c.mention || '', formatDate(c.date_delivrance),
    ]),
  ]
  const csv  = rows.map((r) => r.map((v) => `"${v}"`).join(',')).join('\n')
  const link = document.createElement('a')
  link.href  = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv)
  link.download = 'certificats.csv'
  link.click()
}

onMounted(charger)
</script>

<style scoped>
.user-cell { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 38px; height: 38px; border-radius: 50%;
  background: linear-gradient(135deg, #4caf50, #2196f3);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 0.72rem; font-weight: 900; flex-shrink: 0; overflow: hidden;
  box-shadow: 0 2px 6px rgba(0,0,0,.15);
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
.user-name { font-weight: 600; }
.cert-id { font-family: monospace; font-size: 12px; background: var(--light); padding: 2px 6px; border-radius: 4px; }

/* Prévisualisation */
.preview-box { max-width: 680px; }
.cert-preview {
  border: 3px solid var(--primary); border-radius: 16px;
  padding: 32px 40px; margin-bottom: 20px;
  background: linear-gradient(135deg, #f0fff0, #ffffff);
  text-align: center;
}
.cert-header   { margin-bottom: 16px; }
.cert-logos-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}
.cert-logo-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 70px;
}
.cert-logo-center-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.cert-logo-label {
  font-size: 0.58rem;
  font-weight: 700;
  color: #2e7d32;
  letter-spacing: 1px;
  text-transform: uppercase;
}
.cert-org-subtitle {
  text-align: center;
  border-top: 1px solid #e0e0e0;
  padding-top: 8px;
}
.cert-org      { font-size: 1rem; font-weight: 900; color: var(--secondary); letter-spacing: 2px; }
.cert-sub      { font-size: 0.72rem; color: var(--gray); }
.cert-title    { font-size: 1.1rem; font-weight: 800; color: #1b5e20; letter-spacing: 3px; text-transform: uppercase; margin: 16px 0; border-top: 2px solid #2e7d32; border-bottom: 2px solid #2e7d32; padding: 8px 0; }
.cert-body     { margin: 16px 0; line-height: 2; }
.cert-name     { font-size: 1.5rem; font-weight: 900; color: var(--primary); text-transform: uppercase; margin: 8px 0; }
.cert-formation { font-size: 1.1rem; font-weight: 700; color: var(--secondary); margin: 4px 0; }
.cert-niveau   { margin: 8px 0; }
.cert-mention  { display: inline-block; background: var(--accent); color: #212529; padding: 4px 16px; border-radius: 20px; font-size: 0.9rem; margin: 8px 0; }
.cert-footer   { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 24px; flex-wrap: wrap; gap: 12px; }
.cert-date-lieu { font-size: 0.8rem; color: var(--gray); }
.cert-sign     { text-align: center; font-size: 0.8rem; color: var(--gray); }
.sign-line     { width: 120px; border-bottom: 1px solid var(--gray); margin: 0 auto 6px; }
.cert-id-badge { font-size: 0.7rem; font-family: monospace; background: var(--light); padding: 3px 8px; border-radius: 4px; }
.cert-qr       { width: 64px; height: 64px; margin: 12px auto 0; }
.preview-actions { display: flex; gap: 10px; justify-content: flex-end; }

@media print {
  .modal-overlay { background: white; position: static; }
  .modal-box { box-shadow: none; padding: 0; max-width: 100%; }
  .modal-head, .preview-actions { display: none; }
  .cert-preview { border-color: #000; page-break-inside: avoid; }
}
</style>