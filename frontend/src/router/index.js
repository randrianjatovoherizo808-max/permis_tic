import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { useToast } from '../composables/useToast'

// ── Import des vues ──────────────────────────────────────────────────────────
// Pages publiques
import HomeView              from '../views/HomeView.vue'
import GoogleAuthSuccessView from '../views/GoogleAuthSuccessView.vue'
import LoginView          from '../views/LoginView.vue'
import RegisterView       from '../views/RegisterView.vue'
import ForgotPassword from '../views/ForgotPassword.vue'


// Espace apprenant
import EspaceApprenantView from '../views/EspaceApprenantView.vue'
// Formations publiques
import FormationsPublicView from '../views/FormationsPublicView.vue'
  
// Layout admin (contient la sidebar + <RouterView>)
import AdminLayout        from '../views/AdminLayout.vue'

// Sous-vues admin (lazy-loaded pour réduire le bundle initial)
const DashboardView      = () => import('../views/admin/DashboardView.vue')
const InscriptionsView   = () => import('../views/admin/InscriptionsView.vue')
const ApprenantsView     = () => import('../views/admin/ApprenantsView.vue')
const FormateursView     = () => import('../views/admin/FormateursView.vue')
const FormationsView     = () => import('../views/admin/FormationsView.vue')
const LeconsView         = () => import('../views/admin/LeconsView.vue')
const NotesView          = () => import('../views/admin/NotesView.vue')
const CertificatsView    = () => import('../views/admin/CertificatsView.vue')
const SitesView          = () => import('../views/admin/SitesView.vue')
const CalendrierView     = () => import('../views/admin/CalendrierView.vue')
const ParametresView     = () => import('../views/admin/ParametresView.vue')

// ── Définition des routes ────────────────────────────────────────────────────
const routes = [
  // ── Publiques ──
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { public: true },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { public: true, guestOnly: true },
  },
  {
    path: '/admin-login',
    name: 'admin-login',
    component: LoginView,
    meta: { public: true, guestOnly: true },
  },


{
  path: '/mot-de-passe-oublie',
  name: 'forgot-password',
  component: () => import('../views/ForgotPassword.vue'),
  meta: { public: true, guestOnly: true }
},
  
{
  path: '/reset-password',
  name: 'reset-password',
  component: () => import('../views/ResetPassword.vue'),
  meta: { public: true }
},
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { public: true, guestOnly: true },
  },




  // ── Espace apprenant ──
  {
    path: '/espace-apprenant',
    name: 'espace-apprenant',
    component: EspaceApprenantView,
    meta: { requiresAuth: true, roles: ['etudiant'] },
  },

  // ── Administration ──
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, roles: ['admin', 'formateur'] },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: DashboardView,
      },
      {
        path: 'inscriptions',
        name: 'inscriptions',
        component: InscriptionsView,
        meta: { roles: ['admin'] },        // formateurs exclus
      },
      {
        path: 'apprenants',
        name: 'apprenants',
        component: ApprenantsView,
      },
      {
        path: 'formateurs',
        name: 'formateurs',
        component: FormateursView,
        meta: { roles: ['admin'] },
      },
      {
        path: 'formations',
        name: 'formations',
        component: FormationsView,
      },
      {
        path: 'lecons',
        name: 'lecons',
        component: LeconsView,
      },
      {
        path: 'notes',
        name: 'notes',
        component: NotesView,
      },
      {
        path: 'certificats',
        name: 'certificats',
        component: CertificatsView,
        meta: { roles: ['admin'] },
      },
      {
        path: 'sites',
        name: 'sites',
        component: SitesView,
        meta: { roles: ['admin'] },
      },
      {
        path: 'calendrier',
        name: 'calendrier',
        component: CalendrierView,
      },
      


      
      {
        path: 'parametres',
        name: 'parametres',
        component: ParametresView,
      },
    ],
  },






  
  // ── Google OAuth callback ──
  {
    path: '/auth/google/success',
    name: 'google-auth-success',
    component: GoogleAuthSuccessView,
    meta: { public: true, allowAuthenticated: true },
  },

  



  // ── Catch-all 404 ──
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

// ── Création du router ───────────────────────────────────────────────────────
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes,
  scrollBehavior: () => ({ top: 0 }),


 
  
})



// ── Guards de navigation ─────────────────────────────────────────────────────
router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  // ── Retour depuis Google OAuth → stocker les tokens AVANT restore ──
  if (to.path === '/register' && to.query.step === '2' && to.query.access) {
    localStorage.setItem('access_token',  to.query.access)
    localStorage.setItem('refresh_token', to.query.refresh || '')
    // Laisser RegisterView gérer le reste, ne pas rediriger
    return next()
  }

  // 🔄 restore session (safe)
  if (!auth.user && auth.accessToken) {
    try {
      await auth.restore()
    } catch (e) {
      console.log('restore error:', e)
    }
  }

  const requiresAuth = to.matched.some(r => r.meta?.requiresAuth)
  const guestOnly = to.matched.some(r => r.meta?.guestOnly)

  // 🔓 PUBLIC ROUTES
  if (
    to.path === '/login' ||
    to.path === '/register' ||
    to.path === '/mot-de-passe-oublie'
  ) {
    return next()
  }

  // 🔒 PROTECTED ROUTES
  if (requiresAuth && !auth.isAuthenticated) {
    return next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  }

  // 🔓 GUEST ONLY (skip si la route autorise les utilisateurs connectés)
  const allowAuthenticated = to.matched.some(r => r.meta?.allowAuthenticated)
  if (guestOnly && auth.isAuthenticated && !allowAuthenticated) {
    return next(roleRedirect(auth.user?.role))
  }

  // ✅ Route accessible même connecté (ex: google-auth-success pour nouvel abonnement)
  if (allowAuthenticated) {
    return next()
  }

  // 🧠 ROLE CHECK — la route enfant (plus spécifique) prime sur le parent
  const routeWithRoles = [...to.matched].reverse().find(r => r.meta?.roles)
  const allowedRoles = routeWithRoles?.meta?.roles

  if (allowedRoles && allowedRoles.length) {
    const role = auth.user?.role

    if (!role) {
      return next({ name: 'login' })
    }

    if (!allowedRoles.includes(role)) {
      return next(roleRedirect(role))
    }
  }

  // 🚫 BLOCAGE APPRENANT — accès interdit tant qu'aucune inscription n'est confirmée
  if (to.name === 'espace-apprenant' && auth.user?.role === 'etudiant') {
    const inscriptions = auth.user?.inscriptions || []
    const aConfirme = inscriptions.some(i => i.statut === 'confirme')
    if (!aConfirme) {
      // Rediriger vers la page d'attente/inscription, pas vers home
      return next({ path: '/auth/google/success' })
    }
  }

  next()
})

/** Retourne la route d'accueil selon le rôle */
function roleRedirect(role) {
  if (role === 'etudiant') return { name: 'espace-apprenant' }

  if (role === 'admin') return { name: 'dashboard' }

  if (role === 'formateur') return { name: 'dashboard' }

  return { name: 'login' } // 🔥 IMPORTANT: tsy admin default intsony
}

export default router