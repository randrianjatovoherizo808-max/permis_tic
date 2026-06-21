<template>
  <div class="admin-layout" :data-theme="theme">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar--open': sidebarOpen }">
      <div class="sidebar-header">
        <div class="admin-logo">
          <img src="/logo.png" alt="PIFTIC" class="admin-logo-img" />
        </div>
        <div class="admin-logo-text">
          <span class="admin-logo-title">PERMIS TIC</span>
          <span class="admin-logo-sub">Administration</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <RouterLink
          v-for="item in navItems" :key="item.name"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
          @click="sidebarOpen = false"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ initiales }}</div>
          <div>
            <div class="user-name">{{ auth.user?.prenom }} {{ auth.user?.nom }}</div>
            <div class="user-role">{{ auth.user?.role === 'admin' ? '🔐 Admin' : '👨‍🏫 Formateur' }}</div>
          </div>
        </div>
        <button class="btn-logout" @click="deconnexion">🚪 Déconnexion</button>
      </div>
    </aside>

    <!-- Overlay mobile -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="sidebarOpen = false"></div>

    <!-- Contenu principal -->
    <main class="admin-main">
      <!-- Topbar mobile -->
      <div class="topbar">
        <button class="burger" @click="sidebarOpen = !sidebarOpen">☰</button>
        <span class="topbar-title">🎓 PERMIS TIC</span>
        <div class="topbar-user">{{ auth.user?.prenom }}</div>
        <div class="notif-wrap" ref="notifRefMobile">
          <button class="notif-bell" @click="toggleNotif">
            🔔
            <span v-if="nbNotifs > 0" class="notif-badge">{{ nbNotifs }}</span>
          </button>
        </div>
        <button class="theme-toggle-mini" @click="applyTheme(theme === 'dark' ? 'light' : 'dark')">
          {{ theme === 'dark' ? '🌙' : '☀️' }}
        </button>
      </div>

      <!-- Header desktop avec toggle thème -->
      <div class="page-header">
        <div class="page-header-right">
          <!-- 🔔 Cloche notifications -->
          <div class="notif-wrap" ref="notifRef">
            <button class="notif-bell" @click="toggleNotif" :class="{ active: notifOpen }">
              🔔
              <span v-if="nbNotifs > 0" class="notif-badge">{{ nbNotifs }}</span>
            </button>
            <div v-if="notifOpen" class="notif-dropdown">
              <div class="notif-header">
                <span>🔔 Activité récente</span>
                <button class="notif-close" @click="notifOpen = false">✕</button>
              </div>
              <div v-if="notifLoading" class="notif-empty">Chargement…</div>
              <div v-else-if="notifItems.length === 0" class="notif-empty">Aucune notification.</div>
              <div v-else class="notif-list">
                <RouterLink
                  v-for="n in notifItems" :key="n.id"
                  to="/admin/inscriptions"
                  class="notif-item"
                  @click="notifOpen = false"
                >
                  <span class="notif-icon">{{ n.icon }}</span>
                  <div class="notif-body">
                    <span class="notif-msg">{{ n.message }}</span>
                    <span class="notif-date">{{ n.date }}</span>
                  </div>
                </RouterLink>
              </div>
              <RouterLink to="/admin/inscriptions" class="notif-footer" @click="notifOpen = false">
                Voir toutes les inscriptions →
              </RouterLink>
            </div>
          </div>
          <div class="theme-toggle-wrap">
            <button class="theme-toggle" @click="applyTheme(theme === 'dark' ? 'light' : 'dark')"
                    :title="theme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'">
              <span class="toggle-track" :class="{ dark: theme === 'dark' }">
                <span class="toggle-thumb">{{ theme === 'dark' ? '🌙' : '☀️' }}</span>
              </span>
              <span class="toggle-label">{{ theme === 'dark' ? 'Mode sombre' : 'Mode clair' }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="admin-content">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import api from '../services/api'

const router      = useRouter()
const auth        = useAuthStore()
const sidebarOpen = ref(false)
const theme       = ref(localStorage.getItem('theme') || 'light')

// ── Notifications ─────────────────────────────────────────────────────────
const notifOpen    = ref(false)
const notifLoading = ref(false)
const notifItems   = ref([])
const nbNotifs     = ref(0)
const notifRef     = ref(null)

function formatNotifDate(d) {
  if (!d) return ''
  const date = new Date(d)
  if (isNaN(date)) return ''
  return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

async function chargerNotifications() {
  notifLoading.value = true
  try {
    // Inscriptions en attente comme notifications principales
    const { data: iData } = await api.get('/inscriptions/', { params: { statut: 'en_attente' } })
    const inscriptions = iData.results || iData
    const inscNotifs = inscriptions.slice(0, 5).map(i => ({
      id: 'insc_' + i.id,
      icon: 'ℹ️',
      message: `${i.utilisateur_nom || 'Utilisateur'} — inscription ${i.niveau || ''} en attente`,
      date: formatNotifDate(i.created_at || i.date_inscription),
    }))

    // Notifications API si disponible
    let apiNotifs = []
    try {
      const { data: notifs } = await api.get('/notifications/')
      apiNotifs = (notifs.results || notifs).slice(0, 5).map(n => ({
        id: n.id,
        icon: n.type === 'success' ? '✅' : n.type === 'warning' ? '⚠️' : 'ℹ️',
        message: n.message,
        date: formatNotifDate(n.created_at),
      }))
    } catch {}

    // Fusionner et déduire le badge
    notifItems.value = [...inscNotifs, ...apiNotifs].slice(0, 8)
    nbNotifs.value   = inscriptions.length
  } catch {}
  finally { notifLoading.value = false }
}

async function toggleNotif() {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) await chargerNotifications()
}

// Fermer en cliquant dehors
function handleClickOutside(e) {
  if (notifRef.value && !notifRef.value.contains(e.target)) {
    notifOpen.value = false
  }
}

// Applique le thème au démarrage et à chaque changement
function applyTheme(t) {
  theme.value = t
  localStorage.setItem('theme', t)
  if (t === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
}

onMounted(() => {
  applyTheme(theme.value)
  chargerNotifications()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Écoute les changements depuis ParametresView
window.addEventListener('storage', (e) => {
  if (e.key === 'theme') applyTheme(e.newValue || 'light')
})

const initiales = computed(() => {
  const u = auth.user
  return ((u?.prenom?.[0] || '') + (u?.nom?.[0] || '')).toUpperCase() || 'A'
})

// ── "Page Site" supprimé ──
const navItems = [
  { path: '/admin',              name: 'dashboard',    icon: '📊', label: 'Dashboard' },
  { path: '/admin/inscriptions', name: 'inscriptions', icon: '📋', label: 'Inscriptions' },
  { path: '/admin/apprenants',   name: 'apprenants',   icon: '🎓', label: 'Apprenants' },
  { path: '/admin/formateurs',   name: 'formateurs',   icon: '👨‍🏫', label: 'Formateurs' },
  { path: '/admin/formations',   name: 'formations',   icon: '📘', label: 'Formations' },
  { path: '/admin/lecons',       name: 'lecons',       icon: '📖', label: 'Leçons' },
  { path: '/admin/notes',        name: 'notes',        icon: '📝', label: 'Notes' },
  { path: '/admin/certificats',  name: 'certificats',  icon: '📜', label: 'Certificats' },
  { path: '/admin/calendrier',   name: 'calendrier',   icon: '📅', label: 'Calendrier' },
  { path: '/admin/parametres',   name: 'parametres',   icon: '⚙️', label: 'Paramètres' },
]

function deconnexion() {
  auth.logout()
  router.push('/')
}
</script>

<style scoped>
/* ── Variables thème clair (palette teal ABM) ── */
.admin-layout {
  display: flex; min-height: 100vh;
  --sidebar-bg:    linear-gradient(180deg, #0097A7 0%, #F9C514 100%);
  --sidebar-text:  rgba(255,255,255,0.9);
  --sidebar-hover: rgba(255,255,255,0.15);
  --sidebar-active:rgba(255,255,255,0.25);
  --main-bg:       #f4f6f8;
  --card-bg:       #ffffff;
  --text:          #222;
  --border:        #e5e7eb;
}

/* ── Mode sombre ── */
.admin-layout[data-theme="dark"],
:root[data-theme="dark"] .admin-layout {
  --sidebar-bg:    linear-gradient(180deg, #006064 0%, #b8950a 100%);
  --main-bg:       #111827;
  --card-bg:       #1f2937;
  --text:          #f9fafb;
  --border:        #374151;
}

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  background: var(--sidebar-bg);
  color: white;
  display: flex; flex-direction: column;
  position: fixed; top: 0; left: 0; height: 100vh;
  z-index: 200;
  transition: transform 0.3s ease;
  box-shadow: 4px 0 20px rgba(0,0,0,0.12);
}

.sidebar-header {
  display: flex; align-items: center; gap: 12px;
  padding: 20px 18px;
  border-bottom: 1px solid rgba(255,255,255,0.15);
}

/* ── Animation logo ── */
.admin-logo {
  background: rgba(255,255,255,0.18);
  border-radius: 14px;
  width: 50px; height: 50px;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  transition: transform 0.4s cubic-bezier(.34,1.56,.64,1),
              box-shadow 0.3s ease,
              background 0.3s ease;
  animation: logoFloat 3s ease-in-out infinite;
}
.admin-logo:hover {
  transform: scale(1.12) rotate(-4deg);
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  background: rgba(255,255,255,0.28);
}
.admin-logo-img {
  width: 40px; height: 40px;
  object-fit: contain;
  transition: transform 0.4s ease;
}
.admin-logo:hover .admin-logo-img {
  transform: scale(1.08);
}

@keyframes logoFloat {
  0%,100% { transform: translateY(0);    }
  50%      { transform: translateY(-4px); }
}

.admin-logo-title {
  font-weight: 900; font-size: 0.95rem;
  letter-spacing: 1px; display: block;
  color: white;
}
.admin-logo-sub {
  font-size: 0.65rem; opacity: 0.75;
  letter-spacing: 0.5px; display: block;
  color: white;
}

/* ── Nav ── */
.sidebar-nav { flex: 1; padding: 12px 10px; overflow-y: auto; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 14px; border-radius: 12px;
  color: rgba(255,255,255,0.85);
  text-decoration: none; font-size: 0.88rem; font-weight: 600;
  margin-bottom: 4px;
  transition: all 0.2s;
}
.nav-item:hover  { background: var(--sidebar-hover); color: white; transform: translateX(3px); }
.nav-item--active {
  background: var(--sidebar-active);
  color: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.nav-icon { font-size: 1.1rem; width: 22px; text-align: center; flex-shrink: 0; }

/* ── Footer sidebar ── */
.sidebar-footer { padding: 14px 14px 20px; border-top: 1px solid rgba(255,255,255,0.15); }
.user-info { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.user-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 0.85rem; flex-shrink: 0;
}
.user-name { font-size: 0.82rem; font-weight: 700; color: white; }
.user-role { font-size: 0.72rem; opacity: 0.75; color: white; }
.btn-logout {
  width: 100%; padding: 9px;
  border: 2px solid rgba(255,255,255,0.4);
  background: transparent; color: white;
  border-radius: 20px; cursor: pointer;
  font-size: 0.82rem; font-weight: 600;
  transition: 0.2s;
}
.btn-logout:hover { background: rgba(255,255,255,0.15); }

/* ── Overlay ── */
.sidebar-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 190; display: none;
}

/* ── Main ── */
.admin-main {
  flex: 1; margin-left: 240px;
  display: flex; flex-direction: column;
  min-height: 100vh;
  background: var(--main-bg);
  color: var(--text);
  transition: background 0.3s, color 0.3s;
}

.topbar {
  display: none;
  background: var(--card-bg);
  border-bottom: 1px solid var(--border);
  padding: 12px 16px;
  align-items: center; gap: 12px;
  position: sticky; top: 0; z-index: 50;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.burger { background: none; border: none; font-size: 1.4rem; cursor: pointer; padding: 4px; }
.topbar-title { font-weight: 900; color: #2e7d32; flex: 1; }
.topbar-user { font-size: 0.85rem; color: #888; }
.admin-content { padding: 28px; flex: 1; }

/* ── Header avec toggle ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 12px 28px 0;
}
.page-header-right { display: flex; align-items: center; gap: 12px; }
.theme-toggle-wrap { display: flex; align-items: center; }
.theme-toggle {
  display: flex; align-items: center; gap: 10px;
  background: none; border: none; cursor: pointer;
  padding: 6px 12px 6px 6px;
  border-radius: 30px;
  transition: background 0.2s;
}
.theme-toggle:hover { background: rgba(0,151,167,0.10); }
.toggle-track {
  width: 52px; height: 28px;
  background: #e5e7eb;
  border-radius: 20px;
  position: relative;
  transition: background 0.3s;
  flex-shrink: 0;
}
.toggle-track.dark { background: #374151; }
.toggle-thumb {
  position: absolute;
  top: 3px; left: 3px;
  width: 22px; height: 22px;
  border-radius: 50%;
  background: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  transition: transform 0.3s cubic-bezier(.34,1.56,.64,1);
}
.toggle-track.dark .toggle-thumb { transform: translateX(24px); }
.toggle-label {
  font-size: 13px; font-weight: 600;
  color: var(--text, #444);
  white-space: nowrap;
}

/* ── Notification bell ── */
.notif-wrap {
  position: relative;
}
.notif-bell {
  background: none; border: none; cursor: pointer;
  font-size: 1.3rem; padding: 6px 8px; border-radius: 10px;
  position: relative; transition: background 0.2s;
  line-height: 1;
}
.notif-bell:hover, .notif-bell.active {
  background: rgba(0,151,167,0.10);
}
.notif-badge {
  position: absolute; top: 2px; right: 2px;
  background: #e53935; color: white;
  font-size: 10px; font-weight: 800;
  min-width: 16px; height: 16px;
  border-radius: 10px; padding: 0 4px;
  display: flex; align-items: center; justify-content: center;
  border: 2px solid white;
  line-height: 1;
}
.notif-dropdown {
  position: absolute; top: calc(100% + 10px); right: 0;
  width: 320px; max-height: 420px;
  background: var(--card-bg, #fff);
  border: 1px solid var(--border, #e5e7eb);
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
  z-index: 999;
  overflow: hidden;
  display: flex; flex-direction: column;
}
.notif-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border, #e5e7eb);
  font-weight: 700; font-size: 13px;
  color: var(--text, #222);
  background: var(--card-bg, #fff);
}
.notif-close {
  background: none; border: none; cursor: pointer;
  font-size: 14px; color: #888; padding: 2px 6px;
  border-radius: 6px;
}
.notif-close:hover { background: rgba(0,0,0,0.06); }
.notif-list { overflow-y: auto; flex: 1; }
.notif-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #f0f0f0);
  text-decoration: none; color: var(--text, #222);
  transition: background 0.15s;
  cursor: pointer;
}
.notif-item:hover { background: rgba(0,151,167,0.06); }
.notif-icon { font-size: 1.1rem; flex-shrink: 0; margin-top: 1px; }
.notif-body { display: flex; flex-direction: column; gap: 3px; flex: 1; }
.notif-msg { font-size: 13px; color: var(--text, #333); line-height: 1.4; }
.notif-date { font-size: 11px; color: #888; }
.notif-empty {
  padding: 24px 16px; text-align: center;
  font-size: 13px; color: #888;
}
.notif-footer {
  display: block; text-align: center;
  padding: 12px; font-size: 12px; font-weight: 600;
  color: #0097A7; text-decoration: none;
  border-top: 1px solid var(--border, #e5e7eb);
  background: var(--card-bg, #fff);
  transition: background 0.15s;
}
.notif-footer:hover { background: rgba(0,151,167,0.06); }

@media (max-width: 768px) {
  .notif-dropdown { right: -60px; width: 290px; }
}

.theme-toggle-mini {
  background: none; border: none;
  cursor: pointer; font-size: 18px;
  padding: 4px 6px; border-radius: 8px;
  transition: background 0.2s;
}
.theme-toggle-mini:hover { background: rgba(0,0,0,0.06); }

/* ── Mobile ── */
@media (max-width: 768px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar--open { transform: translateX(0); }
  .sidebar-overlay { display: block; }
  .admin-main { margin-left: 0; }
  .topbar { display: flex; }
  .admin-content { padding: 12px 10px; }
  .sidebar { width: 260px; }
  /* Nav items plus larges sur mobile */
  .nav-item { padding: 13px 18px; font-size: 13px; }
}

@media (max-width: 480px) {
  .admin-content { padding: 10px 8px; }
  .page-header { padding: 8px 10px 0; }
}
</style>