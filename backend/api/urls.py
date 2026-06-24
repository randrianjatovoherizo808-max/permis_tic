from django import views
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    home,
    CustomTokenObtainPairView,
    me,
    logout,
    change_password,
    register,
     forgot_password,
     verify_otp,
     reset_password,

    google_login_redirect,
    google_callback,

    users_list,
    user_detail,

    stats,

    formations_list,
    formation_detail,
    formation_lecons,

    lecons_list,
    lecon_detail,

    inscriptions_list,
    mon_inscription,
    inscrire_niveau,
    inscription_confirmer,
    inscription_rejeter,

    notes_list,
    note_detail,
    mes_notes,

    certificats_list,
    certificat_detail,

    sites_list,
    site_detail,

    sessions_list,
    session_detail,

    settings_view,
    notifications,
    admin_reset,

    google_register_formation,
    auto_login
)

urlpatterns = [

    # ═══════════════════════════
    # HEALTH CHECK
    # ═══════════════════════════
    path('home/', home),



    # ═══════════════════════════
    # AUTH
    # ═══════════════════════════
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('auth/me/', me),
    path('auth/logout/', logout),
    path('auth/change-password/', change_password),
    path('auth/register/', register),
   path('auth/forgot-password/', forgot_password),
    path('auth/verify-otp/', verify_otp),
    path('auth/reset-password/', reset_password),
    # ═══════════════════════════
    # GOOGLE OAUTH
    # ═══════════════════════════
    path('auth/google/', google_login_redirect),
    path('auth/google/callback/', google_callback),
    path('auth/auto-login/', auto_login),

    path('google/register/formation/', google_register_formation),

    # ═══════════════════════════
    # USERS
    # ═══════════════════════════
    path('users/', users_list),
    path('users/<int:pk>/', user_detail),

    # ═══════════════════════════
    # STATS
    # ═══════════════════════════
    path('stats/', stats),

    # ═══════════════════════════
    # FORMATIONS
    # ═══════════════════════════
    path('formations/', formations_list),
    path('formations/<int:pk>/', formation_detail),
    path('formations/<int:pk>/lecons/', formation_lecons),

    # ═══════════════════════════
    # LEÇONS
    # ═══════════════════════════
    path('lecons/', lecons_list),
    path('lecons/<int:pk>/', lecon_detail),

    # ═══════════════════════════
    # INSCRIPTIONS
    # ═══════════════════════════
    path('inscriptions/', inscriptions_list),
    path('inscriptions/mon-inscription/', mon_inscription),
    path('inscriptions/inscrire/', inscrire_niveau),
    path('inscriptions/<int:pk>/confirmer/', inscription_confirmer),
    path('inscriptions/<int:pk>/rejeter/', inscription_rejeter),

    # ═══════════════════════════
    # NOTES
    # ═══════════════════════════
    path('notes/', notes_list),
    path('notes/<int:pk>/', note_detail),
    path('notes/mes-notes/', mes_notes),

    # ═══════════════════════════
    # CERTIFICATS
    # ═══════════════════════════
    path('certificats/', certificats_list),
    path('certificats/<int:pk>/', certificat_detail),

    # ═══════════════════════════
    # SITES
    # ═══════════════════════════
    path('sites/', sites_list),
    path('sites/<int:pk>/', site_detail),

    # ═══════════════════════════
    # SESSIONS
    # ═══════════════════════════
    path('sessions/', sessions_list),
    path('sessions/<int:pk>/', session_detail),

    # ═══════════════════════════
    # SETTINGS / ADMIN TOOLS
    # ═══════════════════════════
    path('settings/', settings_view),
    path('parametres/', settings_view),  # alias frontend
    path('notifications/', notifications),
    path('admin/reset/', admin_reset),



    



    
]