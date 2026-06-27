<template>
  <div class="home">

    <!-- ══ TOPBAR (contacts) ══ -->
    <div class="topbar">
      <div class="topbar-inner">
        <div class="topbar-left">
          <span>📞 {{ p.telephone }}</span>
          <span>✉️ {{ p.email }}</span>
        </div>
        <div class="topbar-right">
          <!-- Sélecteur de langue -->
          <LangSwitcher variant="light" />
          <!-- Login -->
          <button class="topbar-btn-connexion" @click="goLogin">{{ t.login }}</button>
        </div>
      </div>
    </div>

    <!-- ══ HEADER PRINCIPAL ══ -->
    <header class="main-header">
      <div class="header-inner">

        <!-- Logo -->
        <div class="logo" @click="$router.push('/')" style="cursor:pointer;">
          <div class="logo-wrap">
            <img :src="p.photo_url || '/logo.png'" alt="logo" class="logo-img" @error="(e) => e.target.src='/logo.png'" />
            <span class="logo-ring r1"></span>
            <span class="logo-ring r2"></span>
          </div>
          <div class="logo-badge">
            <span class="badge-p">P</span>
            <div class="badge-main">
              <div class="badge-top">
                <span class="badge-if">IF</span>
                <span class="badge-tic">TI</span>
              </div>
              <div class="badge-bottom">CNFPPS</div>
            </div>
            <span class="badge-c">C</span>
          </div>
        </div>

        <!-- Titre central -->
        <div class="header-center">
          <h1 class="site-title">{{ p.slogan }}</h1>
        </div>

        <!-- Actions -->
        <div class="header-actions">
          <div class="wa-display">
            <span class="wa-label">{{ p.whatsapp_nom || 'WhatsApp' }}</span>
            <a :href="`https://wa.me/${p.whatsapp?.replace(/[\s+]/g,'') || '261389839798'}`"
               class="wa-num" target="_blank" rel="noopener">
              {{ p.whatsapp || '0389839798' }}
            </a>
          </div>
          <button class="btn-register" @click="$router.push('/register')">
            {{ t.sinscrire }}
          </button>
        </div>

        <!-- Burger mobile -->
        <button class="burger" @click="menuOpen = !menuOpen">☰</button>
      </div>
    </header>

    <!-- ══ NAVIGATION ══ -->
    <nav class="main-nav" :class="{ open: menuOpen }">
      <div class="nav-inner">
        <button
          v-for="item in navItems" :key="item.key"
          class="nav-link"
          :class="{ active: activeNav === item.key }"
          @click="handleNav(item)"
        >
          {{ item.label }}
        </button>
      </div>
    </nav>

    <!-- ══ HERO ══ -->
    <section class="hero" v-show="activeNav === 'accueil'">
      <div class="hero-content">
        <div class="hero-badge">{{ t.badge }}</div>
        <h2 class="hero-title">{{ t.heroTitle1 }}<br><span class="hero-accent">{{ t.heroAccent }}</span></h2>
        <p class="hero-desc">{{ t.heroDesc }}</p>
        <button class="btn-cta" @click="handleNav(navItems[1])">{{ t.commencerBtn }}</button>
      </div>

      <!-- Stats -->
      <div class="stats-band">
        <div class="stat-item" v-for="s in statsItems" :key="s.label">
          <div class="stat-icon">{{ s.icon }}</div>
          <div class="stat-num">{{ s.value }}</div>
          <div class="stat-lbl">{{ s.label }}</div>
        </div>
      </div>
    </section>

    <!-- ══ SECTION ACCUEIL : 3 CARTES NIVEAU ══ -->
    <section class="niveau-showcase" v-show="activeNav === 'accueil'">
      <div class="ns-wrap">
        <div class="ns-header">
          <span class="ns-badge">🎯 {{ t.nos3niveaux }}</span>
          <h2 class="ns-title">{{ t.nsTitre1 }}<br><span class="ns-accent">{{ t.nsTitre2 }}</span></h2>
          <p class="ns-sub">{{ t.nsSub }}</p>
        </div>

        <div class="niveau-cards-grid">

          <!-- ── Niveau A ── -->
          <div class="nv-card nv-a" @mouseenter="hovered = 'A'" @mouseleave="hovered = null" :class="{ glow: hovered === 'A' }">
            <div class="nv-card-top">
              <div class="nv-icon-ring nv-ring-a">
                <span class="nv-icon">💻</span>
              </div>
              <div>
                <div class="nv-label">{{ niveauTextes.a.titre }}</div>
                <div class="nv-sublabel">{{ niveauTextes.a.sous }}</div>
              </div>
            </div>
            <div class="nv-anim-box">
              <transition name="textslide" mode="out-in">
                <div class="nv-anim-text" :key="tickers.A">
                  <span class="nv-anim-icon">{{ nivoA[tickers.A].icon }}</span>
                  <span class="nv-anim-name">{{ nivoA[tickers.A].name }}</span>
                </div>
              </transition>
            </div>
            <div class="nv-dots">
              <span v-for="(_, i) in nivoA" :key="i" class="nv-dot" :class="{ active: tickers.A === i }"></span>
            </div>
            <div class="nv-desc">{{ niveauTextes.a.desc }}</div>
            <button class="nv-btn nv-btn-a" @click="handleNav(navItems[1])">{{ t.decouvrir }}</button>
          </div>

          <!-- ── Niveau B ── -->
          <div class="nv-card nv-b" @mouseenter="hovered = 'B'" @mouseleave="hovered = null" :class="{ glow: hovered === 'B' }">
            <div class="nv-card-top">
              <div class="nv-icon-ring nv-ring-b">
                <span class="nv-icon">🎨</span>
              </div>
              <div>
                <div class="nv-label">{{ niveauTextes.b.titre }}</div>
                <div class="nv-sublabel">{{ niveauTextes.b.sous }}</div>
              </div>
            </div>
            <div class="nv-anim-box">
              <transition name="textslide" mode="out-in">
                <div class="nv-anim-text" :key="tickers.B">
                  <span class="nv-anim-icon">{{ nivoB[tickers.B].icon }}</span>
                  <span class="nv-anim-name">{{ nivoB[tickers.B].name }}</span>
                </div>
              </transition>
            </div>
            <div class="nv-dots">
              <span v-for="(_, i) in nivoB" :key="i" class="nv-dot" :class="{ active: tickers.B === i }"></span>
            </div>
            <div class="nv-desc">{{ niveauTextes.b.desc }}</div>
            <button class="nv-btn nv-btn-b" @click="handleNav(navItems[1])">{{ t.decouvrir }}</button>
          </div>

          <!-- ── Niveau C ── -->
          <div class="nv-card nv-c" @mouseenter="hovered = 'C'" @mouseleave="hovered = null" :class="{ glow: hovered === 'C' }">
            <div class="nv-card-top">
              <div class="nv-icon-ring nv-ring-c">
                <span class="nv-icon">🚀</span>
              </div>
              <div>
                <div class="nv-label">{{ niveauTextes.c.titre }}</div>
                <div class="nv-sublabel">{{ niveauTextes.c.sous }}</div>
              </div>
            </div>
            <div class="nv-anim-box">
              <transition name="textslide" mode="out-in">
                <div class="nv-anim-text" :key="tickers.C">
                  <span class="nv-anim-icon">{{ nivoC[tickers.C].icon }}</span>
                  <span class="nv-anim-name">{{ nivoC[tickers.C].name }}</span>
                </div>
              </transition>
            </div>
            <div class="nv-dots">
              <span v-for="(_, i) in nivoC" :key="i" class="nv-dot" :class="{ active: tickers.C === i }"></span>
            </div>
            <div class="nv-desc">{{ niveauTextes.c.desc }}</div>
            <button class="nv-btn nv-btn-c" @click="handleNav(navItems[1])">{{ t.decouvrir }}</button>
          </div>

        </div>
      </div>
    </section>

    <!-- ══ FORMATIONS ══ (visible seulement si nav = formations) -->
    <section id="formations-section" class="formations-section" v-show="activeNav === 'formations'">
      <div class="section-wrap">

        <div class="section-header">
          <h2 class="section-title">{{ t.nosFormations }}</h2>
          <p class="section-sub">{{ t.choixNiveau }}</p>
        </div>

        <!-- Filtres niveau -->
        <div class="niveau-tabs">
          <button
            v-for="n in niveaux" :key="n.value"
            class="niveau-tab"
            :class="['tab-' + n.value.toLowerCase(), { active: niveauActif === n.value }]"
            @click="niveauActif = n.value"
          >
            <span class="tab-icon">{{ n.icon }}</span>
            <span>{{ n.label }}</span>
          </button>
        </div>

        <!-- Grille -->
        <div v-if="loading" class="loading-state">
          <div class="dots">
            <span></span><span></span><span></span>
          </div>
          <p>{{ t.chargement }}</p>
        </div>

        <div v-else class="formations-grid">
          <div
            v-for="f in formationsFiltrees" :key="f.id"
            class="formation-card"
            :class="'card-' + f.niveau.toLowerCase()"
          >
            <!-- Bande supérieure -->
            <div class="card-band" :class="'band-' + f.niveau.toLowerCase()">
              <div class="band-left">
                <span class="band-icon">{{ niveauIcon(f.niveau) }}</span>
                <span class="band-label">{{ t.niveau }} {{ f.niveau }}</span>
              </div>
              <span class="band-duree">⏱ {{ f.duree }}h</span>
            </div>

            <div class="card-body">
              <h3 class="card-title">{{ f.nom }}</h3>
              <p class="card-desc">{{ f.description || t.descDefault }}</p>

              <!-- Méta -->
              <div class="card-meta">
                <div class="meta-pill">
                  <span>👥</span>
                  <span>{{ f.places }} {{ t.places }}</span>
                </div>
                <div class="meta-pill" v-if="f.coefficient">
                  <span>⚖️</span>
                  <span>Coef. {{ f.coefficient }}</span>
                </div>
              </div>

              <!-- Barre de capacité -->
              <div class="cap-bar-wrap">
                <div class="cap-bar" :class="'cap-' + f.niveau.toLowerCase()"></div>
              </div>

              <button class="btn-inscr" :class="'btn-' + f.niveau.toLowerCase()"
                      @click="$router.push('/register')">
                {{ t.sinscrireBtn }}
              </button>
            </div>
          </div>

          <div v-if="formationsFiltrees.length === 0" class="empty-formations">
            <span>📭</span>
            <p>{{ t.aucuneFormation }}</p>
          </div>
        </div>
      </div>
    </section>



    <!-- ══ CTA FINAL ══ -->
    <section class="cta-section">
      <div class="cta-inner">
        <div class="cta-text">
          <h2>{{ t.ctaTitre }}</h2>
          <p>{{ t.ctaDesc }}</p>
        </div>

      </div>
    </section>

    <!-- ══ FOOTER ══ -->
    <footer class="footer">
      <div class="footer-inner">
        <div class="footer-logo">
          <img :src="p.photo_url || '/logo.png'" alt="logo" style="height:36px;object-fit:contain;" @error="(e) => e.target.src='/logo.png'" />
          <div>
            <div class="footer-name">{{ p.nom }}</div>
            <div class="footer-sub">{{ t.footerTexte }}</div>
          </div>
        </div>
        <div class="footer-links">
          <span v-if="p.adresse">📍 {{ p.adresse }}</span>
          <span v-if="p.telephone">📞 {{ p.telephone }}</span>
          <span v-if="p.email">✉️ {{ p.email }}</span>
          <a v-if="p.facebook" :href="p.facebook" target="_blank" rel="noopener" style="color:inherit;">📘 Facebook</a>
        </div>
        <div class="footer-copy">
          © {{ new Date().getFullYear() }} {{ p.nom }} — {{ t.droits }}
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useLangStore } from '../store/lang'
import { useParametresStore } from '../store/parametres'
import { storeToRefs } from 'pinia'
import api from '../services/api'
import LangSwitcher from '../components/LangSwitcher.vue'

const router      = useRouter()
const auth        = useAuthStore()
const langStore   = useLangStore()

// storeToRefs garantit la réactivité dans le template
const { langActif, t } = storeToRefs(langStore)
const safeT    = computed(() => t.value || {})

const loading     = ref(true)
const formations  = ref([])
const niveauActif = ref('A')
const menuOpen    = ref(false)
const activeNav   = ref('accueil')
const hovered     = ref(null)

// ── Contenu animé des 3 cartes niveau ────────────────────────────────────────
// Données des niveaux — chargées depuis l'API (modifiables dans l'admin)
const nivoA = ref([
  { name: 'Word',        icon: '📝' },
  { name: 'Excel',       icon: '📊' },
  { name: 'PowerPoint',  icon: '📽️' },
])
const nivoB = ref([
  { name: 'Photoshop',   icon: '🖼️' },
  { name: 'Illustrator', icon: '✏️' },
  { name: 'UI/UX Design',icon: '🎨' },
])
const nivoC = ref([
  { name: 'React',         icon: '⚛️' },
  { name: 'Laravel',       icon: '🔴' },
  { name: 'Cybersécurité', icon: '🔐' },
])
// Textes des niveaux depuis l'API
const niveauTextes = ref({
  a: { titre: 'Niveau A', sous: 'Débutant',       desc: 'Maîtrisez les outils bureautiques essentiels.' },
  b: { titre: 'Niveau B', sous: 'Intermédiaire',   desc: 'Explorez le design graphique professionnel.' },
  c: { titre: 'Niveau C', sous: 'Avancé',          desc: 'Devenez développeur ou expert cybersécurité.' },
})

const tickers = ref({ A: 0, B: 0, C: 0 })
let tickerInterval = null

const stats = ref({ formations: 0, apprenants: 0, formateurs: 0, reussite: 0 })

// ── Paramètres dynamiques (store partagé) ───────────────────────────────────
const _pStore = useParametresStore()
const p       = _pStore.p

async function chargerParametres() {
  await _pStore.charger()
}

const statsItems = computed(() => [
  { value: stats.value.formations,            label: t.value.statFormations, icon: '📘' },
  { value: stats.value.apprenants,            label: t.value.statApprenants, icon: '🎓' },
  { value: stats.value.formateurs,            label: t.value.statFormateurs, icon: '👨‍🏫' },
  { value: (stats.value.reussite || 0) + '%', label: t.value.statReussite,   icon: '🏆' },
])

const niveaux = computed(() => [
  { value: 'A', label: t.value.niveauA, icon: '🔵' },
  { value: 'B', label: t.value.niveauB, icon: '🟠' },
  { value: 'C', label: t.value.niveauC, icon: '🟣' },
])



const navItems = computed(() => [
  { key: 'accueil',    label: safeT.value.accueil || '🏠 ACCUEIL',    action: () => { window.scrollTo({ top: 0, behavior: 'smooth' }) } },
  { key: 'formations', label: safeT.value.formations || '📘 NOS FORMATIONS',  action: scrollFormations },
  { key: 'apprenant',  label: safeT.value.apprenant || '🎓 ESPACE APPRENANT',   action: goApprenant },
])

function handleNav(item) {
  activeNav.value = item.key
  menuOpen.value  = false
  item.action()
}

function scrollFormations() {
  document.getElementById('formations-section')?.scrollIntoView({ behavior: 'smooth' })
}
function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}

const formationsFiltrees = computed(() =>
  formations.value.filter(f => f.niveau === niveauActif.value)
)

function niveauIcon(niveau) {
  return { A: '💻', B: '🎨', C: '🚀' }[niveau] || '📘'
}

function goApprenant() {
  if (auth.user?.role === 'etudiant') router.push('/espace-apprenant')
  else router.push('/login')
}
function goLogin() {
  if (auth.isAuthenticated) {
    if (auth.user?.role === 'etudiant') router.push('/espace-apprenant')
    else router.push('/admin')
  } else {
    router.push('/login')
  }
}

async function charger() {
  try {
    const { data } = await api.get('/formations/')
    formations.value = data.results || data
    stats.value.formations = formations.value.length
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function chargerStats() {
  try {
    // Charger les paramètres (niveaux modifiables depuis admin)
    const { data: pData } = await api.get('/parametres/').catch(() => ({ data: {} }))
    if (pData.niveau_a_items?.length) nivoA.value = pData.niveau_a_items
    if (pData.niveau_b_items?.length) nivoB.value = pData.niveau_b_items
    if (pData.niveau_c_items?.length) nivoC.value = pData.niveau_c_items
    if (pData.niveau_a_titre) niveauTextes.value.a = { titre: pData.niveau_a_titre, sous: pData.niveau_a_sous, desc: pData.niveau_a_desc }
    if (pData.niveau_b_titre) niveauTextes.value.b = { titre: pData.niveau_b_titre, sous: pData.niveau_b_sous, desc: pData.niveau_b_desc }
    if (pData.niveau_c_titre) niveauTextes.value.c = { titre: pData.niveau_c_titre, sous: pData.niveau_c_sous, desc: pData.niveau_c_desc }

    const { data } = await api.get('/stats/')
    // Animer les chiffres qui changent
    const keys = ['formations', 'apprenants', 'formateurs', 'reussite']
    keys.forEach(k => {
      if (data[k] !== undefined && data[k] !== stats.value[k]) {
        const els = document.querySelectorAll('.stat-num')
        els.forEach(el => {
          el.classList.remove('updated')
          void el.offsetWidth // reflow
          el.classList.add('updated')
        })
      }
    })
    Object.assign(stats.value, data)
  } catch {}
}

let statsInterval = null

onMounted(() => {
  charger()
  chargerStats()
  chargerParametres()
  statsInterval = setInterval(chargerStats, 60000)

  // Animation ticker : change toutes les 2.5 secondes avec décalage par niveau
  tickerInterval = setInterval(() => {
    tickers.value.A = (tickers.value.A + 1) % nivoA.value.length
  }, 2500)
  setTimeout(() => {
    setInterval(() => {
      tickers.value.B = (tickers.value.B + 1) % nivoB.value.length
    }, 2500)
  }, 833)
  setTimeout(() => {
    setInterval(() => {
      tickers.value.C = (tickers.value.C + 1) % nivoC.value.length
    }, 2500)
  }, 1666)
})

onUnmounted(() => {
  clearInterval(statsInterval)
  clearInterval(tickerInterval)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=DM+Sans:wght@400;500;600&display=swap');

* { box-sizing: border-box; }
.home { min-height: 100vh; display: flex; flex-direction: column; font-family: 'DM Sans', sans-serif; background: #f8faf8; }

/* ── Topbar ── */
.topbar { background: #2e7d32; color: rgba(255,255,255,.9); font-size: 13px; padding: 7px 0; }
.topbar-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
.topbar-left  { display: flex; gap: 20px; }
.topbar-right { display: flex; gap: 10px; }
.topbar-btn { background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.3); color: white; padding: 4px 14px; border-radius: 20px; cursor: pointer; font-size: 12px; font-weight: 600; transition: .2s; }
.topbar-btn:hover { background: rgba(255,255,255,.22); }

.topbar-btn-connexion { background: white; color: #1b5e20; border: none; padding: 6px 18px; border-radius: 20px; cursor: pointer; font-size: 12px; font-weight: 700; transition: .2s; }
.topbar-btn-connexion:hover { background: #e8f5e9; transform: translateY(-1px); }
.topbar-btn-register { background: transparent; color: white; border: 2px solid rgba(255,255,255,.8); padding: 5px 16px; border-radius: 20px; cursor: pointer; font-size: 12px; font-weight: 700; transition: .2s; }
.topbar-btn-register:hover { background: rgba(255,255,255,.15); }
.topbar-auth { display: flex; flex-direction: column; align-items: center; gap: 3px; }
.topbar-btn-seconnecter { background: none; border: none; color: rgba(255,255,255,.7); font-size: 11px; cursor: pointer; padding: 0; transition: .2s; }
.topbar-btn-seconnecter:hover { color: white; text-decoration: underline; }

/* ── Header ── */
.main-header { background: #fff; border-bottom: 2px solid #c8e6c9; padding: 14px 0; box-shadow: 0 2px 12px rgba(0,0,0,.06); }
.header-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 16px; }

.logo { display: flex; align-items: center; gap: 10px; }
.logo-wrap { position: relative; width: 52px; height: 52px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.logo-img { width: 46px; height: 46px; object-fit: contain; animation: logoBounce 3s ease-in-out infinite; position: relative; z-index: 2; }
.logo-ring { position: absolute; inset: 0; border-radius: 50%; border: 2px solid rgba(76,175,80,.4); animation: ringPulse 3s ease-out infinite; }
.logo-ring.r2 { animation-delay: 1s; }
@keyframes logoBounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
@keyframes ringPulse { 0%{transform:scale(1);opacity:.7} 100%{transform:scale(2.2);opacity:0} }
.logo-badge { display: flex; align-items: stretch; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.18); height: 46px; }
.badge-p { background: #fff; color: #e53935; font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 900; width: 34px; display: flex; align-items: center; justify-content: center; border-right: 2px solid #e53935; }
.badge-main { background: #2e7d32; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 0 10px; gap: 1px; }
.badge-top { display: flex; align-items: baseline; gap: 3px; }
.badge-if { color: #ff5252; font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 900; letter-spacing: 1px; }
.badge-tic { color: #69f0ae; font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 900; letter-spacing: 1px; }
.badge-bottom { color: rgba(255,255,255,.85); font-size: .55rem; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase; }
.badge-c { background: #1b5e20; color: #69f0ae; font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 900; width: 34px; display: flex; align-items: center; justify-content: center; border-left: 1px solid rgba(255,255,255,.2); line-height: 1; }

.header-center { text-align: center; }
.site-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #333; margin: 0; }

.header-actions { display: flex; align-items: center; gap: 16px; justify-content: flex-end; }
.wa-display { text-align: right; }
.btn-register { background: #2e7d32; color: white; border: none; padding: 10px 22px; border-radius: 25px; font-weight: 700; font-size: 14px; cursor: pointer; transition: .2s; white-space: nowrap; }
.btn-register:hover { background: #1b5e20; transform: translateY(-1px); box-shadow: 0 6px 16px rgba(46,125,50,.3); }
.wa-display { text-align: right; }
.wa-label { display: block; font-size: 11px; color: #888; font-weight: 400; }
.wa-num   { display: block; font-size: 1.05rem; font-weight: 900; color: #2e7d32;
            text-decoration: none; letter-spacing: .3px; }

.burger { display: none; background: none; border: none; font-size: 1.6rem; cursor: pointer; color: #333; }

/* ── Nav ── */
.main-nav { background: #1b5e20; }
.nav-inner { max-width: 1200px; margin: 0 auto; padding: 0 24px; display: flex; gap: 2px; overflow-x: auto; }
.nav-link { background: none; border: none; color: rgba(255,255,255,.8); padding: 14px 20px; font-size: .82rem; font-weight: 700; letter-spacing: .8px; cursor: pointer; transition: .2s; white-space: nowrap; border-bottom: 3px solid transparent; }
.nav-link:hover  { color: white; background: rgba(255,255,255,.08); }
.nav-link.active { color: #F9C514; border-bottom-color: #F9C514; background: rgba(255,255,255,.08); }

/* ── Hero ── */
.hero { background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 45%, #F9C514 100%); color: white; padding: 64px 24px 0; }
.hero-content { max-width: 700px; margin: 0 auto; text-align: center; }
.hero-badge { display: inline-block; background: rgba(249,197,20,.2); border: 1px solid rgba(249,197,20,.5); color: #F9C514; padding: 6px 18px; border-radius: 20px; font-size: 13px; font-weight: 700; margin-bottom: 20px; letter-spacing: .5px; }
.hero-title { font-family: 'Syne', sans-serif; font-size: clamp(2rem, 5vw, 3.2rem); font-weight: 900; margin: 0 0 16px; line-height: 1.1; }
.hero-accent { color: #F9C514; }
.hero-desc { font-size: 1rem; color: rgba(255,255,255,.8); line-height: 1.7; margin-bottom: 32px; max-width: 560px; margin-left: auto; margin-right: auto; }
.hero-cta { display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; margin-bottom: 48px; }
.btn-hero-primary { background: #F9C514; color: #1b5e20; border: none; padding: 14px 32px; border-radius: 30px; font-weight: 800; font-size: .95rem; cursor: pointer; transition: .2s; box-shadow: 0 6px 20px rgba(249,197,20,.4); }
.btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(249,197,20,.5); }
.btn-hero-outline { background: transparent; color: white; border: 2px solid rgba(255,255,255,.6); padding: 14px 32px; border-radius: 30px; font-weight: 700; font-size: .95rem; cursor: pointer; transition: .2s; }
.btn-hero-outline:hover { background: rgba(255,255,255,.1); border-color: white; }

/* Stats band */
.stats-band { background: rgba(0,0,0,.2); border-top: 1px solid rgba(255,255,255,.1); display: flex; justify-content: center; gap: 0; flex-wrap: wrap; margin: 0 -24px; }
.stat-item { padding: 20px 48px; text-align: center; border-right: 1px solid rgba(255,255,255,.1); }
.stat-item:last-child { border-right: none; }
.stat-icon { font-size: 1.2rem; margin-bottom: 4px; }
.stat-num { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 900; color: #F9C514; transition: transform .3s; }
.stat-lbl { font-size: .75rem; color: rgba(255,255,255,.7); text-transform: uppercase; letter-spacing: .8px; margin-top: 2px; }

/* ── Formations ── */
.formations-section { padding: 60px 0 80px; background: #f8faf8; }
.section-wrap { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.section-header { text-align: center; margin-bottom: 44px; }
.section-title { font-family: 'Syne', sans-serif; font-size: clamp(1.6rem,3vw,2.2rem); font-weight: 900; color: #1b5e20; margin: 0 0 10px; }
.section-sub { color: #888; font-size: .95rem; }

/* Niveau tabs */
.niveau-tabs { display: flex; justify-content: center; gap: 12px; margin-bottom: 40px; flex-wrap: wrap; }
.niveau-tab { display: flex; align-items: center; gap: 8px; padding: 12px 28px; border: 2px solid #e0e0e0; border-radius: 50px; background: white; font-weight: 700; font-size: .88rem; cursor: pointer; transition: .25s; color: #999; box-shadow: 0 2px 8px rgba(0,0,0,.06); }
.niveau-tab:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(0,0,0,.1); }
.niveau-tab.active.tab-a { border-color: #2196F3; background: linear-gradient(135deg,#e3f2fd,#bbdefb); color: #1565c0; box-shadow: 0 6px 18px rgba(33,150,243,.25); }
.niveau-tab.active.tab-b { border-color: #FF9800; background: linear-gradient(135deg,#fff8e1,#ffe0b2); color: #e65100; box-shadow: 0 6px 18px rgba(255,152,0,.25); }
.niveau-tab.active.tab-c { border-color: #9C27B0; background: linear-gradient(135deg,#f3e5f5,#e1bee7); color: #6a1b9a; box-shadow: 0 6px 18px rgba(156,39,176,.25); }
.tab-icon { font-size: 1rem; }

/* Grille formations */
/* ── Grille formations ─── */
.formations-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 24px; }

/* Carte */
.formation-card {
  background: white; border-radius: 22px; overflow: hidden;
  box-shadow: 0 2px 16px rgba(0,0,0,.07);
  transition: transform .3s cubic-bezier(.34,1.56,.64,1), box-shadow .3s;
  display: flex; flex-direction: column; border: 1.5px solid transparent;
}
.formation-card:hover { transform: translateY(-6px); box-shadow: 0 16px 40px rgba(0,0,0,.12); }
.card-a { border-color: rgba(30,136,229,.15); }
.card-b { border-color: rgba(239,108,0,.15); }
.card-c { border-color: rgba(142,36,170,.15); }

/* Bande colorée */
.card-band { display: flex; align-items: center; justify-content: space-between; padding: 14px 20px; }
.band-a { background: linear-gradient(120deg,#1e88e5,#1565c0); color: white; }
.band-b { background: linear-gradient(120deg,#ef6c00,#e64a19); color: white; }
.band-c { background: linear-gradient(120deg,#8e24aa,#6a1b9a); color: white; }
.band-left { display: flex; align-items: center; gap: 10px; }
.band-icon { font-size: 1.2rem; }
.band-label { font-size: .75rem; font-weight: 800; letter-spacing: .8px; text-transform: uppercase; }
.band-duree { font-size: .75rem; background: rgba(255,255,255,.22); backdrop-filter: blur(4px); border-radius: 20px; padding: 3px 11px; font-weight: 700; }

/* Corps */
.card-body { padding: 22px 22px 20px; display: flex; flex-direction: column; flex: 1; }
.card-title { font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 900; color: #1a1a2e; margin: 0 0 6px; text-transform: capitalize; }
.card-desc { font-size: .82rem; color: #9199a8; line-height: 1.65; margin-bottom: 16px; flex: 1; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* Méta pills */
.card-meta { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.meta-pill { display: inline-flex; align-items: center; gap: 5px; background: #f4f6fa; border-radius: 20px; padding: 4px 12px; font-size: .78rem; font-weight: 700; color: #555; }

/* Barre capacité */
.cap-bar-wrap { height: 4px; background: #f0f2f5; border-radius: 10px; margin-bottom: 18px; overflow: hidden; }
.cap-bar { height: 100%; border-radius: 10px; width: 60%; transition: width .6s ease; }
.cap-a { background: linear-gradient(90deg,#1e88e5,#64b5f6); }
.cap-b { background: linear-gradient(90deg,#ef6c00,#ffa726); }
.cap-c { background: linear-gradient(90deg,#8e24aa,#ce93d8); }

/* Bouton s'inscrire */
.btn-inscr { width: 100%; padding: 13px; border: none; border-radius: 14px; font-size: .9rem; font-weight: 800; cursor: pointer; transition: transform .2s, box-shadow .2s; letter-spacing: .3px; }
.btn-inscr:hover { transform: translateY(-2px); }
.btn-a { background: linear-gradient(135deg,#1e88e5,#1565c0); color: white; box-shadow: 0 6px 18px rgba(30,136,229,.3); }
.btn-b { background: linear-gradient(135deg,#ef6c00,#e64a19); color: white; box-shadow: 0 6px 18px rgba(239,108,0,.3); }
.btn-c { background: linear-gradient(135deg,#8e24aa,#6a1b9a); color: white; box-shadow: 0 6px 18px rgba(142,36,170,.3); }
.btn-a:hover { box-shadow: 0 10px 26px rgba(30,136,229,.45); }
.btn-b:hover { box-shadow: 0 10px 26px rgba(239,108,0,.45); }
.btn-c:hover { box-shadow: 0 10px 26px rgba(142,36,170,.45); }


.loading-state { text-align: center; padding: 60px 20px; color: #888; }
.dots { display: flex; justify-content: center; gap: 8px; margin-bottom: 14px; }
.dots span { width: 10px; height: 10px; border-radius: 50%; background: #2e7d32; animation: dotBounce 1.2s ease-in-out infinite; }
.dots span:nth-child(2) { animation-delay: .2s; } .dots span:nth-child(3) { animation-delay: .4s; }
@keyframes dotBounce { 0%,80%,100%{transform:scale(0)} 40%{transform:scale(1)} }
@keyframes statPulse { 0%{transform:scale(1)} 50%{transform:scale(1.08)} 100%{transform:scale(1)} }
.stat-num { animation: none; }
.stat-num.updated { animation: statPulse .4s ease; }

.empty-formations { grid-column: 1/-1; text-align: center; padding: 48px; color: #aaa; }
.empty-formations span { font-size: 3rem; display: block; margin-bottom: 12px; }



/* ── CTA ── */
.cta-section { background: linear-gradient(135deg, #F9C514, #f57f17); padding: 60px 24px; }
.cta-inner { max-width: 900px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; gap: 32px; flex-wrap: wrap; }
.cta-text h2 { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 900; color: #1b5e20; margin: 0 0 8px; }
.cta-text p  { color: rgba(27,94,32,.7); font-size: .95rem; margin: 0; }
.cta-buttons { display: flex; gap: 14px; flex-wrap: wrap; }
.btn-cta-primary { background: #1b5e20; color: white; border: none; padding: 13px 28px; border-radius: 25px; font-weight: 700; font-size: .9rem; cursor: pointer; transition: .2s; }
.btn-cta-primary:hover { background: #2e7d32; transform: translateY(-1px); }
.btn-cta-outline { background: transparent; color: #1b5e20; border: 2px solid #1b5e20; padding: 13px 28px; border-radius: 25px; font-weight: 700; font-size: .9rem; cursor: pointer; transition: .2s; }
.btn-cta-outline:hover { background: rgba(27,94,32,.08); }

/* ── Footer ── */
.footer { background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #F9C514 100%); color: rgba(255,255,255,.95); padding: 36px 24px; }
.footer-inner { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 16px; text-align: center; }
.footer-logo { display: flex; align-items: center; gap: 12px; }
.footer-name { font-family: 'Syne', sans-serif; font-weight: 900; color: white; font-size: 1.1rem; }
.footer-sub  { font-size: .7rem; opacity: .7; }
.footer-links { display: flex; gap: 24px; flex-wrap: wrap; justify-content: center; font-size: .85rem; }
.footer-copy  { font-size: .75rem; opacity: .5; margin-top: 8px; }

/* ── Responsive ── */
@media (max-width: 900px) {
  .header-inner { grid-template-columns: auto auto; }
  .niveaux-grid { grid-template-columns: 1fr; }
  .cta-inner { flex-direction: column; text-align: center; }
  .stat-item { padding: 16px 24px; }
}
@media (max-width: 600px) {
  /* Pas de menu burger - navigation complète visible comme sur PC */
  .burger { display: none !important; }
  .main-nav { display: block !important; }
  .nav-inner { flex-direction: row; flex-wrap: wrap; justify-content: center; }
  .nav-link { padding: 8px 12px; font-size: 12px; }
  .stats-band { display: grid; grid-template-columns: 1fr 1fr; }
  .stat-item { border-right: none; border-bottom: 1px solid rgba(255,255,255,.1); padding: 14px 20px; }
  .footer-links { flex-direction: column; gap: 8px; }
  .hero { padding: 40px 16px 60px; }
  .niveau-cards-grid { grid-template-columns: 1fr; max-width: 100%; }
  .nv-card { padding: 24px 20px; }
  .cta-inner { padding: 32px 16px; }
}

/* ══════════════════════════════════════════════════════════
   HERO CTA BUTTON
══════════════════════════════════════════════════════════ */
.btn-cta {
  display: inline-flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, #1b5e20, #F9C514);
  color: white; border: none; border-radius: 50px;
  padding: 16px 36px; font-size: 1rem; font-weight: 700;
  cursor: pointer; margin-top: 24px;
  box-shadow: 0 8px 24px rgba(27,94,32,.35);
  transition: transform .2s, box-shadow .2s;
}
.btn-cta:hover { transform: translateY(-3px); box-shadow: 0 14px 32px rgba(27,94,32,.45); }

/* ══════════════════════════════════════════════════════════
   SECTION SHOWCASE 3 NIVEAUX
══════════════════════════════════════════════════════════ */
.niveau-showcase {
  background: linear-gradient(160deg, #e8f5e9 0%, #fffde7 55%, #fff9c4 100%);
  padding: 80px 24px 100px;
}
.ns-wrap { max-width: 1100px; margin: 0 auto; }

.ns-header { text-align: center; margin-bottom: 56px; }
.ns-badge {
  display: inline-block; background: rgba(46,125,50,.1);
  color: #1b5e20; border-radius: 50px; padding: 8px 20px;
  font-size: 13px; font-weight: 700; letter-spacing: .5px; margin-bottom: 16px;
}
.ns-title {
  font-family: 'Syne', sans-serif; font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 900; color: #1a1a2e; line-height: 1.2; margin: 0 0 14px;
}
.ns-accent { color: #1b5e20; }
.ns-sub { color: #666; font-size: 1.05rem; margin: 0; }

/* ── Grid 3 cartes ── */
.niveau-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}
@media (max-width: 900px) { .niveau-cards-grid { grid-template-columns: 1fr; max-width: 420px; margin: 0 auto; } }

/* ── Carte commune ── */
.nv-card {
  background: white;
  border-radius: 24px;
  padding: 32px 28px 28px;
  box-shadow: 0 4px 20px rgba(0,0,0,.07);
  transition: transform .3s cubic-bezier(.34,1.56,.64,1), box-shadow .3s;
  position: relative; overflow: hidden; cursor: default;
}
.nv-card::before {
  content: ''; position: absolute; inset: 0;
  opacity: 0; transition: opacity .3s;
  pointer-events: none; border-radius: 24px;
}
.nv-card:hover { transform: translateY(-8px) scale(1.02); }

/* Glow par couleur */
.nv-card.nv-a:hover { box-shadow: 0 20px 50px rgba(30,100,200,.2); }
.nv-card.nv-b:hover { box-shadow: 0 20px 50px rgba(230,100,20,.2); }
.nv-card.nv-c:hover { box-shadow: 0 20px 50px rgba(120,40,180,.2); }

/* ── Header de carte ── */
.nv-card-top { display: flex; align-items: center; gap: 16px; margin-bottom: 28px; }
.nv-icon-ring {
  width: 56px; height: 56px; border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; flex-shrink: 0;
}
.nv-ring-a { background: linear-gradient(135deg, #e3f2fd, #bbdefb); }
.nv-ring-b { background: linear-gradient(135deg, #fff3e0, #ffe0b2); }
.nv-ring-c { background: linear-gradient(135deg, #f3e5f5, #e1bee7); }

.nv-label { font-size: 1.1rem; font-weight: 800; color: #1a1a2e; }
.nv-sublabel { font-size: .8rem; font-weight: 500; color: #999; margin-top: 2px; }

/* ── Zone animée ── */
.nv-anim-box {
  height: 72px; display: flex; align-items: center; justify-content: center;
  border-radius: 16px; margin-bottom: 16px; overflow: hidden;
}
.nv-a .nv-anim-box { background: linear-gradient(135deg, #e3f2fd 0%, #e8f5e9 100%); }
.nv-b .nv-anim-box { background: linear-gradient(135deg, #fff3e0 0%, #fce4ec 100%); }
.nv-c .nv-anim-box { background: linear-gradient(135deg, #f3e5f5 0%, #ede7f6 100%); }

.nv-anim-text { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.nv-anim-icon { font-size: 1.5rem; line-height: 1; }
.nv-anim-name { font-size: 1.1rem; font-weight: 800; letter-spacing: -.3px; }
.nv-a .nv-anim-name { color: #1565c0; }
.nv-b .nv-anim-name { color: #e65100; }
.nv-c .nv-anim-name { color: #6a1b9a; }

/* ── Dots indicateurs ── */
.nv-dots { display: flex; justify-content: center; gap: 6px; margin-bottom: 20px; }
.nv-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #ddd; transition: all .3s;
}
.nv-a .nv-dot.active { background: #1e88e5; transform: scale(1.4); }
.nv-b .nv-dot.active { background: #ef6c00; transform: scale(1.4); }
.nv-c .nv-dot.active { background: #8e24aa; transform: scale(1.4); }

/* ── Description ── */
.nv-desc { font-size: .88rem; color: #666; line-height: 1.6; margin-bottom: 24px; text-align: center; }

/* ── Bouton ── */
.nv-btn {
  width: 100%; padding: 13px; border: none; border-radius: 14px;
  font-size: .95rem; font-weight: 700; cursor: pointer;
  transition: transform .2s, box-shadow .2s; letter-spacing: .3px;
}
.nv-btn:hover { transform: translateY(-2px); }
.nv-btn-a { background: linear-gradient(135deg, #1e88e5, #1565c0); color: white; box-shadow: 0 6px 18px rgba(30,136,229,.3); }
.nv-btn-b { background: linear-gradient(135deg, #ef6c00, #e64a19); color: white; box-shadow: 0 6px 18px rgba(239,108,0,.3); }
.nv-btn-c { background: linear-gradient(135deg, #8e24aa, #6a1b9a); color: white; box-shadow: 0 6px 18px rgba(142,36,170,.3); }
.nv-btn-a:hover { box-shadow: 0 10px 26px rgba(30,136,229,.45); }
.nv-btn-b:hover { box-shadow: 0 10px 26px rgba(239,108,0,.45); }
.nv-btn-c:hover { box-shadow: 0 10px 26px rgba(142,36,170,.45); }

/* ── Transition texte slide ── */
.textslide-enter-active,
.textslide-leave-active { transition: all .45s cubic-bezier(.4,0,.2,1); }
.textslide-enter-from   { opacity: 0; transform: translateY(18px); }
.textslide-leave-to     { opacity: 0; transform: translateY(-18px); }
.textslide-enter-to,
.textslide-leave-from   { opacity: 1; transform: translateY(0); }

</style>