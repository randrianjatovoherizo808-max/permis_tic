import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useParametresStore = defineStore('parametres', () => {

  const p = ref({
    nom:          'PERMIS TIC',
    adresse:      'PIFTIC CNFPPSH — Ampandrianomby, Antananarivo',
    telephone:    '033 300 5845',
    email:        'contact@permistic.mg',
    photo_url:    '',
    whatsapp:     '0389839798',
    whatsapp_nom: 'Thierry – WhatsApp',
    slogan:       'Formation Numérique — Madagascar',
    description:  '',
    facebook:     '',
    footer_texte: 'Centre de Formation Professionnelle',
    niveau_a_titre: 'Niveau A', niveau_a_sous: 'Débutant',      niveau_a_desc: '', niveau_a_items: [],
    niveau_b_titre: 'Niveau B', niveau_b_sous: 'Intermédiaire', niveau_b_desc: '', niveau_b_items: [],
    niveau_c_titre: 'Niveau C', niveau_c_sous: 'Avancé',        niveau_c_desc: '', niveau_c_items: [],
  })

  const loaded = ref(false)

  // Valeurs BDD parasites à ignorer (remplacées par les defaults du store)
  const VALEURS_PARASITES = [
    'whatsapp disponible',
    'formation proffessionnelle a mada',
    'formation proffessionnelle numeric bureautic',
  ]

  function valeurValide(v) {
    if (v === undefined || v === null || v === '') return false
    if (typeof v === 'string' && VALEURS_PARASITES.includes(v.toLowerCase().trim())) return false
    return true
  }

  /** Charge les paramètres depuis l'API (appelé une seule fois) */
  async function charger() {
    if (loaded.value) return
    try {
      const { data } = await api.get('/parametres/')
      if (data) {
        Object.keys(p.value).forEach(k => {
          if (valeurValide(data[k])) {
            p.value[k] = data[k]
          }
        })
      }
      loaded.value = true
    } catch { /* silencieux, valeurs par défaut */ }
  }

  /** Sauvegarde les paramètres et met à jour le store immédiatement */
  async function sauvegarder(payload) {
    await api.patch('/parametres/', payload)
    // Mise à jour réactive immédiate — le header se met à jour sans rechargement
    Object.keys(payload).forEach(k => {
      if (k in p.value) p.value[k] = payload[k]
    })
  }

  return { p, loaded, charger, sauvegarder }
})