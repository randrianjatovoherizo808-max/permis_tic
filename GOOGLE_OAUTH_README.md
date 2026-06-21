# Configuration Google OAuth

## 🚨 IMPORTANT : Configuration requise

L'erreur `401: invalid_client` indique que les identifiants Google OAuth ne sont pas configurés correctement.

## 📋 Étapes pour corriger :

### 1. Créer une application Google OAuth

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez-en un existant
3. Activez l'API Google+ :
   - APIs & Services → Bibliothèque → Google+ API
4. Créez des identifiants OAuth :
   - APIs & Services → Identifiants
   - Créer des identifiants → ID client OAuth 2.0
   - Type d'application : **Application Web**
   - Nom : "Permis TIC App"
   - URI d'autorisation : `http://localhost:8000`
   - URI de redirection : `http://localhost:8000/api/auth/google/callback/`

### 2. Configurer les variables d'environnement

Modifiez le fichier `.env` avec vos vraies valeurs :

```env
GOOGLE_CLIENT_ID=votre_vrai_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=votre_vrai_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback/
FRONTEND_URL=http://localhost:5181
```

### 3. Redémarrer le serveur

```bash
python manage.py runserver
```

## 🔧 Valeurs actuelles (pour développement seulement)

Actuellement, le projet utilise des valeurs de développement qui évitent l'erreur 401 mais ne permettent pas une vraie authentification Google.

**Remplacez-les par vos vraies identifiants Google OAuth !**