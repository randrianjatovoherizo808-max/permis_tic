from django.db import models
from django.contrib.auth.models import User


# ── Profil étendu (téléphone, rôle explicite) ─────────────────────────────────
class Profil(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('formateur', 'Formateur'), ('etudiant', 'Étudiant')]
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    telephone = models.CharField(max_length=30, blank=True)
    photo_url = models.URLField(blank=True, default='')
    role      = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"


# ── Site de formation ─────────────────────────────────────────────────────────
class Site(models.Model):
    nom       = models.CharField(max_length=200)
    adresse   = models.TextField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    photo_url = models.URLField(blank=True, default='')
    email     = models.EmailField(blank=True)
    actif     = models.BooleanField(default=True)

    def __str__(self):
        return self.nom


# ── Formation ─────────────────────────────────────────────────────────────────
class Formation(models.Model):
    NIVEAU_CHOICES = [('A', 'Niveau A'), ('B', 'Niveau B'), ('C', 'Niveau C')]
    nom         = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    niveau      = models.CharField(max_length=1, choices=NIVEAU_CHOICES)
    duree       = models.IntegerField(default=20, help_text='Durée en heures')
    places      = models.IntegerField(default=30)
    coefficient = models.IntegerField(default=2)
    formateur   = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='formations_enseignees'
    )
    cree_le     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} (Niveau {self.niveau})"


# ── Leçon ─────────────────────────────────────────────────────────────────────
class Lecon(models.Model):
    formation  = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='lecons')
    titre      = models.CharField(max_length=200)
    contenu    = models.TextField(blank=True)
    ordre      = models.IntegerField(default=0)
    ressources = models.TextField(blank=True, help_text='URLs séparées par des virgules')
    fichier    = models.FileField(upload_to='lecons/fichiers/', null=True, blank=True)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return f"{self.formation.nom} — {self.titre}"


# ── Inscription ───────────────────────────────────────────────────────────────
class Inscription(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme',   'Confirmé'),
        ('rejete',     'Rejeté'),
    ]
    NIVEAU_CHOICES = [('A', 'Niveau A'), ('B', 'Niveau B'), ('C', 'Niveau C')]

    utilisateur      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions')
    formation        = models.ForeignKey('Formation', null=True, blank=True, on_delete=models.SET_NULL, related_name='inscriptions')
    niveau           = models.CharField(max_length=1, choices=NIVEAU_CHOICES)
    statut           = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    motif_rejet      = models.TextField(blank=True)
    telephone        = models.CharField(max_length=30, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['utilisateur', 'formation'],
                condition=models.Q(formation__isnull=False),
                name='unique_inscription_formation'
            ),
            models.UniqueConstraint(
                fields=['utilisateur', 'niveau'],
                condition=models.Q(formation__isnull=True),
                name='unique_inscription_niveau'
            ),
        ]

    def __str__(self):
        return f"{self.utilisateur.get_full_name()} → Niveau {self.niveau} ({self.statut})"


# ── Session (Calendrier) ──────────────────────────────────────────────────────
class Session(models.Model):
    formation  = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='sessions')
    site       = models.ForeignKey(Site, null=True, blank=True, on_delete=models.SET_NULL)
    formateur  = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sessions_animees'
    )
    date_debut = models.DateField()
    date_fin   = models.DateField()
    heure      = models.TimeField(null=True, blank=True)
    notes      = models.TextField(blank=True)

    def __str__(self):
        return f"{self.formation.nom} — {self.date_debut}"


# ── Note ──────────────────────────────────────────────────────────────────────
class Note(models.Model):
    apprenant   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    formation   = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='notes')
    valeur      = models.DecimalField(max_digits=5, decimal_places=2)
    commentaire = models.TextField(blank=True)
    date        = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.apprenant.get_full_name()} — {self.formation.nom} : {self.valeur}/20"


# ── Certificat ────────────────────────────────────────────────────────────────
class Certificat(models.Model):
    apprenant    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificats')
    formation    = models.ForeignKey(Formation, on_delete=models.SET_NULL, null=True, blank=True, related_name='certificats')
    niveau       = models.CharField(max_length=1, choices=[('A', 'Niveau A'), ('B', 'Niveau B'), ('C', 'Niveau C')], blank=True, default='')
    numero       = models.CharField(max_length=50, unique=True)
    date_delivrance = models.DateField(auto_now_add=True)
    date_debut   = models.DateField(null=True, blank=True)
    date_fin     = models.DateField(null=True, blank=True)
    mention      = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Certificat {self.numero} — {self.apprenant.get_full_name()}"


# ── Paramètres de l'établissement ────────────────────────────────────────────
class Parametres(models.Model):
    nom           = models.CharField(max_length=200, default='PERMIS TIC')
    adresse       = models.TextField(blank=True)
    telephone     = models.CharField(max_length=30, blank=True)
    email         = models.EmailField(blank=True)
    photo_url     = models.URLField(blank=True, default='')
    # Contact WhatsApp affiché sur la page d'accueil
    whatsapp      = models.CharField(max_length=30, blank=True, default='')
    whatsapp_nom  = models.CharField(max_length=100, blank=True, default='')
    # Textes UI personnalisables
    slogan        = models.CharField(max_length=255, blank=True, default='')
    description   = models.TextField(blank=True, default='')
    # Réseaux sociaux
    facebook      = models.URLField(blank=True, default='')
    # Pied de page
    footer_texte  = models.CharField(max_length=255, blank=True, default='Centre de Formation Professionnelle')
    # Contenu des 3 niveaux (JSON : liste de {name, icon})
    niveau_a_titre = models.CharField(max_length=100, blank=True, default='Niveau A')
    niveau_a_sous  = models.CharField(max_length=100, blank=True, default='Débutant')
    niveau_a_desc  = models.TextField(blank=True, default='Maîtrisez les outils bureautiques essentiels utilisés dans tous les métiers.')
    niveau_a_items = models.JSONField(default=list, blank=True)  # [{name, icon}, ...]
    niveau_b_titre = models.CharField(max_length=100, blank=True, default='Niveau B')
    niveau_b_sous  = models.CharField(max_length=100, blank=True, default='Intermédiaire')
    niveau_b_desc  = models.TextField(blank=True, default='Explorez le design graphique et créez des visuels professionnels percutants.')
    niveau_b_items = models.JSONField(default=list, blank=True)
    niveau_c_titre = models.CharField(max_length=100, blank=True, default='Niveau C')
    niveau_c_sous  = models.CharField(max_length=100, blank=True, default='Avancé')
    niveau_c_desc  = models.TextField(blank=True, default='Devenez développeur ou expert cybersécurité avec les technologies actuelles.')
    niveau_c_items = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name_plural = 'Paramètres'

    def __str__(self):
        return self.nom

    @classmethod
    def instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class OtpCode(models.Model):
    """Code OTP pour réinitialisation mot de passe (style Google/Facebook)."""
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    def is_valid(self):
        from django.utils import timezone
        import datetime
        # Valide 10 minutes
        return not self.used and (timezone.now() - self.created_at) < datetime.timedelta(minutes=10)

    def __str__(self):
        return f"OTP {self.code} pour {self.user.email}"