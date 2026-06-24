import socket
import json
import logging
import random
import uuid
import urllib.parse

import requests

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives



from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.db.models import Q


def _send_html_email(subject, to_email, preheader, body_html, cta_link=None, cta_label=None):
    """Envoie un email HTML professionnel sans encodage quoted-printable."""
    cta_block = ""
    if cta_link and cta_label:
        cta_block = f"""
        <tr><td align="center" style="padding:28px 0 8px;">
          <a href="{cta_link}"
             style="background:#4CAF50;color:#fff;text-decoration:none;
                    padding:14px 36px;border-radius:8px;font-size:15px;
                    font-weight:700;display:inline-block;letter-spacing:.3px;">
            {cta_label}
          </a>
        </td></tr>
        <tr><td align="center" style="padding:12px 0 0;font-size:12px;color:#888;">
          Ou copiez ce lien dans votre navigateur :<br>
          <a href="{cta_link}" style="color:#4CAF50;word-break:break-all;font-size:11px;">{cta_link}</a>
        </td></tr>"""

    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{subject}</title></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">
<span style="display:none;max-height:0;overflow:hidden;">{preheader}</span>
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:40px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0"
       style="background:#fff;border-radius:16px;overflow:hidden;
              box-shadow:0 4px 24px rgba(0,0,0,.08);max-width:600px;width:100%;">
  <!-- Header -->
  <tr><td style="background:linear-gradient(135deg,#4CAF50,#2196F3);padding:36px 40px;text-align:center;">
    <div style="font-size:32px;margin-bottom:8px;">🎓</div>
    <h1 style="color:#fff;margin:0;font-size:22px;font-weight:800;letter-spacing:.5px;">PERMIS TIC</h1>
    <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:13px;">Plateforme de formation numérique</p>
  </td></tr>
  <!-- Body -->
  <tr><td style="padding:36px 40px;">
    <table width="100%" cellpadding="0" cellspacing="0">
      <tr><td style="font-size:15px;color:#333;line-height:1.7;">
        {body_html}
      </td></tr>
      {cta_block}
    </table>
  </td></tr>
  <!-- Footer -->
  <tr><td style="background:#f8f9fa;padding:20px 40px;text-align:center;
                 border-top:1px solid #eee;">
    <p style="margin:0;font-size:12px;color:#999;">
      © 2025 Permis TIC · Madagascar<br>
      Cet email a été envoyé automatiquement, merci de ne pas y répondre.
    </p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""

    text = f"{preheader}\n\n{subject}\n\nLien : {cta_link or ''}"
    from_email = settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL or 'noreply@permistic.mg'
    msg = EmailMultiAlternatives(subject, text, from_email, [to_email])
    msg.attach_alternative(html, "text/html")

    # ✅ Timeout socket explicite : évite de bloquer le worker Gunicorn
    # si le serveur SMTP (Gmail) est lent ou ne répond pas.
    # EMAIL_TIMEOUT dans settings.py fixe aussi le délai Django côté connexion.
    _prev_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(15)
    try:
        msg.send()
    finally:
        socket.setdefaulttimeout(_prev_timeout)

from .models import (
    Profil, Site, Formation, Lecon,
    Inscription, Session, Note, Certificat, Parametres, OtpCode
)
from .serializers import (
    UserSerializer, UserCreateSerializer,
    SiteSerializer, FormationSerializer, LeconSerializer,
    InscriptionSerializer, SessionSerializer, NoteSerializer,
    CertificatSerializer, ParametresSerializer
)
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode
)

from django.utils.encoding import (
    force_bytes,
    force_str
)

# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_staff_or_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# ══════════════════════════════════════════════════════════════════════════════
#  AUTHENTIFICATION JWT
# ══════════════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Étape 1 : envoie un code OTP à 6 chiffres (valide 10 min)."""
    email = request.data.get('email', '').strip().lower()
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Réponse neutre — ne pas révéler si l'email existe
        return Response({'message': 'Si cet email existe, un code vous a été envoyé.'})

    # Invalide les anciens OTP de cet utilisateur
    OtpCode.objects.filter(user=user, used=False).update(used=True)

    # Génère un code à 6 chiffres
    code = f"{random.randint(0, 999999):06d}"
    OtpCode.objects.create(user=user, code=code)

    _send_html_email(
        subject   = '🔐 Votre code de vérification – Permis TIC',
        to_email  = email,
        preheader = f'Votre code de réinitialisation : {code}',
        body_html = (
            f"<p>Bonjour <strong>{user.first_name}</strong>,</p>"
            f"<p>Vous avez demandé la réinitialisation de votre mot de passe.</p>"
            f"<p>Voici votre code de vérification à 6 chiffres :</p>"
            f"<div style='text-align:center;margin:28px 0;'>"
            f"<span style='font-size:42px;font-weight:900;letter-spacing:12px;"
            f"color:#4CAF50;font-family:monospace;'>{code}</span></div>"
            f"<p style='text-align:center;font-size:13px;color:#888;'>Ce code est valide <strong>10 minutes</strong>.</p>"
            f"<p style='margin-top:20px;padding:14px 18px;background:#fff8e1;border-left:4px solid #FF9800;"
            f"border-radius:6px;font-size:13px;color:#555;'>"
            f"⚠️ Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</p>"
        ),
    )
    return Response({'message': 'Code envoyé'})
    
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """Étape 2 : vérifie le code OTP saisi par l'utilisateur."""
    email = request.data.get('email', '').strip().lower()
    code  = request.data.get('code', '').strip()
    try:
        user = User.objects.get(email=email)
        otp  = OtpCode.objects.filter(user=user, code=code, used=False).last()
        if not otp or not otp.is_valid():
            return Response({'error': 'Code incorrect ou expiré.'}, status=400)
        return Response({'message': 'Code valide'})
    except User.DoesNotExist:
        return Response({'error': 'Compte introuvable.'}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Étape 3 : change le mot de passe après vérification OTP."""
    email    = request.data.get('email', '').strip().lower()
    code     = request.data.get('code', '').strip()
    password = request.data.get('password', '')

    if len(password) < 6:
        return Response({'error': 'Le mot de passe doit contenir au moins 6 caractères.'}, status=400)
    try:
        user = User.objects.get(email=email)
        otp  = OtpCode.objects.filter(user=user, code=code, used=False).last()
        if not otp or not otp.is_valid():
            return Response({'error': 'Code incorrect ou expiré.'}, status=400)
        otp.used = True
        otp.save()
        user.set_password(password)
        user.save()
        return Response({'message': 'Mot de passe modifié avec succès.'})
    except User.DoesNotExist:
        return Response({'error': 'Compte introuvable.'}, status=400)






class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email']    = user.email
        token['username'] = user.username
        return token

    def validate(self, attrs):
        username_or_email = attrs.get('username', '')
        # Accepte email à la place du username
        try:
            user = User.objects.get(email=username_or_email)
            attrs['username'] = user.username
        except User.DoesNotExist:
            pass
        return super().validate(attrs)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ══════════════════════════════════════════════════════════════════════════════
#  ENDPOINTS AUTH
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    return Response({"message": "Permis TIC API 🚀"})


@api_view(['GET'])
def google_login(request):
    return Response({"message": "Google endpoint OK"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    role = 'admin' if user.is_superuser else 'formateur' if user.is_staff else 'etudiant'
    try:
        tel = user.profil.telephone
    except Profil.DoesNotExist:
        tel = ''
    # Statut des inscriptions de l'étudiant (pour le blocage frontend)
    inscriptions_statut = []
    if role == 'etudiant':
        inscriptions_statut = list(
            Inscription.objects.filter(utilisateur=user)
            .values('niveau', 'statut', 'motif_rejet')
        )

    return Response({
        'id':         user.id,
        'email':      user.email,
        'username':   user.username,
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'prenom':     user.first_name,
        'nom':        user.last_name,
        'is_staff':   user.is_staff,
        'is_superuser': user.is_superuser,
        'role':       role,
        'telephone':  tel,
        'is_active':  user.is_active,
        'photo_url':  getattr(user.profil, 'photo_url', '') if hasattr(user, 'profil') else '',
        # Liste des inscriptions avec leur statut (utilisé par le router pour bloquer l'accès)
        'inscriptions': inscriptions_statut,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response({'message': 'Déconnecté avec succès'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    user        = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    if not user.check_password(old_password):
        return Response({'error': 'Ancien mot de passe incorrect'}, status=400)
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Mot de passe modifié avec succès'})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Inscription apprenant (public) ou création par admin."""
    prenom    = request.data.get('prenom', '').strip()
    nom       = request.data.get('nom', '').strip()
    email     = request.data.get('email', '').strip().lower()
    password  = request.data.get('password', '')
    telephone = request.data.get('telephone', '')
    # role = 'formateur' seulement si envoyé par un admin connecté
    role = request.data.get('role', 'etudiant')
    if role != 'etudiant' and not is_staff_or_admin(request.user):
        role = 'etudiant'

    if not all([prenom, nom, email]):
        return Response({'error': 'Champs obligatoires manquants.'}, status=400)
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Cet email est déjà utilisé.'}, status=400)

    base = email.split('@')[0]
    username, i = base, 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{i}"; i += 1

    # Tous les comptes sont actifs dès la création.
    # Pour les étudiants, c'est le STATUT DE L'INSCRIPTION qui contrôle l'accès aux cours.
    # (is_active=False bloquerait la connexion JWT elle-même, ce qu'on ne veut pas)
    is_active    = True
    is_staff     = role in ['formateur', 'admin']
    is_superuser = role == 'admin'

    user = User(
        username=username, email=email,
        first_name=prenom, last_name=nom,
        is_active=is_active,
        is_staff=is_staff,
        is_superuser=is_superuser,
    )
    if password:
        user.set_password(password)
    else:
        user.set_unusable_password()
    user.save()

    Profil.objects.update_or_create(
        user=user, defaults={'telephone': telephone, 'role': role}
    )

    # Inscription à la formation choisie lors de l'inscription (apprenant public)
    formation_id = request.data.get('formation', None)
    niveau_brut  = request.data.get('niveau', '').upper()

    if role == 'etudiant':
        formation_obj = None
        niveau_final  = None

        if formation_id:
            try:
                formation_obj = Formation.objects.get(pk=formation_id)
                niveau_final  = formation_obj.niveau
            except Formation.DoesNotExist:
                pass

        if not formation_obj and niveau_brut in ('A', 'B', 'C'):
            niveau_final = niveau_brut

        if niveau_final:
            from django.db import IntegrityError
            try:
                Inscription.objects.get_or_create(
                    utilisateur=user,
                    formation=formation_obj,
                    niveau=niveau_final,
                    defaults={'telephone': telephone, 'statut': 'en_attente'}
                )
            except IntegrityError:
                pass  # Inscription déjà existante, on ignore

    return Response({'message': 'Compte créé avec succès.'}, status=201)


# ══════════════════════════════════════════════════════════════════════════════
#  GOOGLE OAUTH 2.0
# ══════════════════════════════════════════════════════════════════════════════

GOOGLE_AUTH_URL     = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL    = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
GOOGLE_REDIRECT_URI = 'http://127.0.0.1:8000/accounts/google/login/callback/'


@api_view(['GET'])
@permission_classes([AllowAny])
def google_login_redirect(request):
    params = {
        'client_id':     settings.GOOGLE_CLIENT_ID,
        'redirect_uri':  settings.GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope':         'openid email profile',
        'access_type':   'offline',
        'prompt':        'select_account',
    }
    return redirect(f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}")


@api_view(['GET'])
@permission_classes([AllowAny])
def google_callback(request):
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5181')
    code  = request.GET.get('code')
    error = request.GET.get('error')

    if error or not code:
        return redirect(f"{frontend_url}/login?error=google_denied")

    # Échange code → tokens Google
    try:
        token_resp = requests.post(GOOGLE_TOKEN_URL, data={
            'code':          code,
            'client_id':     settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri':  settings.GOOGLE_REDIRECT_URI,
            'grant_type':    'authorization_code',
        }, timeout=10)
        token_resp.raise_for_status()
        google_access = token_resp.json().get('access_token')
    except Exception:
        return redirect(f"{frontend_url}/login?error=google_token_failed")

    if not google_access:
        return redirect(f"{frontend_url}/login?error=google_no_token")

    # Récupère le profil Google
    try:
        info_resp = requests.get(
            GOOGLE_USERINFO_URL,
            headers={'Authorization': f"Bearer {google_access}"},
            timeout=10,
        )
        info_resp.raise_for_status()
        info = info_resp.json()
    except Exception:
        return redirect(f"{frontend_url}/login?error=google_userinfo_failed")

    g_email  = info.get('email', '').lower()
    g_prenom  = info.get('given_name', '')
    g_nom     = info.get('family_name', '')
    g_picture = info.get('picture', '')
    g_sub    = info.get('sub', '')

    if not g_email:
        return redirect(f"{frontend_url}/login?error=google_no_email")

    user, created = User.objects.get_or_create(
        email=g_email,
        defaults={
            'username':   f"g_{g_sub}" if g_sub else g_email.split('@')[0],
            'first_name': g_prenom,
            'last_name':  g_nom,
            'is_active':  True,
        }
    )
    if created:
        user.set_unusable_password()
        user.save()
        Profil.objects.create(user=user, role='etudiant')
        # ✅ Nouveau compte Google : pas d'inscription automatique créée ici.
        # Le frontend détectera is_new_user=1 et redirigera vers la page
        # de sélection de niveau pour que l'étudiant choisisse sa formation.
    else:
        if not user.is_active:
            return redirect(f"{frontend_url}/login?error=account_disabled")
        # Synchronise prénom/nom depuis Google si vides
        updated = False
        if not user.first_name and g_prenom:
            user.first_name = g_prenom; updated = True
        if not user.last_name and g_nom:
            user.last_name = g_nom; updated = True
        if updated:
            user.save(update_fields=['first_name', 'last_name'])

    # Vérifie les droits réels en base (is_staff / is_superuser)
    # Un admin créé via Django admin a is_superuser=True mais peut n'avoir
    # jamais eu de Profil → on le crée si nécessaire avec le bon rôle
    role_reel = 'admin' if user.is_superuser else 'formateur' if user.is_staff else 'etudiant'
    profil, _ = Profil.objects.get_or_create(user=user, defaults={'role': role_reel})
    profil_updated = []
    if profil.role != role_reel:
        profil.role = role_reel; profil_updated.append('role')
    if g_picture and profil.photo_url != g_picture:
        profil.photo_url = g_picture; profil_updated.append('photo_url')
    if profil_updated:
        profil.save(update_fields=profil_updated)

    refresh = RefreshToken.for_user(user)
    role = 'admin' if user.is_superuser else 'formateur' if user.is_staff else 'etudiant'

    # Pour les étudiants : liste des niveaux inscrits
    niveaux_inscrits = []
    if role == 'etudiant':
        inscriptions = Inscription.objects.filter(utilisateur=user).values('niveau', 'statut')
        niveaux_inscrits = list(inscriptions)

    # Vérifier si l'utilisateur a déjà une inscription confirmée (pour s'inscrire à un autre cours)
    a_inscription_confirmee = False
    if role == 'etudiant':
        a_inscription_confirmee = Inscription.objects.filter(
            utilisateur=user, statut='confirme'
        ).exists()

    photo_url = ''
    if hasattr(user, 'profil'):
        photo_url = getattr(user.profil, 'photo_url', '') or ''

    params = urllib.parse.urlencode({
        'access':                str(refresh.access_token),
        'refresh':               str(refresh),
        'role':                  role,
        'niveaux_inscrits':      json.dumps(niveaux_inscrits),
        'new_inscription':       '1' if a_inscription_confirmee else '0',
        'photo_url':             photo_url,
        # ✅ is_new_user=1 → le frontend doit rediriger vers la sélection de niveau
        'is_new_user':           '1' if created else '0',
    })
    return redirect(f"{frontend_url}/auth/google/success?{params}")


# ══════════════════════════════════════════════════════════════════════════════
#  UTILISATEURS
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users_list(request):
    role = request.query_params.get('role')
    qs   = User.objects.all().order_by('last_name', 'first_name')
    if role == 'etudiant':
        qs = qs.filter(is_staff=False, is_superuser=False)
    elif role == 'formateur':
        qs = qs.filter(is_staff=True, is_superuser=False)
    elif role == 'admin':
        qs = qs.filter(is_superuser=True)
    return Response(UserSerializer(qs, many=True).data)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    try:
        user = get_object_or_404(User, pk=pk)

        # S'assurer que le Profil existe (evite crash sur profil manquant)
        Profil.objects.get_or_create(user=user, defaults={'role': (
            'admin' if user.is_superuser else 'formateur' if user.is_staff else 'etudiant'
        )})

        if request.method == 'GET':
            return Response(UserSerializer(user).data)

        if request.method == 'PATCH':
            if not is_staff_or_admin(request.user):
                return Response(status=403)
            for field, value in request.data.items():
                if field == 'is_active':
                    user.is_active = bool(value)
                elif field == 'first_name':
                    user.first_name = value
                elif field == 'last_name':
                    user.last_name = value
                elif field == 'email':
                    user.email = value
            user.save()
            return Response(UserSerializer(user).data)

        if request.method == 'DELETE':
            if not is_admin(request.user):
                return Response(status=403)
            user.delete()
            return Response(status=204)

    except Exception as e:
        logging.error(f"user_detail error pk={pk}: {e}", exc_info=True)
        return Response({'error': 'Une erreur est survenue.'}, status=500)
    

  










# ══════════════════════════════════════════════════════════════════════════════
#  STATISTIQUES
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([AllowAny])
def stats(request):
    nb_formations  = Formation.objects.count()
    nb_apprenants  = User.objects.filter(is_staff=False, is_superuser=False, is_active=True).count()
    nb_formateurs  = User.objects.filter(is_staff=True, is_superuser=False).count()
    nb_en_attente  = Inscription.objects.filter(statut='en_attente').count()
    nb_confirmes   = Inscription.objects.filter(statut='confirme').count()
    nb_certificats = Certificat.objects.count()

    # Taux de réussite réel : % d'étudiants ayant au moins une note >= 50
    from django.db.models import Avg
    total_notes = Note.objects.count()
    if total_notes == 0:
        reussite_reel = 0
    else:
        notes_reussies = Note.objects.filter(valeur__gte=50).count()
        reussite_reel  = round((notes_reussies / total_notes) * 100)

    return Response({
        'formations':              nb_formations,
        'apprenants':              nb_apprenants,
        'formateurs':              nb_formateurs,
        'inscriptions_en_attente': nb_en_attente,
        'inscriptions_confirmees': nb_confirmes,
        'certificats':             nb_certificats,
        'reussite':                reussite_reel,
    })


# ══════════════════════════════════════════════════════════════════════════════
#  FORMATIONS
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def formations_list(request):
    if request.method == 'GET':
        niveau = request.query_params.get('niveau')
        qs = Formation.objects.all().order_by('niveau', 'nom')
        if niveau:
            qs = qs.filter(niveau=niveau)
        return Response(FormationSerializer(qs, many=True).data)

    if not is_staff_or_admin(request.user):
        return Response(status=403)
    s = FormationSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def formation_detail(request, pk):
    formation = get_object_or_404(Formation, pk=pk)
    if request.method == 'GET':
        return Response(FormationSerializer(formation).data)
    if not is_staff_or_admin(request.user):
        return Response(status=403)
    if request.method == 'PUT':
        s = FormationSerializer(formation, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    formation.delete()
    return Response(status=204)


# ── Leçons d'une formation ────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def formation_lecons(request, pk):
    formation = get_object_or_404(Formation, pk=pk)

    if not request.user.is_staff and not request.user.is_superuser:
        # Vérifier que l'utilisateur a une inscription CONFIRMÉE pour ce niveau
        insc = Inscription.objects.filter(
            utilisateur=request.user,
            niveau=formation.niveau,
        ).first()

        if not insc:
            return Response(
                {"error": "Aucune inscription pour ce niveau"},
                status=403
            )
        if insc.statut != 'confirme':
            return Response(
                {"error": "Inscription en attente de validation", "statut": insc.statut},
                status=403
            )

    lecons = Lecon.objects.filter(formation=formation).order_by('ordre')
    return Response(LeconSerializer(lecons, many=True).data)

# ══════════════════════════════════════════════════════════════════════════════
#  LEÇONS (CRUD global)
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lecons_list(request):
    if request.method == 'GET':
        formation_id = request.query_params.get('formation')
        qs = Lecon.objects.all().order_by('formation', 'ordre')
        if formation_id:
            qs = qs.filter(formation_id=formation_id)
        return Response(LeconSerializer(qs, many=True, context={'request': request}).data)
    if not is_staff_or_admin(request.user):
        return Response(status=403)
    # ✅ Accepte multipart/form-data (avec fichier) ET JSON (sans fichier)
    s = LeconSerializer(data=request.data, context={'request': request})
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def lecon_detail(request, pk):
    lecon = get_object_or_404(Lecon, pk=pk)
    if request.method == 'GET':
        return Response(LeconSerializer(lecon).data)
    if not is_staff_or_admin(request.user):
        return Response(status=403)
    if request.method == 'PUT':
        # ✅ partial=True : on peut modifier sans renvoyer le fichier si inchangé
        s = LeconSerializer(lecon, data=request.data, partial=True, context={'request': request})
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    lecon.delete()
    return Response(status=204)


# ══════════════════════════════════════════════════════════════════════════════
#  INSCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inscriptions_list(request):
    if not is_staff_or_admin(request.user):
        return Response(
            {
                'error': 'Accès réservé aux administrateurs et formateurs.',
                'detail': f"Votre compte ({request.user.email}) n'a pas les droits suffisants. "
                          f"is_staff={request.user.is_staff}, is_superuser={request.user.is_superuser}, "
                          f"is_active={request.user.is_active}"
            },
            status=403
        )
    statut    = request.query_params.get('statut')
    niveau    = request.query_params.get('niveau')
    recherche = request.query_params.get('q', '')
    qs = Inscription.objects.select_related('utilisateur').all()
    if statut:
        qs = qs.filter(statut=statut)
    if niveau:
        qs = qs.filter(niveau=niveau)
    if recherche:
        qs = qs.filter(
            Q(utilisateur__first_name__icontains=recherche) |
            Q(utilisateur__last_name__icontains=recherche) |
            Q(utilisateur__email__icontains=recherche)
        )
    return Response(InscriptionSerializer(qs.order_by('-date_inscription'), many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mon_inscription(request):
    """
    Retourne la liste de toutes les inscriptions de l'apprenant connecté (une par niveau).
    """
    inscriptions = (
        Inscription.objects
        .select_related('formation')
        .filter(utilisateur=request.user)
        .order_by('niveau', '-date_inscription')
    )
    return Response(InscriptionSerializer(inscriptions, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inscrire_niveau(request):
    """
    Inscrit l'apprenant connecté à une formation spécifique OU à un niveau général.
    - Si formation_id fourni : unicité par (utilisateur, formation)
    - Sinon : unicité par (utilisateur, niveau) pour inscription générale
    """.strip()
    telephone    = request.data.get('telephone', '')
    formation_id = request.data.get('formation_id', None)

    # Résoudre la formation en premier
    formation = None
    if formation_id:
        try:
            formation = Formation.objects.get(pk=formation_id)
        except Formation.DoesNotExist:
            return Response({'error': 'Formation introuvable.'}, status=404)

    # Niveau : depuis la formation si fournie, sinon depuis le payload
    if formation:
        niveau = formation.niveau
    else:
        niveau = str(request.data.get('niveau', '') or '').strip().upper()

    if niveau not in ('A', 'B', 'C'):
        return Response({'error': 'Niveau invalide. Choisissez A, B ou C.'}, status=400)

    # Vérifier doublon selon le contexte
    if formation:
        existante = Inscription.objects.filter(utilisateur=request.user, formation=formation).first()
        doublon_msg = f'Vous êtes déjà inscrit(e) à cette formation ({formation.nom}).'
    else:
        existante = Inscription.objects.filter(utilisateur=request.user, formation__isnull=True, niveau=niveau).first()
        doublon_msg = f'Vous avez déjà une inscription pour le Niveau {niveau}.'

    if existante:
        if existante.statut in ('en_attente', 'confirme'):
            return Response({'error': doublon_msg}, status=400)
        elif existante.statut == 'rejete':
            existante.delete()

    from django.db import IntegrityError
    try:
        insc = Inscription.objects.create(
            utilisateur=request.user,
            formation=formation,
            niveau=niveau,
            telephone=telephone,
            statut='en_attente'
        )
    except IntegrityError:
        return Response(
            {'error': 'Vous êtes déjà inscrit(e) à cette formation ou ce niveau.'},
            status=400
        )

    niveau_labels = {'A': 'Niveau A – Débutant', 'B': 'Niveau B – Intermédiaire', 'C': 'Niveau C – Avancé'}
    niveau_label = niveau_labels.get(niveau, f'Niveau {niveau}')

    # Email de confirmation de réception
    try:
        _send_html_email(
            subject   = f'📋 Inscription Niveau {niveau} reçue – En attente de validation',
            to_email  = request.user.email,
            preheader = f"Votre demande d'inscription au {niveau_label} a été reçue.",
            body_html = (
                f"<p>Bonjour <strong>{request.user.first_name}</strong>,</p>"
                f"<p>Votre demande d'inscription au <strong>« {niveau_label} »</strong> "
                f"a bien été reçue.</p>"
                f"<div style='margin:20px 0;padding:16px 20px;background:#fff8e1;"
                f"border-radius:8px;border-left:4px solid #FF9800;'>"
                f"<p style='margin:0;font-size:14px;color:#555;'>"
                f"⏳ <strong>Votre inscription est actuellement en attente de validation "
                f"par l'administrateur.</strong><br>"
                f"Vous recevrez un email dès que votre accès aux cours sera activé.</p></div>"
                f"<p style='font-size:13px;color:#888;'>Merci de votre patience.</p>"
            ),
        )
    except Exception:
        pass

    return Response({'message': f'Inscription au {niveau_label} enregistrée.', 'statut': insc.statut}, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inscription_confirmer(request, pk):
    if not is_admin(request.user):
        return Response(status=403)
    insc = get_object_or_404(Inscription, pk=pk)
    insc.statut = 'confirme'
    insc.save()

    user = insc.utilisateur
    user.is_active = True
    user.save()

    niveau_labels = {'A': 'Niveau A – Débutant', 'B': 'Niveau B – Intermédiaire', 'C': 'Niveau C – Avancé'}
    niveau_label = niveau_labels.get(insc.niveau, f'Niveau {insc.niveau}')

    # Lien de connexion directe (backend génère JWT et redirige)
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5181')
    backend_url  = getattr(settings, 'BACKEND_URL',  'http://localhost:8000')
    token = default_token_generator.make_token(user)
    uid   = urlsafe_base64_encode(force_bytes(user.pk))

    # Utilisateur Google (pas de mot de passe local) → lien direct vers login Google
    if not user.has_usable_password():
        reset_link    = f"{frontend_url}/login"
        cta_label_txt = '🔑 Se connecter avec Google'
        cta_note      = (
            "<div style='margin:20px 0;padding:16px 20px;background:#e8f5e9;"
            "border-radius:8px;border-left:4px solid #4CAF50;'>"
            "<p style='margin:0;font-size:13px;color:#2e7d32;'>"
            "<strong>📌 Votre compte est lié à Google.</strong><br>"
            "Cliquez sur le bouton ci-dessous et connectez-vous avec votre compte Google "
            "pour accéder directement à votre espace apprenant.</p></div>"
        )
    else:
        # Utilisateur classique → lien auto-login via backend
        reset_link    = f"{backend_url}/api/auth/auto-login/?uid={uid}&token={token}"
        cta_label_txt = '🔓 Accéder à mon espace apprenant'
        cta_note      = (
            "<div style='margin:20px 0;padding:16px 20px;background:#e8f5e9;"
            "border-radius:8px;border-left:4px solid #4CAF50;'>"
            "<p style='margin:0;font-size:13px;color:#2e7d32;'>"
            "<strong>📌 Première connexion ?</strong><br>"
            "Utilisez le bouton ci-dessous pour accéder directement "
            "à votre espace apprenant.</p></div>"
        )

    # Liste des cours du niveau validé
    formations_niveau = Formation.objects.filter(niveau=insc.niveau).values_list('nom', flat=True)
    cours_html = ''.join(
        f"<li style='margin:4px 0;'>📘 {nom}</li>" for nom in formations_niveau
    ) or "<li>Aucun cours disponible pour l'instant.</li>"

    try:
        _send_html_email(
            subject   = f'✅ Inscription {niveau_label} validée – Permis TIC',
            to_email  = user.email,
            preheader = f'Votre inscription au {niveau_label} a été validée !',
            body_html = (
                f"<p>Bonjour <strong>{user.first_name}</strong>,</p>"
                f"<p>🎉 Bonne nouvelle ! Votre inscription au <strong>« {niveau_label} »</strong> "
                f"a été <strong>validée</strong> par l'administrateur.</p>"
                f"<p>Vous avez désormais accès à tous les cours de ce niveau :</p>"
                f"<ul style='margin:12px 0 16px 20px;padding:0;font-size:14px;color:#333;'>{cours_html}</ul>"
                + cta_note
            ),
            cta_link  = reset_link,
            cta_label = cta_label_txt,
        )
    except Exception:
        pass

    return Response(InscriptionSerializer(insc).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def inscription_rejeter(request, pk):
    if not is_admin(request.user):
        return Response(status=403)
    insc = get_object_or_404(Inscription, pk=pk)
    insc.statut      = 'rejete'
    insc.motif_rejet = request.data.get('motif', '')
    insc.save()

    user = insc.utilisateur
    niveau_labels = {'A': 'Niveau A – Débutant', 'B': 'Niveau B – Intermédiaire', 'C': 'Niveau C – Avancé'}
    niveau_label  = niveau_labels.get(insc.niveau, f'Niveau {insc.niveau}')
    frontend_url  = getattr(settings, 'FRONTEND_URL', 'http://localhost:5181')

    motif_html = (
        f"<div style='margin:16px 0;padding:14px 18px;background:#fff3e0;"
        f"border-radius:8px;border-left:4px solid #FF9800;'>"
        f"<p style='margin:0;font-size:13px;color:#7a4f00;'>"
        f"<strong>📋 Motif :</strong> {insc.motif_rejet}</p></div>"
    ) if insc.motif_rejet else ''

    try:
        _send_html_email(
            subject   = f'❌ Inscription {niveau_label} non retenue – Permis TIC',
            to_email  = user.email,
            preheader = f"Votre demande d'inscription au {niveau_label} n'a pas été retenue.",
            body_html = (
                f"<p>Bonjour <strong>{user.first_name}</strong>,</p>"
                f"<p>Nous vous informons que votre demande d'inscription au "
                f"<strong>« {niveau_label} »</strong> n'a pas été retenue "
                f"par l'administrateur.</p>"
                + motif_html +
                f"<div style='margin:20px 0;padding:16px 20px;background:#fce4ec;"
                f"border-radius:8px;border-left:4px solid #e91e63;'>"
                f"<p style='margin:0;font-size:13px;color:#880e4f;'>"
                f"<strong>💡 Vous pouvez vous inscrire à une autre formation.</strong><br>"
                f"Connectez-vous à votre compte et choisissez un autre cours ou niveau.</p></div>"
                f"<p style='font-size:13px;color:#888;'>"
                f"Pour toute question, contactez l'administration.</p>"
            ),
            cta_link  = f"{frontend_url}/login",
            cta_label = '📋 Choisir une autre formation',
        )
    except Exception:
        pass

    return Response(InscriptionSerializer(insc).data)


# ══════════════════════════════════════════════════════════════════════════════
#  NOTES
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def notes_list(request):
    if request.method == 'GET':
        formation_id = request.query_params.get('formation')
        qs = Note.objects.select_related('apprenant', 'formation').all()
        if formation_id:
            qs = qs.filter(formation_id=formation_id)
        return Response(NoteSerializer(qs, many=True).data)
    if not is_staff_or_admin(request.user):
        return Response(status=403)
    s = NoteSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'GET':
        return Response(NoteSerializer(note).data)
    if not is_staff_or_admin(request.user):
        return Response(status=403)
    if request.method == 'PUT':
        s = NoteSerializer(note, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    note.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mes_notes(request):
    notes = Note.objects.filter(apprenant=request.user).select_related('formation')
    return Response(NoteSerializer(notes, many=True).data)


# ══════════════════════════════════════════════════════════════════════════════
#  CERTIFICATS
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def certificats_list(request):
    if request.method == 'GET':
        if not is_staff_or_admin(request.user):
            return Response(status=403)
        qs = Certificat.objects.select_related('apprenant', 'formation').all()
        return Response(CertificatSerializer(qs, many=True).data)
    if not is_admin(request.user):
        return Response(status=403)
    data = request.data.copy()
    if not data.get('numero'):
        data['numero'] = f"CERT-{uuid.uuid4().hex[:8].upper()}"
    # formation est optionnelle : si absente ou vide, forcer null
    if not data.get('formation'):
        data['formation'] = None
    s = CertificatSerializer(data=data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    logging.getLogger(__name__).error("Certificat errors: %s", s.errors)
    return Response(s.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def certificat_detail(request, pk):
    cert = get_object_or_404(Certificat, pk=pk)
    if request.method == 'GET':
        return Response(CertificatSerializer(cert).data)
    if not is_admin(request.user):
        return Response(status=403)
    if request.method == 'PUT':
        s = CertificatSerializer(cert, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    cert.delete()
    return Response(status=204)


# ══════════════════════════════════════════════════════════════════════════════
#  SITES
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sites_list(request):
    if request.method == 'GET':
        return Response(SiteSerializer(Site.objects.all(), many=True).data)
    if not is_admin(request.user):
        return Response(status=403)
    s = SiteSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def site_detail(request, pk):
    site = get_object_or_404(Site, pk=pk)
    if request.method == 'GET':
        return Response(SiteSerializer(site).data)
    if not is_admin(request.user):
        return Response(status=403)
    if request.method == 'PUT':
        s = SiteSerializer(site, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    site.delete()
    return Response(status=204)


# ══════════════════════════════════════════════════════════════════════════════
#  SESSIONS (CALENDRIER)
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sessions_list(request):
    if request.method == 'GET':
        formation_id = request.query_params.get('formation')
        site_id      = request.query_params.get('site')
        qs = Session.objects.select_related('formation', 'site', 'formateur').all()
        if formation_id:
            qs = qs.filter(formation_id=formation_id)
        if site_id:
            qs = qs.filter(site_id=site_id)
        return Response(SessionSerializer(qs.order_by('date_debut'), many=True).data)
    if not is_staff_or_admin(request.user):
        return Response(status=403)
    s = SessionSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def session_detail(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'GET':
        return Response(SessionSerializer(session).data)
    if not is_staff_or_admin(request.user):
        return Response(status=403)
    if request.method == 'PUT':
        s = SessionSerializer(session, data=request.data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    session.delete()
    return Response(status=204)


# ══════════════════════════════════════════════════════════════════════════════
#  PARAMÈTRES & NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def settings_view(request):
    p = Parametres.instance()
    if request.method == 'GET':
        # GET public : la page d'accueil lit les paramètres sans token
        return Response(ParametresSerializer(p).data)
    # PATCH réservé aux admins/staff uniquement
    if not request.user.is_authenticated or not is_staff_or_admin(request.user):
        return Response({'error': 'Permission refusée — réservé aux administrateurs.'}, status=403)
    s = ParametresSerializer(p, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications(request):
    """Notifications rapides pour l'admin (inscriptions en attente)."""
    n = Inscription.objects.filter(statut='en_attente').count()
    items = []
    if n:
        items.append({'type': 'inscriptions', 'message': f"{n} inscription(s) en attente", 'count': n})
    return Response(items)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_reset(request):
    """Réinitialisation des données de test (admin seulement)."""
    if not is_admin(request.user):
        return Response(status=403)
    # Supprime données de test en gardant les comptes admin
    Inscription.objects.filter(statut='en_attente').delete()
    return Response({'message': 'Données réinitialisées.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def google_register_formation(request):
    """Inscription via Google : par formation ou par niveau general."""
    telephone    = request.data.get('telephone', '')
    formation_id = request.data.get('formation_id', None)

    # 1) Resolution de la formation
    formation = None
    if formation_id:
        try:
            formation = Formation.objects.get(pk=formation_id)
        except Formation.DoesNotExist:
            return Response({'error': 'Formation introuvable.'}, status=404)

    # 2) Resolution du niveau
    # Si une formation est choisie, on prend son niveau ; sinon le champ 'niveau' du payload
    if formation:
        niveau = formation.niveau
    else:
        niveau = str(request.data.get('niveau', '') or '').strip().upper()

    if niveau not in ('A', 'B', 'C'):
        return Response({'error': 'Niveau invalide. Choisissez A, B ou C.'}, status=400)

    # 3) Gestion des doublons
    if formation:
        existante   = Inscription.objects.filter(utilisateur=request.user, formation=formation).first()
        doublon_msg = f"Vous etes deja inscrit(e) a la formation {formation.nom}."
    else:
        existante   = Inscription.objects.filter(utilisateur=request.user, formation__isnull=True, niveau=niveau).first()
        doublon_msg = f"Vous avez deja une inscription pour le Niveau {niveau}."

    if existante:
        if existante.statut == 'confirme':
            return Response({'error': doublon_msg, 'code': 'already_confirmed'}, status=400)
        elif existante.statut == 'en_attente':
            return Response(
                {'error': "Votre inscription est deja en attente de validation.", 'code': 'already_pending'},
                status=400
            )
        elif existante.statut == 'rejete':
            existante.delete()

    # 4) Création de l'inscription
    insc = Inscription.objects.create(
        utilisateur=request.user,
        formation=formation,
        niveau=niveau,
        telephone=telephone,
        statut='en_attente'
    )

    niveau_labels = {'A': 'Niveau A – Débutant', 'B': 'Niveau B – Intermédiaire', 'C': 'Niveau C – Avancé'}
    niveau_label  = niveau_labels.get(niveau, f'Niveau {niveau}')
    nom_cours     = formation.nom if formation else niveau_label

    # 5) Email de confirmation
    try:
        _send_html_email(
            subject   = f'📋 Inscription {nom_cours} reçue – En attente de validation',
            to_email  = request.user.email,
            preheader = f"Votre demande d'inscription au {nom_cours} a bien été reçue.",
            body_html = (
                f"<p>Bonjour <strong>{request.user.first_name or request.user.username}</strong>,</p>"
                f"<p>Votre demande d'inscription au <strong>« {nom_cours} »</strong> "
                f"a bien été reçue.</p>"
                f"<div style='margin:20px 0;padding:16px 20px;background:#fff8e1;"
                f"border-radius:8px;border-left:4px solid #FF9800;'>"
                f"<p style='margin:0;font-size:14px;color:#555;'>"
                f"⏳ <strong>Votre inscription est actuellement en attente de validation "
                f"par l'administrateur.</strong><br>"
                f"Vous recevrez un email dès que votre accès aux cours sera activé.</p></div>"
                f"<p style='font-size:13px;color:#888;'>Merci de votre patience.</p>"
            ),
        )
    except Exception:
        pass  # Ne pas bloquer l'inscription si l'email échoue

    return Response({
        'message': f"Inscription à {nom_cours} enregistrée.",
        'statut': insc.statut
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auto_login(request):
    """Connexion automatique via lien email (uid + token Django)."""
    uid_b64 = request.GET.get('uid', '')
    token   = request.GET.get('token', '')
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5181')
    try:
        uid  = force_str(urlsafe_base64_decode(uid_b64))
        user = User.objects.get(pk=uid)
    except Exception:
        return redirect(f"{frontend_url}/login?error=invalid_link")

    if not default_token_generator.check_token(user, token):
        return redirect(f"{frontend_url}/login?error=expired_link")

    refresh = RefreshToken.for_user(user)
    inscriptions = Inscription.objects.filter(utilisateur=user).values('niveau', 'statut')
    niveaux_inscrits = list(inscriptions)
    photo_url = getattr(getattr(user, 'profil', None), 'photo_url', '') or ''

    params = urllib.parse.urlencode({
        'access':           str(refresh.access_token),
        'refresh':          str(refresh),
        'role':             'etudiant',
        'niveaux_inscrits': json.dumps(niveaux_inscrits),
        'photo_url':        photo_url,
        'is_new_user':      '0',
    })
    return redirect(f"{frontend_url}/auth/google/success?{params}")