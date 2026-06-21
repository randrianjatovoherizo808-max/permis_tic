from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Profil, Site, Formation, Lecon,
    Inscription, Session, Note, Certificat, Parametres
)


# ── Utilisateur ───────────────────────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    role      = serializers.SerializerMethodField()
    prenom    = serializers.CharField(source='first_name')
    nom       = serializers.CharField(source='last_name')
    telephone = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'prenom', 'nom', 'role',
                  'telephone', 'photo_url', 'is_active', 'date_joined']

    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        if obj.is_staff:
            return 'formateur'
        return 'etudiant'

    def get_telephone(self, obj):
        try:
            return obj.profil.telephone
        except Profil.DoesNotExist:
            return ''

    def get_photo_url(self, obj):
        try:
            return obj.profil.photo_url or ''
        except Exception:
            return ''


class UserCreateSerializer(serializers.ModelSerializer):
    """Pour créer formateur ou apprenant depuis l'admin."""
    prenom    = serializers.CharField(write_only=True)
    nom       = serializers.CharField(write_only=True)
    telephone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password  = serializers.CharField(write_only=True, required=False, allow_blank=True)
    role      = serializers.ChoiceField(
        choices=['etudiant', 'formateur', 'admin'], write_only=True, required=False
    )

    class Meta:
        model  = User
        fields = ['id', 'email', 'prenom', 'nom', 'telephone', 'password', 'role']

    def create(self, validated_data):
        prenom    = validated_data.pop('prenom', '')
        nom       = validated_data.pop('nom', '')
        telephone = validated_data.pop('telephone', '')
        password  = validated_data.pop('password', '')
        role      = validated_data.pop('role', 'etudiant')
        email     = validated_data['email'].lower()

        # username unique dérivé de l'email
        base = email.split('@')[0]
        username, i = base, 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{i}"; i += 1

        user = User(
            username=username, email=email,
            first_name=prenom, last_name=nom,
            is_active=True,
            is_staff=(role in ['formateur', 'admin']),
            is_superuser=(role == 'admin'),
        )
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()

        Profil.objects.update_or_create(
            user=user,
            defaults={'telephone': telephone, 'role': role}
        )
        return user


# ── Site ──────────────────────────────────────────────────────────────────────
class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Site
        fields = '__all__'


# ── Formation ─────────────────────────────────────────────────────────────────
class FormationSerializer(serializers.ModelSerializer):
    formateur_nom = serializers.SerializerMethodField()

    class Meta:
        model  = Formation
        fields = ['id', 'nom', 'description', 'niveau', 'duree',
                  'places', 'coefficient', 'formateur', 'formateur_nom', 'cree_le']

    def get_formateur_nom(self, obj):
        if obj.formateur:
            return obj.formateur.get_full_name() or obj.formateur.email
        return None


# ── Leçon ─────────────────────────────────────────────────────────────────────
class LeconSerializer(serializers.ModelSerializer):
    formation_nom = serializers.CharField(source='formation.nom', read_only=True)

    class Meta:
        model  = Lecon
        fields = ['id', 'formation', 'formation_nom', 'titre', 'contenu', 'ordre', 'ressources', 'fichier']


# ── Inscription ───────────────────────────────────────────────────────────────
class InscriptionSerializer(serializers.ModelSerializer):
    utilisateur_nom   = serializers.SerializerMethodField()
    utilisateur_email = serializers.CharField(source='utilisateur.email', read_only=True)
    utilisateur_photo = serializers.SerializerMethodField()
    niveau_label      = serializers.SerializerMethodField()
    formation_nom     = serializers.CharField(source='formation.nom', read_only=True, allow_null=True)
    formation_niveau  = serializers.CharField(source='formation.niveau', read_only=True, allow_null=True)

    class Meta:
        model  = Inscription
        fields = ['id', 'utilisateur', 'utilisateur_nom', 'utilisateur_email',
                  'utilisateur_photo',
                  'formation', 'formation_nom', 'formation_niveau',
                  'niveau', 'niveau_label',
                  'statut', 'motif_rejet', 'telephone', 'date_inscription']

    def get_utilisateur_photo(self, obj):
        try:
            return obj.utilisateur.profil.photo_url or ''
        except Exception:
            return ''

    def get_utilisateur_nom(self, obj):
        return obj.utilisateur.get_full_name() or obj.utilisateur.email

    def get_niveau_label(self, obj):
        labels = {'A': 'Niveau A – Débutant', 'B': 'Niveau B – Intermédiaire', 'C': 'Niveau C – Avancé'}
        return labels.get(obj.niveau, f'Niveau {obj.niveau}')


# ── Session (Calendrier) ──────────────────────────────────────────────────────
class SessionSerializer(serializers.ModelSerializer):
    formation_nom  = serializers.CharField(source='formation.nom', read_only=True)
    formation_niveau = serializers.CharField(source='formation.niveau', read_only=True)
    site_nom       = serializers.CharField(source='site.nom', read_only=True, allow_null=True)
    formateur_nom  = serializers.SerializerMethodField()

    class Meta:
        model  = Session
        fields = ['id', 'formation', 'formation_nom', 'formation_niveau',
                  'site', 'site_nom', 'formateur', 'formateur_nom',
                  'date_debut', 'date_fin', 'heure', 'notes']

    def get_formateur_nom(self, obj):
        if obj.formateur:
            return obj.formateur.get_full_name() or obj.formateur.email
        return None


# ── Note ──────────────────────────────────────────────────────────────────────
class NoteSerializer(serializers.ModelSerializer):
    apprenant_nom    = serializers.SerializerMethodField()
    apprenant_photo  = serializers.SerializerMethodField()
    formation_nom    = serializers.CharField(source='formation.nom', read_only=True)
    formation_niveau = serializers.CharField(source='formation.niveau', read_only=True)

    class Meta:
        model  = Note
        fields = ['id', 'apprenant', 'apprenant_nom', 'apprenant_photo',
                  'formation', 'formation_nom', 'formation_niveau',
                  'valeur', 'commentaire', 'date']

    def get_apprenant_nom(self, obj):
        return obj.apprenant.get_full_name() or obj.apprenant.email

    def get_apprenant_photo(self, obj):
        try:
            return obj.apprenant.profil.photo_url or ''
        except Exception:
            return ''


# ── Certificat ────────────────────────────────────────────────────────────────
class CertificatSerializer(serializers.ModelSerializer):
    apprenant_nom    = serializers.SerializerMethodField()
    formation_nom    = serializers.SerializerMethodField()
    formation_niveau = serializers.SerializerMethodField()
    formation        = serializers.PrimaryKeyRelatedField(
        queryset=Formation.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model  = Certificat
        fields = ['id', 'apprenant', 'apprenant_nom',
                  'formation', 'formation_nom', 'formation_niveau',
                  'niveau', 'numero', 'date_delivrance',
                  'date_debut', 'date_fin', 'mention']

    def get_apprenant_nom(self, obj):
        return obj.apprenant.get_full_name() or obj.apprenant.email

    def get_formation_nom(self, obj):
        if obj.formation:
            return obj.formation.nom
        if obj.niveau:
            return {'A': 'Niveau A – Débutant', 'B': 'Niveau B – Intermédiaire', 'C': 'Niveau C – Avancé'}.get(obj.niveau, f'Niveau {obj.niveau}')
        return ''

    def get_formation_niveau(self, obj):
        if obj.formation:
            return obj.formation.niveau
        return obj.niveau or ''


# ── Paramètres ────────────────────────────────────────────────────────────────
class ParametresSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Parametres
        fields = [
            'nom', 'adresse', 'telephone', 'email', 'photo_url',
            'whatsapp', 'whatsapp_nom',
            'slogan', 'description',
            'facebook', 'footer_texte',
            # Niveaux A / B / C
            'niveau_a_titre', 'niveau_a_sous', 'niveau_a_desc', 'niveau_a_items',
            'niveau_b_titre', 'niveau_b_sous', 'niveau_b_desc', 'niveau_b_items',
            'niveau_c_titre', 'niveau_c_sous', 'niveau_c_desc', 'niveau_c_items',
        ]