<template>
  <!-- ── Écran de chargement léger ── -->
  <Transition name="splash">
    <div v-if="showSplash" class="splash-screen">
      <div class="splash-dots">
        <span class="dot dot-1"></span>
        <span class="dot dot-2"></span>
        <span class="dot dot-3"></span>
      </div>
    </div>
  </Transition>

  <!-- App principale -->
  <RouterView v-if="!showSplash" />

  <!-- Toast global -->
  <Transition name="toast">
    <div v-if="toast.visible" class="toast" :class="`toast--${toast.type}`">
      {{ toast.message }}
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from './composables/useToast'

const { toast } = useToast()

const showSplash = ref(true)

onMounted(async () => {
  // Bypass immédiat si retour Google OAuth ou auto-login
  const params = new URLSearchParams(window.location.search)
  if (
    window.location.pathname.includes('/auth/google/success') ||
    window.location.pathname.includes('/auto-login') ||
    params.has('access') ||
    params.has('refresh')
  ) {
    showSplash.value = false
    return
  }

  // Minimum 800ms pour éviter le flash, puis disparaît dès que le DOM est prêt
  await new Promise(r => setTimeout(r, 5000))
  showSplash.value = false
})
</script>

<style>
/* ── Reset & variables ──────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --primary:   #4CAF50;
  --secondary: #F9C514;
  --bg:        #f4f6f8;
  --card:      #ffffff;
  --text:      #222222;
  --gray:      #666666;
  --border:    #e5e7eb;
  --shadow:    0 2px 16px rgba(0,0,0,0.08);
  --accent:    #FFC107;
  --danger:    #F44336;
  --info:      #2196F3;
  --light:     #f8f9fa;
  --gray:      #6c757d;
  --bg:        #f5f7fb;
  --card:      #ffffff;
  --text:      #212529;
  --border:    #dee2e6;
  --niveau-a:  #2196F3;
  --niveau-b:  #FF9800;
  --niveau-c:  #9C27B0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: var(--bg);
  color: var(--text);
  font-size: 14px;
  line-height: 1.5;
}

/* ── Écran de chargement léger ─────────────────────────────────────────────── */
.splash-screen {
  position: fixed;
  inset: 0;
  background: linear-gradient(160deg, #f0faf0 0%, #fffde7 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  gap: 16px;
}

/* Logo + anneau spinner */
.splash-logo-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 18px 26px;
}

.splash-badge { display: flex; align-items: stretch; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 18px rgba(0,0,0,.2); height: 74px; animation: logoPulse 1.8s ease-in-out infinite; }
.splash-badge-p { background: #fff; color: #e53935; font-family: 'Syne', sans-serif; font-size: 2.4rem; font-weight: 900; width: 54px; display: flex; align-items: center; justify-content: center; border-right: 3px solid #e53935; }
.splash-badge-main { background: #2e7d32; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 0 16px; gap: 2px; }
.splash-badge-top { display: flex; align-items: baseline; gap: 5px; }
.splash-badge-if { color: #ff5252; font-family: 'Syne', sans-serif; font-size: 1.85rem; font-weight: 900; letter-spacing: 1.5px; }
.splash-badge-tic { color: #69f0ae; font-family: 'Syne', sans-serif; font-size: 1.85rem; font-weight: 900; letter-spacing: 1.5px; }
.splash-badge-bottom { color: rgba(255,255,255,.85); font-size: .85rem; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; }
.splash-badge-c { background: #1b5e20; color: #69f0ae; font-family: 'Syne', sans-serif; font-size: 3.2rem; font-weight: 900; width: 54px; display: flex; align-items: center; justify-content: center; border-left: 1px solid rgba(255,255,255,.2); line-height: 1; }

.splash-logo {
  width: 72px;
  height: 72px;
  object-fit: contain;
  border-radius: 16px;
  background: #fff;
  padding: 6px;
  box-shadow: 0 4px 20px rgba(76,175,80,0.2);
  animation: logoPulse 1.8s ease-in-out infinite;
}

/* splash-ring supprimé */

.splash-title {
  font-size: 1.4rem;
  font-weight: 900;
  color: #2e7d32;
  letter-spacing: 2px;
}

.splash-subtitle {
  font-size: 0.82rem;
  color: #888;
}

/* Points animés 3 points vert/jaune */
.splash-dots {
  display: flex;
  gap: 14px;
  margin-top: 20px;
}
.dot {
  width: 16px; height: 16px;
  border-radius: 50%;
  animation: dotBounce 0.8s ease-in-out infinite;
}
.dot-1 { background: #4CAF50; animation-delay: 0s; }
.dot-2 { background: #F9C514; animation-delay: 0.2s; }
.dot-3 { background: #4CAF50; animation-delay: 0.4s; }


@keyframes logoPulse  {
  0%,100% { transform: scale(1);    box-shadow: 0 4px 20px rgba(76,175,80,0.2); }
  50%     { transform: scale(1.05); box-shadow: 0 6px 28px rgba(76,175,80,0.35); }
}
@keyframes dotBounce {
  0%,80%,100% { transform: scale(0.6); opacity: 0.4; }
  40%         { transform: scale(1.1); opacity: 1; }
}

/* Transition sortie fluide */
.splash-enter-active { transition: opacity 0.3s ease; }
.splash-leave-active { transition: opacity 0.4s ease; }
.splash-enter-from, .splash-leave-to { opacity: 0; }

/* ── Boutons ────────────────────────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px 18px;
  border: none;
  border-radius: 50px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  white-space: nowrap;
}
.btn:hover  { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.btn:active { transform: scale(0.97); }
.btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; box-shadow: none; }

.btn-primary  { background: var(--primary);   color: #fff; }
.btn-danger   { background: var(--danger);    color: #fff; }
.btn-outline  { background: transparent; border: 2px solid var(--primary); color: var(--primary); }
.btn-outline:hover { background: var(--primary); color: #fff; }
.btn-sm  { padding: 6px 12px; font-size: 12px; }
.btn-xs  { padding: 4px 8px;  font-size: 11px; }
.btn-full { width: 100%; }

/* ── Formulaires ────────────────────────────────────────────────────────────── */
.form-group        { margin-bottom: 16px; }
.form-group label  { display: block; margin-bottom: 5px; font-weight: 600; font-size: 13px; color: var(--text); }
.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid var(--border);
  border-radius: 12px;
  font-size: 14px;
  background: var(--card);
  color: var(--text);
  transition: border-color 0.2s;
  outline: none;
}
.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus { border-color: var(--primary); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 500px) { .form-row { grid-template-columns: 1fr; } }

/* ── Carte ──────────────────────────────────────────────────────────────────── */
.card {
  background: var(--card);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  border: 1px solid var(--border);
}

/* ── Tableau ────────────────────────────────────────────────────────────────── */
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px 14px; text-align: left; border-bottom: 1px solid var(--border); }
th { font-size: 12px; font-weight: 700; color: var(--gray); text-transform: uppercase; letter-spacing: 0.5px; background: var(--light); }
tbody tr:hover { background: rgba(76,175,80,0.04); }
.empty-td { text-align: center; color: var(--gray); padding: 32px; font-size: 13px; }

/* ── Badges / statuts ───────────────────────────────────────────────────────── */
.badge           { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.badge--success  { background: rgba(76,175,80,0.15);  color: #2E7D32; }
.badge--danger   { background: rgba(244,67,54,0.12);  color: #B71C1C; }
.badge--warning  { background: rgba(255,193,7,0.2);   color: #856404; }
.badge--info     { background: rgba(33,150,243,0.12); color: #1565C0; }

.niveau-badge     { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; color: #fff; }
.niveau-a, .niveau-badge.niveau-a { background: var(--niveau-a); }
.niveau-b, .niveau-badge.niveau-b { background: var(--niveau-b); }
.niveau-c, .niveau-badge.niveau-c { background: var(--niveau-c); }

/* ── Modales ────────────────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: center; justify-content: center;
  z-index: 500; padding: 16px;
}
.modal-box {
  background: var(--card);
  border-radius: 20px;
  padding: 24px;
  width: 100%; max-width: 560px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.2);
}
.modal-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.modal-head h3 { font-size: 1.05rem; }
.close-btn {
  background: none; border: none; font-size: 1.6rem;
  cursor: pointer; color: var(--gray); line-height: 1;
  padding: 0 4px;
}

/* ── Titres de page ─────────────────────────────────────────────────────────── */
.page-title   { font-size: 1.3rem; font-weight: 800; margin-bottom: 20px; }
.page-header  { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.card-title   { font-size: 0.95rem; font-weight: 700; margin-bottom: 14px; }

/* ── Cellule utilisateur ─────────────────────────────────────────────────────── */
.user-cell    { display: flex; align-items: center; gap: 10px; }
.avatar       {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: #fff; font-weight: 900; font-size: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

/* ── Filtres / recherche ──────────────────────────────────────────────────────── */
.filters {
  display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
  margin-bottom: 16px;
}
.search-input {
  flex: 1; min-width: 180px;
  padding: 9px 14px; border: 1.5px solid var(--border);
  border-radius: 50px; font-size: 13px;
  background: var(--card); color: var(--text);
  outline: none; transition: border-color 0.2s;
}
.search-input:focus { border-color: var(--primary); }
.filters select {
  padding: 9px 14px; border: 1.5px solid var(--border);
  border-radius: 50px; font-size: 13px;
  background: var(--card); color: var(--text);
  outline: none; cursor: pointer;
}

/* ── Actions dans tableau ─────────────────────────────────────────────────────── */
.actions { display: flex; gap: 6px; }

/* ── Input mot de passe ───────────────────────────────────────────────────────── */
.input-pwd          { position: relative; }
.input-pwd input    { padding-right: 44px; }
.input-pwd button   {
  position: absolute; right: 12px; top: 50%;
  transform: translateY(-50%);
  background: none; border: none; cursor: pointer; font-size: 1rem;
}

/* ── Alertes inline ───────────────────────────────────────────────────────────── */
.alert         { padding: 10px 14px; border-radius: 10px; font-size: 13px; margin-bottom: 12px; }
.alert-success { background: rgba(76,175,80,0.12);  color: #2E7D32; border-left: 3px solid var(--primary); }
.alert-error   { background: rgba(244,67,54,0.10);  color: var(--danger); border-left: 3px solid var(--danger); }

/* ── Toast ────────────────────────────────────────────────────────────────────── */
.toast {
  position: fixed; bottom: 24px; left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px; border-radius: 50px;
  font-size: 13px; font-weight: 600;
  z-index: 9999; max-width: 90%;
  text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.2);
}
.toast--success { background: var(--primary);  color: #fff; }
.toast--error   { background: var(--danger);   color: #fff; }
.toast--info    { background: var(--info);     color: #fff; }
.toast--warning { background: var(--accent);   color: #212529; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s ease; }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(20px); }

/* ── Utilitaires ──────────────────────────────────────────────────────────────── */
.text-gray   { color: var(--gray); }
.text-center { text-align: center; }
.mt-4 { margin-top: 16px; }
.mt-8 { margin-top: 32px; }

/* ══ RESPONSIVE GLOBAL ════════════════════════════════════════════════════════ */

/* Tableaux scrollables sur mobile */
@media (max-width: 768px) {
  .card { padding: 14px; border-radius: 12px; }

  /* Tableaux → scroll horizontal */
  .card > table,
  .card > div > table { display: block; overflow-x: auto; -webkit-overflow-scrolling: touch; white-space: nowrap; }

  th, td { padding: 10px 10px; font-size: 12px; }

  /* Page header empilé */
  .page-header { flex-wrap: wrap; gap: 10px; }
  .page-header .btn { font-size: 12px; padding: 8px 14px; }
  .page-title { font-size: 1.1rem; }

  /* Filtres en colonne */
  .filters { flex-direction: column; align-items: stretch; }
  .search-input, .filters select { width: 100%; min-width: unset; }

  /* Modales plein écran sur mobile */
  .modal-overlay { padding: 0; align-items: flex-end; }
  .modal-box {
    border-radius: 20px 20px 0 0;
    max-height: 92vh;
    width: 100%;
    max-width: 100%;
    padding: 20px 16px 32px;
  }

  /* Boutons action plus espacés */
  .actions { gap: 4px; flex-wrap: wrap; }
  .btn-sm { padding: 5px 8px; font-size: 11px; }

  /* Form row → 1 colonne */
  .form-row { grid-template-columns: 1fr; }
}

@media (max-width: 480px) {
  body { font-size: 13px; }

  .card { padding: 12px; }
  .page-title { font-size: 1rem; }

  /* Toast plein largeur */
  .toast { left: 12px; right: 12px; transform: none; width: auto; max-width: none; }
  .toast-enter-from, .toast-leave-to { transform: translateY(20px); }

  /* Avatar plus petit */
  .avatar { width: 28px; height: 28px; font-size: 10px; }

  /* Badges compacts */
  .badge, .niveau-badge { font-size: 10px; padding: 2px 7px; }
}

/* ══ MODE SOMBRE GLOBAL ══════════════════════════════════════════════════ */
:root[data-theme="dark"] {
  --bg:        #111827;
  --card:      #1f2937;
  --text:      #f9fafb;
  --gray:      #9ca3af;
  --border:    #374151;
  --shadow:    0 2px 16px rgba(0,0,0,0.3);
}
:root[data-theme="dark"] body        { background: #111827; color: #f9fafb; }
:root[data-theme="dark"] .card       { background: #1f2937; border-color: #374151; color: #f9fafb; }
:root[data-theme="dark"] input,
:root[data-theme="dark"] select,
:root[data-theme="dark"] textarea    { background: #374151; border-color: #4b5563; color: #f9fafb; }
:root[data-theme="dark"] .table th   { background: #374151; color: #f9fafb; }
:root[data-theme="dark"] .table td   { border-color: #374151; color: #e5e7eb; }
:root[data-theme="dark"] .page-title { color: #f9fafb; }
:root[data-theme="dark"] label       { color: #d1d5db; }

</style>