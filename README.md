# PERMIS TIC — Guide d'installation complet

## Structure des fichiers à copier

```
django_project/
├── api/
│   ├── __init__.py          ← REMPLACER
│   ├── admin.py             ← REMPLACER
│   ├── models.py            ← REMPLACER (nouveaux modèles)
│   ├── serializers.py       ← NOUVEAU
│   ├── views.py             ← REMPLACER (tous les endpoints)
│   ├── urls.py              ← REMPLACER (toutes les routes)
│   └── migrations/
│       ├── __init__.py      ← REMPLACER
│       └── 0001_initial.py  ← REMPLACER (nouvelle migration)
├── backend/
│   ├── settings.py          ← REMPLACER
│   └── urls.py              ← REMPLACER
├── frontend/                ← REMPLACER TOUT LE DOSSIER
└── requirements.txt         ← NOUVEAU
```

---

## 1. Installation Backend

```bash
cd django_project

# Installer les dépendances Python
pip install -r requirements.txt

# Supprimer l'ancienne base et recréer
# (dans psql ou pgAdmin : DROP DATABASE projet; CREATE DATABASE projet;)

# Appliquer les nouvelles migrations
python manage.py migrate

# Créer un super-utilisateur admin
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

---

## 2. Installation Frontend

```bash
cd django_project/frontend

# Installer les dépendances (pinia + vue-router ajoutés)
npm install

# Lancer le serveur de dev
npm run dev
# → http://localhost:5181
```

---

## 3. Configuration Google OAuth (OBLIGATOIRE pour la connexion Google)

### Étape A — Créer les credentials Google

1. Aller sur https://console.cloud.google.com/
2. Créer un projet ou sélectionner un existant
3. Menu **APIs & Services** → **Credentials**
4. Cliquer **+ Create Credentials** → **OAuth 2.0 Client ID**
5. Type d'application : **Web application**
6. **Authorized redirect URIs** — ajouter :
   ```
   http://localhost:8000/api/auth/google/callback/
   ```
7. Copier le **Client ID** et le **Client Secret**

### Étape B — Configurer Django

Dans `backend/settings.py`, remplacer :
```python
GOOGLE_CLIENT_ID     = 'VOTRE_CLIENT_ID.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'VOTRE_CLIENT_SECRET'
```

---

## 4. Flux complet de la connexion Google

```
[LoginView] Clic "Continuer avec Google"
    ↓
window.location.href = "http://localhost:8000/api/auth/google/"
    ↓
[Django] google_login_redirect() → redirige vers Google
    ↓
[Google] Page de consentement
    ↓
[Django] google_callback() → échange code, récupère profil,
         crée/connecte user, génère JWT
    ↓
Redirect vers: http://localhost:5181/auth/google/success?access=...&refresh=...&role=...
    ↓
[Vue] GoogleAuthSuccessView → sauvegarde tokens → redirige selon rôle
      • etudiant   → /espace-apprenant
      • admin      → /admin
      • formateur  → /admin
```

---

## 5. Endpoints API disponibles

| Méthode | URL | Description |
|---------|-----|-------------|
| POST | `/api/auth/token/` | Login (email+password) |
| POST | `/api/auth/token/refresh/` | Refresh JWT |
| GET | `/api/auth/me/` | Profil utilisateur connecté |
| POST | `/api/auth/register/` | Inscription apprenant |
| GET | `/api/auth/google/` | Démarrer Google OAuth |
| GET | `/api/auth/google/callback/` | Callback Google OAuth |
| GET | `/api/users/` | Liste utilisateurs (admin) |
| GET | `/api/stats/` | Statistiques dashboard |
| GET/POST | `/api/formations/` | Formations |
| GET/POST | `/api/formations/lecons/` | Leçons |
| GET/POST | `/api/inscriptions/` | Inscriptions (admin) |
| GET | `/api/inscriptions/mon-inscription/` | Mon inscription (étudiant) |
| POST | `/api/inscriptions/{id}/confirmer/` | Confirmer inscription |
| POST | `/api/inscriptions/{id}/rejeter/` | Rejeter inscription |
| GET/POST | `/api/formations/notes/` | Notes |
| GET | `/api/notes/mes-notes/` | Mes notes (étudiant) |
| GET/POST | `/api/certificats/` | Certificats |
| GET/POST | `/api/sites/` | Sites de formation |
| GET/POST | `/api/sessions/` | Sessions calendrier |
| GET/PATCH | `/api/settings/` | Paramètres établissement |
| GET | `/api/notifications/` | Notifications admin |
