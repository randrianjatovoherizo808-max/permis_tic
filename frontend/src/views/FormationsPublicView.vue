<template>
  <div class="page">
    <div class="page-header">
      <h1>Nos Formations</h1>
      <p>Choisissez votre niveau et commencez votre parcours numérique</p>
    </div>

    <!-- Filtre niveau -->
    <div class="niveau-filter">
      <button
        v-for="n in ['A','B','C']" :key="n"
        class="niveau-btn"
        :class="['niv-'+n.toLowerCase(), { active: niveauSelec === n }]"
        @click="niveauSelec = n"
      >
        <span class="niv-dot"></span>
        Niveau {{ n }}
      </button>
    </div>

    <!-- Grille formations -->
    <div v-if="loading" class="loading">Chargement…</div>
    <div v-else class="formations-grid">
      <div
        v-for="f in formationsFiltrees"
        :key="f.id"
        class="formation-card"
        :class="'card-niv-' + f.niveau.toLowerCase()"
      >
        <!-- En-tête coloré -->
        <div class="card-header" :class="'bg-niv-' + f.niveau.toLowerCase()">
          <span class="card-niveau">🚀 NIVEAU {{ f.niveau }}</span>
          <span class="card-duree">⏱ {{ f.duree }}h</span>
        </div>

        <!-- Corps -->
        <div class="card-body">
          <h3 class="card-nom">{{ f.nom }}</h3>
          <p class="card-desc">{{ f.description || 'Formation professionnelle en informatique.' }}</p>

          <div class="card-meta">
            <span>👥 {{ f.places }} places</span>
            <span>⚖️ Coef. {{ f.coefficient || 1 }}</span>
          </div>

          <!-- Barre de remplissage -->
          <div class="places-bar">
            <div
              class="places-fill"
              :class="'fill-niv-' + f.niveau.toLowerCase()"
              :style="{ width: Math.min(100, ((f.places_prises || 0) / (f.places || 1)) * 100) + '%' }"
            ></div>
          </div>
        </div>

        <!-- Bouton -->
        <button
          class="btn-inscrire"
          :class="'btn-niv-' + f.niveau.toLowerCase()"
          @click="sinscrire(f)"
        >
          S'inscrire →
        </button>
      </div>

      <div v-if="formationsFiltrees.length === 0" class="empty">
        Aucune formation disponible pour le Niveau {{ niveauSelec }}.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router     = useRouter()
const formations = ref([])
const loading    = ref(true)
const niveauSelec = ref('A')

const formationsFiltrees = computed(() =>
  formations.value.filter(f => f.niveau === niveauSelec.value)
)

function sinscrire(formation) {
  // Passe formation_id en query param → RegisterView pré-remplit automatiquement
  router.push({ path: '/register', query: { formation: formation.id } })
}

onMounted(async () => {
  try {
    const { data } = await api.get('/formations/')
    formations.value = data.results || data
    // Auto-sélectionner le niveau du 1er cours si disponible
    if (formations.value.length > 0) {
      niveauSelec.value = formations.value[0].niveau
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page { padding: 40px 30px; background: #f5f5f0; min-height: 100vh; }

.page-header { text-align: center; margin-bottom: 32px; }
.page-header h1 { font-size: 2.2rem; font-weight: 900; color: #1a3c34; }
.page-header p  { color: #666; font-size: 1rem; margin-top: 6px; }

/* Filtres niveau */
.niveau-filter { display: flex; justify-content: center; gap: 12px; margin-bottom: 32px; flex-wrap: wrap; }
.niveau-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 22px; border-radius: 30px;
  border: 2px solid #e0e0e0; background: white;
  font-weight: 700; font-size: 14px; cursor: pointer; transition: .2s;
  color: #555;
}
.niv-dot { width: 12px; height: 12px; border-radius: 50%; display: inline-block; }
.niv-a .niv-dot { background: #2196F3; }
.niv-b .niv-dot { background: #FF5722; }
.niv-c .niv-dot { background: #9C27B0; }
.niveau-btn.active { border-color: currentColor; }
.niv-a.active { color: #2196F3; background: #e3f2fd; border-color: #2196F3; }
.niv-b.active { color: #FF5722; background: #fbe9e7; border-color: #FF5722; }
.niv-c.active { color: #9C27B0; background: #f3e5f5; border-color: #9C27B0; }

/* Grille */
.formations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto;
}

/* Carte */
.formation-card {
  background: white; border-radius: 20px;
  overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  display: flex; flex-direction: column;
  transition: transform .2s, box-shadow .2s;
}
.formation-card:hover { transform: translateY(-4px); box-shadow: 0 8px 28px rgba(0,0,0,0.13); }

/* En-tête coloré */
.card-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 18px; color: white; font-weight: 800;
}
.bg-niv-a { background: #2196F3; }
.bg-niv-b { background: #FF5722; }
.bg-niv-c { background: #9C27B0; }
.card-niveau { font-size: 13px; letter-spacing: 1px; }
.card-duree  { font-size: 12px; background: rgba(255,255,255,0.25); padding: 3px 10px; border-radius: 20px; }

/* Corps */
.card-body { padding: 18px 18px 12px; flex: 1; }
.card-nom  { font-size: 1.1rem; font-weight: 800; color: #1a1a1a; margin-bottom: 6px; }
.card-desc { font-size: 12.5px; color: #777; line-height: 1.5; margin-bottom: 12px; }
.card-meta { display: flex; gap: 12px; font-size: 12px; color: #555; margin-bottom: 10px; }

/* Barre places */
.places-bar  { height: 4px; background: #eee; border-radius: 4px; overflow: hidden; }
.places-fill { height: 100%; border-radius: 4px; transition: width .4s; }
.fill-niv-a  { background: #2196F3; }
.fill-niv-b  { background: #FF5722; }
.fill-niv-c  { background: #9C27B0; }

/* Bouton */
.btn-inscrire {
  margin: 12px 18px 18px; padding: 13px;
  border: none; border-radius: 12px; cursor: pointer;
  font-weight: 800; font-size: 14px; color: white;
  transition: opacity .2s; width: calc(100% - 36px);
}
.btn-inscrire:hover { opacity: .88; }
.btn-niv-a { background: #2196F3; }
.btn-niv-b { background: #FF5722; }
.btn-niv-c { background: #9C27B0; }

.loading { text-align: center; padding: 40px; color: #888; }
.empty   { text-align: center; padding: 40px; color: #aaa; grid-column: 1/-1; }

@media (max-width: 600px) {
  .page { padding: 24px 14px; }
  .page-header h1 { font-size: 1.6rem; }
  .niveau-filter { gap: 8px; }
  .niveau-btn { padding: 8px 16px; font-size: 13px; }
  .formations-grid { grid-template-columns: 1fr; gap: 16px; }
}
</style>